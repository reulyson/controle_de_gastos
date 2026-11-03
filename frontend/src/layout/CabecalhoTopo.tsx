import { useCarteira } from '@/compartilhado/contexto/ContextoCarteira';
import { MenuNovoLancamento } from '@/layout/MenuNovoLancamento';

export function CabecalhoTopo() {
  const { carteiraAtiva, carregando } = useCarteira();

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/90 backdrop-blur-md">
      <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 lg:px-6">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-fin-teal-700">
            Carteira ativa
          </p>
          <h1 className="text-lg font-bold text-slate-800">
            {carregando ? 'Carregando...' : (carteiraAtiva?.nome ?? 'Nenhuma carteira')}
          </h1>
        </div>
        <MenuNovoLancamento />
      </div>
    </header>
  );
}
