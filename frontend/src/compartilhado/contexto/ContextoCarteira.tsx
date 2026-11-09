import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '@/compartilhado/api/servicos';
import { chavesConsulta } from '@/compartilhado/api/chavesConsulta';
import type { Carteira } from '@/compartilhado/api/tipos';
import { useAuth } from '@/compartilhado/contexto/ContextoAuth';
import { anosNavegaveis, idComoTexto } from '@/compartilhado/formatacao';

interface ContextoCarteiraValor {
  carteiras: Carteira[];
  carteiraAtiva: Carteira | null;
  carteiraId: string | null;
  carregando: boolean;
  erro: Error | null;
  anoPadrao: number;
  anoSelecionado: number;
  anosDisponiveis: number[];
  podeAnoAnterior: boolean;
  podeAnoProximo: boolean;
  precisaEscolherPadrao: boolean;
  semCarteira: boolean;
  definirPadrao: (id: string) => Promise<void>;
  definirAno: (ano: number) => void;
  anoAnterior: () => void;
  anoProximo: () => void;
}

const ContextoCarteira = createContext<ContextoCarteiraValor | null>(null);

function anoCivilAtual(): number {
  return new Date().getFullYear();
}

function escolherAnoInicial(
  carteira: Carteira | null | undefined,
  anos: number[],
): number {
  const atual = anoCivilAtual();
  const preferido = carteira?.ano_padrao;
  if (preferido != null && anos.includes(preferido)) {
    return preferido;
  }
  if (anos.includes(atual)) {
    return atual;
  }
  return anos[anos.length - 1] ?? atual;
}

export function ProvedorCarteira({ children }: { children: ReactNode }) {
  const { autenticado } = useAuth();
  const qc = useQueryClient();
  const anoAtual = anoCivilAtual();
  const [anoSelecionado, setAnoSelecionado] = useState<number>(anoAtual);
  const [anoAlinhadoCarteiraId, setAnoAlinhadoCarteiraId] = useState<string | null>(null);

  const consulta = useQuery({
    queryKey: chavesConsulta.carteiras.todas,
    queryFn: api.carteiras.listar,
    enabled: autenticado,
  });

  const carteiras = consulta.data ?? [];
  const padrao = carteiras.find((c) => c.padrao);
  const precisaEscolherPadrao = carteiras.length > 1 && !padrao;
  const carteiraAtiva =
    padrao ?? (carteiras.length === 1 ? carteiras[0] : null);
  const carteiraId =
    carteiraAtiva?.id !== undefined && carteiraAtiva?.id !== null
      ? idComoTexto(carteiraAtiva.id)
      : null;

  const consultaAnos = useQuery({
    queryKey: carteiraId ? chavesConsulta.carteiras.anos(carteiraId) : ['carteiras-anos-vazio'],
    queryFn: async () => {
      const resp = await api.carteiras.listarAnos(carteiraId!);
      return resp.anos;
    },
    enabled: autenticado && Boolean(carteiraId),
  });

  const anosDisponiveis = useMemo(
    () => anosNavegaveis(consultaAnos.data ?? [], anoAtual),
    [anoAtual, consultaAnos.data],
  );

  useEffect(() => {
    if (!carteiraId) return;
    if (anoAlinhadoCarteiraId === carteiraId) return;
    if (consultaAnos.isLoading) return;
    setAnoSelecionado(escolherAnoInicial(carteiraAtiva, anosDisponiveis));
    setAnoAlinhadoCarteiraId(carteiraId);
  }, [
    anoAlinhadoCarteiraId,
    anosDisponiveis,
    carteiraAtiva,
    carteiraId,
    consultaAnos.isLoading,
  ]);

  useEffect(() => {
    if (!anosDisponiveis.length) return;
    if (!anosDisponiveis.includes(anoSelecionado)) {
      setAnoSelecionado(
        anosDisponiveis.includes(anoAtual)
          ? anoAtual
          : anosDisponiveis[anosDisponiveis.length - 1],
      );
    }
  }, [anoAtual, anoSelecionado, anosDisponiveis]);

  const mutPadrao = useMutation({
    mutationFn: (id: string) => api.carteiras.definirPadrao(id),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: chavesConsulta.carteiras.todas });
    },
  });

  const indiceAno = anosDisponiveis.indexOf(anoSelecionado);
  const podeAnoAnterior = indiceAno > 0;
  const podeAnoProximo = indiceAno >= 0 && indiceAno < anosDisponiveis.length - 1;

  const definirAno = useCallback(
    (ano: number) => {
      if (anosDisponiveis.includes(ano)) {
        setAnoSelecionado(ano);
      }
    },
    [anosDisponiveis],
  );

  const anoAnterior = useCallback(() => {
    if (indiceAno > 0) setAnoSelecionado(anosDisponiveis[indiceAno - 1]);
  }, [anosDisponiveis, indiceAno]);

  const anoProximo = useCallback(() => {
    if (indiceAno >= 0 && indiceAno < anosDisponiveis.length - 1) {
      setAnoSelecionado(anosDisponiveis[indiceAno + 1]);
    }
  }, [anosDisponiveis, indiceAno]);

  const valor = useMemo<ContextoCarteiraValor>(
    () => ({
      carteiras,
      carteiraAtiva,
      carteiraId,
      carregando: autenticado ? consulta.isLoading : false,
      erro: consulta.error instanceof Error ? consulta.error : null,
      anoPadrao: carteiraAtiva?.ano_padrao ?? anoAtual,
      anoSelecionado,
      anosDisponiveis,
      podeAnoAnterior,
      podeAnoProximo,
      precisaEscolherPadrao,
      semCarteira: autenticado && !consulta.isLoading && carteiras.length === 0,
      definirPadrao: async (id: string) => {
        await mutPadrao.mutateAsync(id);
      },
      definirAno,
      anoAnterior,
      anoProximo,
    }),
    [
      anoAnterior,
      anoAtual,
      anoProximo,
      anoSelecionado,
      anosDisponiveis,
      autenticado,
      carteiraAtiva,
      carteiraId,
      carteiras,
      consulta.error,
      consulta.isLoading,
      definirAno,
      mutPadrao,
      podeAnoAnterior,
      podeAnoProximo,
      precisaEscolherPadrao,
    ],
  );

  return <ContextoCarteira.Provider value={valor}>{children}</ContextoCarteira.Provider>;
}

export function useCarteira(): ContextoCarteiraValor {
  const ctx = useContext(ContextoCarteira);
  if (!ctx) {
    throw new Error('useCarteira deve ser usado dentro de ProvedorCarteira');
  }
  return ctx;
}
