"""Dependências FastAPI de autenticação e ownership."""

from __future__ import annotations

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modulos.modelos import Carteira, Usuario
from app.nucleo.banco import obter_sessao
from app.nucleo.seguranca import decodificar_access_token

_bearer = HTTPBearer(auto_error=False)


def obter_usuario_atual(
    credenciais: HTTPAuthorizationCredentials | None = Depends(_bearer),
    sessao: Session = Depends(obter_sessao),
) -> Usuario:
    if credenciais is None or not credenciais.credentials:
        raise HTTPException(status_code=401, detail="Não autenticado")
    try:
        payload = decodificar_access_token(credenciais.credentials)
        usuario_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado") from exc

    usuario = sessao.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Não autenticado")
    return usuario


def obter_carteira_do_usuario(
    carteira_id: int,
    usuario: Usuario,
    sessao: Session,
) -> Carteira:
    carteira = sessao.scalar(
        select(Carteira).where(
            Carteira.id == carteira_id,
            Carteira.usuario_id == usuario.id,
        )
    )
    if carteira is None:
        raise HTTPException(status_code=404, detail="Carteira não encontrada")
    return carteira
