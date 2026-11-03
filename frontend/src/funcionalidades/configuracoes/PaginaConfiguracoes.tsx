import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { api } from '@/compartilhado/api/servicos';
import { chavesConsulta } from '@/compartilhado/api/chavesConsulta';
import { useCarteira } from '@/compartilhado/contexto/ContextoCarteira';
import { idComoTexto } from '@/compartilhado/formatacao';
import { Botao } from '@/compartilhado/ui/Botao';
import { EstadoConsulta } from '@/compartilhado/ui/EstadoConsulta';
import { ANOS_DISPONIVEIS } from '@/tema/tokens';

export function PaginaConfiguracoes() {
  const { carteiraId, carteiraAtiva } = useCarteira();
  const qc = useQueryClient();

  const [limiteCheque, setLimiteCheque] = useState('');
  const [saldoInicial, setSaldoInicial] = useState('');
  const [anoPadrao, setAnoPadrao] = useState<number>(ANOS_DISPONIVEIS[0]);
  const [ajusteValor, setAjusteValor] = useState('');
  const [ajusteDescricao, setAjusteDescricao] = useState('');
  const [mesReabrir, setMesReabrir] = useState(new Date().getMonth() + 1);
  const [anoReabrir, setAnoReabrir] = useState<number>(ANOS_DISPONIVEIS[0]);
  const [novaCategoria, setNovaCategoria] = useState('');
  const [tipoCategoria, setTipoCategoria] = useState<'receita' | 'despesa' | 'ambos'>('ambos');

  useEffect(() => {
    if (!carteiraAtiva) return;
    setLimiteCheque(String(carteiraAtiva.limite_cheque ?? ''));
    setSaldoInicial(String(carteiraAtiva.saldo_inicial ?? ''));
    setAnoPadrao(carteiraAtiva.ano_padrao ?? ANOS_DISPONIVEIS[0]);
  }, [carteiraAtiva]);

  const categorias = useQuery({
    queryKey: chavesConsulta.categorias.todas,
    queryFn: api.categorias.listar,
  });

  const salvarConfig = useMutation({
    mutationFn: () => {
      if (!carteiraId) throw new Error('Carteira não disponível');
      return api.carteiras.atualizarConfig(carteiraId, {
        limite_cheque: limiteCheque ? Number(limiteCheque.replace(',', '.')) : undefined,
        saldo_inicial: saldoInicial ? Number(saldoInicial.replace(',', '.')) : undefined,
        ano_padrao: anoPadrao,
      });
    },
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: chavesConsulta.carteiras.todas });
    },
  });

  const ajustarExtrato = useMutation({
    mutationFn: () => {
      if (!carteiraId) throw new Error('Carteira não disponível');
      return api.carteiras.ajustarExtrato(carteiraId, {
        valor: Number(ajusteValor.replace(',', '.')),
        descricao: ajusteDescricao.trim() || undefined,
      });
    },
    onSuccess: () => {
      setAjusteValor('');
      setAjusteDescricao('');
    },
  });

  const reabrirMes = useMutation({
    mutationFn: () => {
      if (!carteiraId) throw new Error('Carteira não disponível');
      return api.carteiras.reabrirMes(carteiraId, mesReabrir, anoReabrir);
    },
    onSuccess: async () => {
      if (carteiraId) {
        await qc.invalidateQueries({ queryKey: ['grade-controle', carteiraId] });
      }
    },
  });

  const criarCategoria = useMutation({
    mutationFn: () => api.categorias.criar({ nome: novaCategoria.trim(), tipo: tipoCategoria }),
    onSuccess: async () => {
      setNovaCategoria('');
      await qc.invalidateQueries({ queryKey: chavesConsulta.categorias.todas });
    },
  });

  const excluirCategoria = useMutation({
    mutationFn: (id: string) => api.categorias.excluir(id),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: chavesConsulta.categorias.todas });
    },
  });

  if (!carteiraId) {
    return (
      <EstadoConsulta vazio mensagemVazio="Nenhuma carteira disponível para configurar." />
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-800">Configurações</h2>
        <p className="text-sm text-slate-500">Parâmetros da carteira e manutenção</p>
      </div>

      <section className="fin-panel space-y-4 p-5">
        <h3 className="font-semibold text-slate-800">Carteira</h3>
        <div className="grid gap-4 md:grid-cols-3">
          <div>
            <label className="fin-label" htmlFor="limite">
              Limite cheque especial
            </label>
            <input
              id="limite"
              className="fin-input"
              value={limiteCheque}
              onChange={(e) => setLimiteCheque(e.target.value)}
            />
          </div>
          <div>
            <label className="fin-label" htmlFor="saldo">
              Saldo inicial
            </label>
            <input
              id="saldo"
              className="fin-input"
              value={saldoInicial}
              onChange={(e) => setSaldoInicial(e.target.value)}
            />
          </div>
          <div>
            <label className="fin-label" htmlFor="ano-padrao">
              Ano padrão
            </label>
            <select
              id="ano-padrao"
              className="fin-input"
              value={anoPadrao}
              onChange={(e) => setAnoPadrao(Number(e.target.value))}
            >
              {ANOS_DISPONIVEIS.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </div>
        </div>
        <Botao carregando={salvarConfig.isPending} onClick={() => salvarConfig.mutate()}>
          Salvar parâmetros
        </Botao>
      </section>

      <section className="fin-panel space-y-4 p-5">
        <h3 className="font-semibold text-slate-800">Ajustar extrato</h3>
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="fin-label" htmlFor="ajuste-valor">
              Valor
            </label>
            <input
              id="ajuste-valor"
              className="fin-input"
              value={ajusteValor}
              onChange={(e) => setAjusteValor(e.target.value)}
            />
          </div>
          <div>
            <label className="fin-label" htmlFor="ajuste-desc">
              Descrição
            </label>
            <input
              id="ajuste-desc"
              className="fin-input"
              value={ajusteDescricao}
              onChange={(e) => setAjusteDescricao(e.target.value)}
            />
          </div>
        </div>
        <Botao
          variante="secundario"
          disabled={!ajusteValor}
          carregando={ajustarExtrato.isPending}
          onClick={() => ajustarExtrato.mutate()}
        >
          Registrar ajuste
        </Botao>
      </section>

      <section className="fin-panel space-y-4 p-5">
        <h3 className="font-semibold text-slate-800">Reabrir mês</h3>
        <div className="flex flex-wrap gap-3">
          <input
            type="number"
            min={1}
            max={12}
            className="fin-input w-24"
            value={mesReabrir}
            onChange={(e) => setMesReabrir(Number(e.target.value))}
          />
          <select
            className="fin-input w-auto"
            value={anoReabrir}
            onChange={(e) => setAnoReabrir(Number(e.target.value))}
          >
            {ANOS_DISPONIVEIS.map((a) => (
              <option key={a} value={a}>
                {a}
              </option>
            ))}
          </select>
          <Botao variante="secundario" carregando={reabrirMes.isPending} onClick={() => reabrirMes.mutate()}>
            Reabrir
          </Botao>
        </div>
      </section>

      <section className="fin-panel space-y-4 p-5">
        <h3 className="font-semibold text-slate-800">Categorias (opcional)</h3>
        <div className="flex flex-wrap gap-2">
          <input
            className="fin-input min-w-[200px] flex-1"
            placeholder="Nome da categoria"
            value={novaCategoria}
            onChange={(e) => setNovaCategoria(e.target.value)}
          />
          <select
            className="fin-input w-auto"
            value={tipoCategoria}
            onChange={(e) =>
              setTipoCategoria(e.target.value as 'receita' | 'despesa' | 'ambos')
            }
          >
            <option value="ambos">Ambos</option>
            <option value="receita">Receita</option>
            <option value="despesa">Despesa</option>
          </select>
          <Botao
            disabled={!novaCategoria.trim()}
            carregando={criarCategoria.isPending}
            onClick={() => criarCategoria.mutate()}
          >
            Adicionar
          </Botao>
        </div>
        <ul className="divide-y divide-slate-100 rounded-xl border border-slate-200">
          {categorias.data?.map((c) => (
            <li key={c.id} className="flex items-center justify-between px-4 py-2 text-sm">
              <span>
                {c.nome}{' '}
                <span className="text-xs text-slate-400 capitalize">({c.tipo})</span>
              </span>
              <button
                type="button"
                className="text-rose-600 hover:underline"
                onClick={() => excluirCategoria.mutate(idComoTexto(c.id))}
              >
                Remover
              </button>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
