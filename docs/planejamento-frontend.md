# Planejamento frontend — FinFlow

## Stack

React 18, TypeScript strict, Vite, Tailwind, React Router, TanStack Query, Recharts, Material Symbols.

## Estrutura

```text
frontend/src/
  aplicativo/          # main, rotas, provedores
  layout/              # CascoAplicacao, BarraLateral, MenuNovoLancamento
  compartilhado/
    api/               # cliente, servicos, tipos, chavesConsulta
    ui/                # Botao, GavetaLateral, CartaoKpi, SeletorCategoriaTags
    formatacao.ts
  funcionalidades/
    controle/          # PaginaControle, TabelaFinanceiraAnual, CelulaFinanceira, gavetas
    lancamentos/       # PaginaLancamentos (DRY receita|despesa)
    cartoes/           # PaginaCartoes, GavetaNovoCartao, GavetaNovaCompra, GavetaDetalheFaturaCartao
    relatorios/
    configuracoes/
```

## Rotas

| Path | Página |
|------|--------|
| `/controle` | Grade anual + indicadores + fechar mês |
| `/receitas` | Listagem + mesma gaveta do menu |
| `/despesas` | Idem |
| `/cartoes` | Cadastro cartão + compras |
| `/relatorios` | Gráficos (Recharts) |
| `/configuracoes` | Cheque, saldo, extrato, reabrir mês, categorias |

## Interações Controle

- **Valor** na célula → `GavetaDetalheCelula` (receita/despesa) ou `GavetaDetalheFaturaCartao` (fatura).
- **Check** → `POST /pagamentos` (sem abrir gaveta); valida cheque no backend.
- **Resumo mês** / clique coluna → cards KPIs do mês selecionado.
- **Ano** 2026–2028 no header.
- Cadastro **não** na grade — só `MenuNovoLancamento` ou botões das páginas.

## Componentes DRY

- `GavetaFormularioLancamento` — receita e despesa.
- `CelulaFinanceira` — variantes receita / despesa / fatura.
- `GavetaLateral` — shell Cancelar/Salvar.
- `PaginaLancamentos` — `tipo` prop.
- `EstadoConsulta` — loading / erro / vazio.

## Server state

- Query keys em `chavesConsulta.ts`.
- Após mutation: invalidar grade + listagens + indicadores.
- Valores monetários exibidos via `formatacao.ts`; totais vêm da API.

## Como rodar

```powershell
cd frontend
copy .env.example .env
npm install
npm run dev
```

Build: `npm run build` (tsc + vite).
