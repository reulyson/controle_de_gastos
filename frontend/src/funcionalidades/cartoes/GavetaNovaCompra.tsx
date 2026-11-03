import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { api } from '@/compartilhado/api/servicos';
import { chavesConsulta } from '@/compartilhado/api/chavesConsulta';
import type { RecorrenciaLancamento } from '@/compartilhado/api/tipos';
import { useCarteira } from '@/compartilhado/contexto/ContextoCarteira';
import { idComoTexto } from '@/compartilhado/formatacao';
import { Botao } from '@/compartilhado/ui/Botao';
import { GavetaLateral } from '@/compartilhado/ui/GavetaLateral';

interface GavetaNovaCompraProps {
  aberta: boolean;
  onFechar: () => void;
}

export function GavetaNovaCompra({ aberta, onFechar }: GavetaNovaCompraProps) {
  const { carteiraId, anoPadrao } = useCarteira();
  const qc = useQueryClient();

  const [cartaoId, setCartaoId] = useState('');
  const [descricao, setDescricao] = useState('');
  const [valor, setValor] = useState('');
  const [parcelas, setParcelas] = useState('1');
  const [recorrencia, setRecorrencia] = useState<RecorrenciaLancamento>('unica');
  const [mes, setMes] = useState(new Date().getMonth() + 1);
  const [ano, setAno] = useState(anoPadrao);

  const cartoes = useQuery({
    queryKey: carteiraId ? chavesConsulta.cartoes.lista(carteiraId) : ['cartoes-vazio'],
    queryFn: () => api.cartoes.listar(carteiraId!),
    enabled: Boolean(carteiraId) && aberta,
  });

  useEffect(() => {
    if (!aberta) return;
    setDescricao('');
    setValor('');
    setParcelas('1');
    setRecorrencia('unica');
    setMes(new Date().getMonth() + 1);
    setAno(anoPadrao);
    if (cartoes.data?.[0]) setCartaoId(idComoTexto(cartoes.data[0].id));
  }, [aberta, anoPadrao, cartoes.data]);

  const salvar = useMutation({
    mutationFn: () =>
      api.compras.criar({
        cartao_id: cartaoId,
        descricao: descricao.trim(),
        valor: Number(valor.replace(',', '.')),
        parcelas: Number(parcelas),
        recorrencia,
        mes_referencia: mes,
        ano_referencia: ano,
      }),
    onSuccess: async () => {
      if (carteiraId) {
        await qc.invalidateQueries({ queryKey: ['grade-controle', carteiraId] });
      }
      onFechar();
    },
  });

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
            disabled={!cartaoId || !descricao.trim() || !valor}
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
            Cartão
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
        </div>
        <div>
          <label className="fin-label" htmlFor="desc-compra">
            Descrição
          </label>
          <input
            id="desc-compra"
            className="fin-input"
            value={descricao}
            onChange={(e) => setDescricao(e.target.value)}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="fin-label" htmlFor="valor-compra">
              Valor
            </label>
            <input
              id="valor-compra"
              className="fin-input"
              value={valor}
              onChange={(e) => setValor(e.target.value)}
            />
          </div>
          <div>
            <label className="fin-label" htmlFor="parcelas">
              Parcelas
            </label>
            <input
              id="parcelas"
              type="number"
              min={1}
              className="fin-input"
              value={parcelas}
              onChange={(e) => setParcelas(e.target.value)}
            />
          </div>
        </div>
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
                    : 'border-slate-200'
                }`}
              >
                {r === 'unica' ? 'Única' : 'Mensal'}
              </button>
            ))}
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="fin-label" htmlFor="mes-compra">
              Mês
            </label>
            <input
              id="mes-compra"
              type="number"
              min={1}
              max={12}
              className="fin-input"
              value={mes}
              onChange={(e) => setMes(Number(e.target.value))}
            />
          </div>
          <div>
            <label className="fin-label" htmlFor="ano-compra">
              Ano
            </label>
            <input
              id="ano-compra"
              type="number"
              className="fin-input"
              value={ano}
              onChange={(e) => setAno(Number(e.target.value))}
            />
          </div>
        </div>
      </div>
    </GavetaLateral>
  );
}
