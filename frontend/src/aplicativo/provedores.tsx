import { ProvedorCarteira } from '@/compartilhado/contexto/ContextoCarteira';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import { useState } from 'react';

export function Provedores({ children }: { children: ReactNode }) {
  const [cliente] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      }),
  );

  return (
    <QueryClientProvider client={cliente}>
      <ProvedorCarteira>{children}</ProvedorCarteira>
    </QueryClientProvider>
  );
}
