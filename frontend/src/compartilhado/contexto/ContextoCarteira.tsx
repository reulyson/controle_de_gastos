import { createContext, useContext, useMemo, type ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/compartilhado/api/servicos';
import { chavesConsulta } from '@/compartilhado/api/chavesConsulta';
import type { Carteira } from '@/compartilhado/api/tipos';
import { ANOS_DISPONIVEIS } from '@/tema/tokens';

interface ContextoCarteiraValor {
  carteiras: Carteira[];
  carteiraAtiva: Carteira | null;
  carteiraId: string | null;
  carregando: boolean;
  erro: Error | null;
  anoPadrao: number;
}

const ContextoCarteira = createContext<ContextoCarteiraValor | null>(null);

export function ProvedorCarteira({ children }: { children: ReactNode }) {
  const consulta = useQuery({
    queryKey: chavesConsulta.carteiras.todas,
    queryFn: api.carteiras.listar,
  });

  const carteiraAtiva = consulta.data?.[0] ?? null;

  const valor = useMemo<ContextoCarteiraValor>(
    () => ({
      carteiras: consulta.data ?? [],
      carteiraAtiva,
      carteiraId:
        carteiraAtiva?.id !== undefined && carteiraAtiva?.id !== null
          ? String(carteiraAtiva.id)
          : null,
      carregando: consulta.isLoading,
      erro: consulta.error instanceof Error ? consulta.error : null,
      anoPadrao:
        carteiraAtiva?.ano_padrao ?? ANOS_DISPONIVEIS[0],
    }),
    [carteiraAtiva, consulta.data, consulta.error, consulta.isLoading],
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
