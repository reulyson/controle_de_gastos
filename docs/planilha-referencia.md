# Planilha de referência — Controle de gastos

**Planilha:** [Controle de gastos](https://docs.google.com/spreadsheets/d/1FFxDFcwyX9xJJcM5MWfeJUCURE51aXBdjbjbAHjmoW4/edit)

**Papel:** modelo visual e de regras. **Não** é carga inicial do banco (MVP sem seed).

## Abas

| Aba | Comportamento na app |
|-----|----------------------|
| 2026 / 2027 / 2028 | Grade anual por ano (seletor no header) |
| Cartões | Página Cartões + linha de fatura no Controle |

## Anatomia da aba anual

```text
RECEITAS (valor por mês)
DESPESAS (valor + TRUE/FALSE pago)
RESUMO: TOTAL ORÇADO | TOTAL PAGO | TOTAL CAIXA
```

## Totais de referência — nov/2026 (validação futura opcional)

| Indicador | Valor planilha |
|-----------|----------------|
| Total receita | R$ 7.898,85 |
| Total despesa | R$ 7.629,66 |
| Total orçado | R$ 269,19 |
| Total pago (exemplo) | R$ 5.973,81 |
| Total caixa (exemplo) | R$ 1.925,04 |

Use apenas para teste manual ou script `scripts/importar_planilha.py` / teste de paridade opcional — **não** no bootstrap.

## Catálogo sugerido (documentação)

Linhas típicas da planilha (exemplos): salário, benefícios, aluguel, contas, cartões Itaú/Bradesco, etc. O usuário **recadastra** no app via Novo lançamento.

## TRUE / FALSE

Espelhado pelo **check** da célula (pago/recebido) e pelo `POST /pagamentos`.
