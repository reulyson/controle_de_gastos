"""Configurações da aplicação carregadas de variáveis de ambiente."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracao(BaseSettings):
    """Parâmetros globais do FinFlow.

    Attributes:
        nome_aplicacao: Nome exibido na documentação OpenAPI.
        url_banco: URL de conexão SQLAlchemy (SQLite por padrão).
        debug: Habilita recarregamento e logs verbosos.
    """

    model_config = SettingsConfigDict(env_file=".env", env_prefix="FINFLOW_", extra="ignore")

    nome_aplicacao: str = "FinFlow"
    url_banco: str = "sqlite:///./finflow.db"
    debug: bool = False


@lru_cache
def obter_configuracao() -> Configuracao:
    """Retorna instância cacheada das configurações.

    Returns:
        Configuracao: Objeto com parâmetros resolvidos.
    """
    return Configuracao()
