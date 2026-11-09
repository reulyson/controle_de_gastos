import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '@/compartilhado/api/servicos';
import { chavesConsulta } from '@/compartilhado/api/chavesConsulta';
import type { Carteira, TipoCarteira } from '@/compartilhado/api/tipos';
import { useAuth } from '@/compartilhado/contexto/ContextoAuth';
import { useCarteira } from '@/compartilhado/contexto/ContextoCarteira';
import { cn, formatarMoeda, formatarTitulo, idComoTexto } from '@/compartilhado/formatacao';
import { Botao } from '@/compartilhado/ui/Botao';
import { CampoMoeda } from '@/compartilhado/ui/CampoMoeda';
import { EstadoConsulta } from '@/compartilhado/ui/EstadoConsulta';

interface RascunhoCarteira {
  limiteCheque: number | null;
  tipoCarteira: TipoCarteira;
}

const TIPOS_CARTEIRA: { valor: TipoCarteira; rotulo: string }[] = [
  { valor: 'pessoal', rotulo: 'Pessoal' },
  { valor: 'empresarial', rotulo: 'Empresarial' },
  { valor: 'conjunto', rotulo: 'Conjunto' },
];

function rascunhoDe(c: Carteira): RascunhoCarteira {
  return {
    limiteCheque:
      c.limite_cheque !== undefined && c.limite_cheque !== null
        ? Number(c.limite_cheque)
        : null,
    tipoCarteira: c.tipo_carteira ?? 'pessoal',
  };
}

function saldoCarteiraExibido(c: Carteira): number | null {
  if (c.saldo_atual !== undefined && c.saldo_atual !== null) {
    const n = Number(c.saldo_atual);
    return Number.isFinite(n) ? n : null;
  }
  if (c.saldo_inicial !== undefined && c.saldo_inicial !== null) {
    const n = Number(c.saldo_inicial);
    return Number.isFinite(n) ? n : null;
  }
  return null;
}

export function PaginaConfiguracoes() {
  const { usuario, atualizarNome } = useAuth();
  const { carteiras, definirPadrao } = useCarteira();
  const qc = useQueryClient();

  const [nomeUsuario, setNomeUsuario] = useState(usuario?.nome ?? '');
  const [editandoPerfil, setEditandoPerfil] = useState(false);
  const [msgPerfil, setMsgPerfil] = useState<string | null>(null);
  const [erroPerfil, setErroPerfil] = useState<string | null>(null);

  const [rascunhos, setRascunhos] = useState<Record<string, RascunhoCarteira>>({});
  const [editandoCarteiraId, setEditandoCarteiraId] = useState<string | null>(null);
  const [novaCategoria, setNovaCategoria] = useState('');
  const [erroSalvarId, setErroSalvarId] = useState<string | null>(null);
  const [msgSalvar, setMsgSalvar] = useState<string | null>(null);

  useEffect(() => {
    if (!editandoPerfil) {
      setNomeUsuario(usuario?.nome ?? '');
    }
  }, [usuario?.nome, editandoPerfil]);

  useEffect(() => {
    setRascunhos((atual) => {
      const proximo: Record<string, RascunhoCarteira> = {};
      for (const c of carteiras) {
        const id = idComoTexto(c.id);
        if (editandoCarteiraId === id && atual[id]) {
          proximo[id] = atual[id];
        } else {
          proximo[id] = rascunhoDe(c);
        }
      }
      return proximo;
    });
  }, [carteiras, editandoCarteiraId]);

  const categorias = useQuery({
    queryKey: chavesConsulta.categorias.todas,
    queryFn: api.categorias.listar,
  });

  const categoriasOrdenadas = useMemo(() => {
    const lista = categorias.data ?? [];
    const padrao = lista
      .filter((c) => c.origem !== 'pessoal')
      .sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));
    const pessoal = lista
      .filter((c) => c.origem === 'pessoal')
      .sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));
    return [...padrao, ...pessoal];
  }, [categorias.data]);

  const salvarPerfil = useMutation({
    mutationFn: () => atualizarNome(formatarTitulo(nomeUsuario)),
    onSuccess: () => {
      setErroPerfil(null);
      setMsgPerfil('Dados salvos.');
      setEditandoPerfil(false);
    },
    onError: (err) => {
      setMsgPerfil(null);
      setErroPerfil(err instanceof Error ? err.message : 'Falha ao salvar');
    },
  });

  const salvarConfig = useMutation({
    mutationFn: (id: string) => {
      const r = rascunhos[id];
      if (!r) throw new Error('Carteira não encontrada');
      return api.carteiras.atualizarConfig(id, {
        limite_cheque: r.limiteCheque ?? undefined,
        tipo_carteira: r.tipoCarteira,
      });
    },
    onSuccess: async (_data, id) => {
      setErroSalvarId(null);
      setMsgSalvar(id);
      setEditandoCarteiraId(null);
      await qc.invalidateQueries({ queryKey: chavesConsulta.carteiras.todas });
    },
    onError: (_err, id) => {
      setErroSalvarId(id);
      setMsgSalvar(null);
    },
  });

  const tornarPadrao = useMutation({
    mutationFn: (id: string) => definirPadrao(id),
  });

  const criarCategoria = useMutation({
    mutationFn: () =>
      api.categorias.criar({
        nome: formatarTitulo(novaCategoria),
      }),
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

  const atualizarRascunho = (id: string, patch: Partial<RascunhoCarteira>) => {
    setRascunhos((atual) => ({
      ...atual,
      [id]: { ...atual[id], ...patch },
    }));
    setMsgSalvar(null);
  };

  const cancelarPerfil = () => {
    setNomeUsuario(usuario?.nome ?? '');
    setEditandoPerfil(false);
    setErroPerfil(null);
    setMsgPerfil(null);
  };

  const iniciarEdicaoCarteira = (id: string, carteira: Carteira) => {
    setRascunhos((atual) => ({ ...atual, [id]: rascunhoDe(carteira) }));
    setEditandoCarteiraId(id);
    setErroSalvarId(null);
    setMsgSalvar(null);
  };

  const cancelarCarteira = (id: string, carteira: Carteira) => {
    setRascunhos((atual) => ({ ...atual, [id]: rascunhoDe(carteira) }));
    setEditandoCarteiraId(null);
    setErroSalvarId(null);
    setMsgSalvar(null);
  };

  if (carteiras.length === 0) {
    return (
      <EstadoConsulta vazio mensagemVazio="Nenhuma carteira disponível para configurar." />
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-800">Configurações</h2>
        <p className="text-sm text-slate-500">Carteiras, seus dados e categorias</p>
      </div>

      <section className="fin-panel space-y-4 p-5">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h3 className="font-semibold text-slate-800">Seus dados</h3>
          {!editandoPerfil ? (
            <Botao
              variante="secundario"
              className="px-3 py-1.5 text-xs"
              onClick={() => {
                setEditandoPerfil(true);
                setMsgPerfil(null);
                setErroPerfil(null);
              }}
            >
              Editar
            </Botao>
          ) : null}
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="fin-label" htmlFor="nome-usuario">
              Nome
            </label>
            <input
              id="nome-usuario"
              className={cn('fin-input', !editandoPerfil && 'bg-slate-50 text-slate-600')}
              value={nomeUsuario}
              disabled={!editandoPerfil}
              onChange={(e) => {
                setNomeUsuario(e.target.value);
                setMsgPerfil(null);
              }}
            />
          </div>
          <div>
            <label className="fin-label" htmlFor="email-usuario">
              E-mail
            </label>
            <input
              id="email-usuario"
              className="fin-input bg-slate-50 text-slate-500"
              value={usuario?.email ?? ''}
              readOnly
            />
          </div>
        </div>
        {editandoPerfil ? (
          <div className="flex flex-wrap gap-2">
            <Botao
              carregando={salvarPerfil.isPending}
              disabled={!nomeUsuario.trim()}
              onClick={() => salvarPerfil.mutate()}
            >
              Salvar
            </Botao>
            <Botao
              variante="secundario"
              disabled={salvarPerfil.isPending}
              onClick={cancelarPerfil}
            >
              Cancelar
            </Botao>
          </div>
        ) : null}
        {erroPerfil ? <p className="text-sm text-rose-600">{erroPerfil}</p> : null}
        {msgPerfil ? <p className="text-sm text-fin-teal-700">{msgPerfil}</p> : null}
      </section>

      <div className="space-y-4">
        <h3 className="font-semibold text-slate-800">Carteiras</h3>
        {carteiras.map((c) => {
          const id = idComoTexto(c.id);
          const r = rascunhos[id] ?? rascunhoDe(c);
          const editando = editandoCarteiraId === id;
          const salvandoEsta =
            salvarConfig.isPending && salvarConfig.variables === id;
          const rotuloTipo =
            TIPOS_CARTEIRA.find((t) => t.valor === r.tipoCarteira)?.rotulo ?? 'Pessoal';
          const saldo = saldoCarteiraExibido(c);
          return (
            <section key={id} className="fin-panel space-y-4 p-5">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h4 className="font-semibold text-slate-800">
                  {c.nome}
                  {c.padrao ? (
                    <span className="ml-2 text-xs font-medium text-fin-teal-700">
                      (padrão)
                    </span>
                  ) : null}
                  <span className="ml-2 text-xs font-medium text-slate-500">
                    · {rotuloTipo}
                  </span>
                </h4>
                <div className="flex flex-wrap gap-2">
                  {!c.padrao ? (
                    <Botao
                      variante="secundario"
                      className="px-3 py-1.5 text-xs"
                      carregando={tornarPadrao.isPending && tornarPadrao.variables === id}
                      onClick={() => tornarPadrao.mutate(id)}
                    >
                      Definir como padrão
                    </Botao>
                  ) : null}
                  {!editando ? (
                    <Botao
                      variante="secundario"
                      className="px-3 py-1.5 text-xs"
                      onClick={() => iniciarEdicaoCarteira(id, c)}
                    >
                      Editar
                    </Botao>
                  ) : null}
                </div>
              </div>
              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <label className="fin-label" htmlFor={`saldo-${id}`}>
                    Saldo
                  </label>
                  <input
                    id={`saldo-${id}`}
                    className="fin-input bg-slate-50 text-slate-600 tabular-nums"
                    value={saldo !== null ? formatarMoeda(saldo) : '—'}
                    readOnly
                    disabled
                  />
                </div>
                <CampoMoeda
                  id={`limite-${id}`}
                  label="Limite cheque especial"
                  valor={r.limiteCheque}
                  disabled={!editando}
                  onChange={(v) => atualizarRascunho(id, { limiteCheque: v })}
                />
                <div>
                  <label className="fin-label" htmlFor={`tipo-${id}`}>
                    Tipo
                  </label>
                  <select
                    id={`tipo-${id}`}
                    className={cn('fin-input', !editando && 'bg-slate-50 text-slate-600')}
                    value={r.tipoCarteira}
                    disabled={!editando}
                    onChange={(e) =>
                      atualizarRascunho(id, {
                        tipoCarteira: e.target.value as TipoCarteira,
                      })
                    }
                  >
                    {TIPOS_CARTEIRA.map((t) => (
                      <option key={t.valor} value={t.valor}>
                        {t.rotulo}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              {editando ? (
                <div className="flex flex-wrap gap-2">
                  <Botao carregando={salvandoEsta} onClick={() => salvarConfig.mutate(id)}>
                    Salvar
                  </Botao>
                  <Botao
                    variante="secundario"
                    disabled={salvandoEsta}
                    onClick={() => cancelarCarteira(id, c)}
                  >
                    Cancelar
                  </Botao>
                </div>
              ) : null}
              {erroSalvarId === id && salvarConfig.error instanceof Error ? (
                <p className="text-sm text-rose-600">{salvarConfig.error.message}</p>
              ) : null}
              {msgSalvar === id ? (
                <p className="text-sm text-fin-teal-700">Parâmetros salvos.</p>
              ) : null}
            </section>
          );
        })}

        <div>
          <Link
            to="/carteiras/nova"
            className="inline-flex items-center gap-2 rounded-xl border border-dashed border-fin-teal-400 bg-fin-teal-50/50 px-4 py-3 text-sm font-semibold text-fin-teal-800 hover:bg-fin-teal-50"
          >
            <span className="material-symbols-outlined text-base">add</span>
            Nova carteira
          </Link>
        </div>
      </div>

      <section className="fin-panel space-y-4 p-5">
        <h3 className="font-semibold text-slate-800">Categorias</h3>
        <p className="text-sm text-slate-500">
          Valem para todas as transações. Padrão do sistema não pode ser removido.
        </p>
        <div className="flex flex-wrap gap-2">
          <input
            className="fin-input min-w-[200px] flex-1"
            placeholder="Nome da categoria"
            value={novaCategoria}
            onChange={(e) => setNovaCategoria(e.target.value)}
          />
          <Botao
            disabled={!novaCategoria.trim()}
            carregando={criarCategoria.isPending}
            onClick={() => criarCategoria.mutate()}
          >
            Adicionar
          </Botao>
        </div>
        {criarCategoria.error instanceof Error ? (
          <p className="text-sm text-rose-600">{criarCategoria.error.message}</p>
        ) : null}
        <div className="max-h-64 overflow-y-auto rounded-xl border border-slate-200">
          <ul className="divide-y divide-slate-100">
            {categoriasOrdenadas.map((c) => {
              const pessoal = c.origem === 'pessoal';
              return (
                <li
                  key={c.id}
                  className="flex items-center justify-between gap-3 px-4 py-2 text-sm"
                >
                  <span className="min-w-0 truncate font-medium text-slate-800">
                    {formatarTitulo(c.nome)}
                  </span>
                  <div className="flex shrink-0 items-center gap-3">
                    <span
                      className={cn(
                        'rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide',
                        pessoal
                          ? 'bg-slate-100 text-slate-600'
                          : 'bg-fin-teal-50 text-fin-teal-800',
                      )}
                    >
                      {pessoal ? 'Pessoal' : 'Padrão'}
                    </span>
                    {pessoal ? (
                      <button
                        type="button"
                        className="text-rose-600 hover:underline"
                        onClick={() => excluirCategoria.mutate(idComoTexto(c.id))}
                      >
                        Remover
                      </button>
                    ) : null}
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      </section>
    </div>
  );
}
