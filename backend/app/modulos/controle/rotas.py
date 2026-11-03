"""Endpoint grade-controle."""

from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modulos.modelos import DespesaMensal, ReceitaMensal
from app.nucleo.banco import obter_sessao
from app.nucleo_financeiro.servico_calculos import ServicoCalculos

roteador = APIRouter(prefix="/controle", tags=["Controle"])


class LinhaReceita(BaseModel):
    """Linha de receita na grade."""

    id: int
    receita_id: int
    valor: Decimal
    recebido: bool


class LinhaDespesa(BaseModel):
    """Linha de despesa na grade."""

    id: int
    despesa_id: int
    valor: Decimal
    pago: bool


class IndicadoresGrade(BaseModel):
    """Totais e indicadores do mês."""

    total_receita: Decimal
    total_despesa: Decimal
    total_orcado: Decimal
    total_pago: Decimal
    saldo_caixa: Decimal
    cheque_livre: Decimal


class GradeControleResposta(BaseModel):
    """Resposta completa da grade."""

    ano: int
    mes: int
    receitas: list[LinhaReceita] = Field(default_factory=list)
    despesas: list[LinhaDespesa] = Field(default_factory=list)
    indicadores: IndicadoresGrade


@roteador.get("/grade-controle", response_model=GradeControleResposta)
def grade_controle(
    ano: int = Query(..., ge=2000),
    mes: int = Query(..., ge=1, le=12),
    sessao: Session = Depends(obter_sessao),
) -> GradeControleResposta:
    """Retorna grade do mês com listas e indicadores."""
    receitas = sessao.scalars(
        select(ReceitaMensal).where(ReceitaMensal.ano == ano, ReceitaMensal.mes == mes)
    ).all()
    despesas = sessao.scalars(
        select(DespesaMensal).where(DespesaMensal.ano == ano, DespesaMensal.mes == mes)
    ).all()

    calc = ServicoCalculos(sessao)
    ind_raw = calc.indicadores(ano, mes)

    return GradeControleResposta(
        ano=ano,
        mes=mes,
        receitas=[
            LinhaReceita(id=r.id, receita_id=r.receita_id, valor=r.valor, recebido=r.recebido)
            for r in receitas
        ],
        despesas=[
            LinhaDespesa(id=d.id, despesa_id=d.despesa_id, valor=d.valor, pago=d.pago)
            for d in despesas
        ],
        indicadores=IndicadoresGrade(**{k: ind_raw[k] for k in IndicadoresGrade.model_fields}),
    )
