/** Vazio = same-origin (proxy Vite /api → backend). Em prod use URL absoluta se necessário. */
const baseUrl = () =>
  (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '');


export class ErroApi extends Error {
  status: number;
  corpo?: unknown;

  constructor(mensagem: string, status: number, corpo?: unknown) {
    super(mensagem);
    this.name = 'ErroApi';
    this.status = status;
    this.corpo = corpo;
  }
}

type MetodoHttp = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

interface OpcoesFetch {
  method?: MetodoHttp;
  body?: unknown;
  signal?: AbortSignal;
  autenticado?: boolean;
  credentials?: RequestCredentials;
}

let accessTokenMemoria: string | null = null;
let renovando: Promise<boolean> | null = null;
let aoSessaoExpirada: (() => void) | null = null;

export function definirAccessToken(token: string | null): void {
  accessTokenMemoria = token;
}

export function obterAccessToken(): string | null {
  return accessTokenMemoria;
}

export function aoExpirarSessao(callback: (() => void) | null): void {
  aoSessaoExpirada = callback;
}

function mensagemErroApi(dados: unknown, status: number): string {
  if (typeof dados !== 'object' || dados === null || !('detail' in dados)) {
    return `Erro ${status} ao chamar a API`;
  }
  const detail = (dados as { detail: unknown }).detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    const partes = detail.map((item) => {
      if (typeof item !== 'object' || item === null) return String(item);
      const erro = item as { loc?: unknown[]; msg?: string };
      const campo = Array.isArray(erro.loc)
        ? erro.loc.filter((p) => p !== 'body').join('.')
        : '';
      const msg = erro.msg ?? 'inválido';
      return campo ? `${campo}: ${msg}` : msg;
    });
    return partes.filter(Boolean).join('; ') || `Erro ${status} ao chamar a API`;
  }
  return `Erro ${status} ao chamar a API`;
}

/**
 * Renova o access via cookie de refresh (serializado).
 * Em falha não apaga o access atual — quem encerra a sessão é o fluxo 401 / limparSessao.
 */
export async function tentarRefresh(): Promise<boolean> {
  if (renovando) return renovando;
  renovando = (async () => {
    try {
      const resposta = await fetch(`${baseUrl()}/api/v1/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
      });
      if (!resposta.ok) return false;
      const dados = (await resposta.json()) as { access_token?: string };
      if (!dados.access_token) return false;
      definirAccessToken(dados.access_token);
      return true;
    } catch {
      return false;
    } finally {
      renovando = null;
    }
  })();
  return renovando;
}

export async function requisicaoApi<T>(
  caminho: string,
  opcoes: OpcoesFetch = {},
): Promise<T> {
  const {
    method = 'GET',
    body,
    signal,
    autenticado = true,
    credentials = 'include',
  } = opcoes;

  const executar = async (jaTentouRefresh: boolean): Promise<T> => {
    const headers: HeadersInit = {};
    let payload: BodyInit | undefined;

    if (body !== undefined) {
      headers['Content-Type'] = 'application/json';
      payload = JSON.stringify(body);
    }
    if (autenticado && accessTokenMemoria) {
      headers.Authorization = `Bearer ${accessTokenMemoria}`;
    }

    const resposta = await fetch(`${baseUrl()}${caminho}`, {
      method,
      headers,
      body: payload,
      signal,
      credentials,
    });

    if (resposta.status === 401 && autenticado && !jaTentouRefresh) {
      const ok = await tentarRefresh();
      if (ok) return executar(true);
      aoSessaoExpirada?.();
      throw new ErroApi('Sessão expirada', 401);
    }

    const texto = await resposta.text();
    let dados: unknown = undefined;
    if (texto) {
      try {
        dados = JSON.parse(texto) as unknown;
      } catch {
        dados = texto;
      }
    }

    if (!resposta.ok) {
      throw new ErroApi(mensagemErroApi(dados, resposta.status), resposta.status, dados);
    }

    return dados as T;
  };

  return executar(false);
}
