import { requisicaoApi } from './cliente';
import type {
  AjusteExtratoPayload,
  Cartao,
  Carteira,
  Categoria,
  CompraCartao,
  ConfiguracaoCarteira,
  CriarCartaoPayload,
  CriarCompraPayload,
  CriarDespesaPayload,
  CriarReceitaPayload,
  Despesa,
  FechamentoMesPayload,
  FaturaCartaoDetalhe,
  GradeControle,
  PagamentoPayload,
  Receita,
  RelatorioResumo,
  Tag,
} from './tipos';

export const api = {
  carteiras: {
    listar: () => requisicaoApi<Carteira[]>('/api/v1/carteiras'),
    atualizarConfig: (id: string, body: ConfiguracaoCarteira) =>
      requisicaoApi<Carteira>(`/api/v1/carteiras/${id}`, {
        method: 'PATCH',
        body,
      }),
    gradeControle: (id: string, ano: number, mes?: number) => {
      const params = mes !== undefined ? `?mes=${mes}` : '';
      return requisicaoApi<GradeControle>(
        `/api/v1/carteiras/${id}/anos/${ano}/grade-controle${params}`,
      );
    },
    relatorio: (id: string, ano: number) =>
      requisicaoApi<RelatorioResumo>(`/api/v1/carteiras/${id}/anos/${ano}/relatorio`),
    ajustarExtrato: (id: string, body: AjusteExtratoPayload) =>
      requisicaoApi<void>(`/api/v1/carteiras/${id}/ajustes-extrato`, {
        method: 'POST',
        body,
      }),
    reabrirMes: (id: string, mes: number, ano: number) =>
      requisicaoApi<void>(`/api/v1/carteiras/${id}/fechamentos/reabrir`, {
        method: 'POST',
        body: { mes, ano },
      }),
  },
  receitas: {
    listar: (carteiraId: string) =>
      requisicaoApi<Receita[]>(`/api/v1/receitas?carteira_id=${carteiraId}`),
    criar: (body: CriarReceitaPayload) =>
      requisicaoApi<Receita>('/api/v1/receitas', { method: 'POST', body }),
    atualizar: (id: string, body: Partial<CriarReceitaPayload>) =>
      requisicaoApi<Receita>(`/api/v1/receitas/${id}`, { method: 'PUT', body }),
    excluir: (id: string) =>
      requisicaoApi<void>(`/api/v1/receitas/${id}`, { method: 'DELETE' }),
  },
  despesas: {
    listar: (carteiraId: string) =>
      requisicaoApi<Despesa[]>(`/api/v1/despesas?carteira_id=${carteiraId}`),
    criar: (body: CriarDespesaPayload) =>
      requisicaoApi<Despesa>('/api/v1/despesas', { method: 'POST', body }),
    atualizar: (id: string, body: Partial<CriarDespesaPayload>) =>
      requisicaoApi<Despesa>(`/api/v1/despesas/${id}`, { method: 'PUT', body }),
    excluir: (id: string) =>
      requisicaoApi<void>(`/api/v1/despesas/${id}`, { method: 'DELETE' }),
  },
  categorias: {
    listar: () => requisicaoApi<Categoria[]>('/api/v1/categorias'),
    criar: (body: { nome: string; tipo: Categoria['tipo'] }) =>
      requisicaoApi<Categoria>('/api/v1/categorias', { method: 'POST', body }),
    excluir: (id: string) =>
      requisicaoApi<void>(`/api/v1/categorias/${id}`, { method: 'DELETE' }),
  },
  tags: {
    listar: () => requisicaoApi<Tag[]>('/api/v1/tags'),
    criar: (nome: string) =>
      requisicaoApi<Tag>('/api/v1/tags', { method: 'POST', body: { nome } }),
  },
  cartoes: {
    listar: (carteiraId: string) =>
      requisicaoApi<Cartao[]>(`/api/v1/cartoes?carteira_id=${carteiraId}`),
    criar: (body: CriarCartaoPayload) =>
      requisicaoApi<Cartao>('/api/v1/cartoes', { method: 'POST', body }),
    fatura: (id: string, ano: number, mes: number) =>
      requisicaoApi<FaturaCartaoDetalhe>(
        `/api/v1/cartoes/${id}/faturas/${ano}/${mes}`,
      ),
  },
  compras: {
    listar: (cartaoId: string) =>
      requisicaoApi<CompraCartao[]>(`/api/v1/compras?cartao_id=${cartaoId}`),
    criar: (body: CriarCompraPayload) =>
      requisicaoApi<CompraCartao>('/api/v1/compras', { method: 'POST', body }),
  },
  pagamentos: {
    alternar: (body: PagamentoPayload) =>
      requisicaoApi<void>('/api/v1/pagamentos', { method: 'POST', body }),
  },
  fechamentos: {
    fecharMes: (carteiraId: string, body: FechamentoMesPayload) =>
      requisicaoApi<void>(`/api/v1/carteiras/${carteiraId}/fechamentos`, {
        method: 'POST',
        body,
      }),
  },
};
