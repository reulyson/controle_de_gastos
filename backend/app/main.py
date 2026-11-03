"""Ponto de entrada FastAPI do FinFlow."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.roteador import roteador_v1
from app.modulos.modelos import garantir_bootstrap
from app.nucleo.banco import Base, SessaoLocal, engine
from app.nucleo.configuracao import obter_configuracao


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Inicializa banco, PRAGMA e bootstrap ao subir."""
    Base.metadata.create_all(bind=engine)
    sessao = SessaoLocal()
    try:
        garantir_bootstrap(sessao)
    finally:
        sessao.close()
    yield


def criar_aplicacao() -> FastAPI:
    """Factory da aplicação FastAPI.

    Returns:
        FastAPI: Instância configurada.
    """
    cfg = obter_configuracao()
    app = FastAPI(title=cfg.nome_aplicacao, lifespan=lifespan)
    app.include_router(roteador_v1)

    @app.get("/saude")
    def saude() -> dict[str, str]:
        """Verificação de saúde."""
        return {"status": "ok"}

    return app


app = criar_aplicacao()
