"""Fixtures pytest."""

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["FINFLOW_URL_BANCO"] = "sqlite://"

from app.main import app
from app.modulos.modelos import garantir_bootstrap
from app.nucleo.banco import Base, obter_sessao


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
    yield eng
    Base.metadata.drop_all(bind=eng)


@pytest.fixture()
def sessao(engine_teste) -> Generator[Session, None, None]:
    """Sessão com bootstrap."""
    SessionLocal = sessionmaker(bind=engine_teste)
    db = SessionLocal()
    garantir_bootstrap(db)
    yield db
    db.close()


@pytest.fixture()
def cliente(engine_teste) -> Generator[TestClient, None, None]:
    """Cliente HTTP com override de sessão."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_teste)

    def _override():
        db = SessionLocal()
        try:
            garantir_bootstrap(db)
            yield db
        finally:
            db.close()

    app.dependency_overrides[obter_sessao] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
