export const ANOS_DISPONIVEIS = [2026, 2027, 2028] as const;

export type AnoDisponivel = (typeof ANOS_DISPONIVEIS)[number];

export const MESES = [
  { valor: 1, rotulo: 'Janeiro' },
  { valor: 2, rotulo: 'Fevereiro' },
  { valor: 3, rotulo: 'Março' },
  { valor: 4, rotulo: 'Abril' },
  { valor: 5, rotulo: 'Maio' },
  { valor: 6, rotulo: 'Junho' },
  { valor: 7, rotulo: 'Julho' },
  { valor: 8, rotulo: 'Agosto' },
  { valor: 9, rotulo: 'Setembro' },
  { valor: 10, rotulo: 'Outubro' },
  { valor: 11, rotulo: 'Novembro' },
  { valor: 12, rotulo: 'Dezembro' },
] as const;

export const CORES_GRAFICO = ['#0d9488', '#64748b', '#14b8a6', '#334155', '#2dd4bf', '#475569'];
