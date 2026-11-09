import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { api } from '@/compartilhado/api/servicos';
import { chavesConsulta } from '@/compartilhado/api/chavesConsulta';
import type { IdRecurso, RecorrenciaLancamento, TipoLancamento } from '@/compartilhado/api/tipos';
import { useCarteira } from '@/compartilhado/contexto/ContextoCarteira';
import { dataReferenciaISO, formatarTitulo, mesAnoDeISO } from '@/compartilhado/formatacao';
import { Botao } from '@/compartilhado/ui/Botao';
import { CampoData } from '@/compartilhado/ui/CampoData';
import { CampoMoeda } from '@/compartilhado/ui/CampoMoeda';
import { GavetaLateral } from '@/compartilhado/ui/GavetaLateral';
import { SeletorCategoria } from '@/compartilhado/ui/SeletorCategoria';
import { SeletorSegmento } from '@/compartilhado/ui/SeletorSegmento';
import { ToggleLinha } from '@/compartilhado/ui/ToggleLinha';

interface GavetaFormularioLancamentoProps {
  aberta: boolean;
  tipo: TipoLancamento;
  onFechar: () => void;
}

const TIPOS_LANCAMENTO = [
  { valor: 'unica' as const, rotulo: 'Transação' },
  { valor: 'mensal' as const, rotulo: 'Recorrente' },
];

export function GavetaFormularioLancamento({
  aberta,
  tipo,
  onFechar,
}: GavetaFormularioLancamentoProps) {
  const { carteiraId, anoSelecionado } = useCarteira();
  const qc = useQueryClient();

  const [recorrencia, setRecorrencia] = useState<RecorrenciaLancamento>('unica');
  const [descricao, setDescricao] = useState('');
  const [categoriaId, setCategoriaId] = useState<IdRecurso | null>(null);
  const [valor, setValor] = useState<number | null>(null);
  const [data, setData] = useState(() => dataReferenciaISO(anoSelecionado));
  const [meses, setMeses] = useState('12');
  const [valorVariavel, setValorVariavel] = useState(false);

  useEffect(() => {
    if (!aberta) return;
    setRecorrencia('unica');
    setDescricao('');
    setCategoriaId(null);
    setValor(null);
    setData(dataReferenciaISO(anoSelecionado));
    setMeses('12');
    setValorVariavel(false);
  }, [aberta, anoSelecionado]);

  const salvar = useMutation({
    mutationFn: async () => {
      if (!carteiraId) throw new Error('Carteira não disponível');
      if (valor === null || valor <= 0) throw new Error('Informe um valor válido');
      const { mes, ano } = mesAnoDeISO(data);
      const payload = {
        carteira_id: carteiraId,
        descricao: formatarTitulo(descricao),
        valor,
        categoria_id: categoriaId,
        recorrencia,
        mes_referencia: mes,
        ano_referencia: ano,
        ...(recorrencia === 'mensal'
          ? {
              quantidade_meses: Math.max(1, Number(meses) || 12),
              valor_variavel: valorVariavel,
            }
          : {}),
      };
      if (tipo === 'receita') return api.receitas.criar(payload);
      return api.despesas.criar(payload);
    },
    onSuccess: async () => {
      if (!carteiraId) return;
      await qc.invalidateQueries({ queryKey: chavesConsulta.receitas.lista(carteiraId) });
      await qc.invalidateQueries({ queryKey: chavesConsulta.despesas.lista(carteiraId) });
      await qc.invalidateQueries({ queryKey: chavesConsulta.carteiras.anos(carteiraId) });
      await qc.invalidateQueries({
        queryKey: ['grade-controle', carteiraId],
      });
      onFechar();
    },
  });

  const titulo = tipo === 'receita' ? 'Nova receita' : 'Nova despesa';
  const podeSalvar =
    Boolean(descricao.trim()) && valor !== null && valor > 0 && Boolean(carteiraId) && Boolean(data);

  return (
    <GavetaLateral
      aberta={aberta}
      titulo={titulo}
      onFechar={onFechar}
      rodape={
        <div className="flex justify-end gap-2">
          <Botao variante="secundario" onClick={onFechar}>
            Cancelar
          </Botao>
          <Botao
            carregando={salvar.isPending}
            onClick={() => salvar.mutate()}
            disabled={!podeSalvar}
          >
            Salvar
          </Botao>
        </div>
      }
    >
      <form
        className="space-y-4"
        onSubmit={(e) => {
          e.preventDefault();
          if (podeSalvar) salvar.mutate();
        }}
      >
        <SeletorSegmento
          rotulo="Tipo"
          valor={recorrencia}
          opcoes={TIPOS_LANCAMENTO}
          onChange={setRecorrencia}
        />

        <div>
          <label className="fin-label" htmlFor="descricao">
            Descrição *
          </label>
          <input
            id="descricao"
            className="fin-input"
            value={descricao}
            onChange={(e) => setDescricao(e.target.value)}
            required
          />
        </div>

        <SeletorCategoria
          tipo={tipo}
          categoriaId={categoriaId}
          onCategoriaChange={setCategoriaId}
        />

        <CampoMoeda
          id="valor"
          label="Valor (R$)"
          valor={valor}
          onChange={setValor}
          obrigatorio
        />

        <CampoData
          id="data-lancamento"
          label="Data"
          valor={data}
          onChange={setData}
          obrigatorio
        />

        {recorrencia === 'mensal' ? (
          <>
            <div>
              <label className="fin-label" htmlFor="meses-lancamento">
                Meses
              </label>
              <input
                id="meses-lancamento"
                type="number"
                min={1}
                className="fin-input"
                value={meses}
                onChange={(e) => setMeses(e.target.value)}
              />
            </div>
            <ToggleLinha
              titulo="Valor variável"
              descricao="Mantém o valor só no mês inicial; os demais ficam zerados"
              ativo={valorVariavel}
              onAlternar={() => setValorVariavel((v) => !v)}
            />
          </>
        ) : null}

        {salvar.error instanceof Error ? (
          <p className="text-sm text-rose-600">{salvar.error.message}</p>
        ) : null}
      </form>
    </GavetaLateral>
  );
}
