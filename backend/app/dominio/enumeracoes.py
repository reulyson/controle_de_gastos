"""Enumerações de domínio do FinFlow."""

from enum import StrEnum


class TipoCategoria(StrEnum):
    """Classificação de uma categoria financeira."""

    RECEITA = "receita"
    DESPESA = "despesa"
    COMPRA = "compra"


class TipoRecorrencia(StrEnum):
    """Periodicidade de lançamentos."""

    UNICA = "unica"
    MENSAL = "mensal"


class TipoCompraCartao(StrEnum):
    """Modalidade de compra no cartão."""

    UNICA = "unica"
    PARCELADA = "parcelada"
    RECORRENTE = "recorrente"


class StatusFechamento(StrEnum):
    """Estado de um fechamento mensal."""

    ABERTO = "aberto"
    FECHADO = "fechado"
