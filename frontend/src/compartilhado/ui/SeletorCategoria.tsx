import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useMemo, useRef, useState } from 'react';
import { api } from '@/compartilhado/api/servicos';
import { chavesConsulta } from '@/compartilhado/api/chavesConsulta';
import type { IdRecurso, TipoCategoria } from '@/compartilhado/api/tipos';
import { cn, idComoTexto } from '@/compartilhado/formatacao';

interface SeletorCategoriaProps {
  tipo: TipoCategoria;
  categoriaId: IdRecurso | null;
  onCategoriaChange: (id: IdRecurso | null) => void;
  id?: string;
}

/**
 * Combobox creatable: após escolher/criar, exibe chip (estilo tag).
 */
export function SeletorCategoria({
  tipo,
  categoriaId,
  onCategoriaChange,
  id = 'categoria',
}: SeletorCategoriaProps) {
  const qc = useQueryClient();
  const [aberto, setAberto] = useState(false);
  const [busca, setBusca] = useState('');
  const [editando, setEditando] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const categorias = useQuery({
    queryKey: chavesConsulta.categorias.todas,
    queryFn: api.categorias.listar,
  });

  const selecionada = categorias.data?.find(
    (c) => idComoTexto(c.id) === (categoriaId != null ? idComoTexto(categoriaId) : ''),
  );

  const filtradas = useMemo(() => {
    const lista = categorias.data ?? [];
    const q = busca.trim().toLowerCase();
    const porTipo = lista.filter(
      (c) => c.tipo === tipo || c.tipo === 'ambos' || tipo === 'ambos',
    );
    const base = q
      ? lista.filter((c) => c.nome.toLowerCase().includes(q))
      : porTipo;
    // Preferência: primeiro as do tipo atual, depois demais com o mesmo nome digitado
    return [...base].sort((a, b) => {
      const aOk = a.tipo === tipo || a.tipo === 'ambos' ? 0 : 1;
      const bOk = b.tipo === tipo || b.tipo === 'ambos' ? 0 : 1;
      return aOk - bOk || a.nome.localeCompare(b.nome, 'pt-BR');
    });
  }, [busca, categorias.data, tipo]);

  const nomeBusca = busca.trim();
  const existenteExata = categorias.data?.find(
    (c) => c.nome.toLowerCase() === nomeBusca.toLowerCase(),
  );
  const podeCriar = nomeBusca.length > 0 && !existenteExata;

  const criar = useMutation({
    mutationFn: (nome: string) =>
      api.categorias.criar({
        nome,
      }),
    onSuccess: async (cat) => {
      await qc.invalidateQueries({ queryKey: chavesConsulta.categorias.todas });
      onCategoriaChange(cat.id);
      setBusca('');
      setAberto(false);
      setEditando(false);
    },
  });

  const confirmar = () => {
    if (!nomeBusca) return;
    if (existenteExata) {
      onCategoriaChange(existenteExata.id);
      setBusca('');
      setAberto(false);
      setEditando(false);
      return;
    }
    if (podeCriar && !criar.isPending) {
      criar.mutate(nomeBusca);
    }
  };

  const limpar = () => {
    onCategoriaChange(null);
    setBusca('');
    setEditando(true);
    setAberto(true);
    window.setTimeout(() => inputRef.current?.focus(), 0);
  };

  const mostrarChip = categoriaId != null && selecionada && !editando;

  return (
    <div className="relative">
      <span className="fin-label">Categoria</span>

      {mostrarChip ? (
        <div className="mt-1 flex flex-wrap items-center gap-2">
          <span className="inline-flex items-center gap-1 rounded-full bg-fin-teal-600 px-3 py-1.5 text-xs font-semibold text-white">
            {selecionada.nome}
            <button
              type="button"
              className="ml-0.5 rounded-full p-0.5 hover:bg-fin-teal-700"
              aria-label={`Remover categoria ${selecionada.nome}`}
              onClick={limpar}
            >
              <span className="material-symbols-outlined text-sm leading-none">close</span>
            </button>
          </span>
          <button
            type="button"
            className="text-xs font-semibold text-fin-teal-700 hover:underline"
            onClick={limpar}
          >
            Trocar
          </button>
        </div>
      ) : (
        <>
          <input
            ref={inputRef}
            id={id}
            className="fin-input mt-1"
            placeholder="Escolher ou digitar nova..."
            value={busca}
            autoComplete="off"
            onFocus={() => setAberto(true)}
            onChange={(e) => {
              setBusca(e.target.value);
              setAberto(true);
              setEditando(true);
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                e.stopPropagation();
                confirmar();
              }
              if (e.key === 'Escape') {
                setAberto(false);
                if (categoriaId) setEditando(false);
              }
            }}
            onBlur={() => {
              window.setTimeout(() => setAberto(false), 180);
            }}
          />

          {aberto ? (
            <ul className="absolute z-20 mt-1 max-h-48 w-full overflow-auto rounded-xl border border-slate-200 bg-white py-1 shadow-panel">
              <li>
                <button
                  type="button"
                  className="w-full px-3 py-2 text-left text-sm text-slate-500 hover:bg-slate-50"
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => {
                    onCategoriaChange(null);
                    setBusca('');
                    setAberto(false);
                    setEditando(true);
                  }}
                >
                  Sem categoria
                </button>
              </li>
              {filtradas.map((c) => (
                <li key={idComoTexto(c.id)}>
                  <button
                    type="button"
                    className={cn(
                      'w-full px-3 py-2 text-left text-sm hover:bg-fin-teal-50',
                      categoriaId != null &&
                        idComoTexto(categoriaId) === idComoTexto(c.id) &&
                        'bg-fin-teal-50 font-semibold text-fin-teal-800',
                    )}
                    onMouseDown={(e) => e.preventDefault()}
                    onClick={() => {
                      onCategoriaChange(c.id);
                      setBusca('');
                      setAberto(false);
                      setEditando(false);
                    }}
                  >
                    {c.nome}
                    {c.tipo !== tipo && c.tipo !== 'ambos' ? (
                      <span className="ml-2 text-xs text-slate-400">({c.tipo})</span>
                    ) : null}
                  </button>
                </li>
              ))}
              {podeCriar ? (
                <li>
                  <button
                    type="button"
                    className="w-full px-3 py-2 text-left text-sm font-semibold text-fin-teal-700 hover:bg-fin-teal-50"
                    disabled={criar.isPending}
                    onMouseDown={(e) => e.preventDefault()}
                    onClick={() => criar.mutate(nomeBusca)}
                  >
                    + Criar &quot;{nomeBusca}&quot; (Enter)
                  </button>
                </li>
              ) : null}
              {existenteExata && filtradas.every((c) => c.id !== existenteExata.id) ? (
                <li>
                  <button
                    type="button"
                    className="w-full px-3 py-2 text-left text-sm font-semibold text-fin-teal-700 hover:bg-fin-teal-50"
                    onMouseDown={(e) => e.preventDefault()}
                    onClick={() => {
                      onCategoriaChange(existenteExata.id);
                      setBusca('');
                      setAberto(false);
                      setEditando(false);
                    }}
                  >
                    Usar &quot;{existenteExata.nome}&quot;
                  </button>
                </li>
              ) : null}
              {filtradas.length === 0 && !podeCriar && !existenteExata ? (
                <li className="px-3 py-2 text-sm text-slate-400">Nenhuma categoria</li>
              ) : null}
            </ul>
          ) : null}
        </>
      )}

      {criar.error instanceof Error ? (
        <p className="mt-1 text-xs text-rose-600">{criar.error.message}</p>
      ) : null}
    </div>
  );
}
