import { useQuery } from '@tanstack/react-query';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { api } from '@/compartilhado/api/servicos';
import { chavesConsulta } from '@/compartilhado/api/chavesConsulta';
import { useCarteira } from '@/compartilhado/contexto/ContextoCarteira';
import { formatarMesAbreviado, formatarMoeda } from '@/compartilhado/formatacao';
import { EstadoConsulta } from '@/compartilhado/ui/EstadoConsulta';
import { CORES_GRAFICO } from '@/tema/tokens';

export function PaginaRelatorios() {
  const { carteiraId, anoSelecionado: ano } = useCarteira();

  const consulta = useQuery({
    queryKey: carteiraId ? chavesConsulta.relatorio.resumo(carteiraId, ano) : ['relatorio-vazio'],
    queryFn: () => api.carteiras.relatorio(carteiraId!, ano),
    enabled: Boolean(carteiraId),
  });

  const dadosMeses =
    consulta.data?.meses.map((m) => ({
      nome: formatarMesAbreviado(m.mes),
      receitas: m.receitas,
      despesas: m.despesas,
      saldo: m.saldo,
    })) ?? [];

  const temDados =
    dadosMeses.some((d) => d.receitas !== 0 || d.despesas !== 0) ||
    (consulta.data?.por_categoria.length ?? 0) > 0;

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-bold text-slate-800">Relatórios</h2>
        <p className="text-sm text-slate-500">Visão gráfica quando houver dados</p>
      </div>

      <EstadoConsulta
        carregando={consulta.isLoading}
        erro={consulta.error instanceof Error ? consulta.error : null}
        vazio={!consulta.isLoading && !temDados}
        mensagemVazio="Sem dados para gráficos neste ano."
        onRecarregar={() => void consulta.refetch()}
      >
        <div className="grid gap-4 xl:grid-cols-2">
          <div className="fin-panel p-4">
            <h3 className="mb-4 font-semibold text-slate-800">Receitas x Despesas</h3>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={dadosMeses}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="nome" tick={{ fontSize: 12 }} />
                  <YAxis tickFormatter={(v) => formatarMoeda(Number(v))} width={90} tick={{ fontSize: 11 }} />
                  <Tooltip formatter={(v: number) => formatarMoeda(v)} />
                  <Legend />
                  <Bar dataKey="receitas" fill={CORES_GRAFICO[0]} name="Receitas" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="despesas" fill={CORES_GRAFICO[1]} name="Despesas" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="fin-panel p-4">
            <h3 className="mb-4 font-semibold text-slate-800">Saldo mensal</h3>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={dadosMeses}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="nome" tick={{ fontSize: 12 }} />
                  <YAxis tickFormatter={(v) => formatarMoeda(Number(v))} width={90} tick={{ fontSize: 11 }} />
                  <Tooltip formatter={(v: number) => formatarMoeda(v)} />
                  <Line
                    type="monotone"
                    dataKey="saldo"
                    stroke={CORES_GRAFICO[2]}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    name="Saldo"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {(consulta.data?.por_categoria.length ?? 0) > 0 ? (
          <div className="fin-panel overflow-hidden">
            <h3 className="border-b border-slate-100 px-4 py-3 font-semibold">Por categoria</h3>
            <table className="w-full text-sm">
              <tbody>
                {consulta.data?.por_categoria.map((c) => (
                  <tr key={`${c.nome}-${c.tipo}`} className="border-t border-slate-100">
                    <td className="px-4 py-2">{c.nome}</td>
                    <td className="px-4 py-2 capitalize text-slate-500">{c.tipo}</td>
                    <td className="px-4 py-2 text-right font-semibold">{formatarMoeda(c.valor)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </EstadoConsulta>
    </div>
  );
}
