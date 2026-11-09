"""CRUD de cartões, compras e faturas."""

from datetime import date
from decimal import Decimal
import re

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dominio.enumeracoes import TipoCompraCartao
from app.dominio.regras_cartao import regra_item_fatura, total_fatura, valor_parcela
from app.modulos.modelos import Cartao, CompraCartao, Fatura, FaturaItem, ParcelaCartao, Usuario
from app.nucleo.banco import obter_sessao
from app.nucleo.deps_auth import obter_carteira_do_usuario, obter_usuario_atual

roteador = APIRouter(prefix="/cartoes", tags=["Cartões"])

_FINAL4 = re.compile(r"^\d{4}$")


class CartaoCriar(BaseModel):
    carteira_id: int
    nome: str = Field(..., min_length=1, max_length=120)
    bandeira: str | None = None
    final_4: str | None = None
    dia_fechamento: int = Field(default=1, ge=1, le=28)
    dia_vencimento: int = Field(default=10, ge=1, le=28)
    limite: Decimal | None = Field(default=None, max_digits=14, decimal_places=2)

    @field_validator("final_4")
    @classmethod
    def validar_final4(cls, valor: str | None) -> str | None:
        if valor is None or valor == "":
            return None
        if not _FINAL4.match(valor):
            raise ValueError("final_4 deve ter exatamente 4 dígitos")
        return valor


class CartaoAtualizar(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    bandeira: str | None = None
    final_4: str | None = None
    dia_fechamento: int | None = Field(default=None, ge=1, le=28)
    dia_vencimento: int | None = Field(default=None, ge=1, le=28)
    limite: Decimal | None = Field(default=None, max_digits=14, decimal_places=2)

    @field_validator("final_4")
    @classmethod
    def validar_final4(cls, valor: str | None) -> str | None:
        if valor is None or valor == "":
            return None
        if not _FINAL4.match(valor):
            raise ValueError("final_4 deve ter exatamente 4 dígitos")
        return valor


class CartaoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    carteira_id: int
    nome: str
    bandeira: str | None = None
    final_4: str | None = None
    limite: Decimal = Decimal("0.00")
    dia_fechamento: int
    dia_vencimento: int
    ativo: bool


class CompraCriar(BaseModel):
    descricao: str
    valor_total: Decimal = Field(..., max_digits=14, decimal_places=2)
    data_compra: date
    tipo_compra: TipoCompraCartao = TipoCompraCartao.UNICA
    parcelas_total: int = Field(default=1, ge=1)
    categoria_id: int | None = None
    ano_fatura: int
    mes_fatura: int


class CompraResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cartao_id: int
    descricao: str
    valor_total: Decimal
    tipo_compra: str
    parcelas_total: int


def _cartao_do_usuario(cartao_id: int, usuario: Usuario, sessao: Session) -> Cartao:
    cartao = sessao.get(Cartao, cartao_id)
    if cartao is None:
        raise HTTPException(status_code=404, detail="Cartão não encontrado")
    obter_carteira_do_usuario(cartao.carteira_id, usuario, sessao)
    return cartao


@roteador.get("", response_model=list[CartaoResposta])
def listar_cartoes(
    carteira_id: int = Query(...),
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> list[Cartao]:
    obter_carteira_do_usuario(carteira_id, usuario, sessao)
    return list(
        sessao.scalars(select(Cartao).where(Cartao.carteira_id == carteira_id)).all()
    )


@roteador.post("", response_model=CartaoResposta, status_code=201)
def criar_cartao(
    corpo: CartaoCriar,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> Cartao:
    obter_carteira_do_usuario(corpo.carteira_id, usuario, sessao)
    cartao = Cartao(
        carteira_id=corpo.carteira_id,
        nome=corpo.nome.strip(),
        bandeira=(corpo.bandeira or "").strip() or None,
        final_4=corpo.final_4,
        limite=corpo.limite or Decimal("0.00"),
        dia_fechamento=corpo.dia_fechamento,
        dia_vencimento=corpo.dia_vencimento,
    )
    sessao.add(cartao)
    sessao.commit()
    sessao.refresh(cartao)
    return cartao


@roteador.patch("/{cartao_id}", response_model=CartaoResposta)
def atualizar_cartao(
    cartao_id: int,
    corpo: CartaoAtualizar,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> Cartao:
    cartao = _cartao_do_usuario(cartao_id, usuario, sessao)
    dados = corpo.model_dump(exclude_unset=True)
    if "nome" in dados and dados["nome"] is not None:
        cartao.nome = dados["nome"].strip()
    if "bandeira" in dados:
        cartao.bandeira = (dados["bandeira"] or "").strip() or None
    if "final_4" in dados:
        cartao.final_4 = dados["final_4"]
    if "limite" in dados and dados["limite"] is not None:
        cartao.limite = dados["limite"]
    if "dia_fechamento" in dados and dados["dia_fechamento"] is not None:
        cartao.dia_fechamento = dados["dia_fechamento"]
    if "dia_vencimento" in dados and dados["dia_vencimento"] is not None:
        cartao.dia_vencimento = dados["dia_vencimento"]
    sessao.commit()
    sessao.refresh(cartao)
    return cartao


@roteador.post("/{cartao_id}/compras", response_model=CompraResposta, status_code=201)
def criar_compra(
    cartao_id: int,
    corpo: CompraCriar,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> CompraCartao:
    _cartao_do_usuario(cartao_id, usuario, sessao)

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
def listar_compras(
    cartao_id: int,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> list[CompraCartao]:
    _cartao_do_usuario(cartao_id, usuario, sessao)
    return list(sessao.scalars(select(CompraCartao).where(CompraCartao.cartao_id == cartao_id)).all())


class FaturaItemResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    descricao: str
    valor: Decimal
    tipo_compra: str
    marcado_pago: bool
    permite_marcar_pago: bool
    apenas_informativo: bool


class FaturaDetalheResposta(BaseModel):
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
    usuario: Usuario = Depends(obter_usuario_atual),
) -> FaturaDetalheResposta:
    cartao = _cartao_do_usuario(cartao_id, usuario, sessao)
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
    usuario: Usuario = Depends(obter_usuario_atual),
) -> list[FaturaItemResposta]:
    _cartao_do_usuario(cartao_id, usuario, sessao)
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
