import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect, useMemo, useState } from 'react';
import { api } from '@/compartilhado/api/servicos';
import { chavesConsulta } from '@/compartilhado/api/chavesConsulta';
import type { CelulaGrade, IdRecurso, LinhaGrade } from '@/compartilhado/api/tipos';
import { useCarteira } from '@/compartilhado/contexto/ContextoCarteira';
import { useResumoMes } from '@/compartilhado/contexto/ContextoResumoMes';
import { formatarMesCompleto } from '@/compartilhado/formatacao';
import { Botao } from '@/compartilhado/ui/Botao';
import { EstadoConsulta } from '@/compartilhado/ui/EstadoConsulta';
import { MESES } from '@/tema/tokens';
import {
  GavetaDetalheCelula,
  type EscopoValorMensal,
} from '@/funcionalidades/controle/GavetaDetalheCelula';
import { IndicadoresControle } from '@/funcionalidades/controle/IndicadoresControle';
import { ModalFecharMes } from '@/funcionalidades/controle/ModalFecharMes';
import { TabelaFinanceiraAnual } from '@/funcionalidades/controle/TabelaFinanceiraAnual';
import { GavetaDetalheFaturaCartao } from '@/funcionalidades/cartoes/GavetaDetalheFaturaCartao';

export function PaginaControle() {
  const { carteiraId, anoSelecionado: ano } = useCarteira();
  const { definirResumoMes, limparResumoMes } = useResumoMes();
  const qc = useQueryClient();
  const [mesResumo, setMesResumo] = useState(new Date().getMonth() + 1);
  const [celulaDetalhe, setCelulaDetalhe] = useState<{
    celula: CelulaGrade;
    rotulo: string;
    recorrente: boolean;
  } | null>(null);
  const [faturaContexto, setFaturaContexto] = useState<{
    cartaoId: IdRecurso;
    mes: number;
    rotulo: string;
  } | null>(null);
  const [modalFechar, setModalFechar] = useState(false);

  const consulta = useQuery({
    queryKey: carteiraId
      ? chavesConsulta.grade.controle(carteiraId, ano, mesResumo)
      : ['grade-controle-vazio'],
    queryFn: () => api.carteiras.gradeControle(carteiraId!, ano, mesResumo),
    enabled: Boolean(carteiraId),
  });

  const pagamento = useMutation({
    mutationFn: api.pagamentos.alternar,
    onSettled: async () => {
      if (carteiraId) {
        await qc.invalidateQueries({
          queryKey: chavesConsulta.grade.controle(carteiraId, ano, mesResumo),
        });
      }
    },
  });

  const fecharMes = useMutation({
    mutationFn: () =>
      api.fechamentos.fecharMes(carteiraId!, { mes: mesResumo, ano }),
    onSuccess: async () => {
      setModalFechar(false);
      if (carteiraId) {
        await qc.invalidateQueries({
          queryKey: chavesConsulta.grade.controle(carteiraId, ano, mesResumo),
        });
      }
    },
  });

  const salvarValorCelula = useMutation({
    mutationFn: async (args: {
      celula: CelulaGrade;
      valor: number;
      escopo: EscopoValorMensal;
    }) => {
      const id = String(args.celula.id);
      const body = { valor: args.valor, escopo: args.escopo };
      if (args.celula.tipo === 'receita') {
        return api.mensais.atualizarReceita(id, body);
      }
      return api.mensais.atualizarDespesa(id, body);
    },
    onSuccess: async () => {
      setCelulaDetalhe(null);
      if (carteiraId) {
        await qc.invalidateQueries({
          queryKey: chavesConsulta.grade.controle(carteiraId, ano, mesResumo),
        });
      }
    },
  });

  const grade = consulta.data;
  const linhas = grade?.linhas ?? [];
  const indicadores = grade?.indicadores;

  const mesFechado = grade?.mes_fechado ?? false;

  useEffect(() => {
    if (!indicadores) {
      limparResumoMes();
      return;
    }
    definirResumoMes({
      saldoCarteira: Number(indicadores.saldo_caixa),
      chequeLivre: Number(indicadores.cheque_livre),
    });
  }, [definirResumoMes, indicadores, limparResumoMes]);

  useEffect(() => () => limparResumoMes(), [limparResumoMes]);

  const abrirFatura = (linha: LinhaGrade, mes: number) => {
    const ref = linha.celulas.find((c) => c.mes === mes)?.referencia_id ?? linha.id;
    setFaturaContexto({ cartaoId: ref, mes, rotulo: linha.rotulo });
  };

  const tituloResumo = useMemo(
    () => `Resumo — ${formatarMesCompleto(mesResumo)}/${ano}`,
    [mesResumo, ano],
  );

  if (!carteiraId) {
    return (
      <EstadoConsulta
        carregando={false}
        vazio
        mensagemVazio="Cadastre uma carteira na API para começar o controle."
      />
    );
  }

  return (
    <div className="space-y-3">
      <div>
        <h2 className="text-xl font-bold leading-tight text-slate-800">Painel de controle</h2>
        <p className="text-xs text-slate-500">Grade anual com visão do mês selecionado</p>
      </div>

      <div className="fin-panel p-3">
        <h3 className="mb-3 text-sm font-semibold text-slate-800">{tituloResumo}</h3>
        <EstadoConsulta
          carregando={consulta.isLoading}
          erro={consulta.error instanceof Error ? consulta.error : null}
          onRecarregar={() => void consulta.refetch()}
        >
          {indicadores ? <IndicadoresControle indicadores={indicadores} /> : null}
        </EstadoConsulta>
      </div>

      <EstadoConsulta
        carregando={consulta.isLoading}
        erro={consulta.error instanceof Error ? consulta.error : null}
        onRecarregar={() => void consulta.refetch()}
      >
        <div className="fin-panel overflow-hidden">
          <div className="flex flex-wrap items-center gap-2 border-b border-slate-100 px-3 py-2">
            <select
              className="fin-input w-auto min-w-[140px] py-1.5 text-sm"
              value={mesResumo}
              onChange={(e) => setMesResumo(Number(e.target.value))}
              aria-label="Mês da visão"
            >
              {MESES.map((m) => (
                <option key={m.valor} value={m.valor}>
                  {m.rotulo}
                </option>
              ))}
            </select>
            <Botao
              variante="secundario"
              className="px-3 py-1.5 text-xs"
              icone={<span className="material-symbols-outlined text-sm">lock</span>}
              onClick={() => setModalFechar(true)}
              disabled={mesFechado}
            >
              {mesFechado ? 'Mês fechado' : 'Fechar mês'}
            </Botao>
          </div>
          <TabelaFinanceiraAnual
            linhas={linhas}
            mesResumo={mesResumo}
            onAbrirDetalhe={(celula, linha) =>
              setCelulaDetalhe({
                celula,
                rotulo: linha.rotulo,
                recorrente: linha.recorrencia === 'mensal',
              })
            }
            onAbrirFatura={abrirFatura}
            semPainel
          />
        </div>
      </EstadoConsulta>

      <GavetaDetalheCelula
        celula={celulaDetalhe?.celula ?? null}
        rotuloLinha={celulaDetalhe?.rotulo}
        recorrente={celulaDetalhe?.recorrente ?? false}
        ano={ano}
        salvando={salvarValorCelula.isPending || pagamento.isPending}
        onFechar={() => setCelulaDetalhe(null)}
        onSalvarValor={(args) => salvarValorCelula.mutate(args)}
        onAlternarPago={(celula, pago) => {
          if (!celula.referencia_id) return;
          pagamento.mutate({
            tipo: celula.tipo,
            referencia_id: celula.referencia_id,
            mes: celula.mes,
            ano,
            pago,
          });
        }}
      />

      <GavetaDetalheFaturaCartao
        cartaoId={faturaContexto?.cartaoId ?? null}
        ano={ano}
        mes={faturaContexto?.mes ?? mesResumo}
        rotulo={faturaContexto?.rotulo}
        aberta={faturaContexto !== null}
        onFechar={() => setFaturaContexto(null)}
      />

      <ModalFecharMes
        aberto={modalFechar}
        mes={mesResumo}
        ano={ano}
        carregando={fecharMes.isPending}
        onConfirmar={() => fecharMes.mutate()}
        onCancelar={() => setModalFechar(false)}
      />
    </div>
  );
}
