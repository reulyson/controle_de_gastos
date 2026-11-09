import { Fragment } from 'react';
import type { CelulaGrade, LinhaGrade } from '@/compartilhado/api/tipos';
import {
  cn,
  formatarMesAbreviado,
  formatarMoeda,
  formatarMoedaCompacta,
  formatarTitulo,
} from '@/compartilhado/formatacao';
import { CelulaFinanceira } from '@/funcionalidades/controle/CelulaFinanceira';

interface TabelaFinanceiraAnualProps {
  linhas: LinhaGrade[];
  mesResumo: number;
  onAbrirDetalhe: (celula: CelulaGrade, linha: LinhaGrade) => void;
  onAbrirFatura?: (linha: LinhaGrade, mes: number) => void;
  /** Quando true, não envolve em fin-panel (pai já fornece o painel). */
  semPainel?: boolean;
}

const SECOES: LinhaGrade['secao'][] = ['RECEITAS', 'DESPESAS', 'CARTOES'];

const rotulosSecao: Record<LinhaGrade['secao'], string> = {
  RECEITAS: 'Receitas',
  DESPESAS: 'Despesas',
  CARTOES: 'Cartões',
};

export function TabelaFinanceiraAnual({
  linhas,
  mesResumo,
  onAbrirDetalhe,
  onAbrirFatura,
  semPainel = false,
}: TabelaFinanceiraAnualProps) {
  const meses = Array.from({ length: 12 }, (_, i) => i + 1);

  const linhasPorSecao = (secao: LinhaGrade['secao']) =>
    linhas.filter((l) => l.secao === secao);

  const celulaMes = (linha: LinhaGrade, mes: number) =>
    linha.celulas.find((c) => c.mes === mes);

  const tabela = (
    <div className="overflow-x-auto">
      <table className="w-full table-fixed border-collapse text-sm">
        <colgroup>
          <col className="w-[7.5rem]" />
          {meses.map((m) => (
            <col key={m} />
          ))}
        </colgroup>
        <thead>
          <tr className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <th className="sticky left-0 z-10 border border-slate-100 bg-slate-50 px-2 py-1.5">
              Item
            </th>
            {meses.map((m) => {
              const ativo = m === mesResumo;
              return (
                <th
                  key={m}
                  className={cn(
                    'border px-0.5 py-1.5 text-center font-semibold',
                    ativo
                      ? 'border-orange-200 bg-orange-100 text-orange-800'
                      : 'border-slate-100',
                  )}
                >
                  {formatarMesAbreviado(m)}
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {SECOES.map((secao) => {
            const grupo = linhasPorSecao(secao);
            return (
              <Fragment key={secao}>
                <tr className="bg-fin-teal-900/5">
                  <td
                    colSpan={13}
                    className="border border-slate-100 px-2 py-1.5 text-xs font-bold uppercase tracking-wider text-fin-teal-800"
                  >
                    {rotulosSecao[secao]}
                  </td>
                </tr>
                {grupo.length === 0 ? (
                  <tr key={`vazio-${secao}`}>
                    <td
                      colSpan={13}
                      className="border border-slate-100 px-2 py-3 text-center text-xs italic text-slate-400"
                    >
                      Nenhum lançamento nesta seção
                    </td>
                  </tr>
                ) : (
                  grupo.map((linha) => (
                    <tr key={linha.id} className="hover:bg-slate-50/80">
                      <td className="sticky left-0 z-10 max-w-[7.5rem] border border-slate-100 bg-white px-2 py-1 font-medium text-slate-700">
                        <div className="truncate" title={formatarTitulo(linha.rotulo)}>
                          {formatarTitulo(linha.rotulo)}
                        </div>
                        {linha.categoria ? (
                          <div
                            className="truncate text-xs text-slate-400"
                            title={formatarTitulo(linha.categoria)}
                          >
                            {formatarTitulo(linha.categoria)}
                          </div>
                        ) : null}
                      </td>
                      {meses.map((m) => {
                        const cel = celulaMes(linha, m);
                        const mesAtivo = m === mesResumo;
                        if (secao === 'CARTOES' && cel && onAbrirFatura) {
                          return (
                            <td
                              key={`${linha.id}-${m}`}
                              className={cn(
                                'border px-0.5 py-0.5 text-center',
                                mesAtivo
                                  ? 'border-orange-200 bg-orange-50'
                                  : 'border-slate-100',
                              )}
                            >
                              <button
                                type="button"
                                className="w-full truncate rounded px-0.5 py-0.5 text-xs font-semibold tabular-nums text-fin-teal-700 hover:bg-fin-teal-50"
                                onClick={() => onAbrirFatura(linha, m)}
                                title={
                                  cel.valor ? formatarMoeda(Number(cel.valor)) : undefined
                                }
                              >
                                {cel.valor
                                  ? formatarMoedaCompacta(cel.valor)
                                  : '—'}
                              </button>
                            </td>
                          );
                        }
                        return (
                          <CelulaFinanceira
                            key={`${linha.id}-${m}`}
                            celula={cel}
                            mesAtivo={mesAtivo}
                            onAbrirDetalhe={(c) => onAbrirDetalhe(c, linha)}
                          />
                        );
                      })}
                    </tr>
                  ))
                )}
              </Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );

  if (semPainel) return tabela;

  return <div className="fin-panel overflow-hidden">{tabela}</div>;
}
