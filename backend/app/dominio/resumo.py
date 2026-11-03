"""Agregados de totais financeiros por competência."""

from dataclasses import dataclass
from decimal import Decimal

from app.dominio.dinheiro import ZERO, decimal_de, somar


@dataclass(slots=True)
class TotaisCompetencia:
    """Totais consolidados de uma competência.

    Attributes:
        total_receita: Soma de receitas previstas/realizadas.
        total_despesa: Soma de despesas previstas/realizadas.
        total_orcado: Despesas + receitas planejadas (despesa - receita planejada líquida).
        total_pago: Valores efetivamente pagos no período.
        saldo_caixa: Saldo de caixa após movimentos.
    """

    total_receita: Decimal = ZERO
    total_despesa: Decimal = ZERO
    total_orcado: Decimal = ZERO
    total_pago: Decimal = ZERO
    saldo_caixa: Decimal = ZERO

    @classmethod
    def vazio(cls, saldo_inicial: Decimal | None = None) -> "TotaisCompetencia":
        """Cria totais zerados com saldo inicial opcional.

        Args:
            saldo_inicial: Saldo de abertura do mês.

        Returns:
            TotaisCompetencia: Instância com zeros.
        """
        saldo = decimal_de(saldo_inicial or ZERO)
        return cls(saldo_caixa=saldo)

    def calcular_orcado(self) -> Decimal:
        """Orçado líquido = despesas orçadas menos receitas orçadas.

        Returns:
            Decimal: Valor orçado líquido.
        """
        return decimal_de(self.total_despesa - self.total_receita)

    def calcular_saldo_caixa(
        self,
        saldo_inicial: Decimal,
        receitas_realizadas: Decimal,
        despesas_pagas: Decimal,
    ) -> Decimal:
        """Atualiza saldo de caixa com fórmula padrão.

        Args:
            saldo_inicial: Saldo no início da competência.
            receitas_realizadas: Créditos no período.
            despesas_pagas: Débitos pagos no período.

        Returns:
            Decimal: Saldo final de caixa.
        """
        return decimal_de(saldo_inicial + receitas_realizadas - despesas_pagas)


def consolidar_totais(
    receitas: list[Decimal],
    despesas: list[Decimal],
    pagos: list[Decimal],
    saldo_inicial: Decimal,
) -> TotaisCompetencia:
    """Consolida listas de valores em totais de competência.

    Args:
        receitas: Valores de receita.
        despesas: Valores de despesa orçada.
        pagos: Valores pagos.
        saldo_inicial: Saldo de abertura.

    Returns:
        TotaisCompetencia: Totais calculados.
    """
    total_receita = somar(*receitas) if receitas else ZERO
    total_despesa = somar(*despesas) if despesas else ZERO
    total_pago = somar(*pagos) if pagos else ZERO
    saldo = decimal_de(saldo_inicial + total_receita - total_pago)
    totais = TotaisCompetencia(
        total_receita=total_receita,
        total_despesa=total_despesa,
        total_orcado=decimal_de(total_despesa - total_receita),
        total_pago=total_pago,
        saldo_caixa=saldo,
    )
    return totais
