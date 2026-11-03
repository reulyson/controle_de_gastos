import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { api } from '@/compartilhado/api/servicos';
import { chavesConsulta } from '@/compartilhado/api/chavesConsulta';
import { useCarteira } from '@/compartilhado/contexto/ContextoCarteira';
import { Botao } from '@/compartilhado/ui/Botao';
import { GavetaLateral } from '@/compartilhado/ui/GavetaLateral';

interface GavetaNovoCartaoProps {
  aberta: boolean;
  onFechar: () => void;
}

export function GavetaNovoCartao({ aberta, onFechar }: GavetaNovoCartaoProps) {
  const { carteiraId } = useCarteira();
  const qc = useQueryClient();
  const [nome, setNome] = useState('');
  const [bandeira, setBandeira] = useState('');
  const [limite, setLimite] = useState('');
  const [diaFechamento, setDiaFechamento] = useState('1');
  const [diaVencimento, setDiaVencimento] = useState('10');

  useEffect(() => {
    if (!aberta) return;
    setNome('');
    setBandeira('');
    setLimite('');
    setDiaFechamento('1');
    setDiaVencimento('10');
  }, [aberta]);

  const salvar = useMutation({
    mutationFn: () => {
      if (!carteiraId) throw new Error('Carteira não disponível');
      return api.cartoes.criar({
        carteira_id: carteiraId,
        nome: nome.trim(),
        bandeira: bandeira.trim() || undefined,
        limite: limite ? Number(limite.replace(',', '.')) : undefined,
        dia_fechamento: Number(diaFechamento),
        dia_vencimento: Number(diaVencimento),
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
      titulo="Cadastrar cartão"
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
          <input id="nome-cartao" className="fin-input" value={nome} onChange={(e) => setNome(e.target.value)} />
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
          <label className="fin-label" htmlFor="limite">
            Limite (R$)
          </label>
          <input
            id="limite"
            className="fin-input"
            value={limite}
            onChange={(e) => setLimite(e.target.value)}
          />
        </div>
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
      </div>
    </GavetaLateral>
  );
}
