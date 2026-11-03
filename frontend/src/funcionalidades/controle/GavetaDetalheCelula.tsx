import { useEffect, useState } from 'react';
import type { CelulaGrade, IdRecurso } from '@/compartilhado/api/tipos';
import {
  formatarMesCompleto,
  formatarMoeda,
  idComoTexto,
} from '@/compartilhado/formatacao';
import { Botao } from '@/compartilhado/ui/Botao';
import { GavetaLateral } from '@/compartilhado/ui/GavetaLateral';

export type EscopoValorMensal = 'somente_mes' | 'deste_mes_em_diante';

interface GavetaDetalheCelulaProps {
  celula: CelulaGrade | null;
  rotuloLinha?: string;
  ano: number;
  salvando?: boolean;
  onFechar: () => void;
  onSalvarValor: (args: {
    celula: CelulaGrade;
    valor: number;
    escopo: EscopoValorMensal;
  }) => void;
  onAlternarPago: (celula: CelulaGrade, pago: boolean) => void;
}

/**
 * Gaveta ao clicar no valor da célula (receita/despesa).
 * Permite marcar pago/recebido e editar valor só neste mês ou deste mês em diante.
 */
export function GavetaDetalheCelula({
  celula,
  rotuloLinha,
  ano,
  salvando = false,
  onFechar,
  onSalvarValor,
  onAlternarPago,
}: GavetaDetalheCelulaProps) {
  const [novoValor, setNovoValor] = useState('');
  const [escopo, setEscopo] = useState<EscopoValorMensal>('somente_mes');
  const [marcarPago, setMarcarPago] = useState(false);

  useEffect(() => {
    if (!celula) return;
    setNovoValor(String(celula.valor ?? ''));
    setEscopo('somente_mes');
    setMarcarPago(celula.pago);
  }, [celula]);

  const aberta = celula !== null && celula.tipo !== 'cartao';
  const rotuloStatus = celula?.tipo === 'receita' ? 'Recebido' : 'Pago';
  const podeSalvar =
    Boolean(celula) &&
    novoValor.trim() !== '' &&
    !Number.isNaN(Number(novoValor.replace(',', '.'))) &&
    (escopo === 'somente_mes' || escopo === 'deste_mes_em_diante');

  const salvar = () => {
    if (!celula || !podeSalvar) return;
    const valor = Number(novoValor.replace(',', '.'));
    onSalvarValor({ celula, valor, escopo });
    if (marcarPago !== celula.pago) {
      onAlternarPago(celula, marcarPago);
    }
  };

  return (
    <GavetaLateral
      aberta={aberta}
      titulo={
        celula
          ? `${rotuloLinha ?? 'Lançamento'} — ${formatarMesCompleto(celula.mes)}/${ano}`
          : 'Detalhe'
      }
      onFechar={onFechar}
      rodape={
        <div className="flex justify-end gap-2">
          <Botao variante="fantasma" onClick={onFechar}>
            Cancelar
          </Botao>
          <Botao
            variante="primario"
            disabled={!podeSalvar || salvando}
            carregando={salvando}
            onClick={salvar}
          >
            Salvar
          </Botao>
        </div>
      }
    >
      {celula ? (
        <div className="space-y-5 text-sm">
          <div>
            <p className="fin-label">Valor neste mês</p>
            <p className="text-lg font-bold text-fin-teal-700">
              {formatarMoeda(celula.valor)}
            </p>
            <p className="mt-1 text-slate-500">
              Status: {celula.pago ? rotuloStatus : 'Pendente'}
            </p>
          </div>

          <label className="flex items-center gap-2 font-medium text-slate-700">
            <input
              type="checkbox"
              className="size-4 rounded border-slate-300 text-fin-teal-600"
              checked={marcarPago}
              onChange={(e) => setMarcarPago(e.target.checked)}
            />
            Marcar como {rotuloStatus.toLowerCase()}
          </label>

          <div>
            <label className="fin-label" htmlFor="novo-valor-celula">
              Novo valor *
            </label>
            <input
              id="novo-valor-celula"
              className="fin-input"
              inputMode="decimal"
              value={novoValor}
              onChange={(e) => setNovoValor(e.target.value)}
            />
          </div>

          <fieldset className="space-y-2">
            <legend className="fin-label">Aplicar em</legend>
            <label className="flex items-center gap-2">
              <input
                type="radio"
                name="escopo-valor"
                checked={escopo === 'somente_mes'}
                onChange={() => setEscopo('somente_mes')}
              />
              Desse mês ({formatarMesCompleto(celula.mes)}/{ano})
            </label>
            <label className="flex items-center gap-2">
              <input
                type="radio"
                name="escopo-valor"
                checked={escopo === 'deste_mes_em_diante'}
                onChange={() => setEscopo('deste_mes_em_diante')}
              />
              Esse e os próximos
            </label>
          </fieldset>

          {celula.referencia_id !== undefined ? (
            <p className="text-xs text-slate-400">
              Ref. {idComoTexto(celula.referencia_id as IdRecurso)}
            </p>
          ) : null}
        </div>
      ) : null}
    </GavetaLateral>
  );
}
