export const chavesConsulta = {
  carteiras: {
    todas: ['carteiras'] as const,
    anos: (carteiraId: string) => ['carteiras', carteiraId, 'anos'] as const,
  },
  grade: {
    controle: (carteiraId: string, ano: number, mes: number) =>
      ['grade-controle', carteiraId, ano, mes] as const,
  },
  receitas: {
    lista: (carteiraId: string) => ['receitas', carteiraId] as const,
  },
  despesas: {
    lista: (carteiraId: string) => ['despesas', carteiraId] as const,
  },
  categorias: {
    todas: ['categorias'] as const,
  },
  tags: {
    todas: ['tags'] as const,
  },
  cartoes: {
    lista: (carteiraId: string) => ['cartoes', carteiraId] as const,
    fatura: (cartaoId: string, ano: number, mes: number) =>
      ['fatura-cartao', cartaoId, ano, mes] as const,
  },
  relatorio: {
    resumo: (carteiraId: string, ano: number) =>
      ['relatorio', carteiraId, ano] as const,
  },
};
