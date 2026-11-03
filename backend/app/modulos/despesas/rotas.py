"""CRUD de despesas."""

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dominio.enumeracoes import TipoRecorrencia
from app.dominio.liquidacao import SaldoInsuficienteError
from app.modulos.modelos import Despesa
from app.nucleo.banco import obter_sessao
from app.nucleo_financeiro.servico_pagamentos import ServicoPagamentos
from app.nucleo_financeiro.servico_recorrencia import ServicoRecorrencia

roteador = APIRouter(prefix="/despesas", tags=["Despesas"])


class DespesaCriar(BaseModel):
    """Criação de despesa (contrato frontend)."""

    carteira_id: int | None = None
    descricao: str = Field(..., min_length=1, max_length=255)
    valor: Decimal = Field(..., max_digits=14, decimal_places=2)
    categoria_id: int | None = None
    recorrencia: TipoRecorrencia = TipoRecorrencia.UNICA
    mes_referencia: int | None = Field(default=None, ge=1, le=12)
    ano_referencia: int | None = Field(default=None, ge=2000)
    tag_ids: list[int] | None = None


class DespesaAtualizar(BaseModel):
    """Atualização parcial."""

    descricao: str | None = None
    valor: Decimal | None = Field(default=None, max_digits=14, decimal_places=2)
    categoria_id: int | None = None
    recorrencia: TipoRecorrencia | None = None
    ativo: bool | None = None


class DespesaResposta(BaseModel):
    """Despesa retornada."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    carteira_id: int | None = None
    descricao: str
    valor: Decimal
    categoria_id: int | None
    recorrencia: str
    tipo: str = "despesa"
    mes_referencia: int | None = None
    ano_referencia: int | None = None
    ativo: bool


def _gerar_mensais_ao_criar(sessao: Session, despesa: Despesa, corpo: DespesaCriar) -> None:
    if corpo.mes_referencia is None or corpo.ano_referencia is None:
        return
    meses = 12 if corpo.recorrencia == TipoRecorrencia.MENSAL else 1
    ServicoRecorrencia(sessao).gerar_despesas_mensais(
        despesa.id,
        corpo.ano_referencia,
        corpo.mes_referencia,
        meses if meses > 1 else None,
    )


@roteador.get("", response_model=list[DespesaResposta])
def listar(
    carteira_id: int | None = Query(default=None),
    sessao: Session = Depends(obter_sessao),
) -> list[DespesaResposta]:
    """Lista despesas."""
    _ = carteira_id
    despesas = sessao.scalars(select(Despesa)).all()
    return [
        DespesaResposta(
            id=d.id,
            carteira_id=carteira_id,
            descricao=d.descricao,
            valor=d.valor,
            categoria_id=d.categoria_id,
            recorrencia=d.recorrencia,
            ativo=d.ativo,
        )
        for d in despesas
    ]


@roteador.post("", response_model=DespesaResposta, status_code=201)
def criar(corpo: DespesaCriar, sessao: Session = Depends(obter_sessao)) -> DespesaResposta:
    """Cria despesa e gera ocorrências mensais."""
    despesa = Despesa(
        descricao=corpo.descricao,
        valor=corpo.valor,
        categoria_id=corpo.categoria_id,
        recorrencia=corpo.recorrencia.value,
    )
    sessao.add(despesa)
    sessao.commit()
    sessao.refresh(despesa)
    _gerar_mensais_ao_criar(sessao, despesa, corpo)
    return DespesaResposta(
        id=despesa.id,
        carteira_id=corpo.carteira_id,
        descricao=despesa.descricao,
        valor=despesa.valor,
        categoria_id=despesa.categoria_id,
        recorrencia=despesa.recorrencia,
        mes_referencia=corpo.mes_referencia,
        ano_referencia=corpo.ano_referencia,
        ativo=despesa.ativo,
    )


@roteador.get("/{despesa_id}", response_model=DespesaResposta)
def obter(despesa_id: int, sessao: Session = Depends(obter_sessao)) -> DespesaResposta:
    """Obtém despesa."""
    despesa = sessao.get(Despesa, despesa_id)
    if despesa is None:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    return DespesaResposta.model_validate(despesa)


@roteador.put("/{despesa_id}", response_model=DespesaResposta)
@roteador.patch("/{despesa_id}", response_model=DespesaResposta)
def atualizar(
    despesa_id: int,
    corpo: DespesaAtualizar,
    sessao: Session = Depends(obter_sessao),
) -> DespesaResposta:
    """Atualiza despesa."""
    despesa = sessao.get(Despesa, despesa_id)
    if despesa is None:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    dados = corpo.model_dump(exclude_unset=True)
    if "recorrencia" in dados and dados["recorrencia"] is not None:
        dados["recorrencia"] = dados["recorrencia"].value
    for chave, valor in dados.items():
        setattr(despesa, chave, valor)
    sessao.commit()
    sessao.refresh(despesa)
    return DespesaResposta.model_validate(despesa)


@roteador.delete("/{despesa_id}", status_code=204)
def excluir(despesa_id: int, sessao: Session = Depends(obter_sessao)) -> None:
    """Exclui despesa."""
    despesa = sessao.get(Despesa, despesa_id)
    if despesa is None:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    sessao.delete(despesa)
    sessao.commit()


class MarcarPagoCorpo(BaseModel):
    """Corpo legado para marcar despesa mensal paga."""

    despesa_mensal_id: int


@roteador.post("/marcar-pago")
def marcar_pago(corpo: MarcarPagoCorpo, sessao: Session = Depends(obter_sessao)) -> dict[str, int]:
    """Marca despesa mensal como paga (legado)."""
    try:
        pagamento = ServicoPagamentos(sessao).marcar_despesa_paga(corpo.despesa_mensal_id)
    except SaldoInsuficienteError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"pagamento_id": pagamento.id}
