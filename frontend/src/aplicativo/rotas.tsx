import { CascoAplicacao } from '@/layout/CascoAplicacao';
import { PaginaControle } from '@/funcionalidades/controle/PaginaControle';
import { PaginaLancamentos } from '@/funcionalidades/lancamentos/PaginaLancamentos';
import { PaginaCartoes } from '@/funcionalidades/cartoes/PaginaCartoes';
import { PaginaRelatorios } from '@/funcionalidades/relatorios/PaginaRelatorios';
import { PaginaConfiguracoes } from '@/funcionalidades/configuracoes/PaginaConfiguracoes';
import { createBrowserRouter, Navigate } from 'react-router-dom';

export const rotas = createBrowserRouter([
  {
    path: '/',
    element: <CascoAplicacao />,
    children: [
      { index: true, element: <PaginaControle /> },
      { path: 'receitas', element: <PaginaLancamentos tipo="receita" /> },
      { path: 'despesas', element: <PaginaLancamentos tipo="despesa" /> },
      { path: 'cartoes', element: <PaginaCartoes /> },
      { path: 'relatorios', element: <PaginaRelatorios /> },
      { path: 'configuracoes', element: <PaginaConfiguracoes /> },
      { path: '*', element: <Navigate to="/" replace /> },
    ],
  },
]);
