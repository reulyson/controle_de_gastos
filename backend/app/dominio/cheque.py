"""Cálculo de cheque especial disponível."""

from decimal import Decimal

from app.dominio.dinheiro import ZERO, decimal_de
from app.dominio.liquidacao import uso_cheque_especial


def cheque_livre(limite_total: Decimal, saldo_atual: Decimal) -> Decimal:
    """Calcula limite de cheque ainda disponível.

    Args:
        limite_total: Limite contratado de cheque especial.
        saldo_atual: Saldo atual da conta (pode ser negativo).

    Returns:
        Decimal: Valor livre = limite - uso_atual.
    """
    limite = decimal_de(limite_total)
    uso = uso_cheque_especial(saldo_atual)
    livre = limite - uso
    if livre < ZERO:
        return ZERO
    return decimal_de(livre)
