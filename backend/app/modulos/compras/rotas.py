"""Compras de cartão (alias REST)."""

from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dominio.enumeracoes import TipoCompraCartao, TipoRecorrencia
from app.dominio.regras_cartao import total_fatura, valor_parcela
from app.modulos.modelos import Cartao, CompraCartao, Fatura, FaturaItem, ParcelaCartao, Usuario
from app.nucleo.banco import obter_sessao
from app.nucleo.deps_auth import obter_carteira_do_usuario, obter_usuario_atual

roteador = APIRouter(prefix="/compras", tags=["Compras"])


class CompraCriarFrontend(BaseModel):
    """Payload alinhado ao frontend."""

    cartao_id: int
    descricao: str
    valor: Decimal = Field(..., max_digits=14, decimal_places=2)
    parcelas: int | None = Field(default=None, ge=1)
    quantidade_meses: int | None = Field(default=None, ge=1, le=120)
    recorrencia: TipoRecorrencia = TipoRecorrencia.UNICA
    data_vencimento: date | None = None
    mes_referencia: int | None = Field(default=None, ge=1, le=12)
    ano_referencia: int | None = Field(default=None, ge=2000)
    categoria_id: int | None = None


class CompraRespostaFrontend(BaseModel):
    """Compra retornada ao frontend."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    cartao_id: int
    descricao: str
    valor: Decimal
    mes_referencia: int
    ano_referencia: int
    parcelas: int | None = None
    recorrencia: str | None = None
    pago: bool = False


def _tipo_compra(rec: TipoRecorrencia, parcelas: int) -> TipoCompraCartao:
    if rec == TipoRecorrencia.MENSAL:
        return TipoCompraCartao.RECORRENTE
    if parcelas > 1:
        return TipoCompraCartao.PARCELADA
    return TipoCompraCartao.UNICA


def _competencia_inicial(corpo: CompraCriarFrontend, data_ref: date) -> tuple[int, int]:
    if corpo.ano_referencia is not None and corpo.mes_referencia is not None:
        return corpo.ano_referencia, corpo.mes_referencia
    return data_ref.year, data_ref.month


def _qtd_e_valor(tipo: TipoCompraCartao, corpo: CompraCriarFrontend) -> tuple[int, Decimal]:
    if tipo == TipoCompraCartao.RECORRENTE:
        qtd = corpo.quantidade_meses or 12
        return qtd, corpo.valor
    if tipo == TipoCompraCartao.PARCELADA:
        qtd = corpo.parcelas or 1
        return qtd, valor_parcela(corpo.valor, qtd)
    return 1, corpo.valor


def _avancar_mes(ano: int, mes: int) -> tuple[int, int]:
    if mes == 12:
        return ano + 1, 1
    return ano, mes + 1


def _registrar_compra(
    sessao: Session,
    cartao_id: int,
    corpo: CompraCriarFrontend,
) -> CompraCartao:
    cartao = sessao.get(Cartao, cartao_id)
    if cartao is None:
        raise HTTPException(status_code=404, detail="Cartão não encontrado")

    data_ref = corpo.data_vencimento or date.today()
    parcelas_informadas = corpo.parcelas or 1
    tipo = _tipo_compra(corpo.recorrencia, parcelas_informadas)
    qtd, valor_item = _qtd_e_valor(tipo, corpo)
    ano, mes = _competencia_inicial(corpo, data_ref)

    compra = CompraCartao(
        cartao_id=cartao_id,
        descricao=corpo.descricao,
        valor_total=corpo.valor,
        tipo_compra=tipo.value,
        data_compra=data_ref,
        parcelas_total=qtd,
        categoria_id=corpo.categoria_id,
    )
    sessao.add(compra)
    sessao.flush()

    for numero in range(1, qtd + 1):
        parcela = ParcelaCartao(
            compra_id=compra.id,
            numero=numero,
            valor=valor_item,
            ano=ano,
            mes=mes,
        )
        sessao.add(parcela)
        sessao.flush()

        fat = sessao.scalar(
            select(Fatura).where(Fatura.cartao_id == cartao_id, Fatura.ano == ano, Fatura.mes == mes)
        )
        if fat is None:
            fat = Fatura(cartao_id=cartao_id, ano=ano, mes=mes)
            sessao.add(fat)
            sessao.flush()

        item = FaturaItem(
            fatura_id=fat.id,
            descricao=f"{corpo.descricao} ({numero}/{qtd})" if qtd > 1 else corpo.descricao,
            valor=valor_item,
            tipo_compra=tipo.value,
            parcela_id=parcela.id,
            marcado_pago=False,
        )
        sessao.add(item)

        valores = list(
            sessao.scalars(select(FaturaItem.valor).where(FaturaItem.fatura_id == fat.id))
        )
        fat.valor_total = total_fatura([Decimal(str(v)) for v in valores])
        ano, mes = _avancar_mes(ano, mes)

    sessao.commit()
    sessao.refresh(compra)
    return compra


@roteador.get("", response_model=list[CompraRespostaFrontend])
def listar_compras(
    cartao_id: int = Query(...),
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> list[CompraRespostaFrontend]:
    """Lista compras de um cartão."""
    cartao = sessao.get(Cartao, cartao_id)
    if cartao is None:
        raise HTTPException(status_code=404, detail="Cartão não encontrado")
    obter_carteira_do_usuario(cartao.carteira_id, usuario, sessao)
    compras = sessao.scalars(select(CompraCartao).where(CompraCartao.cartao_id == cartao_id)).all()
    resposta: list[CompraRespostaFrontend] = []
    for c in compras:
        parcela = sessao.scalar(
            select(ParcelaCartao)
            .where(ParcelaCartao.compra_id == c.id)
            .order_by(ParcelaCartao.numero)
            .limit(1)
        )
        resposta.append(
            CompraRespostaFrontend(
                id=c.id,
                cartao_id=c.cartao_id,
                descricao=c.descricao,
                valor=c.valor_total,
                mes_referencia=parcela.mes if parcela else 1,
                ano_referencia=parcela.ano if parcela else date.today().year,
                parcelas=c.parcelas_total,
                recorrencia="mensal"
                if c.tipo_compra == TipoCompraCartao.RECORRENTE.value
                else "unica",
            )
        )
    return resposta


@roteador.post("", response_model=CompraRespostaFrontend, status_code=201)
def criar_compra(
    corpo: CompraCriarFrontend,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> CompraRespostaFrontend:
    """Registra compra no cartão."""
    cartao = sessao.get(Cartao, corpo.cartao_id)
    if cartao is None:
        raise HTTPException(status_code=404, detail="Cartão não encontrado")
    obter_carteira_do_usuario(cartao.carteira_id, usuario, sessao)
    compra = _registrar_compra(sessao, corpo.cartao_id, corpo)
    parcela = sessao.scalar(
        select(ParcelaCartao).where(ParcelaCartao.compra_id == compra.id).limit(1)
    )
    data_ref = corpo.data_vencimento or date.today()
    return CompraRespostaFrontend(
        id=compra.id,
        cartao_id=compra.cartao_id,
        descricao=compra.descricao,
        valor=compra.valor_total,
        mes_referencia=parcela.mes if parcela else data_ref.month,
        ano_referencia=parcela.ano if parcela else data_ref.year,
        parcelas=compra.parcelas_total,
        recorrencia=corpo.recorrencia.value,
    )
