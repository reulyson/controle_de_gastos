import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { api } from '@/compartilhado/api/servicos';
import {
  aoExpirarSessao,
  definirAccessToken,
  obterAccessToken,
} from '@/compartilhado/api/cliente';
import type { UsuarioAuth } from '@/compartilhado/api/tipos';

/** Access JWT = 15 min no backend; renovar um pouco antes. */
const INTERVALO_REFRESH_MS = 12 * 60 * 1000;

interface ContextoAuthValor {
  usuario: UsuarioAuth | null;
  autenticado: boolean;
  carregando: boolean;
  login: (email: string, senha: string) => Promise<void>;
  cadastrar: (nome: string, email: string, senha: string) => Promise<void>;
  logout: () => Promise<void>;
  atualizarUsuario: () => Promise<void>;
  atualizarNome: (nome: string) => Promise<void>;
}

const ContextoAuth = createContext<ContextoAuthValor | null>(null);

export function ProvedorAuth({ children }: { children: ReactNode }) {
  const qc = useQueryClient();
  const [usuario, setUsuario] = useState<UsuarioAuth | null>(null);
  const [carregando, setCarregando] = useState(true);

  const limparSessao = useCallback(() => {
    definirAccessToken(null);
    setUsuario(null);
    void qc.clear();
  }, [qc]);

  /** Renova access via cookie; não desloga se ainda houver access (falha transitória). */
  const renovarAccessSePossivel = useCallback(async () => {
    const ok = await api.auth.refresh();
    if (!ok && !obterAccessToken()) {
      limparSessao();
    }
    return ok;
  }, [limparSessao]);

  const atualizarUsuario = useCallback(async () => {
    const eu = await api.auth.eu();
    setUsuario(eu);
  }, []);

  const atualizarNome = useCallback(async (nome: string) => {
    const eu = await api.auth.atualizarPerfil({ nome });
    setUsuario(eu);
  }, []);

  useEffect(() => {
    aoExpirarSessao(() => {
      limparSessao();
    });
    return () => aoExpirarSessao(null);
  }, [limparSessao]);

  useEffect(() => {
    let ativo = true;
    (async () => {
      try {
        const ok = await api.auth.refresh();
        if (!ok || !obterAccessToken()) {
          if (ativo) setCarregando(false);
          return;
        }
        const eu = await api.auth.eu();
        if (ativo) setUsuario(eu);
      } catch {
        limparSessao();
      } finally {
        if (ativo) setCarregando(false);
      }
    })();
    return () => {
      ativo = false;
    };
  }, [limparSessao]);

  useEffect(() => {
    if (!usuario) return;

    const intervalo = window.setInterval(() => {
      void renovarAccessSePossivel();
    }, INTERVALO_REFRESH_MS);

    const aoVisivel = () => {
      if (document.visibilityState === 'visible') {
        void renovarAccessSePossivel();
      }
    };

    document.addEventListener('visibilitychange', aoVisivel);

    return () => {
      window.clearInterval(intervalo);
      document.removeEventListener('visibilitychange', aoVisivel);
    };
  }, [usuario, renovarAccessSePossivel]);

  const login = useCallback(
    async (email: string, senha: string) => {
      await api.auth.login({ email, senha });
      await atualizarUsuario();
    },
    [atualizarUsuario],
  );

  const cadastrar = useCallback(
    async (nome: string, email: string, senha: string) => {
      await api.auth.cadastrar({ nome, email, senha });
      await atualizarUsuario();
    },
    [atualizarUsuario],
  );

  const logout = useCallback(async () => {
    try {
      await api.auth.logout();
    } finally {
      limparSessao();
    }
  }, [limparSessao]);

  const valor = useMemo<ContextoAuthValor>(
    () => ({
      usuario,
      autenticado: Boolean(usuario),
      carregando,
      login,
      cadastrar,
      logout,
      atualizarUsuario,
      atualizarNome,
    }),
    [usuario, carregando, login, cadastrar, logout, atualizarUsuario, atualizarNome],
  );

  return <ContextoAuth.Provider value={valor}>{children}</ContextoAuth.Provider>;
}

export function useAuth(): ContextoAuthValor {
  const ctx = useContext(ContextoAuth);
  if (!ctx) throw new Error('useAuth deve ser usado dentro de ProvedorAuth');
  return ctx;
}
