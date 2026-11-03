# Documentação FinFlow

Índice da documentação versionada do monorepo **controle_gastos** (aplicação familiar de controle de gastos).

## Como navegar

| Documento | Conteúdo |
|-----------|----------|
| [arquitetura.md](arquitetura.md) | Monorepo, camadas, mapa DRY, stack e boas práticas |
| [planejamento-backend.md](planejamento-backend.md) | Modelagem, núcleo financeiro, APIs, módulos |
| [planejamento-frontend.md](planejamento-frontend.md) | Shell, rotas, componentes, ordem UI |
| [decisoes.md](decisoes.md) | Decisões de produto e engenharia (fonte de verdade) |
| [layout-telas.md](layout-telas.md) | Wireframes das telas e gavetas |
| [planilha-referencia.md](planilha-referencia.md) | Espelho da planilha Google (referência, **não** seed) |

Quick start e comandos: [README.md](../README.md) na raiz.

## Convenções

- Nomes de domínio e UI em **português**.
- Dinheiro: `Decimal` / `Numeric(14,2)` — nunca `float`.
- Totais e caixa só em `nucleo_financeiro/servico_calculos.py`.
- Docstrings (Python) e JSDoc (TypeScript) em PT nos pontos públicos.
