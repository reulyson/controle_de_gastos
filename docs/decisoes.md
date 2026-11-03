# Decisões FinFlow

Documento vivo — atualizar antes de migrations grandes.

## Produto (MVP)

| Tema | Decisão |
|------|---------|
| Seed | **Nenhum** lançamento no startup; bootstrap 1 carteira + 1 conta |
| Modos UI | **Sem** Previsto / Realizado / Consolidado (v2 eventual) |
| Cadastro | Só menu **Novo lançamento** ou páginas; **não** na grade Controle |
| Célula | Valor → gaveta; Check → pago/recebido direto |
| Categorias | Creatable na gaveta; Config > Categorias opcional |
| Despesa | Sem dia de vencimento na v1 |
| Cartão (menu) | = **Nova compra**; cadastrar cartão só em Cartões |
| Fatura na grade | Valor clicável → lista de compras; check em **recorrentes** |
| Única / parcelada | Compõem total da fatura; sem check fino na gaveta (v1) |
| Cards | Saldo caixa + Cheque livre + KPIs do **mês selecionado** |
| Cheque | Limite **total** único; caixa único; sem modal por banco |
| Saldo | Híbrido C: movimentações + **Ajustar saldo com extrato** |
| Fechamento | MVP: saldo final → inicial seguinte; pendências sem duplicar; 🔒 |
| Auth | Sem login na v1 |
| Banco | SQLite MVP; schema preparado para PostgreSQL |

## Engenharia

| Tema | Decisão |
|------|---------|
| DRY | Fórmulas só em `nucleo_financeiro`; front não soma crítico |
| Docstrings | Google style PT em domínio/serviços; JSDoc em hooks/UI compartilhada |
| Docs | Pacote em `docs/` + README raiz |
| Git | Commit por fase / marco testável |
| Dinheiro | `Decimal` / `Numeric(14,2)` |
| Idioma | Nomes PT em domínio, rotas e UI |

## Regras de valor na célula

- **Só este mês:** PATCH da ocorrência da competência.
- **Este mês e os próximos:** atualiza ocorrência atual + futuras (≥ competência); passado intacto.

## Pagamento vs limite de cheque

- Após marcar pago, se `saldo_caixa >= -limite` → OK (usa cheque automaticamente se negativo).
- Se `saldo_caixa < -limite` → bloquear com mensagem “Passou o limite do cheque especial”.

## Fora do MVP

Auth, modos avançados, cheque por banco, import CSV obrigatório, Open Finance, multi-carteira UI.
