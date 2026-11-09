import { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/compartilhado/contexto/ContextoAuth';
import { useCarteira } from '@/compartilhado/contexto/ContextoCarteira';
import { useResumoMes } from '@/compartilhado/contexto/ContextoResumoMes';
import { cn, formatarMoeda, formatarTitulo, idComoTexto } from '@/compartilhado/formatacao';
import { Botao } from '@/compartilhado/ui/Botao';
import { MenuNovoLancamento } from '@/layout/MenuNovoLancamento';

export function CabecalhoTopo() {
  const local = useLocation();
  const navigate = useNavigate();
  const { logout, usuario } = useAuth();
  const {
    carteiraAtiva,
    carteiras,
    carregando,
    definirPadrao,
    anoSelecionado,
    anoAnterior,
    anoProximo,
    podeAnoAnterior,
    podeAnoProximo,
  } = useCarteira();
  const { saldoCarteira, chequeLivre } = useResumoMes();

  const [menuCarteiraAberto, setMenuCarteiraAberto] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const rota = local.pathname;
  const ehConfig = rota.startsWith('/configuracoes');
  const ehRelatorios = rota.startsWith('/relatorios');
  const mostraCarteira = !ehConfig;
  const mostraAno = !ehConfig;
  const mostraNovo = !ehConfig && !ehRelatorios;

  useEffect(() => {
    if (!menuCarteiraAberto) return;
    const fechar = (e: MouseEvent) => {
      if (!menuRef.current?.contains(e.target as Node)) {
        setMenuCarteiraAberto(false);
      }
    };
    document.addEventListener('mousedown', fechar);
    return () => document.removeEventListener('mousedown', fechar);
  }, [menuCarteiraAberto]);

  const nomeUsuario = formatarTitulo(usuario?.nome ?? '');

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/90 backdrop-blur-md">
      <div className="flex flex-wrap items-center justify-between gap-2 px-3 py-1.5 lg:px-4">
        <div className="flex min-w-0 flex-wrap items-end gap-3">
          {mostraCarteira ? (
            <>
              <div className="min-w-0">
                <p className="text-[10px] font-semibold uppercase tracking-wide text-fin-teal-700">
                  Carteira ativa
                </p>
                <div className="relative mt-0" ref={menuRef}>
                  <button
                    type="button"
                    className="inline-flex max-w-full items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-2.5 py-1 text-left text-sm font-bold text-slate-800 hover:border-fin-teal-300"
                    onClick={() => setMenuCarteiraAberto((v) => !v)}
                  >
                    <span className="truncate">
                      {carregando
                        ? 'Carregando...'
                        : (carteiraAtiva?.nome ?? 'Nenhuma carteira')}
                    </span>
                    <span className="material-symbols-outlined text-base text-slate-500">
                      expand_more
                    </span>
                  </button>
                  {menuCarteiraAberto ? (
                    <div className="absolute left-0 z-40 mt-1 min-w-[220px] overflow-hidden rounded-xl border border-slate-200 bg-white py-1 shadow-panel">
                      {carteiras.map((c) => {
                        const id = idComoTexto(c.id);
                        const ativa =
                          carteiraAtiva != null && idComoTexto(carteiraAtiva.id) === id;
                        return (
                          <button
                            key={id}
                            type="button"
                            className={cn(
                              'flex w-full items-center justify-between px-4 py-2 text-left text-sm hover:bg-fin-teal-50',
                              ativa && 'font-semibold text-fin-teal-800',
                            )}
                            onClick={() => {
                              setMenuCarteiraAberto(false);
                              if (!ativa) void definirPadrao(id);
                            }}
                          >
                            <span>{c.nome}</span>
                            {ativa ? (
                              <span className="material-symbols-outlined text-base text-fin-teal-600">
                                check
                              </span>
                            ) : null}
                          </button>
                        );
                      })}
                      <div className="my-1 border-t border-slate-100" />
                      <button
                        type="button"
                        className="flex w-full items-center gap-2 px-4 py-2 text-left text-sm font-semibold text-fin-teal-700 hover:bg-fin-teal-50"
                        onClick={() => {
                          setMenuCarteiraAberto(false);
                          navigate('/carteiras/nova');
                        }}
                      >
                        <span className="material-symbols-outlined text-base">add</span>
                        Nova carteira
                      </button>
                    </div>
                  ) : null}
                </div>
              </div>
              <div className="hidden sm:block">
                <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-500">
                  Saldo carteira
                </p>
                <p className="text-sm font-bold tabular-nums text-fin-teal-700">
                  {saldoCarteira != null && Number.isFinite(saldoCarteira)
                    ? formatarMoeda(saldoCarteira)
                    : '—'}
                </p>
              </div>
              <div className="hidden sm:block">
                <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-500">
                  Cheque
                </p>
                <p className="text-sm font-bold tabular-nums text-slate-800">
                  {chequeLivre != null && Number.isFinite(chequeLivre)
                    ? formatarMoeda(chequeLivre)
                    : '—'}
                </p>
              </div>
            </>
          ) : (
            <h1 className="text-sm font-bold text-slate-800">Configurações</h1>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-1.5">
          {mostraAno ? (
            <div className="flex items-center rounded-lg border border-slate-200 bg-white px-0.5 py-0">
              <button
                type="button"
                className="rounded-md p-1 text-slate-600 hover:bg-slate-100 disabled:opacity-40"
                aria-label="Ano anterior"
                disabled={!podeAnoAnterior}
                onClick={anoAnterior}
              >
                <span className="material-symbols-outlined text-lg">chevron_left</span>
              </button>
              <span className="min-w-[3rem] text-center text-xs font-bold text-slate-800">
                {anoSelecionado}
              </span>
              <button
                type="button"
                className="rounded-md p-1 text-slate-600 hover:bg-slate-100 disabled:opacity-40"
                aria-label="Próximo ano"
                disabled={!podeAnoProximo}
                onClick={anoProximo}
              >
                <span className="material-symbols-outlined text-lg">chevron_right</span>
              </button>
            </div>
          ) : null}

          {mostraNovo ? <MenuNovoLancamento /> : null}

          <div className="flex items-center gap-2 lg:hidden">
            <span className="max-w-[140px] truncate text-xs font-semibold text-slate-600">
              {nomeUsuario || 'Usuário'}
            </span>
            <Botao
              variante="secundario"
              className="px-3 py-1 text-xs"
              onClick={() => void logout()}
            >
              Sair
            </Botao>
          </div>
        </div>
      </div>
    </header>
  );
}
