"""CRUD de cartões, compras e faturas."""

from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dominio.enumeracoes import TipoCompraCartao
from app.dominio.regras_cartao import regra_item_fatura, total_fatura, valor_parcela
from app.modulos.modelos import Cartao, CompraCartao, Fatura, FaturaItem, ParcelaCartao
from app.nucleo.banco import obter_sessao
from app.nucleo_financeiro.servico_calculos import ServicoCalculos

roteador = APIRouter(prefix="/cartoes", tags=["Cartões"])


class CartaoCriar(BaseModel):
    """Criação de cartão."""

    carteira_id: int | None = None
    nome: str = Field(..., min_length=1, max_length=120)
    bandeira: str | None = None
    dia_fechamento: int = Field(default=1, ge=1, le=28)
    dia_vencimento: int = Field(default=10, ge=1, le=28)
    limite: Decimal | None = Field(default=None, max_digits=14, decimal_places=2)


class CartaoResposta(BaseModel):
    """Cartão persistido."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    carteira_id: int
    nome: str
    dia_fechamento: int
    dia_vencimento: int
    ativo: bool


class CompraCriar(BaseModel):
    """Nova compra no cartão."""

    descricao: str
    valor_total: Decimal = Field(..., max_digits=14, decimal_places=2)
    data_compra: date
    tipo_compra: TipoCompraCartao = TipoCompraCartao.UNICA
    parcelas_total: int = Field(default=1, ge=1)
    categoria_id: int | None = None
    ano_fatura: int
    mes_fatura: int


class CompraResposta(BaseModel):
    """Compra registrada."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    cartao_id: int
    descricao: str
    valor_total: Decimal
    tipo_compra: str
    parcelas_total: int


@roteador.get("", response_model=list[CartaoResposta])
def listar_cartoes(
    carteira_id: int | None = Query(default=None),
    sessao: Session = Depends(obter_sessao),
) -> list[Cartao]:
    """Lista cartões."""
    stmt = select(Cartao)
    if carteira_id is not None:
        stmt = stmt.where(Cartao.carteira_id == carteira_id)
    return list(sessao.scalars(stmt).all())


@roteador.post("", response_model=CartaoResposta, status_code=201)
def criar_cartao(corpo: CartaoCriar, sessao: Session = Depends(obter_sessao)) -> Cartao:
    """Cria cartão na carteira informada ou principal."""
    carteira = ServicoCalculos(sessao).obter_carteira()
    cid = corpo.carteira_id if corpo.carteira_id is not None else carteira.id
    cartao = Cartao(
        carteira_id=cid,
        nome=corpo.nome,
        dia_fechamento=corpo.dia_fechamento,
        dia_vencimento=corpo.dia_vencimento,
    )
    sessao.add(cartao)
    sessao.commit()
    sessao.refresh(cartao)
    return cartao


@roteador.post("/{cartao_id}/compras", response_model=CompraResposta, status_code=201)
def criar_compra(
    cartao_id: int,
    corpo: CompraCriar,
    sessao: Session = Depends(obter_sessao),
) -> CompraCartao:
    """Registra compra, parcelas e item de fatura."""
    cartao = sessao.get(Cartao, cartao_id)
    if cartao is None:
        raise HTTPException(status_code=404, detail="Cartão não encontrado")

    compra = CompraCartao(
        cartao_id=cartao_id,
        descricao=corpo.descricao,
        valor_total=corpo.valor_total,
        tipo_compra=corpo.tipo_compra.value,
        data_compra=corpo.data_compra,
        parcelas_total=corpo.parcelas_total,
        categoria_id=corpo.categoria_id,
    )
    sessao.add(compra)
    sessao.flush()

    fatura = sessao.scalar(
        select(Fatura).where(
            Fatura.cartao_id == cartao_id,
            Fatura.ano == corpo.ano_fatura,
            Fatura.mes == corpo.mes_fatura,
        )
    )
    if fatura is None:
        fatura = Fatura(cartao_id=cartao_id, ano=corpo.ano_fatura, mes=corpo.mes_fatura)
        sessao.add(fatura)
        sessao.flush()

    regra = regra_item_fatura(corpo.tipo_compra)
    parcelas = corpo.parcelas_total if corpo.tipo_compra == TipoCompraCartao.PARCELADA else 1
    valor_p = valor_parcela(corpo.valor_total, parcelas)

    ano, mes = corpo.ano_fatura, corpo.mes_fatura
    for numero in range(1, parcelas + 1):
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
            descricao=f"{corpo.descricao} ({numero}/{parcelas})",
            valor=valor_p,
            tipo_compra=corpo.tipo_compra.value,
            parcela_id=parcela.id,
            marcado_pago=False,
        )
        sessao.add(item)

        if mes == 12:
            ano, mes = ano + 1, 1
        else:
            mes += 1

    sessao.refresh(fatura)
    todos = list(sessao.scalars(select(FaturaItem.valor).where(FaturaItem.fatura_id == fatura.id)))
    fatura.valor_total = total_fatura([Decimal(str(v)) for v in todos])

    sessao.commit()
    sessao.refresh(compra)
    return compra


@roteador.get("/{cartao_id}/compras", response_model=list[CompraResposta])
def listar_compras(cartao_id: int, sessao: Session = Depends(obter_sessao)) -> list[CompraCartao]:
    """Lista compras de um cartão."""
    return list(sessao.scalars(select(CompraCartao).where(CompraCartao.cartao_id == cartao_id)).all())


class FaturaItemResposta(BaseModel):
    """Item de fatura com flags de pagamento."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    descricao: str
    valor: Decimal
    tipo_compra: str
    marcado_pago: bool
    permite_marcar_pago: bool
    apenas_informativo: bool


class FaturaDetalheResposta(BaseModel):
    """Fatura completa para o frontend."""

    cartao: CartaoResposta
    mes: int
    ano: int
    itens: list[dict]
    total: Decimal


@roteador.get("/{cartao_id}/faturas/{ano}/{mes}", response_model=FaturaDetalheResposta)
def obter_fatura(
    cartao_id: int,
    ano: int,
    mes: int,
    sessao: Session = Depends(obter_sessao),
) -> FaturaDetalheResposta:
    """Detalhe da fatura mensal."""
    cartao = sessao.get(Cartao, cartao_id)
    if cartao is None:
        raise HTTPException(status_code=404, detail="Cartão não encontrado")
    fatura = sessao.scalar(
        select(Fatura).where(Fatura.cartao_id == cartao_id, Fatura.ano == ano, Fatura.mes == mes)
    )
    itens: list[dict] = []
    total = Decimal("0.00")
    if fatura is not None:
        for item in fatura.itens:
            recorrente = item.tipo_compra == TipoCompraCartao.RECORRENTE.value
            itens.append(
                {
                    "id": str(item.id),
                    "descricao": item.descricao,
                    "valor": item.valor,
                    "recorrente": recorrente,
                    "pago": item.marcado_pago,
                }
            )
        total = fatura.valor_total
    return FaturaDetalheResposta(
        cartao=CartaoResposta.model_validate(cartao),
        mes=mes,
        ano=ano,
        itens=itens,
        total=total,
    )


@roteador.get("/{cartao_id}/faturas/{ano}/{mes}/itens", response_model=list[FaturaItemResposta])
def listar_itens_fatura(
    cartao_id: int,
    ano: int,
    mes: int,
    sessao: Session = Depends(obter_sessao),
) -> list[FaturaItemResposta]:
    """Lista itens da fatura com regras de UI."""
    fatura = sessao.scalar(
        select(Fatura).where(Fatura.cartao_id == cartao_id, Fatura.ano == ano, Fatura.mes == mes)
    )
    if fatura is None:
        return []
    resposta: list[FaturaItemResposta] = []
    for item in fatura.itens:
        regra = regra_item_fatura(TipoCompraCartao(item.tipo_compra))
        resposta.append(
            FaturaItemResposta(
                id=item.id,
                descricao=item.descricao,
                valor=item.valor,
                tipo_compra=item.tipo_compra,
                marcado_pago=item.marcado_pago,
                permite_marcar_pago=regra.permite_marcar_pago,
                apenas_informativo=regra.apenas_informativo,
            )
        )
    return resposta
