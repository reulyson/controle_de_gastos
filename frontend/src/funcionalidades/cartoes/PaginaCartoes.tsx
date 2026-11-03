import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { api } from '@/compartilhado/api/servicos';
import { chavesConsulta } from '@/compartilhado/api/chavesConsulta';
import { useCarteira } from '@/compartilhado/contexto/ContextoCarteira';
import type { IdRecurso } from '@/compartilhado/api/tipos';
import { formatarMoeda } from '@/compartilhado/formatacao';
import { Botao } from '@/compartilhado/ui/Botao';
import { EstadoConsulta } from '@/compartilhado/ui/EstadoConsulta';
import { GavetaDetalheFaturaCartao } from '@/funcionalidades/cartoes/GavetaDetalheFaturaCartao';
import { GavetaNovaCompra } from '@/funcionalidades/cartoes/GavetaNovaCompra';
import { GavetaNovoCartao } from '@/funcionalidades/cartoes/GavetaNovoCartao';

export function PaginaCartoes() {
  const { carteiraId, anoPadrao } = useCarteira();
  const [gavetaCartao, setGavetaCartao] = useState(false);
  const [gavetaCompra, setGavetaCompra] = useState(false);
  const [fatura, setFatura] = useState<{ id: IdRecurso; nome: string } | null>(null);

  const consulta = useQuery({
    queryKey: carteiraId ? chavesConsulta.cartoes.lista(carteiraId) : ['cartoes-vazio'],
    queryFn: () => api.cartoes.listar(carteiraId!),
    enabled: Boolean(carteiraId),
  });

  const mesAtual = new Date().getMonth() + 1;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Cartões</h2>
          <p className="text-sm text-slate-500">Cadastro e compras por cartão</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Botao variante="secundario" onClick={() => setGavetaCartao(true)}>
            Cadastrar cartão
          </Botao>
          <Botao
            icone={<span className="material-symbols-outlined text-base">shopping_cart</span>}
            onClick={() => setGavetaCompra(true)}
          >
            Nova compra
          </Botao>
        </div>
      </div>

      <EstadoConsulta
        carregando={consulta.isLoading}
        erro={consulta.error instanceof Error ? consulta.error : null}
        vazio={!consulta.isLoading && (consulta.data?.length ?? 0) === 0}
        mensagemVazio="Nenhum cartão cadastrado."
        onRecarregar={() => void consulta.refetch()}
      >
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {consulta.data?.map((cartao) => (
            <article key={cartao.id} className="fin-panel overflow-hidden">
              <div className="bg-fin-gradient px-4 py-5 text-white">
                <p className="text-xs uppercase tracking-wide text-teal-100/80">
                  {cartao.bandeira ?? 'Cartão'}
                </p>
                <h3 className="text-lg font-bold">{cartao.nome}</h3>
              </div>
              <div className="space-y-2 px-4 py-4 text-sm text-slate-600">
                {cartao.limite !== undefined ? (
                  <p>
                    Limite: <strong>{formatarMoeda(cartao.limite)}</strong>
                  </p>
                ) : null}
                <p>
                  Fechamento: dia {cartao.dia_fechamento ?? '—'} · Vencimento: dia{' '}
                  {cartao.dia_vencimento ?? '—'}
                </p>
                <Botao
                  className="mt-2 w-full"
                  variante="secundario"
                  onClick={() => setFatura({ id: cartao.id, nome: cartao.nome })}
                >
                  Ver fatura do mês
                </Botao>
              </div>
            </article>
          ))}
        </div>
      </EstadoConsulta>

      <GavetaNovoCartao aberta={gavetaCartao} onFechar={() => setGavetaCartao(false)} />
      <GavetaNovaCompra aberta={gavetaCompra} onFechar={() => setGavetaCompra(false)} />
      <GavetaDetalheFaturaCartao
        aberta={fatura !== null}
        cartaoId={fatura?.id ?? null}
        ano={anoPadrao}
        mes={mesAtual}
        rotulo={fatura?.nome}
        onFechar={() => setFatura(null)}
      />
    </div>
  );
}
