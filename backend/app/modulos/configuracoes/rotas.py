"""Metadados da aplicação."""

from fastapi import APIRouter

from app.nucleo.configuracao import obter_configuracao

roteador = APIRouter(prefix="/configuracoes", tags=["Configurações"])


@roteador.get("")
def obter_configuracoes() -> dict[str, str | bool]:
    """Retorna configurações públicas (sem segredos)."""
    cfg = obter_configuracao()
    return {
        "nome_aplicacao": cfg.nome_aplicacao,
        "debug": cfg.debug,
    }
