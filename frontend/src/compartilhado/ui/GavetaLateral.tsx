import { cn } from '@/compartilhado/formatacao';
import type { ReactNode } from 'react';
import { useEffect } from 'react';

interface GavetaLateralProps {
  aberta: boolean;
  titulo: string;
  onFechar: () => void;
  children: ReactNode;
  largura?: 'md' | 'lg';
  rodape?: ReactNode;
}

export function GavetaLateral({
  aberta,
  titulo,
  onFechar,
  children,
  largura = 'md',
  rodape,
}: GavetaLateralProps) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onFechar();
    };
    if (aberta) window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [aberta, onFechar]);

  return (
    <>
      <div
        className={cn(
          'fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-sm transition-opacity',
          aberta ? 'opacity-100' : 'pointer-events-none opacity-0',
        )}
        onClick={onFechar}
        aria-hidden={!aberta}
      />
      <aside
        className={cn(
          'fixed right-0 top-0 z-50 flex h-full flex-col border-l border-slate-200 bg-white shadow-2xl transition-transform duration-300',
          largura === 'md' ? 'w-full max-w-md' : 'w-full max-w-xl',
          aberta ? 'translate-x-0' : 'translate-x-full',
        )}
        role="dialog"
        aria-modal={aberta}
        aria-hidden={!aberta}
      >
        <header className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
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
        <div className="flex-1 overflow-y-auto px-5 py-4">{children}</div>
        {rodape ? (
          <footer className="border-t border-slate-100 px-5 py-4">{rodape}</footer>
        ) : null}
      </aside>
    </>
  );
}
