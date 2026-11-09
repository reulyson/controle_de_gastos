import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '@/compartilhado/contexto/ContextoAuth';
import { useCarteira } from '@/compartilhado/contexto/ContextoCarteira';

export function GuardaAutenticacao() {
  const { autenticado, carregando } = useAuth();
  const local = useLocation();

  if (carregando) {
    return (
      <div className="flex min-h-screen items-center justify-center text-slate-500">
        Carregando...
      </div>
    );
  }

  if (!autenticado) {
    return <Navigate to="/login" replace state={{ from: local }} />;
  }

  return <Outlet />;
}

export function GuardaCarteira() {
  const { semCarteira, precisaEscolherPadrao, carregando } = useCarteira();
  const local = useLocation();

  if (carregando) {
    return (
      <div className="flex min-h-screen items-center justify-center text-slate-500">
        Carregando carteira...
      </div>
    );
  }

  if (semCarteira && local.pathname !== '/carteiras/nova') {
    return <Navigate to="/carteiras/nova" replace />;
  }

  if (precisaEscolherPadrao && local.pathname !== '/carteiras/padrao') {
    return <Navigate to="/carteiras/padrao" replace />;
  }

  return <Outlet />;
}
