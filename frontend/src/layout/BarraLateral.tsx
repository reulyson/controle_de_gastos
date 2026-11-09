import { useAuth } from '@/compartilhado/contexto/ContextoAuth';
import { cn, formatarTitulo } from '@/compartilhado/formatacao';
import { Botao } from '@/compartilhado/ui/Botao';
import { NavLink } from 'react-router-dom';

const CHAVE_LATERAL = 'finflow.lateral.recolhida';

const itens = [
  { para: '/', rotulo: 'Controle', icone: 'grid_view' },
  { para: '/receitas', rotulo: 'Receitas', icone: 'trending_up' },
  { para: '/despesas', rotulo: 'Despesas', icone: 'trending_down' },
  { para: '/cartoes', rotulo: 'Cartões', icone: 'credit_card' },
  { para: '/relatorios', rotulo: 'Relatórios', icone: 'bar_chart' },
  { para: '/configuracoes', rotulo: 'Configurações', icone: 'settings' },
] as const;

export function lerLateralRecolhida(): boolean {
  try {
    const v = localStorage.getItem(CHAVE_LATERAL);
    if (v === null) return true;
    return v === '1';
  } catch {
    return true;
  }
}

function gravarLateralRecolhida(recolhida: boolean): void {
  try {
    localStorage.setItem(CHAVE_LATERAL, recolhida ? '1' : '0');
  } catch {
    /* ignore */
  }
}

interface BarraLateralProps {
  recolhida: boolean;
  onAlternar: () => void;
}

export function BarraLateral({ recolhida, onAlternar }: BarraLateralProps) {
  const { usuario, logout } = useAuth();
  const nome = formatarTitulo(usuario?.nome ?? '');

  return (
    <aside
      className={cn(
        'fixed inset-y-0 left-0 z-40 hidden h-screen flex-col overflow-visible bg-fin-gradient text-white transition-[width] duration-200 lg:flex',
        recolhida ? 'w-14' : 'w-48',
      )}
    >
      <div
        className={cn(
          'relative shrink-0 border-b border-white/10 py-4',
          recolhida ? 'px-2' : 'px-3',
        )}
      >
        <div className={cn('flex items-center', recolhida ? 'justify-center' : 'gap-2')}>
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/15 shadow-glow">
            <span className="material-symbols-outlined text-[20px]">account_balance_wallet</span>
          </div>
          {!recolhida ? (
            <div className="min-w-0">
              <p className="text-[10px] uppercase tracking-widest text-teal-100/80">FinFlow</p>
              <p className="truncate text-base font-bold leading-tight">Controle</p>
            </div>
          ) : null}
        </div>
        <button
          type="button"
          onClick={onAlternar}
          title={recolhida ? 'Expandir menu' : 'Recolher menu'}
          aria-label={recolhida ? 'Expandir menu' : 'Recolher menu'}
          className="absolute top-1/2 right-0 z-50 flex h-5 w-5 -translate-y-1/2 translate-x-1/2 items-center justify-center rounded-full border border-slate-200/80 bg-white text-slate-600 shadow-md transition hover:bg-slate-50"
        >
          <span className="material-symbols-outlined text-[14px] leading-none">
            {recolhida ? 'chevron_right' : 'chevron_left'}
          </span>
        </button>
      </div>
      <nav className="min-h-0 flex-1 space-y-0.5 overflow-y-auto p-2">
        {itens.map((item) => (
          <NavLink
            key={item.para}
            to={item.para}
            end={item.para === '/'}
            title={item.rotulo}
            aria-label={item.rotulo}
            className={({ isActive }) =>
              cn(
                'flex items-center rounded-xl py-2 text-sm font-medium transition',
                recolhida ? 'justify-center px-2' : 'gap-2 px-2.5',
                isActive
                  ? 'bg-white/15 text-white shadow-inner'
                  : 'text-teal-50/80 hover:bg-white/10 hover:text-white',
              )
            }
          >
            <span className="material-symbols-outlined text-[20px]">{item.icone}</span>
            {!recolhida ? <span className="truncate">{item.rotulo}</span> : null}
          </NavLink>
        ))}
      </nav>
      <div className={cn('shrink-0 space-y-2 border-t border-white/10', recolhida ? 'p-2' : 'p-3')}>
        {!recolhida ? (
          <p className="truncate text-xs font-semibold text-white" title={nome || 'Usuário'}>
            {nome || 'Usuário'}
          </p>
        ) : null}
        <Botao
          variante="secundario"
          className={cn(
            'border-white/20 bg-white/10 text-white hover:bg-white/20',
            recolhida ? 'w-full px-2 py-1.5' : 'w-full px-3 py-1.5 text-xs',
          )}
          onClick={() => void logout()}
          title="Sair"
          aria-label="Sair"
        >
          {recolhida ? (
            <span className="material-symbols-outlined text-[20px]">logout</span>
          ) : (
            'Sair'
          )}
        </Botao>
      </div>
    </aside>
  );
}

export { gravarLateralRecolhida };
