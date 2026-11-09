"""CRUD de despesas."""

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dominio.liquidacao import SaldoInsuficienteError
from app.modulos.modelos import Despesa, Usuario
from app.modulos.schemas_lancamento import (
    LancamentoAtualizarBase,
    LancamentoCriarBase,
    aplicar_atualizacao_lancamento,
    gerar_mensais_ao_criar,
)
from app.nucleo.banco import obter_sessao
from app.nucleo.deps_auth import obter_carteira_do_usuario, obter_usuario_atual
from app.nucleo_financeiro.servico_pagamentos import ServicoPagamentos

roteador = APIRouter(prefix="/despesas", tags=["Despesas"])


class DespesaCriar(LancamentoCriarBase):
    """Criação de despesa."""


class DespesaAtualizar(LancamentoAtualizarBase):
    """Atualização de despesa."""


class DespesaResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    carteira_id: int
    descricao: str
    valor: Decimal
    categoria_id: int | None
    recorrencia: str
    valor_variavel: bool = False
    tipo: str = "despesa"
    mes_referencia: int | None = None
    ano_referencia: int | None = None
    ativo: bool


def _resposta(d: Despesa) -> DespesaResposta:
    return DespesaResposta(
        id=d.id,
        carteira_id=d.carteira_id,
        descricao=d.descricao,
        valor=d.valor,
        categoria_id=d.categoria_id,
        recorrencia=d.recorrencia,
        valor_variavel=bool(d.valor_variavel),
        ativo=d.ativo,
    )


@roteador.get("", response_model=list[DespesaResposta])
def listar(
    carteira_id: int = Query(...),
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> list[DespesaResposta]:
    obter_carteira_do_usuario(carteira_id, usuario, sessao)
    despesas = sessao.scalars(select(Despesa).where(Despesa.carteira_id == carteira_id)).all()
    return [_resposta(d) for d in despesas]


@roteador.post("", response_model=DespesaResposta, status_code=201)
def criar(
    corpo: DespesaCriar,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> DespesaResposta:
    obter_carteira_do_usuario(corpo.carteira_id, usuario, sessao)
    despesa = Despesa(
        carteira_id=corpo.carteira_id,
        descricao=corpo.descricao,
        valor=corpo.valor,
        categoria_id=corpo.categoria_id,
        recorrencia=corpo.recorrencia.value,
        valor_variavel=corpo.valor_variavel,
    )
    sessao.add(despesa)
    sessao.commit()
    sessao.refresh(despesa)
    gerar_mensais_ao_criar(
        sessao,
        tipo="despesa",
        lancamento_id=despesa.id,
        recorrencia=corpo.recorrencia,
        mes_referencia=corpo.mes_referencia,
        ano_referencia=corpo.ano_referencia,
        quantidade_meses=corpo.quantidade_meses,
    )
    return DespesaResposta(
        id=despesa.id,
        carteira_id=despesa.carteira_id,
        descricao=despesa.descricao,
        valor=despesa.valor,
        categoria_id=despesa.categoria_id,
        recorrencia=despesa.recorrencia,
        valor_variavel=bool(despesa.valor_variavel),
        mes_referencia=corpo.mes_referencia,
        ano_referencia=corpo.ano_referencia,
        ativo=despesa.ativo,
    )


@roteador.get("/{despesa_id}", response_model=DespesaResposta)
def obter(
    despesa_id: int,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> DespesaResposta:
    despesa = sessao.get(Despesa, despesa_id)
    if despesa is None:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    obter_carteira_do_usuario(despesa.carteira_id, usuario, sessao)
    return _resposta(despesa)


@roteador.put("/{despesa_id}", response_model=DespesaResposta)
@roteador.patch("/{despesa_id}", response_model=DespesaResposta)
def atualizar(
    despesa_id: int,
    corpo: DespesaAtualizar,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> DespesaResposta:
    despesa = sessao.get(Despesa, despesa_id)
    if despesa is None:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    obter_carteira_do_usuario(despesa.carteira_id, usuario, sessao)
    aplicar_atualizacao_lancamento(
        entidade=despesa,
        dados=corpo.model_dump(exclude_unset=True),
    )
    sessao.commit()
    sessao.refresh(despesa)
    return _resposta(despesa)


@roteador.delete("/{despesa_id}", status_code=204)
def excluir(
    despesa_id: int,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> None:
    despesa = sessao.get(Despesa, despesa_id)
    if despesa is None:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    obter_carteira_do_usuario(despesa.carteira_id, usuario, sessao)
    sessao.delete(despesa)
    sessao.commit()


class MarcarPagoCorpo(BaseModel):
    despesa_mensal_id: int


@roteador.post("/marcar-pago")
def marcar_pago(
    corpo: MarcarPagoCorpo,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> dict[str, int]:
    _ = usuario
    try:
        pagamento = ServicoPagamentos(sessao).marcar_despesa_paga(corpo.despesa_mensal_id)
    except SaldoInsuficienteError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"pagamento_id": pagamento.id}
