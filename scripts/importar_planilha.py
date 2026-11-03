"""Script opcional: importação/validação de totais da planilha (não é seed do MVP).

Uso futuro:
  1. Exportar CSV das abas da planilha Google.
  2. Mapear linhas para POST /api/v1/receitas e /despesas.
  3. Comparar totais nov/2026 com a tabela de referência em docs/planilha-referencia.md.

Referência nov/2026:
  receita 7898.85 | despesa 7629.66 | orçado 269.19
"""

from __future__ import annotations

from decimal import Decimal

TOTAIS_REFERENCIA_NOV_2026 = {
    "total_receita": Decimal("7898.85"),
    "total_despesa": Decimal("7629.66"),
    "total_orcado": Decimal("269.19"),
}


def totais_referencia() -> dict[str, Decimal]:
    """Retorna totais de referência da planilha (somente documentação/validação)."""
    return dict(TOTAIS_REFERENCIA_NOV_2026)


def main() -> None:
    """Imprime totais de referência; import completo fica para evolução futura."""
    print("FinFlow — referência planilha nov/2026 (sem import automático no MVP)")
    for chave, valor in totais_referencia().items():
        print(f"  {chave}: {valor}")
    print("Ver docs/planilha-referencia.md e teste opcional de paridade.")


if __name__ == "__main__":
    main()
