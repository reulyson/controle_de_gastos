import { useCallback, useState } from 'react';
import {
  BarraLateral,
  gravarLateralRecolhida,
  lerLateralRecolhida,
} from '@/layout/BarraLateral';
import { CabecalhoTopo } from '@/layout/CabecalhoTopo';
import { cn } from '@/compartilhado/formatacao';
import { Outlet } from 'react-router-dom';

export function CascoAplicacao() {
  const [recolhida, setRecolhida] = useState(lerLateralRecolhida);

  const alternar = useCallback(() => {
    setRecolhida((atual) => {
      const proximo = !atual;
      gravarLateralRecolhida(proximo);
      return proximo;
    });
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-slate-50 to-teal-50/30">
      <BarraLateral recolhida={recolhida} onAlternar={alternar} />
      <div
        className={cn(
          'flex min-w-0 flex-col transition-[padding] duration-200',
          recolhida ? 'lg:pl-14' : 'lg:pl-48',
        )}
      >
        <CabecalhoTopo />
        <main className="flex-1 p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
