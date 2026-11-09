export type TipoLancamento = 'receita' | 'despesa';

export type RecorrenciaLancamento = 'unica' | 'mensal';

export type IdRecurso = string | number;

export interface UsuarioAuth {
  id: IdRecurso;
  email: string;
  nome: string;
}

export interface TokenAuth {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export type TipoCarteira = 'pessoal' | 'empresarial' | 'conjunto';

export interface Carteira {
  id: IdRecurso;
  nome: string;
  tipo_carteira?: TipoCarteira;
  ano_padrao?: number;
  saldo_inicial?: number;
  saldo_atual?: number;
  limite_cheque?: number;
  padrao?: boolean;
}

export type TipoCategoria = TipoLancamento | 'compra' | 'ambos';

export type OrigemCategoria = 'padrao' | 'pessoal';

export interface Categoria {
  id: IdRecurso;
  nome: string;
  tipo: TipoCategoria;
  origem?: OrigemCategoria;
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
  final_4?: string | null;
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
  recorrencia?: RecorrenciaLancamento;
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
  total_pago?: number;
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
  tipo_carteira?: TipoCarteira;
  ano_padrao?: number;
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
  recorrencia: RecorrenciaLancamento;
  mes_referencia?: number;
  ano_referencia?: number;
  quantidade_meses?: number;
  valor_variavel?: boolean;
}

export type CriarDespesaPayload = CriarReceitaPayload;

export interface AtualizarLancamentoPayload {
  descricao?: string;
  valor?: number;
  categoria_id?: IdRecurso | null;
  recorrencia?: RecorrenciaLancamento;
  valor_variavel?: boolean;
  ativo?: boolean;
}

export interface CriarCartaoPayload {
  carteira_id: IdRecurso;
  nome: string;
  bandeira?: string;
  final_4?: string;
  dia_fechamento?: number;
  dia_vencimento?: number;
  limite?: number;
}

export interface AtualizarCartaoPayload {
  nome?: string;
  bandeira?: string;
  final_4?: string;
  dia_fechamento?: number;
  dia_vencimento?: number;
  limite?: number;
}

export interface CriarCarteiraPayload {
  nome: string;
  tipo_carteira?: TipoCarteira;
  limite_cheque?: number;
  saldo_inicial?: number;
  ano_padrao?: number;
  padrao?: boolean;
}

export interface CriarCompraPayload {
  cartao_id: IdRecurso;
  descricao: string;
  valor: number;
  parcelas?: number;
  quantidade_meses?: number;
  recorrencia?: RecorrenciaLancamento;
  data_vencimento?: string;
  mes_referencia?: number;
  ano_referencia?: number;
  categoria_id?: IdRecurso | null;
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
