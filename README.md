# FinFlow — Controle de gastos

Aplicação familiar que traz a planilha **Controle de gastos** para a web: grade anual, lançamentos, cartões, fechamento mensal e cheque especial único.

## Stack

| Camada | Tecnologias |
|--------|-------------|
| Backend | Python · FastAPI · Pydantic v2 · SQLAlchemy 2 · Alembic · SQLite |
| Frontend | React 18 · TypeScript · Vite · Tailwind · TanStack Query · Recharts |
| Engenharia | DRY (`nucleo_financeiro`), docstrings PT, docs em `docs/`, commits por marco |

## Quick start

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

API: `http://127.0.0.1:8000` · OpenAPI: `/docs`

### Frontend

```powershell
cd frontend
copy .env.example .env
npm install
npm run dev
```

UI: `http://127.0.0.1:5173`

### Testes

```powershell
cd backend
python -m pytest -q
```

```powershell
cd frontend
npm run build
```

## Documentação

Índice: [docs/README.md](docs/README.md)

- [Arquitetura e DRY](docs/arquitetura.md)
- [Backend](docs/planejamento-backend.md)
- [Frontend](docs/planejamento-frontend.md)
- [Decisões](docs/decisoes.md)
- [Layout das telas](docs/layout-telas.md)
- [Planilha referência](docs/planilha-referencia.md)

## Convenções

- **Sem seed** da planilha: primeiro acesso com grade vazia (bootstrap: 1 carteira + 1 conta).
- Totais e caixa **só** no backend (`servico_calculos`).
- Dinheiro: `Decimal` / `Numeric(14,2)`.
- Nomes de domínio e UI em português.
- Import CSV / paridade nov/2026: opcional (`scripts/`).

## Planilha

[Controle de gastos (Google Sheets)](https://docs.google.com/spreadsheets/d/1FFxDFcwyX9xJJcM5MWfeJUCURE51aXBdjbjbAHjmoW4/edit) — referência de layout/regras, não carga inicial.
