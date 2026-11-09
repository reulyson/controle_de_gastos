import { cn } from '@/compartilhado/formatacao';
import type { ReactNode } from 'react';
import { useEffect } from 'react';
import { createPortal } from 'react-dom';

type LarguraGaveta = 'sm' | 'md' | 'lg';

const LARGURAS: Record<LarguraGaveta, string> = {
  sm: 'w-full max-w-sm',
  md: 'w-full max-w-md',
  lg: 'w-full max-w-xl',
};

const PADDING_SECAO = 'px-5 py-4';

interface GavetaLateralProps {
  aberta: boolean;
  titulo: string;
  onFechar: () => void;
  children: ReactNode;
  largura?: LarguraGaveta;
  rodape?: ReactNode;
}

/**
 * Painel lateral em portal no `document.body`.
 * Só monta quando aberta — evita faixa fixa no cabeçalho com backdrop-blur.
 */
export function GavetaLateral({
  aberta,
  titulo,
  onFechar,
  children,
  largura = 'md',
  rodape,
}: GavetaLateralProps) {
  useEffect(() => {
    if (!aberta) return undefined;

    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onFechar();
    };
    const overflowAnterior = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    window.addEventListener('keydown', handler);

    return () => {
      document.body.style.overflow = overflowAnterior;
      window.removeEventListener('keydown', handler);
    };
  }, [aberta, onFechar]);

  if (!aberta || typeof document === 'undefined') {
    return null;
  }

  return createPortal(
    <>
      <div
        className="fixed inset-0 z-[80] bg-slate-900/40 backdrop-blur-sm"
        onClick={onFechar}
        aria-hidden
      />
      <aside
        className={cn(
          'fixed right-0 top-0 z-[90] flex h-full flex-col border-l border-slate-200 bg-white shadow-2xl',
          LARGURAS[largura],
        )}
        role="dialog"
        aria-modal="true"
        aria-label={titulo}
      >
        <header
          className={cn(
            'flex shrink-0 items-center justify-between border-b border-slate-100',
            PADDING_SECAO,
          )}
        >
          <h2 className="text-lg font-bold text-slate-800">{titulo}</h2>
          <button
            type="button"
            onClick={onFechar}
            className="rounded-lg p-2 text-slate-500 hover:bg-slate-100"
            aria-label="Fechar"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </header>
        <div className={cn('min-h-0 flex-1 overflow-y-auto', PADDING_SECAO)}>{children}</div>
        {rodape ? (
          <footer className={cn('shrink-0 border-t border-slate-100', PADDING_SECAO)}>
            {rodape}
          </footer>
        ) : null}
      </aside>
    </>,
    document.body,
  );
}
