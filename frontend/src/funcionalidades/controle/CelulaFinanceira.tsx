import type { CelulaGrade } from '@/compartilhado/api/tipos';
import { cn, formatarMoedaCompacta, valorNumerico } from '@/compartilhado/formatacao';

interface CelulaFinanceiraProps {
  celula: CelulaGrade | undefined;
  mesAtivo: boolean;
  onAbrirDetalhe: (celula: CelulaGrade) => void;
}

function classeCorValor(pago: boolean): string {
  return pago ? 'text-emerald-600' : 'text-slate-900';
}

/** Ocorrência mensal existente (inclui valor 0 de variável). */
function temOcorrencia(celula: CelulaGrade | undefined): celula is CelulaGrade {
  return Boolean(celula?.referencia_id);
}

export function CelulaFinanceira({
  celula,
  mesAtivo,
  onAbrirDetalhe,
}: CelulaFinanceiraProps) {
  const valorNum = temOcorrencia(celula) ? valorNumerico(celula.valor) : null;

  if (!temOcorrencia(celula) || valorNum === null) {
    return (
      <td
        className={cn(
          'border border-slate-100 px-0.5 py-0.5 text-center text-xs text-slate-300',
          mesAtivo ? 'bg-orange-50' : 'bg-slate-50/50',
        )}
      >
        —
      </td>
    );
  }

  return (
    <td
      className={cn(
        'border border-slate-100 px-0.5 py-0.5',
        mesAtivo && 'bg-orange-50 ring-1 ring-inset ring-orange-200/80',
      )}
    >
      <button
        type="button"
        onClick={() => onAbrirDetalhe(celula)}
        title={formatarMoedaCompacta(valorNum)}
        className={cn(
          'w-full whitespace-nowrap rounded px-0.5 py-0.5 text-center text-xs font-bold tabular-nums hover:bg-white/80',
          classeCorValor(celula.pago),
        )}
      >
        {formatarMoedaCompacta(valorNum)}
      </button>
    </td>
  );
}
