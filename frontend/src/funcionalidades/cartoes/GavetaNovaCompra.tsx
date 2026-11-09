import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { api } from '@/compartilhado/api/servicos';
import { chavesConsulta } from '@/compartilhado/api/chavesConsulta';
import type { IdRecurso } from '@/compartilhado/api/tipos';
import { useCarteira } from '@/compartilhado/contexto/ContextoCarteira';
import { dataReferenciaISO, formatarTitulo, idComoTexto, mesAnoDeISO } from '@/compartilhado/formatacao';
import { Botao } from '@/compartilhado/ui/Botao';
import { CampoData } from '@/compartilhado/ui/CampoData';
import { CampoMoeda } from '@/compartilhado/ui/CampoMoeda';
import { GavetaLateral } from '@/compartilhado/ui/GavetaLateral';
import { SeletorCategoria } from '@/compartilhado/ui/SeletorCategoria';
import { SeletorSegmento } from '@/compartilhado/ui/SeletorSegmento';

interface GavetaNovaCompraProps {
  aberta: boolean;
  onFechar: () => void;
}

type ModoCompra = 'recorrente' | 'parcelado';

const MODOS_COMPRA = [
  { valor: 'recorrente' as const, rotulo: 'Recorrente' },
  { valor: 'parcelado' as const, rotulo: 'Parcelado' },
];

export function GavetaNovaCompra({ aberta, onFechar }: GavetaNovaCompraProps) {
  const { carteiraId, anoSelecionado } = useCarteira();
  const qc = useQueryClient();

  const [cartaoId, setCartaoId] = useState('');
  const [descricao, setDescricao] = useState('');
  const [categoriaId, setCategoriaId] = useState<IdRecurso | null>(null);
  const [valor, setValor] = useState<number | null>(null);
  const [modo, setModo] = useState<ModoCompra>('recorrente');
  const [meses, setMeses] = useState('12');
  const [parcelas, setParcelas] = useState('2');
  const [vencimento, setVencimento] = useState(() => dataReferenciaISO(anoSelecionado));

  const cartoes = useQuery({
    queryKey: carteiraId ? chavesConsulta.cartoes.lista(carteiraId) : ['cartoes-vazio'],
    queryFn: () => api.cartoes.listar(carteiraId!),
    enabled: Boolean(carteiraId) && aberta,
  });

  useEffect(() => {
    if (!aberta) return;
    setDescricao('');
    setCategoriaId(null);
    setValor(null);
    setModo('recorrente');
    setMeses('12');
    setParcelas('2');
    setVencimento(dataReferenciaISO(anoSelecionado));
    if (cartoes.data?.[0]) setCartaoId(idComoTexto(cartoes.data[0].id));
    else setCartaoId('');
  }, [aberta, anoSelecionado, cartoes.data]);

  const salvar = useMutation({
    mutationFn: () => {
      if (valor === null || valor <= 0) throw new Error('Informe um valor válido');
      const { mes, ano } = mesAnoDeISO(vencimento);
      const recorrente = modo === 'recorrente';
      return api.compras.criar({
        cartao_id: cartaoId,
        descricao: formatarTitulo(descricao),
        valor,
        recorrencia: recorrente ? 'mensal' : 'unica',
        data_vencimento: vencimento,
        mes_referencia: mes,
        ano_referencia: ano,
        categoria_id: categoriaId ?? undefined,
        ...(recorrente
          ? { quantidade_meses: Math.max(1, Number(meses) || 12) }
          : { parcelas: Math.max(1, Number(parcelas) || 1) }),
      });
    },
    onSuccess: async () => {
      if (carteiraId) {
        await qc.invalidateQueries({ queryKey: chavesConsulta.carteiras.anos(carteiraId) });
        await qc.invalidateQueries({ queryKey: ['grade-controle', carteiraId] });
      }
      onFechar();
    },
  });

  const podeSalvar =
    Boolean(cartaoId) &&
    Boolean(descricao.trim()) &&
    valor !== null &&
    valor > 0 &&
    Boolean(vencimento);

  return (
    <GavetaLateral
      aberta={aberta}
      titulo="Nova compra no cartão"
      onFechar={onFechar}
      rodape={
        <div className="flex justify-end gap-2">
          <Botao variante="secundario" onClick={onFechar}>
            Cancelar
          </Botao>
          <Botao
            carregando={salvar.isPending}
            disabled={!podeSalvar}
            onClick={() => salvar.mutate()}
          >
            Salvar
          </Botao>
        </div>
      }
    >
      <div className="space-y-4">
        <div>
          <label className="fin-label" htmlFor="cartao">
            Cartão *
          </label>
          <select
            id="cartao"
            className="fin-input"
            value={cartaoId}
            onChange={(e) => setCartaoId(e.target.value)}
          >
            <option value="">Selecione...</option>
            {cartoes.data?.map((c) => (
              <option key={c.id} value={idComoTexto(c.id)}>
                {c.nome}
              </option>
            ))}
          </select>
          {!cartoes.data?.length ? (
            <p className="mt-1 text-xs text-slate-500">
              Cadastre um cartão na página Cartões antes de lançar a compra.
            </p>
          ) : null}
        </div>

        <div>
          <label className="fin-label" htmlFor="desc-compra">
            Descrição *
          </label>
          <input
            id="desc-compra"
            className="fin-input"
            value={descricao}
            onChange={(e) => setDescricao(e.target.value)}
          />
        </div>

        <SeletorCategoria
          tipo="compra"
          categoriaId={categoriaId}
          onCategoriaChange={setCategoriaId}
        />

        <CampoMoeda
          id="valor-compra"
          label="Valor (R$)"
          valor={valor}
          onChange={setValor}
          obrigatorio
        />

        <SeletorSegmento
          rotulo="Tipo"
          valor={modo}
          opcoes={MODOS_COMPRA}
          onChange={setModo}
        />

        {modo === 'recorrente' ? (
          <div>
            <label className="fin-label" htmlFor="meses-compra">
              Meses
            </label>
            <input
              id="meses-compra"
              type="number"
              min={1}
              className="fin-input"
              value={meses}
              onChange={(e) => setMeses(e.target.value)}
            />
          </div>
        ) : (
          <div>
            <label className="fin-label" htmlFor="parcelas-compra">
              Número de parcelas
            </label>
            <input
              id="parcelas-compra"
              type="number"
              min={1}
              className="fin-input"
              value={parcelas}
              onChange={(e) => setParcelas(e.target.value)}
            />
          </div>
        )}

        <CampoData
          id="vencimento-compra"
          label="Vencimento"
          valor={vencimento}
          onChange={setVencimento}
          obrigatorio
        />

        {salvar.error instanceof Error ? (
          <p className="text-sm text-rose-600">{salvar.error.message}</p>
        ) : null}
      </div>
    </GavetaLateral>
  );
}
