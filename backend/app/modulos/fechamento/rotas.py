"""Rotas de fechamento."""

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.modulos.modelos import Usuario
from app.nucleo.banco import obter_sessao
from app.nucleo.deps_auth import obter_carteira_do_usuario, obter_usuario_atual
from app.nucleo_financeiro.servico_fechamento import ServicoFechamento

roteador = APIRouter(prefix="/fechamento", tags=["Fechamento"])


class FechamentoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ano: int
    mes: int
    saldo_inicial: Decimal
    saldo_final: Decimal
    status: str


@roteador.post("/fechar", response_model=FechamentoResposta)
def fechar_mes(
    carteira_id: int = Query(...),
    ano: int = Query(..., ge=2000),
    mes: int = Query(..., ge=1, le=12),
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> FechamentoResposta:
    obter_carteira_do_usuario(carteira_id, usuario, sessao)
    try:
        fechamento = ServicoFechamento(sessao, carteira_id).fechar_mes(ano, mes)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return FechamentoResposta.model_validate(fechamento)
