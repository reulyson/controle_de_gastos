import type { CelulaGrade } from '@/compartilhado/api/tipos';
import { cn, formatarMoeda } from '@/compartilhado/formatacao';

interface CelulaFinanceiraProps {
  celula: CelulaGrade | undefined;
  mesAtivo: boolean;
  onAbrirDetalhe: (celula: CelulaGrade) => void;
  onAlternarPago: (celula: CelulaGrade) => void;
  alternando?: boolean;
}

export function CelulaFinanceira({
  celula,
  mesAtivo,
  onAbrirDetalhe,
  onAlternarPago,
  alternando,
}: CelulaFinanceiraProps) {
  if (!celula || celula.valor === 0) {
    return <td className="border border-slate-100 bg-slate-50/50 px-1 py-1 text-center text-xs text-slate-300">—</td>;
  }

  return (
    <td
      className={cn(
        'border border-slate-100 px-1 py-1',
        mesAtivo && 'bg-fin-teal-50/40 ring-1 ring-inset ring-fin-teal-200/60',
      )}
    >
      <div className="flex items-center gap-1">
        <button
          type="button"
          disabled={alternando}
          onClick={() => onAlternarPago(celula)}
          className={cn(
            'flex h-6 w-6 shrink-0 items-center justify-center rounded-md border transition',
            celula.pago
              ? 'border-fin-teal-500 bg-fin-teal-500 text-white'
              : 'border-slate-300 bg-white text-transparent hover:border-fin-teal-400',
          )}
          aria-label={celula.pago ? 'Marcar como pendente' : 'Marcar como pago'}
        >
          <span className="material-symbols-outlined text-sm">check</span>
        </button>
        <button
          type="button"
          onClick={() => onAbrirDetalhe(celula)}
          className={cn(
            'min-w-0 flex-1 truncate rounded-md px-1 py-0.5 text-right text-xs font-semibold tabular-nums hover:bg-white',
            celula.pago ? 'text-slate-600' : 'text-slate-900',
          )}
        >
          {formatarMoeda(celula.valor)}
        </button>
      </div>
    </td>
  );
}
