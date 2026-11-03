"""Validações de liquidação e saldo com cheque especial."""

from decimal import Decimal

from app.dominio.dinheiro import ZERO, decimal_de


class SaldoInsuficienteError(Exception):
    """Saldo após pagamento excede limite de cheque especial."""


def validar_pagamento_com_cheque(
    saldo_atual: Decimal,
    valor_pagamento: Decimal,
    limite_cheque_especial: Decimal,
) -> None:
    """Impede pagamento se saldo final ficar abaixo do limite negativo.

    Args:
        saldo_atual: Saldo da conta antes do pagamento.
        valor_pagamento: Valor a debitar (positivo).
        limite_cheque_especial: Limite total de cheque especial (positivo).

    Raises:
        SaldoInsuficienteError: Quando saldo_final < -limite.
    """
    valor = decimal_de(valor_pagamento)
    limite = decimal_de(limite_cheque_especial)
    saldo = decimal_de(saldo_atual)
    saldo_final = saldo - valor
    if saldo_final < -limite:
        msg = (
            f"Pagamento de {valor} deixaria saldo {saldo_final}, "
            f"abaixo do limite de cheque {-limite}"
        )
        raise SaldoInsuficienteError(msg)


def saldo_apos_receita(saldo_atual: Decimal, valor: Decimal) -> Decimal:
    """Calcula saldo após crédito.

    Args:
        saldo_atual: Saldo corrente.
        valor: Valor creditado.

    Returns:
        Decimal: Novo saldo.
    """
    return decimal_de(saldo_atual + valor)


def saldo_apos_despesa(saldo_atual: Decimal, valor: Decimal) -> Decimal:
    """Calcula saldo após débito.

    Args:
        saldo_atual: Saldo corrente.
        valor: Valor debitado.

    Returns:
        Decimal: Novo saldo.
    """
    return decimal_de(saldo_atual - valor)


def uso_cheque_especial(saldo_atual: Decimal) -> Decimal:
    """Quanto do cheque especial está em uso (zero se saldo positivo).

    Args:
        saldo_atual: Saldo da conta.

    Returns:
        Decimal: Uso do cheque (>= 0).
    """
    saldo = decimal_de(saldo_atual)
    if saldo >= ZERO:
        return ZERO
    return decimal_de(-saldo)
