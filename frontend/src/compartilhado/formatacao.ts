import type { IdRecurso } from '@/compartilhado/api/tipos';

export function idComoTexto(id: IdRecurso): string {
  return String(id);
}

const moeda = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
});

export function formatarMoeda(valor: number): string {
  return moeda.format(valor);
}

export function formatarMesAbreviado(mes: number): string {
  const rotulos = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
  return rotulos[mes - 1] ?? String(mes);
}

export function formatarMesCompleto(mes: number): string {
  const rotulos = [
    'Janeiro',
    'Fevereiro',
    'Março',
    'Abril',
    'Maio',
    'Junho',
    'Julho',
    'Agosto',
    'Setembro',
    'Outubro',
    'Novembro',
    'Dezembro',
  ];
  return rotulos[mes - 1] ?? String(mes);
}

export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(' ');
}
