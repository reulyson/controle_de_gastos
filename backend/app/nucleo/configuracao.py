"""Configurações da aplicação carregadas de variáveis de ambiente."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_SECRET_DEV = "dev-only-change-me-finflow-secret-key-32b"


class Configuracao(BaseSettings):
    """Parâmetros globais do FinFlow."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="FINFLOW_", extra="ignore")

    nome_aplicacao: str = "FinFlow"
    url_banco: str = "sqlite:///./finflow.db"
    debug: bool = False
    ambiente: str = "desenvolvimento"
    jwt_secret: str = _SECRET_DEV

    @field_validator("jwt_secret")
    @classmethod
    def secret_nao_vazio(cls, valor: str) -> str:
        if not valor or len(valor) < 16:
            raise ValueError("FINFLOW_JWT_SECRET deve ter pelo menos 16 caracteres")
        return valor

    def garantir_secret_producao(self) -> None:
        if self.ambiente == "producao" and (
            len(self.jwt_secret) < 32 or self.jwt_secret.startswith("dev-only")
        ):
            raise RuntimeError(
                "FINFLOW_JWT_SECRET fraco ou padrão em produção. Defina um secret com 32+ caracteres."
            )


@lru_cache
def obter_configuracao() -> Configuracao:
    """Retorna instância cacheada das configurações."""
    cfg = Configuracao()
    cfg.garantir_secret_producao()
    return cfg
