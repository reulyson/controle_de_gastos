import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '@/compartilhado/api/servicos';
import { chavesConsulta } from '@/compartilhado/api/chavesConsulta';
import { useCarteira } from '@/compartilhado/contexto/ContextoCarteira';
import type { IdRecurso } from '@/compartilhado/api/tipos';
import {
  cn,
  formatarMesCompleto,
  formatarMoeda,
  formatarTitulo,
  idComoTexto,
} from '@/compartilhado/formatacao';
import { EstadoConsulta } from '@/compartilhado/ui/EstadoConsulta';
import { GavetaLateral } from '@/compartilhado/ui/GavetaLateral';

interface GavetaDetalheFaturaCartaoProps {
  aberta: boolean;
  cartaoId: IdRecurso | null;
  ano: number;
  mes: number;
  rotulo?: string;
  onFechar: () => void;
}

export function GavetaDetalheFaturaCartao({
  aberta,
  cartaoId,
  ano,
  mes,
  rotulo,
  onFechar,
}: GavetaDetalheFaturaCartaoProps) {
  const { carteiraId } = useCarteira();
  const qc = useQueryClient();

  const consulta = useQuery({
    queryKey:
      cartaoId && aberta
        ? chavesConsulta.cartoes.fatura(idComoTexto(cartaoId), ano, mes)
        : ['fatura-vazia'],
    queryFn: () => api.cartoes.fatura(idComoTexto(cartaoId!), ano, mes),
    enabled: Boolean(cartaoId) && aberta,
  });

  const pagamento = useMutation({
    mutationFn: (item: { id: IdRecurso; pago: boolean }) =>
      api.pagamentos.alternar({
        tipo: 'cartao',
        referencia_id: item.id,
        mes,
        ano,
        pago: item.pago,
      }),
    onSuccess: async () => {
      if (cartaoId) {
        await qc.invalidateQueries({
          queryKey: chavesConsulta.cartoes.fatura(idComoTexto(cartaoId), ano, mes),
        });
      }
      if (carteiraId) {
        await qc.invalidateQueries({ queryKey: ['grade-controle', carteiraId] });
      }
    },
  });

  const titulo = rotulo
    ? `Fatura — ${rotulo}`
    : `Fatura — ${formatarMesCompleto(mes)}/${ano}`;

  return (
    <GavetaLateral aberta={aberta} titulo={titulo} onFechar={onFechar} largura="lg">
      <EstadoConsulta
        carregando={consulta.isLoading}
        erro={consulta.error instanceof Error ? consulta.error : null}
        onRecarregar={() => void consulta.refetch()}
      >
        {consulta.data ? (
          <div className="space-y-4">
            <div className="rounded-xl bg-fin-teal-50 p-4">
              <p className="text-xs font-semibold uppercase text-fin-teal-800">Total da fatura</p>
              <p className="text-2xl font-bold text-fin-teal-900">
                {formatarMoeda(consulta.data.total)}
              </p>
            </div>
            <ul className="divide-y divide-slate-100 rounded-xl border border-slate-200">
              {consulta.data.itens.map((item) => (
                <li key={item.id} className="flex items-center gap-3 px-4 py-3">
                  <button
                    type="button"
                    disabled={pagamento.isPending}
                    onClick={() =>
                      pagamento.mutate({ id: item.id, pago: !item.pago })
                    }
                    className={cn(
                      'flex h-7 w-7 shrink-0 items-center justify-center rounded-md border',
                      item.pago
                        ? 'border-fin-teal-500 bg-fin-teal-500 text-white'
                        : 'border-slate-300 bg-white',
                    )}
                    aria-label="Alternar pagamento"
                  >
                    <span className="material-symbols-outlined text-sm">check</span>
                  </button>
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium text-slate-800">
                      {formatarTitulo(item.descricao)}
                    </p>
                    {item.recorrente ? (
                      <p className="text-xs text-slate-500">Recorrente</p>
                    ) : null}
                  </div>
                  <p className="font-semibold tabular-nums">{formatarMoeda(item.valor)}</p>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </EstadoConsulta>
    </GavetaLateral>
  );
}
