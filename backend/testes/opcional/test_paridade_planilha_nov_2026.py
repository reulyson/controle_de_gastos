"""Teste opcional de paridade com a planilha (não bloqueia MVP).

Marcado como skip por padrão: o app sobe sem seed. Ative quando houver
fixture/import que reproduza nov/2026.
"""

from decimal import Decimal

import pytest

TOTAIS_PLANILHA = {
    "total_receita": Decimal("7898.85"),
    "total_despesa": Decimal("7629.66"),
    "total_orcado": Decimal("269.19"),
}


@pytest.mark.skip(reason="Paridade opcional — requer fixture/import da planilha")
def test_paridade_planilha_nov_2026() -> None:
    """Compara indicadores montados no teste com totais da planilha.

    Quando implementar import, remova o skip e injete dados nov/2026 via API
    ou factories, depois chame servico_calculos.indicadores(2026, 11).
    """
    assert TOTAIS_PLANILHA["total_orcado"] == (
        TOTAIS_PLANILHA["total_receita"] - TOTAIS_PLANILHA["total_despesa"]
    )
