import type { IndicadoresMes } from '@/compartilhado/api/tipos';
import { CartaoKpi } from '@/compartilhado/ui/CartaoKpi';
import { FaixaResumoCaixa } from '@/funcionalidades/controle/FaixaResumoCaixa';

interface IndicadoresControleProps {
  indicadores: IndicadoresMes;
}

export function IndicadoresControle({ indicadores }: IndicadoresControleProps) {
  return (
    <div>
      <div className="grid gap-3 sm:grid-cols-3">
        <CartaoKpi
          rotulo="Receitas"
          valor={indicadores.receitas}
          icone="trending_up"
          destaque="positivo"
        />
        <CartaoKpi
          rotulo="Despesas"
          valor={indicadores.despesas}
          icone="trending_down"
          destaque="negativo"
        />
        <CartaoKpi rotulo="Orçado" valor={indicadores.orcado} icone="pie_chart" />
      </div>
      <FaixaResumoCaixa
        caixa={Number(indicadores.saldo_caixa)}
        pagos={Number(indicadores.total_pago ?? 0)}
        pendencias={Number(indicadores.pendencias)}
      />
    </div>
  );
}
