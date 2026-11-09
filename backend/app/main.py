"""Ponto de entrada FastAPI do FinFlow."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.v1.roteador import roteador_v1
from app.modulos.modelos import garantir_bootstrap
from app.nucleo.banco import Base, engine
from app.nucleo.configuracao import obter_configuracao


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Inicializa schema e seed de categorias padrão."""
    obter_configuracao()
    Base.metadata.create_all(bind=engine)
    with Session(engine) as sessao:
        garantir_bootstrap(sessao)
        sessao.commit()
    yield


def criar_aplicacao() -> FastAPI:
    """Factory da aplicação FastAPI.

    Returns:
        FastAPI: Instância configurada.
    """
    cfg = obter_configuracao()
    app = FastAPI(title=cfg.nome_aplicacao, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(roteador_v1)

    @app.get("/saude")
    def saude() -> dict[str, str]:
        """Verificação de saúde."""
        return {"status": "ok"}

    return app


app = criar_aplicacao()
