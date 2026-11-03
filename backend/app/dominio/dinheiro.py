"""Utilitários monetários com Decimal."""

from decimal import Decimal, ROUND_HALF_UP

QUANTIZE_CENTAVOS = Decimal("0.01")
ZERO = Decimal("0.00")


def decimal_de(valor: Decimal | str | int | float) -> Decimal:
    """Converte valor para Decimal com duas casas decimais.

    Args:
        valor: Entrada numérica em qualquer formato suportado.

    Returns:
        Decimal: Valor arredondado half-up para centavos.
    """
    if isinstance(valor, Decimal):
        bruto = valor
    else:
        bruto = Decimal(str(valor))
    return bruto.quantize(QUANTIZE_CENTAVOS, rounding=ROUND_HALF_UP)


def somar(*valores: Decimal) -> Decimal:
    """Soma valores monetários.

    Args:
        *valores: Parcelas a somar.

    Returns:
        Decimal: Total quantizado.
    """
    total = sum(valores, ZERO)
    return decimal_de(total)
