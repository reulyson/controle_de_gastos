import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { api } from '@/compartilhado/api/servicos';
import { chavesConsulta } from '@/compartilhado/api/chavesConsulta';
import type { IdRecurso, RecorrenciaLancamento, TipoLancamento } from '@/compartilhado/api/tipos';
import { useCarteira } from '@/compartilhado/contexto/ContextoCarteira';
import { Botao } from '@/compartilhado/ui/Botao';
import { GavetaLateral } from '@/compartilhado/ui/GavetaLateral';
import { SeletorCategoriaTags } from '@/compartilhado/ui/SeletorCategoriaTags';

interface GavetaFormularioLancamentoProps {
  aberta: boolean;
  tipo: TipoLancamento;
  onFechar: () => void;
}

export function GavetaFormularioLancamento({
  aberta,
  tipo,
  onFechar,
}: GavetaFormularioLancamentoProps) {
  const { carteiraId, anoPadrao } = useCarteira();
  const qc = useQueryClient();

  const [descricao, setDescricao] = useState('');
  const [valor, setValor] = useState('');
  const [recorrencia, setRecorrencia] = useState<RecorrenciaLancamento>('unica');
  const [mes, setMes] = useState(new Date().getMonth() + 1);
  const [ano, setAno] = useState(anoPadrao);
  const [categoriaId, setCategoriaId] = useState<IdRecurso | null>(null);
  const [tagIds, setTagIds] = useState<IdRecurso[]>([]);

  useEffect(() => {
    if (!aberta) return;
    setDescricao('');
    setValor('');
    setRecorrencia('unica');
    setMes(new Date().getMonth() + 1);
    setAno(anoPadrao);
    setCategoriaId(null);
    setTagIds([]);
  }, [aberta, anoPadrao]);

  const salvar = useMutation({
    mutationFn: async () => {
      if (!carteiraId) throw new Error('Carteira não disponível');
      const payload = {
        carteira_id: carteiraId,
        descricao: descricao.trim(),
        valor: Number(valor.replace(',', '.')),
        categoria_id: categoriaId,
        tag_ids: tagIds,
        recorrencia,
        mes_referencia: mes,
        ano_referencia: ano,
      };
      if (tipo === 'receita') return api.receitas.criar(payload);
      return api.despesas.criar(payload);
    },
    onSuccess: async () => {
      if (!carteiraId) return;
      await qc.invalidateQueries({ queryKey: chavesConsulta.receitas.lista(carteiraId) });
      await qc.invalidateQueries({ queryKey: chavesConsulta.despesas.lista(carteiraId) });
      await qc.invalidateQueries({
        queryKey: ['grade-controle', carteiraId],
      });
      onFechar();
    },
  });

  const titulo = tipo === 'receita' ? 'Nova receita' : 'Nova despesa';

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
            disabled={!descricao.trim() || !valor || !carteiraId}
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
          salvar.mutate();
        }}
      >
        <div>
          <label className="fin-label" htmlFor="descricao">
            Descrição
          </label>
          <input
            id="descricao"
            className="fin-input"
            value={descricao}
            onChange={(e) => setDescricao(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="fin-label" htmlFor="valor">
            Valor (R$)
          </label>
          <input
            id="valor"
            className="fin-input"
            inputMode="decimal"
            value={valor}
            onChange={(e) => setValor(e.target.value)}
            required
          />
        </div>

        <SeletorCategoriaTags
          tipo={tipo}
          categoriaId={categoriaId}
          onCategoriaChange={setCategoriaId}
          tagIds={tagIds}
          onTagsChange={setTagIds}
        />

        <div>
          <span className="fin-label">Recorrência</span>
          <div className="flex gap-2">
            {(['unica', 'mensal'] as const).map((r) => (
              <button
                key={r}
                type="button"
                onClick={() => setRecorrencia(r)}
                className={`flex-1 rounded-xl border px-3 py-2 text-sm font-semibold ${
                  recorrencia === r
                    ? 'border-fin-teal-500 bg-fin-teal-50 text-fin-teal-800'
                    : 'border-slate-200 text-slate-600'
                }`}
              >
                {r === 'unica' ? 'Única' : 'Mensal'}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="fin-label" htmlFor="mes">
              Mês
            </label>
            <input
              id="mes"
              type="number"
              min={1}
              max={12}
              className="fin-input"
              value={mes}
              onChange={(e) => setMes(Number(e.target.value))}
            />
          </div>
          <div>
            <label className="fin-label" htmlFor="ano">
              Ano
            </label>
            <input
              id="ano"
              type="number"
              className="fin-input"
              value={ano}
              onChange={(e) => setAno(Number(e.target.value))}
            />
          </div>
        </div>

        {salvar.error instanceof Error ? (
          <p className="text-sm text-rose-600">{salvar.error.message}</p>
        ) : null}
      </form>
    </GavetaLateral>
  );
}
