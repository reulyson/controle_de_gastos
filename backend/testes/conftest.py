"""Fixtures pytest."""

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["FINFLOW_URL_BANCO"] = "sqlite://"
os.environ["FINFLOW_AMBIENTE"] = "desenvolvimento"
os.environ["FINFLOW_JWT_SECRET"] = "test-secret-key-at-least-32-chars!!"

from app.main import app
from app.nucleo.banco import Base, obter_sessao
from app.nucleo.configuracao import obter_configuracao
from app.nucleo.rate_limit import limpar_rate_limits

obter_configuracao.cache_clear()


@pytest.fixture()
def engine_teste():
    """Engine SQLite em memória com FK."""
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(eng, "connect")
    def _fk(dbapi_connection, _record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=eng)
    from app.nucleo.seed_categorias import garantir_categorias_padrao

    SessionSeed = sessionmaker(bind=eng)
    seed = SessionSeed()
    try:
        garantir_categorias_padrao(seed)
        seed.commit()
    finally:
        seed.close()
    yield eng
    Base.metadata.drop_all(bind=eng)


@pytest.fixture()
def sessao(engine_teste) -> Generator[Session, None, None]:
    SessionLocal = sessionmaker(bind=engine_teste)
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture()
def cliente(engine_teste) -> Generator[TestClient, None, None]:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_teste)

    def _override():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[obter_sessao] = _override
    limpar_rate_limits()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    limpar_rate_limits()


@pytest.fixture()
def usuario_autenticado(cliente: TestClient) -> dict:
    """Cadastra usuário, cria carteira padrão e retorna headers + ids."""
    limpar_rate_limits()
    cadastro = cliente.post(
        "/api/v1/auth/cadastro",
        json={
            "email": "teste@example.com",
            "nome": "Teste",
            "senha": "senha12345",
        },
    )
    assert cadastro.status_code == 201, cadastro.text
    token = cadastro.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    carteira = cliente.post(
        "/api/v1/carteiras",
        headers=headers,
        json={"nome": "Principal", "limite_cheque": "0.00", "saldo_inicial": "0.00"},
    )
    assert carteira.status_code == 201, carteira.text
    return {
        "headers": headers,
        "token": token,
        "carteira_id": carteira.json()["id"],
        "email": "teste@example.com",
        "senha": "senha12345",
    }
