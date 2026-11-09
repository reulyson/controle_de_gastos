import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { api } from '@/compartilhado/api/servicos';
import { chavesConsulta } from '@/compartilhado/api/chavesConsulta';
import type { Cartao } from '@/compartilhado/api/tipos';
import { useCarteira } from '@/compartilhado/contexto/ContextoCarteira';
import { idComoTexto } from '@/compartilhado/formatacao';
import { Botao } from '@/compartilhado/ui/Botao';
import { CampoMoeda } from '@/compartilhado/ui/CampoMoeda';
import { GavetaLateral } from '@/compartilhado/ui/GavetaLateral';

interface GavetaNovoCartaoProps {
  aberta: boolean;
  onFechar: () => void;
  cartaoEdicao?: Cartao | null;
}

export function GavetaNovoCartao({
  aberta,
  onFechar,
  cartaoEdicao = null,
}: GavetaNovoCartaoProps) {
  const { carteiraId } = useCarteira();
  const qc = useQueryClient();
  const editando = cartaoEdicao != null;
  const [nome, setNome] = useState('');
  const [bandeira, setBandeira] = useState('');
  const [final4, setFinal4] = useState('');
  const [limite, setLimite] = useState<number | null>(null);
  const [diaFechamento, setDiaFechamento] = useState('1');
  const [diaVencimento, setDiaVencimento] = useState('10');

  useEffect(() => {
    if (!aberta) return;
    if (cartaoEdicao) {
      setNome(cartaoEdicao.nome);
      setBandeira(cartaoEdicao.bandeira ?? '');
      setFinal4(cartaoEdicao.final_4 ?? '');
      setLimite(
        cartaoEdicao.limite !== undefined && cartaoEdicao.limite !== null
          ? Number(cartaoEdicao.limite)
          : null,
      );
      setDiaFechamento(String(cartaoEdicao.dia_fechamento ?? 1));
      setDiaVencimento(String(cartaoEdicao.dia_vencimento ?? 10));
      return;
    }
    setNome('');
    setBandeira('');
    setFinal4('');
    setLimite(null);
    setDiaFechamento('1');
    setDiaVencimento('10');
  }, [aberta, cartaoEdicao]);

  const salvar = useMutation({
    mutationFn: () => {
      if (!carteiraId) throw new Error('Carteira não disponível');
      const final = final4.trim();
      if (final && !/^\d{4}$/.test(final)) {
        throw new Error('Informe exatamente 4 dígitos');
      }
      const corpo = {
        nome: nome.trim(),
        bandeira: bandeira.trim() || undefined,
        final_4: final || undefined,
        limite: limite ?? undefined,
        dia_fechamento: Number(diaFechamento),
        dia_vencimento: Number(diaVencimento),
      };
      if (editando && cartaoEdicao) {
        return api.cartoes.atualizar(idComoTexto(cartaoEdicao.id), corpo);
      }
      return api.cartoes.criar({
        carteira_id: carteiraId,
        ...corpo,
      });
    },
    onSuccess: async () => {
      if (carteiraId) {
        await qc.invalidateQueries({ queryKey: chavesConsulta.cartoes.lista(carteiraId) });
      }
      onFechar();
    },
  });

  return (
    <GavetaLateral
      aberta={aberta}
      titulo={editando ? 'Editar cartão' : 'Cadastrar cartão'}
      onFechar={onFechar}
      rodape={
        <div className="flex justify-end gap-2">
          <Botao variante="secundario" onClick={onFechar}>
            Cancelar
          </Botao>
          <Botao carregando={salvar.isPending} disabled={!nome.trim()} onClick={() => salvar.mutate()}>
            Salvar
          </Botao>
        </div>
      }
    >
      <div className="space-y-4">
        <div>
          <label className="fin-label" htmlFor="nome-cartao">
            Nome
          </label>
          <input
            id="nome-cartao"
            className="fin-input"
            value={nome}
            onChange={(e) => setNome(e.target.value)}
          />
        </div>
        <div>
          <label className="fin-label" htmlFor="bandeira">
            Bandeira
          </label>
          <input
            id="bandeira"
            className="fin-input"
            value={bandeira}
            onChange={(e) => setBandeira(e.target.value)}
          />
        </div>
        <div>
          <label className="fin-label" htmlFor="final4">
            4 últimos dígitos
          </label>
          <input
            id="final4"
            className="fin-input"
            inputMode="numeric"
            autoComplete="off"
            maxLength={4}
            value={final4}
            onChange={(e) => setFinal4(e.target.value.replace(/\D/g, '').slice(0, 4))}
            placeholder="1234"
          />
        </div>
        <CampoMoeda id="limite" label="Limite (R$)" valor={limite} onChange={setLimite} />
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="fin-label" htmlFor="fechamento">
              Dia fechamento
            </label>
            <input
              id="fechamento"
              type="number"
              min={1}
              max={31}
              className="fin-input"
              value={diaFechamento}
              onChange={(e) => setDiaFechamento(e.target.value)}
            />
          </div>
          <div>
            <label className="fin-label" htmlFor="vencimento">
              Dia vencimento
            </label>
            <input
              id="vencimento"
              type="number"
              min={1}
              max={31}
              className="fin-input"
              value={diaVencimento}
              onChange={(e) => setDiaVencimento(e.target.value)}
            />
          </div>
        </div>
        {salvar.error instanceof Error ? (
          <p className="text-sm text-rose-600">{salvar.error.message}</p>
        ) : null}
      </div>
    </GavetaLateral>
  );
}
