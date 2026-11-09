"""Hash de senha, JWT e cookies de refresh."""

from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.nucleo.configuracao import obter_configuracao

_password_hash = PasswordHash.recommended()

COOKIE_REFRESH = "finflow_refresh"
ACCESS_MINUTOS = 15
REFRESH_DIAS = 7


def normalizar_email(email: str) -> str:
    return email.strip().lower()


def validar_politica_senha(senha: str, email: str) -> str | None:
    if len(senha) < 8:
        return "Senha deve ter no mínimo 8 caracteres"
    if len(senha) > 128:
        return "Senha deve ter no máximo 128 caracteres"
    if senha.lower() == email.strip().lower():
        return "Senha não pode ser igual ao e-mail"
    return None


def hash_senha(senha: str) -> str:
    return _password_hash.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        return _password_hash.verify(senha, senha_hash)
    except Exception:
        return False


def criar_access_token(usuario_id: int) -> str:
    cfg = obter_configuracao()
    agora = datetime.now(UTC)
    payload = {
        "sub": str(usuario_id),
        "iat": agora,
        "exp": agora + timedelta(minutes=ACCESS_MINUTOS),
        "type": "access",
    }
    return jwt.encode(payload, cfg.jwt_secret, algorithm="HS256")


def decodificar_access_token(token: str) -> dict[str, Any]:
    cfg = obter_configuracao()
    payload = jwt.decode(token, cfg.jwt_secret, algorithms=["HS256"])
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Tipo de token inválido")
    return payload


def gerar_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def expiracao_refresh() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None) + timedelta(days=REFRESH_DIAS)


def cookie_refresh_kwargs() -> dict[str, Any]:
    cfg = obter_configuracao()
    return {
        "key": COOKIE_REFRESH,
        "httponly": True,
        "samesite": "lax",
        "secure": cfg.ambiente == "producao",
        "path": "/api/v1/auth",
        "max_age": REFRESH_DIAS * 24 * 60 * 60,
    }
