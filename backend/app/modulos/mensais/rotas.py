"""Atualização de ocorrências mensais."""

from decimal import Decimal
from typing import Protocol

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modulos.modelos import Despesa, DespesaMensal, Receita, ReceitaMensal, Usuario
from app.nucleo.banco import obter_sessao
from app.nucleo.deps_auth import obter_carteira_do_usuario, obter_usuario_atual

roteador_receitas = APIRouter(prefix="/receitas-mensais", tags=["Receitas mensais"])
roteador_despesas = APIRouter(prefix="/despesas-mensais", tags=["Despesas mensais"])


class AtualizarMensalCorpo(BaseModel):
    """Atualiza valor com escopo."""

    valor: Decimal = Field(..., max_digits=14, decimal_places=2)
    escopo: str = Field(default="somente_mes", pattern="^(somente_mes|deste_mes_em_diante)$")


class _LinhaMensal(Protocol):
    ano: int
    mes: int
    valor: Decimal


def _aplicar_escopo(
    sessao: Session,
    linha: _LinhaMensal,
    valor: Decimal,
    escopo: str,
    *,
    parent_attr: str,
    parent_id: int,
    modelo_mensal: type[ReceitaMensal] | type[DespesaMensal],
    parent: Receita | Despesa,
) -> None:
    if escopo == "somente_mes":
        linha.valor = valor
        return
    mensais = sessao.scalars(
        select(modelo_mensal).where(getattr(modelo_mensal, parent_attr) == parent_id)
    ).all()
    for m in mensais:
        if m.ano > linha.ano or (m.ano == linha.ano and m.mes >= linha.mes):
            m.valor = valor
    parent.valor = valor


@roteador_receitas.patch("/{linha_id}")
def atualizar_receita_mensal(
    linha_id: int,
    corpo: AtualizarMensalCorpo,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> dict[str, str]:
    """Atualiza valor de receita mensal."""
    linha = sessao.get(ReceitaMensal, linha_id)
    if linha is None:
        raise HTTPException(status_code=404, detail="Linha não encontrada")
    receita = sessao.get(Receita, linha.receita_id)
    if receita is None:
        raise HTTPException(status_code=404, detail="Linha não encontrada")
    obter_carteira_do_usuario(receita.carteira_id, usuario, sessao)
    _aplicar_escopo(
        sessao,
        linha,
        corpo.valor,
        corpo.escopo,
        parent_attr="receita_id",
        parent_id=linha.receita_id,
        modelo_mensal=ReceitaMensal,
        parent=receita,
    )
    sessao.commit()
    return {"status": "ok"}


@roteador_despesas.patch("/{linha_id}")
def atualizar_despesa_mensal(
    linha_id: int,
    corpo: AtualizarMensalCorpo,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> dict[str, str]:
    """Atualiza valor de despesa mensal."""
    linha = sessao.get(DespesaMensal, linha_id)
    if linha is None:
        raise HTTPException(status_code=404, detail="Linha não encontrada")
    despesa = sessao.get(Despesa, linha.despesa_id)
    if despesa is None:
        raise HTTPException(status_code=404, detail="Linha não encontrada")
    obter_carteira_do_usuario(despesa.carteira_id, usuario, sessao)
    _aplicar_escopo(
        sessao,
        linha,
        corpo.valor,
        corpo.escopo,
        parent_attr="despesa_id",
        parent_id=linha.despesa_id,
        modelo_mensal=DespesaMensal,
        parent=despesa,
    )
    sessao.commit()
    return {"status": "ok"}
