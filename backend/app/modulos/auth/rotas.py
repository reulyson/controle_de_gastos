"""Cadastro, login, refresh e logout."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import Response as PlainResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modulos.modelos import RefreshToken, Usuario
from app.nucleo.banco import obter_sessao
from app.nucleo.deps_auth import obter_usuario_atual
from app.nucleo.rate_limit import chave_cliente, checar_rate_limit
from app.nucleo.seguranca import (
    COOKIE_REFRESH,
    cookie_refresh_kwargs,
    criar_access_token,
    expiracao_refresh,
    gerar_refresh_token,
    hash_refresh_token,
    hash_senha,
    normalizar_email,
    validar_politica_senha,
    verificar_senha,
)

roteador = APIRouter(prefix="/auth", tags=["Auth"])

MSG_LOGIN_INVALIDO = "E-mail ou senha inválidos"


class CadastroCorpo(BaseModel):
    email: EmailStr
    nome: str = Field(..., min_length=1, max_length=255)
    senha: str = Field(..., min_length=8, max_length=128)


class LoginCorpo(BaseModel):
    email: EmailStr
    senha: str = Field(..., min_length=1, max_length=128)


class TokenResposta(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 900


class UsuarioResposta(BaseModel):
    id: int
    email: str
    nome: str


def _emitir_sessao(response: Response, sessao: Session, usuario: Usuario) -> TokenResposta:
    access = criar_access_token(usuario.id)
    refresh = gerar_refresh_token()
    sessao.add(
        RefreshToken(
            usuario_id=usuario.id,
            token_hash=hash_refresh_token(refresh),
            expira_em=expiracao_refresh(),
            revogado=False,
        )
    )
    sessao.commit()
    response.set_cookie(value=refresh, **cookie_refresh_kwargs())
    return TokenResposta(access_token=access)


def _revogar_todos_refresh(sessao: Session, usuario_id: int) -> None:
    tokens = sessao.scalars(
        select(RefreshToken).where(
            RefreshToken.usuario_id == usuario_id,
            RefreshToken.revogado.is_(False),
        )
    ).all()
    for token in tokens:
        token.revogado = True


@roteador.post("/cadastro", response_model=TokenResposta, status_code=201)
def cadastro(
    corpo: CadastroCorpo,
    request: Request,
    response: Response,
    sessao: Session = Depends(obter_sessao),
) -> TokenResposta:
    checar_rate_limit(chave_cliente(request, "cadastro"), maximo=3)
    email = normalizar_email(str(corpo.email))
    erro_senha = validar_politica_senha(corpo.senha, email)
    if erro_senha:
        raise HTTPException(status_code=422, detail=erro_senha)
    existente = sessao.scalar(select(Usuario).where(Usuario.email == email))
    if existente is not None:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    usuario = Usuario(
        email=email,
        nome=corpo.nome.strip(),
        senha_hash=hash_senha(corpo.senha),
    )
    sessao.add(usuario)
    sessao.commit()
    sessao.refresh(usuario)
    return _emitir_sessao(response, sessao, usuario)


@roteador.post("/login", response_model=TokenResposta)
def login(
    corpo: LoginCorpo,
    request: Request,
    response: Response,
    sessao: Session = Depends(obter_sessao),
) -> TokenResposta:
    email = normalizar_email(str(corpo.email))
    checar_rate_limit(chave_cliente(request, f"login:{email}"), maximo=5)
    usuario = sessao.scalar(select(Usuario).where(Usuario.email == email))
    if usuario is None or not verificar_senha(corpo.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail=MSG_LOGIN_INVALIDO)
    return _emitir_sessao(response, sessao, usuario)


@roteador.post("/refresh", response_model=TokenResposta)
def refresh(
    request: Request,
    response: Response,
    sessao: Session = Depends(obter_sessao),
) -> TokenResposta:
    checar_rate_limit(chave_cliente(request, "refresh"), maximo=20)
    bruto = request.cookies.get(COOKIE_REFRESH)
    if not bruto:
        raise HTTPException(status_code=401, detail="Sessão expirada")
    token_hash = hash_refresh_token(bruto)
    registro = sessao.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    if registro is None:
        raise HTTPException(status_code=401, detail="Sessão expirada")
    if registro.revogado:
        _revogar_todos_refresh(sessao, registro.usuario_id)
        sessao.commit()
        response.delete_cookie(COOKIE_REFRESH, path="/api/v1/auth")
        raise HTTPException(status_code=401, detail="Sessão inválida")
    agora = datetime.now(UTC).replace(tzinfo=None)
    if registro.expira_em < agora:
        registro.revogado = True
        sessao.commit()
        response.delete_cookie(COOKIE_REFRESH, path="/api/v1/auth")
        raise HTTPException(status_code=401, detail="Sessão expirada")

    registro.revogado = True
    usuario = sessao.get(Usuario, registro.usuario_id)
    if usuario is None:
        sessao.commit()
        raise HTTPException(status_code=401, detail="Sessão expirada")
    return _emitir_sessao(response, sessao, usuario)


@roteador.post("/logout", status_code=204, response_class=PlainResponse)
def logout(
    request: Request,
    response: Response,
    sessao: Session = Depends(obter_sessao),
) -> PlainResponse:
    bruto = request.cookies.get(COOKIE_REFRESH)
    if bruto:
        token_hash = hash_refresh_token(bruto)
        registro = sessao.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
        if registro is not None and not registro.revogado:
            registro.revogado = True
            sessao.commit()
    response.delete_cookie(COOKIE_REFRESH, path="/api/v1/auth")
    return PlainResponse(status_code=204)


class PerfilAtualizarCorpo(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)


@roteador.get("/eu", response_model=UsuarioResposta)
def eu(usuario: Usuario = Depends(obter_usuario_atual)) -> UsuarioResposta:
    return UsuarioResposta(id=usuario.id, email=usuario.email, nome=usuario.nome)


@roteador.patch("/eu", response_model=UsuarioResposta)
def atualizar_perfil(
    corpo: PerfilAtualizarCorpo,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> UsuarioResposta:
    """Atualiza nome do usuário (e-mail não é alterável por aqui)."""
    usuario.nome = corpo.nome.strip()
    sessao.add(usuario)
    sessao.commit()
    sessao.refresh(usuario)
    return UsuarioResposta(id=usuario.id, email=usuario.email, nome=usuario.nome)
