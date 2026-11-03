"""Rotas de fechamento."""

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.nucleo.banco import obter_sessao
from app.nucleo_financeiro.servico_fechamento import ServicoFechamento

roteador = APIRouter(prefix="/fechamento", tags=["Fechamento"])


class FechamentoResposta(BaseModel):
    """Fechamento persistido."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    ano: int
    mes: int
    saldo_inicial: Decimal
    saldo_final: Decimal
    status: str


@roteador.post("/fechar", response_model=FechamentoResposta)
def fechar_mes(
    ano: int = Query(..., ge=2000),
    mes: int = Query(..., ge=1, le=12),
    sessao: Session = Depends(obter_sessao),
) -> FechamentoResposta:
    """Fecha competência informada."""
    try:
        fechamento = ServicoFechamento(sessao).fechar_mes(ano, mes)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return FechamentoResposta.model_validate(fechamento)
