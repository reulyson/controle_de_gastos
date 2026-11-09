import { formatarMoeda } from '@/compartilhado/formatacao';

interface ItemFaixa {
  rotulo: string;
  valor: number;
  destaque?: 'negativo' | 'neutro';
}

interface FaixaResumoCaixaProps {
  caixa: number;
  pagos: number;
  pendencias: number;
}

function Item({ rotulo, valor, destaque = 'neutro' }: ItemFaixa) {
  return (
    <div className="min-w-0 flex-1">
      <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">{rotulo}</p>
      <p
        className={
          destaque === 'negativo' && valor > 0
            ? 'mt-0.5 text-sm font-semibold tabular-nums text-rose-600'
            : 'mt-0.5 text-sm font-semibold tabular-nums text-slate-700'
        }
      >
        {formatarMoeda(valor)}
      </p>
    </div>
  );
}

/**
 * Nível 2 do resumo: caixa / pagos / pendências (discreto).
 */
export function FaixaResumoCaixa({ caixa, pagos, pendencias }: FaixaResumoCaixaProps) {
  return (
    <div className="mt-3 flex flex-wrap gap-4 rounded-xl border border-slate-100 bg-slate-50/80 px-3 py-2.5">
      <Item rotulo="Caixa" valor={caixa} />
      <Item rotulo="Pagos" valor={pagos} />
      <Item rotulo="Pendências" valor={pendencias} destaque="negativo" />
    </div>
  );
}
