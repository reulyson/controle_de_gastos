"""Esquemas Pydantic compartilhados."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class EsquemaMonetario(BaseModel):
    """Base com serialização de Decimal como string."""

    model_config = ConfigDict(from_attributes=True)


def campo_monetario() -> Field:
    """Campo decimal com duas casas."""
    return Field(..., max_digits=14, decimal_places=2)


class RespostaDecimal(BaseModel):
    """Wrapper para valores monetários na API."""

    valor: Decimal
