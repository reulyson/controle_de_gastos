"""Compras de cartão (alias REST)."""

from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dominio.enumeracoes import TipoCompraCartao, TipoRecorrencia
from app.dominio.regras_cartao import total_fatura, valor_parcela
from app.modulos.modelos import Cartao, CompraCartao, Fatura, FaturaItem, ParcelaCartao
from app.nucleo.banco import obter_sessao

roteador = APIRouter(prefix="/compras", tags=["Compras"])


class CompraCriarFrontend(BaseModel):
    """Payload alinhado ao frontend."""

    cartao_id: int
    descricao: str
    valor: Decimal = Field(..., max_digits=14, decimal_places=2)
    parcelas: int | None = Field(default=1, ge=1)
    recorrencia: TipoRecorrencia = TipoRecorrencia.UNICA
    mes_referencia: int = Field(..., ge=1, le=12)
    ano_referencia: int = Field(..., ge=2000)


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


def _tipo_compra_de_recorrencia(rec: TipoRecorrencia, parcelas: int) -> TipoCompraCartao:
    if rec == TipoRecorrencia.MENSAL:
        return TipoCompraCartao.RECORRENTE
    if parcelas > 1:
        return TipoCompraCartao.PARCELADA
    return TipoCompraCartao.UNICA


def _registrar_compra(
    sessao: Session,
    cartao_id: int,
    corpo: CompraCriarFrontend,
) -> CompraCartao:
    cartao = sessao.get(Cartao, cartao_id)
    if cartao is None:
        raise HTTPException(status_code=404, detail="Cartão não encontrado")
    parcelas = corpo.parcelas or 1
    tipo = _tipo_compra_de_recorrencia(corpo.recorrencia, parcelas)
    compra = CompraCartao(
        cartao_id=cartao_id,
        descricao=corpo.descricao,
        valor_total=corpo.valor,
        tipo_compra=tipo.value,
        data_compra=date.today(),
        parcelas_total=parcelas if tipo == TipoCompraCartao.PARCELADA else 1,
    )
    sessao.add(compra)
    sessao.flush()

    qtd = parcelas if tipo == TipoCompraCartao.PARCELADA else 1
    valor_p = valor_parcela(corpo.valor, qtd)
    ano, mes = corpo.ano_referencia, corpo.mes_referencia

    for numero in range(1, qtd + 1):
        parcela = ParcelaCartao(
            compra_id=compra.id,
            numero=numero,
            valor=valor_p,
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
            valor=valor_p,
            tipo_compra=tipo.value,
            parcela_id=parcela.id,
            marcado_pago=False,
        )
        sessao.add(item)

        valores = list(
            sessao.scalars(select(FaturaItem.valor).where(FaturaItem.fatura_id == fat.id))
        )
        fat.valor_total = total_fatura([Decimal(str(v)) for v in valores])

        if tipo != TipoCompraCartao.PARCELADA:
            break
        if mes == 12:
            ano, mes = ano + 1, 1
        else:
            mes += 1

    sessao.commit()
    sessao.refresh(compra)
    return compra


@roteador.get("", response_model=list[CompraRespostaFrontend])
def listar_compras(
    cartao_id: int = Query(...),
    sessao: Session = Depends(obter_sessao),
) -> list[CompraRespostaFrontend]:
    """Lista compras de um cartão."""
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
) -> CompraRespostaFrontend:
    """Registra compra no cartão."""
    compra = _registrar_compra(sessao, corpo.cartao_id, corpo)
    parcela = sessao.scalar(
        select(ParcelaCartao).where(ParcelaCartao.compra_id == compra.id).limit(1)
    )
    return CompraRespostaFrontend(
        id=compra.id,
        cartao_id=compra.cartao_id,
        descricao=compra.descricao,
        valor=compra.valor_total,
        mes_referencia=parcela.mes if parcela else corpo.mes_referencia,
        ano_referencia=parcela.ano if parcela else corpo.ano_referencia,
        parcelas=compra.parcelas_total,
        recorrencia=corpo.recorrencia.value,
    )
