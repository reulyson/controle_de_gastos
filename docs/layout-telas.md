# Layout das telas — FinFlow

## Shell

```text
┌─────────────┬──────────────────────────────────────────────┐
│ FinFlow     │  Título + Ano + Resumo mês + Novo lançamento │
│ Controle    ├──────────────────────────────────────────────┤
│ Receitas    │                                              │
│ Despesas    │              ÁREA PRINCIPAL                  │
│ Cartões     │                                              │
│ Relatórios  │                                              │
│ Config      │                                              │
└─────────────┴──────────────────────────────────────────────┘
```

Menu **+ Novo lançamento**: Receita | Despesa | Cartão (= compra).

---

## Controle

```text
Header: Ano [2026▼]  Resumo mês [Nov/2026▼]  [+ Novo lançamento▾]

Cards: [Saldo caixa] [Cheque livre] | [Receitas] [Despesas] [Orçado] [Pendências]
       (caixa único)                   (mês selecionado)

Grade Jan–Dez: RECEITAS / DESPESAS / CARTÕES (faturas)
Rodapé: TOTAL RECEITA | DESPESA | ORÇADO | PAGO | CAIXA
[Fechar mês]   Colunas fechadas 🔒
```

- Valor receita/despesa → `GavetaDetalheCelula`
- Valor fatura → `GavetaDetalheFaturaCartao`
- Check → pago/recebido (valida cheque)

### GavetaDetalheFaturaCartao

```text
┌─ Itaú — Fatura Nov/2026 ────────────────┐
│ Total …                                 │
│ Netflix   Recorrente  [✓]               │
│ Mercado   Parcela 3/12  —               │
│ Notebook  Única         —               │
└─────────────────────────────────────────┘
```

Checks só em **recorrentes**.

### Modal Fechar mês

Saldo inicial, totais, saldo final (pode negativo), uso cheque, pendências → Confirmar.

---

## Receitas / Despesas

Listagem + botão Nova → mesma `GavetaFormularioLancamento` do menu.
Recorrência: Única (mês) | Mensal (até mês X ou N vezes).
Sem vencimento em despesa.

---

## Cartões

- **Cadastrar cartão** → `GavetaNovoCartao`
- **Nova compra** → `GavetaNovaCompra` (única / parcelada / recorrente)

---

## Relatórios

Gráficos Recharts quando houver dados (mesma base de `servico_calculos`).

---

## Configurações

- Limite cheque total
- Saldo inicial / ajustar extrato
- Reabrir mês fechado
- Categorias (opcional)
- Ano padrão
