const baseUrl = () =>
  (import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000').replace(/\/$/, '');

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
}

export async function requisicaoApi<T>(
  caminho: string,
  opcoes: OpcoesFetch = {},
): Promise<T> {
  const { method = 'GET', body, signal } = opcoes;
  const headers: HeadersInit = {};
  let payload: BodyInit | undefined;

  if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
    payload = JSON.stringify(body);
  }

  const resposta = await fetch(`${baseUrl()}${caminho}`, {
    method,
    headers,
    body: payload,
    signal,
  });

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
    const mensagem =
      typeof dados === 'object' &&
      dados !== null &&
      'detail' in dados &&
      typeof (dados as { detail: unknown }).detail === 'string'
        ? (dados as { detail: string }).detail
        : `Erro ${resposta.status} ao chamar a API`;
    throw new ErroApi(mensagem, resposta.status, dados);
  }

  return dados as T;
}
