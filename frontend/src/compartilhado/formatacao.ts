import type { IdRecurso } from '@/compartilhado/api/tipos';

export function idComoTexto(id: IdRecurso): string {
  return String(id);
}

const moeda = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
});

const moedaInput = new Intl.NumberFormat('pt-BR', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export function formatarMoeda(valor: number): string {
  return moeda.format(valor);
}

/** API pode mandar Decimal como string; Number.isFinite(string) é false. */
export function valorNumerico(valor: unknown): number | null {
  if (valor === null || valor === undefined || valor === '') return null;
  const n = typeof valor === 'number' ? valor : Number(valor);
  return Number.isFinite(n) ? n : null;
}

/**
 * Moeda sem "R$ " para células densas da grade (ex.: 3.500,00).
 * Aceita number ou string Decimal da API.
 */
export function formatarMoedaCompacta(valor: number | string): string {
  const n = valorNumerico(valor);
  if (n === null) return '—';
  return moedaInput.format(n);
}

/**
 * Formata número para exibição em input (ex.: 3482.29 → "3.482,29").
 */
export function formatarMoedaInput(valor: number): string {
  if (!Number.isFinite(valor)) return '';
  return moedaInput.format(valor);
}

/**
 * Máscara BRL a partir só dos dígitos (centavos).
 * Digitar 348229 → "3.482,29".
 */
export function mascararMoedaDigitacao(texto: string): { texto: string; valor: number | null } {
  const digitos = texto.replace(/\D/g, '');
  if (!digitos) return { texto: '', valor: null };

  const centavos = Number(digitos);
  if (!Number.isFinite(centavos)) return { texto: '', valor: null };

  const valor = centavos / 100;
  return { texto: formatarMoedaInput(valor), valor };
}

/**
 * Converte texto monetário BR/US em número.
 * Aceita "R$ 3.482,29", "3.482,29", "3482,29", "3482.29".
 */
export function parsearMoeda(texto: string): number | null {
  const bruto = texto.trim();
  if (!bruto) return null;

  // Preferência: só dígitos → interpreta como centavos (máscara digitada)
  if (/^[\d.\s,R$r-]+$/.test(bruto) && bruto.replace(/\D/g, '').length > 0) {
    const soDigitos = bruto.replace(/\D/g, '');
    // Se o texto já está mascarado (tem vírgula), parse clássico
    if (bruto.includes(',')) {
      let limpo = bruto
        .replace(/r\$\s?/gi, '')
        .replace(/\s/g, '')
        .replace(/[^\d,.\-]/g, '');
      limpo = limpo.replace(/\./g, '').replace(',', '.');
      const n = Number(limpo);
      if (!Number.isFinite(n)) return null;
      return Math.round(n * 100) / 100;
    }
    return Math.round(Number(soDigitos)) / 100;
  }

  return null;
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

/**
 * Title Case simples (pt-BR): trim → minúsculas → capitaliza cada palavra.
 */
export function formatarTitulo(texto: string): string {
  const limpo = texto.trim().replace(/\s+/g, ' ');
  if (!limpo) return '';
  return limpo
    .toLocaleLowerCase('pt-BR')
    .split(' ')
    .map((palavra) =>
      palavra.length === 0
        ? palavra
        : palavra.charAt(0).toLocaleUpperCase('pt-BR') + palavra.slice(1),
    )
    .join(' ');
}

export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(' ');
}

/** Monta YYYY-MM-DD com mês/dia zero-padded. */
export function dataISO(ano: number, mes: number, dia: number): string {
  const m = String(mes).padStart(2, '0');
  const d = String(dia).padStart(2, '0');
  return `${ano}-${m}-${d}`;
}

/**
 * Data de referência no ano selecionado (mês/dia = hoje local).
 * Ex.: hoje 08/11/2026 + ano 2028 → "2028-11-08".
 */
export function dataReferenciaISO(anoSelecionado: number): string {
  const hoje = new Date();
  return dataISO(anoSelecionado, hoje.getMonth() + 1, hoje.getDate());
}

/** Data local de hoje no formato YYYY-MM-DD (input type="date"). */
export function dataHojeISO(): string {
  return dataReferenciaISO(new Date().getFullYear());
}

/**
 * Anos navegáveis: ano civil atual ∪ anos com dados (ordenados).
 */
export function anosNavegaveis(
  anosComDados: number[],
  anoAtual: number = new Date().getFullYear(),
): number[] {
  return [...new Set([anoAtual, ...anosComDados])].sort((a, b) => a - b);
}

/** Extrai mês/ano de uma data ISO YYYY-MM-DD. */
export function mesAnoDeISO(dataIso: string): { mes: number; ano: number } {
  const [anoStr, mesStr] = dataIso.split('-');
  const ano = Number(anoStr);
  const mes = Number(mesStr);
  if (!Number.isFinite(ano) || !Number.isFinite(mes) || mes < 1 || mes > 12) {
    const hoje = new Date();
    return { mes: hoje.getMonth() + 1, ano: hoje.getFullYear() };
  }
  return { mes, ano };
}
