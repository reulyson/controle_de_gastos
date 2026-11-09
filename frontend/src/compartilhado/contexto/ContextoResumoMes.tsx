import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react';

interface SnapshotResumoMes {
  saldoCarteira: number | null;
  chequeLivre: number | null;
}

interface ContextoResumoMesValor extends SnapshotResumoMes {
  definirResumoMes: (snap: SnapshotResumoMes) => void;
  limparResumoMes: () => void;
}

const ContextoResumoMes = createContext<ContextoResumoMesValor | null>(null);

const vazio: SnapshotResumoMes = { saldoCarteira: null, chequeLivre: null };

export function ProvedorResumoMes({ children }: { children: ReactNode }) {
  const [snap, setSnap] = useState<SnapshotResumoMes>(vazio);

  const definirResumoMes = useCallback((proximo: SnapshotResumoMes) => {
    setSnap(proximo);
  }, []);

  const limparResumoMes = useCallback(() => {
    setSnap(vazio);
  }, []);

  const valor = useMemo<ContextoResumoMesValor>(
    () => ({
      ...snap,
      definirResumoMes,
      limparResumoMes,
    }),
    [definirResumoMes, limparResumoMes, snap],
  );

  return (
    <ContextoResumoMes.Provider value={valor}>{children}</ContextoResumoMes.Provider>
  );
}

export function useResumoMes(): ContextoResumoMesValor {
  const ctx = useContext(ContextoResumoMes);
  if (!ctx) {
    throw new Error('useResumoMes deve ser usado dentro de ProvedorResumoMes');
  }
  return ctx;
}
