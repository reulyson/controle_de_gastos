export type TipoLancamento = 'receita' | 'despesa';

export type RecorrenciaLancamento = 'unica' | 'mensal';

export type IdRecurso = string | number;

export interface Carteira {
  id: IdRecurso;
  nome: string;
  ano_padrao?: number;
  saldo_inicial?: number;
  limite_cheque?: number;
}

export interface Categoria {
  id: IdRecurso;
  nome: string;
  tipo: TipoLancamento | 'ambos';
  cor?: string;
}

export interface Tag {
  id: IdRecurso;
  nome: string;
}

export interface LancamentoBase {
  id: IdRecurso;
  carteira_id: IdRecurso;
  descricao: string;
  valor: number;
  categoria_id?: IdRecurso | null;
  tag_ids?: IdRecurso[];
  recorrencia: RecorrenciaLancamento;
  mes_referencia?: number;
  ano_referencia?: number;
  pago?: boolean;
  orcado?: number;
  created_at?: string;
}

export interface Receita extends LancamentoBase {
  tipo: 'receita';
}

export interface Despesa extends LancamentoBase {
  tipo: 'despesa';
}

export interface Cartao {
  id: IdRecurso;
  carteira_id: IdRecurso;
  nome: string;
  bandeira?: string;
  dia_fechamento?: number;
  dia_vencimento?: number;
  limite?: number;
}

export interface CompraCartao {
  id: IdRecurso;
  cartao_id: IdRecurso;
  descricao: string;
  valor: number;
  parcelas?: number;
  recorrencia?: RecorrenciaLancamento;
  mes_referencia: number;
  ano_referencia: number;
  pago?: boolean;
}

export interface CelulaGrade {
  id: IdRecurso;
  linha_id: IdRecurso;
  mes: number;
  valor: number;
  orcado?: number;
  pago: boolean;
  tipo: 'receita' | 'despesa' | 'cartao';
  referencia_id?: IdRecurso;
}

export interface LinhaGrade {
  id: IdRecurso;
  secao: 'RECEITAS' | 'DESPESAS' | 'CARTOES';
  rotulo: string;
  categoria?: string;
  celulas: CelulaGrade[];
  total_anual?: number;
}

export interface TotaisGrade {
  total_receita: number;
  total_despesa: number;
  total_orcado: number;
  total_pago: number;
  caixa: number;
}

export interface IndicadoresMes {
  saldo_caixa: number;
  cheque_livre: number;
  receitas: number;
  despesas: number;
  orcado: number;
  pendencias: number;
}

export interface GradeControle {
  ano: number;
  mes_selecionado: number;
  mes_fechado?: boolean;
  indicadores: IndicadoresMes;
  linhas: LinhaGrade[];
  totais: TotaisGrade;
  meses?: { mes: number; status: 'aberto' | 'fechado' }[];
  pendencias_herdadas?: unknown[];
}

export interface FechamentoMesPayload {
  mes: number;
  ano: number;
}

export interface PagamentoPayload {
  tipo: 'receita' | 'despesa' | 'cartao';
  referencia_id: IdRecurso;
  mes: number;
  ano: number;
  pago: boolean;
}

export interface ConfiguracaoCarteira {
  limite_cheque?: number;
  saldo_inicial?: number;
  ano_padrao?: number;
}

export interface AjusteExtratoPayload {
  valor: number;
  descricao?: string;
  data?: string;
}

export interface RelatorioResumo {
  meses: { mes: number; receitas: number; despesas: number; saldo: number }[];
  por_categoria: { nome: string; valor: number; tipo: TipoLancamento }[];
}

export interface CriarReceitaPayload {
  carteira_id: IdRecurso;
  descricao: string;
  valor: number;
  categoria_id?: IdRecurso | null;
  tag_ids?: IdRecurso[];
  recorrencia: RecorrenciaLancamento;
  mes_referencia?: number;
  ano_referencia?: number;
}

export type CriarDespesaPayload = CriarReceitaPayload;

export interface CriarCartaoPayload {
  carteira_id: IdRecurso;
  nome: string;
  bandeira?: string;
  dia_fechamento?: number;
  dia_vencimento?: number;
  limite?: number;
}

export interface CriarCompraPayload {
  cartao_id: IdRecurso;
  descricao: string;
  valor: number;
  parcelas?: number;
  recorrencia?: RecorrenciaLancamento;
  mes_referencia: number;
  ano_referencia: number;
}

export interface FaturaCartaoDetalhe {
  cartao: Cartao;
  mes: number;
  ano: number;
  itens: {
    id: IdRecurso;
    descricao: string;
    valor: number;
    recorrente: boolean;
    pago: boolean;
  }[];
  total: number;
}
