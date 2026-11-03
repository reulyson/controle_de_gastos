import { BarraLateral } from '@/layout/BarraLateral';
import { CabecalhoTopo } from '@/layout/CabecalhoTopo';
import { Outlet } from 'react-router-dom';

export function CascoAplicacao() {
  return (
    <div className="flex min-h-screen bg-gradient-to-br from-slate-100 via-slate-50 to-teal-50/30">
      <BarraLateral />
      <div className="flex min-w-0 flex-1 flex-col">
        <CabecalhoTopo />
        <main className="flex-1 p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
