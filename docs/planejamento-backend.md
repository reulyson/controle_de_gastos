# Planejamento backend — FinFlow

## Conceitos (nunca misturar)

| Conceito | Significado |
|----------|-------------|
| **Competência** | Mês a que a obrigação pertence (colunas Jan–Dez) |
| **Obrigação** | `receitas_mensais` / `despesas_mensais` |
| **Movimentação** | `pagamentos` — caixa efetivo |

## Modelagem (MVP)

- `carteiras` — `limite_cheque_especial_total`, `ano_padrao`
- `contas_financeiras` — caixa único, `saldo_inicial`
- `categorias` — tags creatable (receita/despesa/compra)
- `receitas` + `receitas_mensais`
- `despesas` + `despesas_mensais`
- `pagamentos` (+ rateios quando aplicável)
- `cartoes`, `compras_cartao`, `parcelas_cartao`, `faturas`, `fatura_itens`
- `fechamentos_mensais`, `fechamento_pendencias`

Unicidades: `(receita_id|despesa_id, ano, mes)`, `(cartao_id, competencia)`.

## Núcleo financeiro

| Serviço | Função |
|---------|--------|
| `servico_calculos` | Indicadores oficiais; saldo caixa; cheque livre |
| `servico_pagamentos` | Toggle pago/recebido; bloqueia se `saldo < -limite` |
| `servico_recorrencia` | Gera mensais (única / mensal N vezes ou até mês) |
| `servico_fechamento` | Snapshot; pendências; saldo final → próximo inicial; reabrir |
| `servico_fluxo_caixa` | Movimentações e ajuste de extrato |
| `ServicoGrade` | Monta linhas anuais RECEITAS/DESPESAS/CARTÕES |

## API REST (`/api/v1`)

| Área | Exemplos |
|------|----------|
| Carteiras | `GET/PATCH /carteiras`, `GET .../anos/{ano}/grade-controle?mes=` |
| Relatório | `GET .../anos/{ano}/relatorio` |
| Extrato | `POST .../ajustes-extrato` |
| Fechamento | `POST .../fechamentos`, `POST .../fechamentos/reabrir` |
| Receitas/Despesas | CRUD + `PATCH ...-mensais/{id}` |
| Pagamentos | `POST /pagamentos` |
| Cartões | CRUD; `GET /cartoes/{id}/faturas/{ano}/{mes}` |
| Compras | `GET/POST /compras` |
| Categorias / Tags | `/categorias`, `/tags` (alias) |

## Cheque especial

- Limite global na carteira.
- Ao pagar: se saldo projetado `< -limite` → HTTP 422.
- Uso automático do cheque até o limite (sem modal por banco).

## Fechamento

1. Calcula totais via `servico_calculos`.
2. Grava snapshot + pendências apontando obrigações originais.
3. `saldo_inicial` do mês seguinte = `saldo_final` (pode ser negativo).

## Testes

```powershell
cd backend
pip install -r requirements.txt
python -m pytest -q
```

## Bootstrap

No lifespan: cria 1 carteira “Principal” + 1 conta “Caixa” se o banco estiver vazio. **Sem** linhas da planilha.
