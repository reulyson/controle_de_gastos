import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useMemo, useState } from 'react';
import { api } from '@/compartilhado/api/servicos';
import { chavesConsulta } from '@/compartilhado/api/chavesConsulta';
import type { CelulaGrade, IdRecurso, LinhaGrade, TotaisGrade } from '@/compartilhado/api/tipos';
import { useCarteira } from '@/compartilhado/contexto/ContextoCarteira';
import { formatarMesCompleto } from '@/compartilhado/formatacao';
import { Botao } from '@/compartilhado/ui/Botao';
import { EstadoConsulta } from '@/compartilhado/ui/EstadoConsulta';
import { ANOS_DISPONIVEIS, MESES } from '@/tema/tokens';
import { GavetaDetalheCelula } from '@/funcionalidades/controle/GavetaDetalheCelula';
import { IndicadoresControle } from '@/funcionalidades/controle/IndicadoresControle';
import { ModalFecharMes } from '@/funcionalidades/controle/ModalFecharMes';
import { TabelaFinanceiraAnual } from '@/funcionalidades/controle/TabelaFinanceiraAnual';
import { GavetaDetalheFaturaCartao } from '@/funcionalidades/cartoes/GavetaDetalheFaturaCartao';

const totaisVazios: TotaisGrade = {
  total_receita: 0,
  total_despesa: 0,
  total_orcado: 0,
  total_pago: 0,
  caixa: 0,
};

export function PaginaControle() {
  const { carteiraId, anoPadrao } = useCarteira();
  const qc = useQueryClient();
  const [ano, setAno] = useState(anoPadrao);
  const [mesResumo, setMesResumo] = useState(new Date().getMonth() + 1);
  const [celulaDetalhe, setCelulaDetalhe] = useState<{
    celula: CelulaGrade;
    rotulo: string;
  } | null>(null);
  const [faturaContexto, setFaturaContexto] = useState<{
    cartaoId: IdRecurso;
    mes: number;
    rotulo: string;
  } | null>(null);
  const [modalFechar, setModalFechar] = useState(false);
  const [celulaAlternando, setCelulaAlternando] = useState<IdRecurso | null>(null);

  const consulta = useQuery({
    queryKey: carteiraId
      ? chavesConsulta.grade.controle(carteiraId, ano, mesResumo)
      : ['grade-controle-vazio'],
    queryFn: () => api.carteiras.gradeControle(carteiraId!, ano, mesResumo),
    enabled: Boolean(carteiraId),
  });

  const pagamento = useMutation({
    mutationFn: api.pagamentos.alternar,
    onMutate: ({ referencia_id }) => setCelulaAlternando(referencia_id),
    onSettled: async () => {
      setCelulaAlternando(null);
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

  const grade = consulta.data;
  const linhas = grade?.linhas ?? [];
  const totais = grade?.totais ?? totaisVazios;
  const indicadores = grade?.indicadores;

  const mesFechado = grade?.mes_fechado ?? false;

  const alternarPago = (celula: CelulaGrade) => {
    if (!celula.referencia_id) return;
    pagamento.mutate({
      tipo: celula.tipo,
      referencia_id: celula.referencia_id,
      mes: celula.mes,
      ano,
      pago: !celula.pago,
    });
  };

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
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Painel de controle</h2>
          <p className="text-sm text-slate-500">Grade anual com visão do mês selecionado</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <label className="text-xs font-semibold text-slate-500">
            Ano
            <select
              className="fin-input ml-2 w-auto min-w-[100px]"
              value={ano}
              onChange={(e) => setAno(Number(e.target.value))}
            >
              {ANOS_DISPONIVEIS.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </label>
          <Botao
            variante="secundario"
            icone={<span className="material-symbols-outlined text-base">lock</span>}
            onClick={() => setModalFechar(true)}
            disabled={mesFechado}
          >
            {mesFechado ? 'Mês fechado' : 'Fechar mês'}
          </Botao>
        </div>
      </div>

      <div className="fin-panel p-4">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h3 className="font-semibold text-slate-800">{tituloResumo}</h3>
          <select
            className="fin-input w-auto min-w-[160px]"
            value={mesResumo}
            onChange={(e) => setMesResumo(Number(e.target.value))}
          >
            {MESES.map((m) => (
              <option key={m.valor} value={m.valor}>
                {m.rotulo}
              </option>
            ))}
          </select>
        </div>
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
        <TabelaFinanceiraAnual
          linhas={linhas}
          totais={totais}
          mesResumo={mesResumo}
          onAbrirDetalhe={(celula, rotulo) => setCelulaDetalhe({ celula, rotulo })}
          onAlternarPago={alternarPago}
          celulaAlternando={celulaAlternando}
          onAbrirFatura={abrirFatura}
        />
      </EstadoConsulta>

      <GavetaDetalheCelula
        celula={celulaDetalhe?.celula ?? null}
        rotuloLinha={celulaDetalhe?.rotulo}
        onFechar={() => setCelulaDetalhe(null)}
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
