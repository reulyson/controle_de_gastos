"""Sessão SQLAlchemy e fábrica de engine."""

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.nucleo.configuracao import obter_configuracao

config = obter_configuracao()

connect_args = {"check_same_thread": False} if config.url_banco.startswith("sqlite") else {}
engine = create_engine(config.url_banco, connect_args=connect_args, echo=config.debug)

if config.url_banco.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _ativar_chaves_estrangeiras(dbapi_connection, _connection_record) -> None:
        """Garante integridade referencial no SQLite."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


class Base(DeclarativeBase):
    """Classe base declarativa para modelos ORM."""


SessaoLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def obter_sessao() -> Generator[Session, None, None]:
    """Fornece sessão de banco por requisição.

    Yields:
        Session: Sessão SQLAlchemy ativa.
    """
    sessao = SessaoLocal()
    try:
        yield sessao
    finally:
        sessao.close()
