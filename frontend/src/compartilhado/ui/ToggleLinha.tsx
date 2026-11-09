import { cn } from '@/compartilhado/formatacao';

interface ToggleLinhaProps {
  rotulo?: string;
  titulo: string;
  descricao?: string;
  ativo: boolean;
  onAlternar: () => void;
}

/**
 * Linha com rótulo + switch (valor variável, aplicar em, etc.).
 */
export function ToggleLinha({
  rotulo,
  titulo,
  descricao,
  ativo,
  onAlternar,
}: ToggleLinhaProps) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-xl border border-slate-200 px-3 py-2.5">
      <div className="min-w-0 text-left">
        {rotulo ? <p className="fin-label mb-0">{rotulo}</p> : null}
        <p className="text-sm font-semibold text-slate-800">{titulo}</p>
        {descricao ? <p className="text-xs text-slate-500">{descricao}</p> : null}
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={ativo}
        onClick={onAlternar}
        className={cn(
          'relative h-7 w-12 shrink-0 rounded-full transition-colors',
          ativo ? 'bg-fin-teal-600' : 'bg-slate-300',
        )}
      >
        <span
          className={cn(
            'absolute top-0.5 left-0.5 h-6 w-6 rounded-full bg-white transition-transform',
            ativo ? 'translate-x-5' : 'translate-x-0',
          )}
        />
      </button>
    </div>
  );
}
