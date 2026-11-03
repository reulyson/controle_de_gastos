import { cn, formatarMoeda } from '@/compartilhado/formatacao';

interface CartaoKpiProps {
  rotulo: string;
  valor: number;
  icone: string;
  destaque?: 'positivo' | 'negativo' | 'neutro';
  subtitulo?: string;
}

export function CartaoKpi({ rotulo, valor, icone, destaque = 'neutro', subtitulo }: CartaoKpiProps) {
  return (
    <div className="fin-panel relative overflow-hidden p-4">
      <div className="pointer-events-none absolute -right-6 -top-6 h-24 w-24 rounded-full bg-fin-teal-500/10" />
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{rotulo}</p>
          <p
            className={cn(
              'mt-1 text-xl font-bold tabular-nums',
              destaque === 'positivo' && 'text-fin-teal-700',
              destaque === 'negativo' && 'text-rose-600',
              destaque === 'neutro' && 'text-slate-800',
            )}
          >
            {formatarMoeda(valor)}
          </p>
          {subtitulo ? <p className="mt-1 text-xs text-slate-500">{subtitulo}</p> : null}
        </div>
        <span className="material-symbols-outlined rounded-xl bg-fin-teal-50 p-2 text-fin-teal-700">
          {icone}
        </span>
      </div>
    </div>
  );
}
