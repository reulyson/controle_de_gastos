import { Provedores } from '@/aplicativo/provedores';
import { rotas } from '@/aplicativo/rotas';
import '@/estilos/global.css';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';

const root = document.getElementById('root');
if (!root) {
  throw new Error('Elemento #root não encontrado');
}

createRoot(root).render(
  <StrictMode>
    <Provedores>
      <RouterProvider router={rotas} />
    </Provedores>
  </StrictMode>,
);
