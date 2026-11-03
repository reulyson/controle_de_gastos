import { Botao } from '@/compartilhado/ui/Botao';
import type { ReactNode } from 'react';

interface EstadoConsultaProps {
  carregando?: boolean;
  erro?: Error | null;
  vazio?: boolean;
  mensagemVazio?: string;
  onRecarregar?: () => void;
  children?: ReactNode;
}

export function EstadoConsulta({
  carregando,
  erro,
  vazio,
  mensagemVazio = 'Nenhum dado encontrado.',
  onRecarregar,
  children,
}: EstadoConsultaProps) {
  if (carregando) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-16 text-slate-500">
        <span className="material-symbols-outlined animate-spin text-4xl text-fin-teal-600">
          progress_activity
        </span>
        <p className="text-sm font-medium">Carregando...</p>
      </div>
    );
  }

  if (erro) {
    return (
      <div className="fin-panel mx-auto max-w-lg p-8 text-center">
        <span className="material-symbols-outlined text-4xl text-rose-500">error</span>
        <p className="mt-3 font-semibold text-slate-800">Não foi possível carregar os dados</p>
        <p className="mt-1 text-sm text-slate-500">{erro.message}</p>
        {onRecarregar ? (
          <Botao className="mt-4" variante="secundario" onClick={onRecarregar}>
            Tentar novamente
          </Botao>
        ) : null}
      </div>
    );
  }

  if (vazio) {
    return (
      <div className="fin-panel flex flex-col items-center justify-center gap-2 p-12 text-center">
        <span className="material-symbols-outlined text-4xl text-slate-300">inbox</span>
        <p className="text-sm text-slate-500">{mensagemVazio}</p>
      </div>
    );
  }

  return <>{children}</>;
}
