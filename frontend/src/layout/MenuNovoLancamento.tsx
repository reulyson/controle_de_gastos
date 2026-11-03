import { useState } from 'react';
import { Botao } from '@/compartilhado/ui/Botao';
import { GavetaFormularioLancamento } from '@/funcionalidades/lancamentos/GavetaFormularioLancamento';
import { GavetaNovaCompra } from '@/funcionalidades/cartoes/GavetaNovaCompra';
import type { TipoLancamento } from '@/compartilhado/api/tipos';

type AcaoMenu = TipoLancamento | 'cartao' | null;

export function MenuNovoLancamento() {
  const [menuAberto, setMenuAberto] = useState(false);
  const [acao, setAcao] = useState<AcaoMenu>(null);

  const abrir = (tipo: AcaoMenu) => {
    setMenuAberto(false);
    setAcao(tipo);
  };

  return (
    <>
      <div className="relative">
        <Botao
          icone={<span className="material-symbols-outlined text-base">add</span>}
          onClick={() => setMenuAberto((v) => !v)}
        >
          Novo lançamento
        </Botao>
        {menuAberto ? (
          <>
            <div className="fixed inset-0 z-20" onClick={() => setMenuAberto(false)} />
            <div className="absolute right-0 z-30 mt-2 w-56 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-panel">
              <button
                type="button"
                className="flex w-full items-center gap-2 px-4 py-3 text-left text-sm hover:bg-fin-teal-50"
                onClick={() => abrir('receita')}
              >
                <span className="material-symbols-outlined text-fin-teal-600">trending_up</span>
                Receita
              </button>
              <button
                type="button"
                className="flex w-full items-center gap-2 px-4 py-3 text-left text-sm hover:bg-fin-teal-50"
                onClick={() => abrir('despesa')}
              >
                <span className="material-symbols-outlined text-rose-500">trending_down</span>
                Despesa
              </button>
              <button
                type="button"
                className="flex w-full items-center gap-2 px-4 py-3 text-left text-sm hover:bg-fin-teal-50"
                onClick={() => abrir('cartao')}
              >
                <span className="material-symbols-outlined text-slate-600">credit_card</span>
                Compra no cartão
              </button>
            </div>
          </>
        ) : null}
      </div>

      <GavetaFormularioLancamento
        aberta={acao === 'receita'}
        tipo="receita"
        onFechar={() => setAcao(null)}
      />
      <GavetaFormularioLancamento
        aberta={acao === 'despesa'}
        tipo="despesa"
        onFechar={() => setAcao(null)}
      />
      <GavetaNovaCompra aberta={acao === 'cartao'} onFechar={() => setAcao(null)} />
    </>
  );
}
