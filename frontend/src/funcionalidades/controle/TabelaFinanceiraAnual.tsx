import { Fragment } from 'react';
import type { CelulaGrade, IdRecurso, LinhaGrade, TotaisGrade } from '@/compartilhado/api/tipos';
import { formatarMesAbreviado, formatarMoeda } from '@/compartilhado/formatacao';
import { CelulaFinanceira } from '@/funcionalidades/controle/CelulaFinanceira';

interface TabelaFinanceiraAnualProps {
  linhas: LinhaGrade[];
  totais: TotaisGrade;
  mesResumo: number;
  onAbrirDetalhe: (celula: CelulaGrade, rotulo: string) => void;
  onAlternarPago: (celula: CelulaGrade) => void;
  celulaAlternando?: IdRecurso | null;
  onAbrirFatura?: (linha: LinhaGrade, mes: number) => void;
}

const SECOES: LinhaGrade['secao'][] = ['RECEITAS', 'DESPESAS', 'CARTOES'];

const rotulosSecao: Record<LinhaGrade['secao'], string> = {
  RECEITAS: 'Receitas',
  DESPESAS: 'Despesas',
  CARTOES: 'Cartões',
};

export function TabelaFinanceiraAnual({
  linhas,
  totais,
  mesResumo,
  onAbrirDetalhe,
  onAlternarPago,
  celulaAlternando,
  onAbrirFatura,
}: TabelaFinanceiraAnualProps) {
  const meses = Array.from({ length: 12 }, (_, i) => i + 1);

  const linhasPorSecao = (secao: LinhaGrade['secao']) =>
    linhas.filter((l) => l.secao === secao);

  const celulaMes = (linha: LinhaGrade, mes: number) =>
    linha.celulas.find((c) => c.mes === mes);

  return (
    <div className="fin-panel overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-[960px] w-full border-collapse text-sm">
          <thead>
            <tr className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
              <th className="sticky left-0 z-10 min-w-[180px] border border-slate-100 bg-slate-50 px-3 py-2">
                Item
              </th>
              {meses.map((m) => (
                <th
                  key={m}
                  className="border border-slate-100 px-2 py-2 text-center font-semibold"
                >
                  {formatarMesAbreviado(m)}
                </th>
              ))}
              <th className="border border-slate-100 px-3 py-2 text-right">Total</th>
            </tr>
          </thead>
          <tbody>
            {SECOES.map((secao) => {
              const grupo = linhasPorSecao(secao);
              return (
                <Fragment key={secao}>
                  <tr className="bg-fin-teal-900/5">
                    <td
                      colSpan={14}
                      className="border border-slate-100 px-3 py-2 text-xs font-bold uppercase tracking-wider text-fin-teal-800"
                    >
                      {rotulosSecao[secao]}
                    </td>
                  </tr>
                  {grupo.length === 0 ? (
                    <tr key={`vazio-${secao}`}>
                      <td
                        colSpan={14}
                        className="border border-slate-100 px-3 py-4 text-center text-xs italic text-slate-400"
                      >
                        Nenhum lançamento nesta seção
                      </td>
                    </tr>
                  ) : (
                    grupo.map((linha) => (
                      <tr key={linha.id} className="hover:bg-slate-50/80">
                        <td className="sticky left-0 z-10 border border-slate-100 bg-white px-3 py-2 font-medium text-slate-700">
                          <div>{linha.rotulo}</div>
                          {linha.categoria ? (
                            <div className="text-xs text-slate-400">{linha.categoria}</div>
                          ) : null}
                        </td>
                        {meses.map((m) => {
                          const cel = celulaMes(linha, m);
                          if (secao === 'CARTOES' && cel && onAbrirFatura) {
                            return (
                              <td
                                key={`${linha.id}-${m}`}
                                className="border border-slate-100 px-1 py-1 text-center"
                              >
                                <button
                                  type="button"
                                  className="w-full rounded-md px-1 py-1 text-xs font-semibold text-fin-teal-700 hover:bg-fin-teal-50"
                                  onClick={() => onAbrirFatura(linha, m)}
                                >
                                  {cel.valor ? formatarMoeda(cel.valor) : '—'}
                                </button>
                              </td>
                            );
                          }
                          return (
                            <CelulaFinanceira
                              key={`${linha.id}-${m}`}
                              celula={cel}
                              mesAtivo={m === mesResumo}
                              onAbrirDetalhe={(c) => onAbrirDetalhe(c, linha.rotulo)}
                              onAlternarPago={onAlternarPago}
                              alternando={celulaAlternando === cel?.id}
                            />
                          );
                        })}
                        <td className="border border-slate-100 px-3 py-2 text-right font-semibold tabular-nums">
                          {formatarMoeda(linha.total_anual ?? 0)}
                        </td>
                      </tr>
                    ))
                  )}
                </Fragment>
              );
            })}
            <tr className="bg-slate-800 text-white">
              <td className="sticky left-0 border border-slate-700 bg-slate-800 px-3 py-2 text-xs font-bold uppercase">
                Totais
              </td>
              <td colSpan={12} className="border border-slate-700 px-3 py-2 text-xs">
                <div className="flex flex-wrap gap-x-6 gap-y-1">
                  <span>Receita: {formatarMoeda(totais.total_receita)}</span>
                  <span>Despesa: {formatarMoeda(totais.total_despesa)}</span>
                  <span>Orçado: {formatarMoeda(totais.total_orcado)}</span>
                  <span>Pago: {formatarMoeda(totais.total_pago)}</span>
                  <span>Caixa: {formatarMoeda(totais.caixa)}</span>
                </div>
              </td>
              <td className="border border-slate-700" />
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
