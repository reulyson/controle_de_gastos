"""Endpoint unificado de pagamentos."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.dominio.liquidacao import SaldoInsuficienteError
from app.modulos.modelos import Usuario
from app.nucleo.banco import obter_sessao
from app.nucleo.deps_auth import obter_usuario_atual
from app.nucleo_financeiro.servico_pagamentos import ServicoPagamentos

roteador = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])


class PagamentoCorpo(BaseModel):
    tipo: str = Field(..., pattern="^(receita|despesa|cartao)$")
    referencia_id: int | str
    mes: int = Field(..., ge=1, le=12)
    ano: int = Field(..., ge=2000)
    pago: bool

    @property
    def referencia_id_int(self) -> int:
        return int(self.referencia_id)


@roteador.post("", status_code=204)
def alternar_pagamento(
    corpo: PagamentoCorpo,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> None:
    _ = usuario
    try:
        ServicoPagamentos(sessao).alternar(
            corpo.tipo,
            corpo.referencia_id_int,
            corpo.ano,
            corpo.mes,
            corpo.pago,
        )
    except SaldoInsuficienteError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
