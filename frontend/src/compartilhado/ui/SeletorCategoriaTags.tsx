import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '@/compartilhado/api/servicos';
import { chavesConsulta } from '@/compartilhado/api/chavesConsulta';
import type { IdRecurso, TipoLancamento } from '@/compartilhado/api/tipos';
import { cn, idComoTexto } from '@/compartilhado/formatacao';
import { useState } from 'react';

interface SeletorCategoriaTagsProps {
  tipo: TipoLancamento;
  categoriaId: IdRecurso | null;
  onCategoriaChange: (id: IdRecurso | null) => void;
  tagIds: IdRecurso[];
  onTagsChange: (ids: IdRecurso[]) => void;
}

export function SeletorCategoriaTags({
  tipo,
  categoriaId,
  onCategoriaChange,
  tagIds,
  onTagsChange,
}: SeletorCategoriaTagsProps) {
  const qc = useQueryClient();
  const [novaTag, setNovaTag] = useState('');

  const categorias = useQuery({
    queryKey: chavesConsulta.categorias.todas,
    queryFn: api.categorias.listar,
  });

  const tags = useQuery({
    queryKey: chavesConsulta.tags.todas,
    queryFn: api.tags.listar,
  });

  const criarTag = useMutation({
    mutationFn: (nome: string) => api.tags.criar(nome),
    onSuccess: (tag) => {
      void qc.invalidateQueries({ queryKey: chavesConsulta.tags.todas });
      onTagsChange([...tagIds, tag.id]);
      setNovaTag('');
    },
  });

  const categoriasFiltradas =
    categorias.data?.filter((c) => c.tipo === tipo || c.tipo === 'ambos') ?? [];

  const alternarTag = (id: IdRecurso) => {
    if (tagIds.includes(id)) {
      onTagsChange(tagIds.filter((t) => t !== id));
    } else {
      onTagsChange([...tagIds, id]);
    }
  };

  const adicionarTag = () => {
    const nome = novaTag.trim();
    if (!nome) return;
    const existente = tags.data?.find((t) => t.nome.toLowerCase() === nome.toLowerCase());
    if (existente) {
      if (!tagIds.includes(existente.id)) onTagsChange([...tagIds, existente.id]);
      setNovaTag('');
      return;
    }
    criarTag.mutate(nome);
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="fin-label" htmlFor="categoria">
          Categoria
        </label>
        <select
          id="categoria"
          className="fin-input"
          value={categoriaId != null ? idComoTexto(categoriaId) : ''}
          onChange={(e) => onCategoriaChange(e.target.value || null)}
        >
          <option value="">Sem categoria</option>
          {categoriasFiltradas.map((c) => (
            <option key={c.id} value={idComoTexto(c.id)}>
              {c.nome}
            </option>
          ))}
        </select>
      </div>

      <div>
        <span className="fin-label">Tags</span>
        <div className="flex flex-wrap gap-2">
          {(tags.data ?? []).map((tag) => {
            const ativa = tagIds.includes(tag.id);
            return (
              <button
                key={tag.id}
                type="button"
                onClick={() => alternarTag(tag.id)}
                className={cn(
                  'rounded-full px-3 py-1 text-xs font-semibold transition',
                  ativa
                    ? 'bg-fin-teal-600 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200',
                )}
              >
                {tag.nome}
              </button>
            );
          })}
        </div>
        <div className="mt-2 flex gap-2">
          <input
            className="fin-input flex-1"
            placeholder="Nova tag..."
            value={novaTag}
            onChange={(e) => setNovaTag(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                adicionarTag();
              }
            }}
          />
          <button
            type="button"
            className="rounded-xl border border-slate-200 px-3 text-sm font-semibold text-fin-teal-700 hover:bg-fin-teal-50"
            onClick={adicionarTag}
          >
            Adicionar
          </button>
        </div>
      </div>
    </div>
  );
}
