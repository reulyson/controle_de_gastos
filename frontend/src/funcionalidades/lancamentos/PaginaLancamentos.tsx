import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { api } from '@/compartilhado/api/servicos';
import { chavesConsulta } from '@/compartilhado/api/chavesConsulta';
import type { Despesa, Receita, TipoLancamento } from '@/compartilhado/api/tipos';
import { useCarteira } from '@/compartilhado/contexto/ContextoCarteira';
import { formatarMoeda, idComoTexto } from '@/compartilhado/formatacao';
import { Botao } from '@/compartilhado/ui/Botao';
import { EstadoConsulta } from '@/compartilhado/ui/EstadoConsulta';
import { GavetaFormularioLancamento } from '@/funcionalidades/lancamentos/GavetaFormularioLancamento';

interface PaginaLancamentosProps {
  tipo: TipoLancamento;
}

export function PaginaLancamentos({ tipo }: PaginaLancamentosProps) {
  const { carteiraId } = useCarteira();
  const qc = useQueryClient();
  const [gavetaAberta, setGavetaAberta] = useState(false);

  type LancamentoLista = Receita | Despesa;

  const consulta = useQuery<LancamentoLista[]>({
    queryKey:
      carteiraId && tipo === 'receita'
        ? chavesConsulta.receitas.lista(carteiraId)
        : carteiraId && tipo === 'despesa'
          ? chavesConsulta.despesas.lista(carteiraId)
          : ['lancamentos-vazio', tipo],
    queryFn: async () => {
      if (tipo === 'receita') return api.receitas.listar(carteiraId!);
      return api.despesas.listar(carteiraId!);
    },
    enabled: Boolean(carteiraId),
  });

  const excluir = useMutation({
    mutationFn: (id: string) =>
      tipo === 'receita' ? api.receitas.excluir(id) : api.despesas.excluir(id),
    onSuccess: async () => {
      if (carteiraId) {
        const chave =
          tipo === 'receita'
            ? chavesConsulta.receitas.lista(carteiraId)
            : chavesConsulta.despesas.lista(carteiraId);
        await qc.invalidateQueries({ queryKey: chave });
        await qc.invalidateQueries({ queryKey: ['grade-controle', carteiraId] });
      }
    },
  });

  const titulo = tipo === 'receita' ? 'Receitas' : 'Despesas';

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">{titulo}</h2>
          <p className="text-sm text-slate-500">Lista consolidada de lançamentos</p>
        </div>
        <Botao
          icone={<span className="material-symbols-outlined text-base">add</span>}
          onClick={() => setGavetaAberta(true)}
        >
          Novo
        </Botao>
      </div>

      <EstadoConsulta
        carregando={consulta.isLoading}
        erro={consulta.error instanceof Error ? consulta.error : null}
        vazio={!consulta.isLoading && (consulta.data?.length ?? 0) === 0}
        mensagemVazio={`Nenhuma ${tipo} cadastrada.`}
        onRecarregar={() => void consulta.refetch()}
      >
        <div className="fin-panel overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Descrição</th>
                <th className="px-4 py-3">Recorrência</th>
                <th className="px-4 py-3 text-right">Valor</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {consulta.data?.map((item) => (
                <tr key={item.id} className="border-t border-slate-100">
                  <td className="px-4 py-3 font-medium">{item.descricao}</td>
                  <td className="px-4 py-3 capitalize text-slate-600">{item.recorrencia}</td>
                  <td className="px-4 py-3 text-right font-semibold tabular-nums">
                    {formatarMoeda(item.valor)}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                        item.pago
                          ? 'bg-fin-teal-100 text-fin-teal-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}
                    >
                      {item.pago ? 'Pago' : 'Pendente'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      type="button"
                      className="text-rose-600 hover:underline"
                      onClick={() => excluir.mutate(idComoTexto(item.id))}
                    >
                      Excluir
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </EstadoConsulta>

      <GavetaFormularioLancamento
        aberta={gavetaAberta}
        tipo={tipo}
        onFechar={() => setGavetaAberta(false)}
      />
    </div>
  );
}
