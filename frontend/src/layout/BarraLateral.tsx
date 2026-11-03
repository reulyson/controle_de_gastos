import { cn } from '@/compartilhado/formatacao';
import { NavLink } from 'react-router-dom';

const itens = [
  { para: '/', rotulo: 'Controle', icone: 'grid_view' },
  { para: '/receitas', rotulo: 'Receitas', icone: 'trending_up' },
  { para: '/despesas', rotulo: 'Despesas', icone: 'trending_down' },
  { para: '/cartoes', rotulo: 'Cartões', icone: 'credit_card' },
  { para: '/relatorios', rotulo: 'Relatórios', icone: 'bar_chart' },
  { para: '/configuracoes', rotulo: 'Configurações', icone: 'settings' },
] as const;

export function BarraLateral() {
  return (
    <aside className="hidden w-64 shrink-0 flex-col bg-fin-gradient text-white lg:flex">
      <div className="border-b border-white/10 px-5 py-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/15 shadow-glow">
            <span className="material-symbols-outlined">account_balance_wallet</span>
          </div>
          <div>
            <p className="text-xs uppercase tracking-widest text-teal-100/80">FinFlow</p>
            <p className="text-lg font-bold leading-tight">Controle</p>
          </div>
        </div>
      </div>
      <nav className="flex-1 space-y-1 p-3">
        {itens.map((item) => (
          <NavLink
            key={item.para}
            to={item.para}
            end={item.para === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition',
                isActive
                  ? 'bg-white/15 text-white shadow-inner'
                  : 'text-teal-50/80 hover:bg-white/10 hover:text-white',
              )
            }
          >
            <span className="material-symbols-outlined text-[22px]">{item.icone}</span>
            {item.rotulo}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-white/10 p-4 text-xs text-teal-100/70">
        Planejamento financeiro pessoal
      </div>
    </aside>
  );
}
