import { cn } from '@/compartilhado/formatacao';
import type { ButtonHTMLAttributes, ReactNode } from 'react';

type VarianteBotao = 'primario' | 'secundario' | 'fantasma' | 'perigo';

interface BotaoProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: VarianteBotao;
  icone?: ReactNode;
  carregando?: boolean;
}

const estilosVariante: Record<VarianteBotao, string> = {
  primario:
    'bg-gradient-to-r from-fin-teal-600 to-fin-teal-700 text-white shadow-md hover:from-fin-teal-500 hover:to-fin-teal-600',
  secundario:
    'border border-slate-200 bg-white text-slate-700 hover:border-fin-teal-300 hover:bg-fin-teal-50',
  fantasma: 'text-slate-600 hover:bg-slate-100',
  perigo: 'bg-rose-600 text-white hover:bg-rose-500',
};

export function Botao({
  variante = 'primario',
  icone,
  carregando,
  className,
  children,
  disabled,
  ...props
}: BotaoProps) {
  return (
    <button
      type="button"
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50',
        estilosVariante[variante],
        className,
      )}
      disabled={disabled || carregando}
      {...props}
    >
      {carregando ? (
        <span className="material-symbols-outlined animate-spin text-base">progress_activity</span>
      ) : (
        icone
      )}
      {children}
    </button>
  );
}
