import { cn } from '@/compartilhado/formatacao';

export interface OpcaoSegmento<T extends string> {
  valor: T;
  rotulo: string;
}

interface SeletorSegmentoProps<T extends string> {
  rotulo: string;
  valor: T;
  opcoes: readonly OpcaoSegmento<T>[];
  onChange: (valor: T) => void;
}

export function SeletorSegmento<T extends string>({
  rotulo,
  valor,
  opcoes,
  onChange,
}: SeletorSegmentoProps<T>) {
  return (
    <div>
      <span className="fin-label">{rotulo}</span>
      <div className="flex gap-2">
        {opcoes.map((opcao) => (
          <button
            key={opcao.valor}
            type="button"
            onClick={() => onChange(opcao.valor)}
            className={cn(
              'flex-1 rounded-xl border px-3 py-2 text-sm font-semibold',
              valor === opcao.valor
                ? 'border-fin-teal-500 bg-fin-teal-50 text-fin-teal-800'
                : 'border-slate-200 text-slate-600',
            )}
          >
            {opcao.rotulo}
          </button>
        ))}
      </div>
    </div>
  );
}
