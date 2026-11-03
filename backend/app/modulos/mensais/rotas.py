"""Atualização de ocorrências mensais."""

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modulos.modelos import Despesa, DespesaMensal, Receita, ReceitaMensal
from app.nucleo.banco import obter_sessao

roteador_receitas = APIRouter(prefix="/receitas-mensais", tags=["Receitas mensais"])
roteador_despesas = APIRouter(prefix="/despesas-mensais", tags=["Despesas mensais"])


class AtualizarMensalCorpo(BaseModel):
    """Atualiza valor com escopo."""

    valor: Decimal = Field(..., max_digits=14, decimal_places=2)
    escopo: str = Field(default="somente_mes", pattern="^(somente_mes|deste_mes_em_diante)$")


def _aplicar_escopo_receita(
    sessao: Session,
    linha: ReceitaMensal,
    valor: Decimal,
    escopo: str,
) -> None:
    receita = sessao.get(Receita, linha.receita_id)
    if receita is None:
        return
    if escopo == "somente_mes":
        linha.valor = valor
        return
    mensais = sessao.scalars(
        select(ReceitaMensal).where(ReceitaMensal.receita_id == linha.receita_id)
    ).all()
    for m in mensais:
        if m.ano > linha.ano or (m.ano == linha.ano and m.mes >= linha.mes):
            m.valor = valor
    receita.valor = valor


def _aplicar_escopo_despesa(
    sessao: Session,
    linha: DespesaMensal,
    valor: Decimal,
    escopo: str,
) -> None:
    despesa = sessao.get(Despesa, linha.despesa_id)
    if despesa is None:
        return
    if escopo == "somente_mes":
        linha.valor = valor
        return
    mensais = sessao.scalars(
        select(DespesaMensal).where(DespesaMensal.despesa_id == linha.despesa_id)
    ).all()
    for m in mensais:
        if m.ano > linha.ano or (m.ano == linha.ano and m.mes >= linha.mes):
            m.valor = valor
    despesa.valor = valor


@roteador_receitas.patch("/{linha_id}")
def atualizar_receita_mensal(
    linha_id: int,
    corpo: AtualizarMensalCorpo,
    sessao: Session = Depends(obter_sessao),
) -> dict[str, str]:
    """Atualiza valor de receita mensal."""
    linha = sessao.get(ReceitaMensal, linha_id)
    if linha is None:
        raise HTTPException(status_code=404, detail="Linha não encontrada")
    _aplicar_escopo_receita(sessao, linha, corpo.valor, corpo.escopo)
    sessao.commit()
    return {"status": "ok"}


@roteador_despesas.patch("/{linha_id}")
def atualizar_despesa_mensal(
    linha_id: int,
    corpo: AtualizarMensalCorpo,
    sessao: Session = Depends(obter_sessao),
) -> dict[str, str]:
    """Atualiza valor de despesa mensal."""
    linha = sessao.get(DespesaMensal, linha_id)
    if linha is None:
        raise HTTPException(status_code=404, detail="Linha não encontrada")
    _aplicar_escopo_despesa(sessao, linha, corpo.valor, corpo.escopo)
    sessao.commit()
    return {"status": "ok"}
