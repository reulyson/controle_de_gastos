import type { IndicadoresMes } from '@/compartilhado/api/tipos';
import { CartaoKpi } from '@/compartilhado/ui/CartaoKpi';

interface IndicadoresControleProps {
  indicadores: IndicadoresMes;
}

export function IndicadoresControle({ indicadores }: IndicadoresControleProps) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6">
      <CartaoKpi rotulo="Saldo caixa" valor={indicadores.saldo_caixa} icone="savings" destaque="positivo" />
      <CartaoKpi rotulo="Cheque livre" valor={indicadores.cheque_livre} icone="account_balance" />
      <CartaoKpi rotulo="Receitas" valor={indicadores.receitas} icone="trending_up" destaque="positivo" />
      <CartaoKpi rotulo="Despesas" valor={indicadores.despesas} icone="trending_down" destaque="negativo" />
      <CartaoKpi rotulo="Orçado" valor={indicadores.orcado} icone="pie_chart" />
      <CartaoKpi rotulo="Pendências" valor={indicadores.pendencias} icone="pending_actions" destaque="negativo" />
    </div>
  );
}
