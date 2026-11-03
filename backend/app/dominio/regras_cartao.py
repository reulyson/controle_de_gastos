"""Regras de fatura e itens de cartão."""

from dataclasses import dataclass
from decimal import Decimal

from app.dominio.dinheiro import ZERO, decimal_de, somar
from app.dominio.enumeracoes import TipoCompraCartao


@dataclass(frozen=True, slots=True)
class ItemFaturaRegra:
    """Metadados de exibição de item na fatura.

    Attributes:
        tipo_compra: Modalidade da compra.
        permite_marcar_pago: Se o usuário pode marcar pagamento na fatura.
        apenas_informativo: Item não altera fluxo de caixa diretamente.
    """

    tipo_compra: TipoCompraCartao
    permite_marcar_pago: bool
    apenas_informativo: bool


def regra_item_fatura(tipo_compra: TipoCompraCartao) -> ItemFaturaRegra:
    """Define comportamento de item conforme tipo de compra.

    Args:
        tipo_compra: UNICA, PARCELADA ou RECORRENTE.

    Returns:
        ItemFaturaRegra: Flags de UI e pagamento.
    """
    if tipo_compra == TipoCompraCartao.RECORRENTE:
        return ItemFaturaRegra(
            tipo_compra=tipo_compra,
            permite_marcar_pago=True,
            apenas_informativo=False,
        )
    return ItemFaturaRegra(
        tipo_compra=tipo_compra,
        permite_marcar_pago=False,
        apenas_informativo=True,
    )


def total_fatura(valores: list[Decimal]) -> Decimal:
    """Soma valores de itens da fatura.

    Args:
        valores: Valores dos itens.

    Returns:
        Decimal: Total da fatura.
    """
    if not valores:
        return ZERO
    return somar(*valores)


def valor_parcela(valor_total: Decimal, parcelas: int) -> Decimal:
    """Divide valor total em parcelas iguais (última ajustada externamente se necessário).

    Args:
        valor_total: Valor da compra.
        parcelas: Número de parcelas (>= 1).

    Returns:
        Decimal: Valor de cada parcela arredondado.
    """
    if parcelas < 1:
        msg = "parcelas deve ser >= 1"
        raise ValueError(msg)
    return decimal_de(valor_total / Decimal(parcelas))
