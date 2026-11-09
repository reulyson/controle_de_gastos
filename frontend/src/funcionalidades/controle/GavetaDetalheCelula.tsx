import { useEffect, useState } from 'react';
import type { CelulaGrade } from '@/compartilhado/api/tipos';
import {
  formatarMesCompleto,
  formatarMoeda,
  formatarTitulo,
  valorNumerico,
} from '@/compartilhado/formatacao';
import { Botao } from '@/compartilhado/ui/Botao';
import { CampoMoeda } from '@/compartilhado/ui/CampoMoeda';
import { GavetaLateral } from '@/compartilhado/ui/GavetaLateral';
import { ToggleLinha } from '@/compartilhado/ui/ToggleLinha';

export type EscopoValorMensal = 'somente_mes' | 'deste_mes_em_diante';

interface GavetaDetalheCelulaProps {
  celula: CelulaGrade | null;
  rotuloLinha?: string;
  recorrente?: boolean;
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

function rotuloAcaoPago(tipo: CelulaGrade['tipo'], pago: boolean): string {
  if (tipo === 'receita') return pago ? 'Recebido' : 'Receber';
  return pago ? 'Pago' : 'Pagar';
}

/** OFF = neste mês; ON = recorrente (este mês e restantes). */
function escopoDeToggle(aplicarRecorrente: boolean): EscopoValorMensal {
  return aplicarRecorrente ? 'deste_mes_em_diante' : 'somente_mes';
}

function textoAplicarEm(aplicarRecorrente: boolean): { titulo: string; descricao: string } {
  if (aplicarRecorrente) {
    return { titulo: 'Recorrente', descricao: 'Altera este mês e os que restam' };
  }
  return { titulo: 'Neste mês', descricao: 'Altera só o mês aberto' };
}

function estadoInicial(celula: CelulaGrade) {
  const valor = valorNumerico(celula.valor);
  return {
    novoValor: valor,
    pagoLocal: celula.pago,
    aplicarRecorrente: false,
    editandoValor: false,
  };
}

/**
 * Gaveta ao clicar no valor da célula (receita/despesa).
 */
export function GavetaDetalheCelula({
  celula,
  rotuloLinha,
  recorrente = false,
  ano,
  salvando = false,
  onFechar,
  onSalvarValor,
  onAlternarPago,
}: GavetaDetalheCelulaProps) {
  const [novoValor, setNovoValor] = useState<number | null>(null);
  const [pagoLocal, setPagoLocal] = useState(false);
  const [aplicarRecorrente, setAplicarRecorrente] = useState(false);
  const [editandoValor, setEditandoValor] = useState(false);
  const [rascunhoValor, setRascunhoValor] = useState<number | null>(null);

  useEffect(() => {
    if (!celula) return;
    const inicial = estadoInicial(celula);
    setNovoValor(inicial.novoValor);
    setPagoLocal(inicial.pagoLocal);
    setAplicarRecorrente(inicial.aplicarRecorrente);
    setEditandoValor(inicial.editandoValor);
    setRascunhoValor(inicial.novoValor);
  }, [celula]);

  const aberta = celula !== null && celula.tipo !== 'cartao';
  const valorSalvar = valorNumerico(editandoValor ? rascunhoValor : novoValor);
  const podeSalvar = Boolean(celula) && valorSalvar !== null;
  const aplicarEm = textoAplicarEm(aplicarRecorrente);

  const confirmarEdicaoValor = () => {
    const n = valorNumerico(rascunhoValor);
    if (n === null) return;
    setNovoValor(n);
    setEditandoValor(false);
  };

  const cancelar = () => {
    if (celula) {
      const inicial = estadoInicial(celula);
      setNovoValor(inicial.novoValor);
      setPagoLocal(inicial.pagoLocal);
      setAplicarRecorrente(inicial.aplicarRecorrente);
      setEditandoValor(false);
      setRascunhoValor(inicial.novoValor);
    }
    onFechar();
  };

  const salvar = () => {
    if (!celula || valorSalvar === null || !podeSalvar) return;
    onSalvarValor({
      celula,
      valor: valorSalvar,
      escopo: recorrente ? escopoDeToggle(aplicarRecorrente) : 'somente_mes',
    });
    if (pagoLocal !== celula.pago) {
      onAlternarPago(celula, pagoLocal);
    }
  };

  return (
    <GavetaLateral
      aberta={aberta}
      largura="sm"
      titulo={
        celula
          ? `${formatarTitulo(rotuloLinha ?? 'Lançamento')} — ${formatarMesCompleto(celula.mes)}/${ano}`
          : 'Detalhe'
      }
      onFechar={cancelar}
      rodape={
        <div className="flex justify-end gap-2">
          <Botao variante="fantasma" onClick={cancelar}>
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
            <p className="fin-label">Valor</p>
            {editandoValor ? (
              <div className="flex items-end gap-2">
                <div className="min-w-0 flex-1">
                  <CampoMoeda
                    id="editar-valor-celula"
                    label=""
                    valor={rascunhoValor}
                    onChange={setRascunhoValor}
                    obrigatorio
                  />
                </div>
                <button
                  type="button"
                  onClick={confirmarEdicaoValor}
                  className="mb-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-fin-teal-200 bg-fin-teal-50 text-fin-teal-800 hover:bg-fin-teal-100"
                  title="Confirmar valor"
                  aria-label="Confirmar valor"
                >
                  <span className="material-symbols-outlined text-[22px]">check</span>
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <p className="text-lg font-bold text-fin-teal-700">
                  {formatarMoeda(valorNumerico(novoValor ?? celula.valor) ?? 0)}
                </p>
                <button
                  type="button"
                  onClick={() => {
                    setRascunhoValor(novoValor);
                    setEditandoValor(true);
                  }}
                  className="rounded-lg p-1.5 text-slate-500 hover:bg-slate-100 hover:text-fin-teal-700"
                  title="Editar valor"
                  aria-label="Editar valor"
                >
                  <span className="material-symbols-outlined text-[20px]">edit</span>
                </button>
              </div>
            )}
          </div>

          <Botao
            variante={pagoLocal ? 'primario' : 'secundario'}
            className="w-full"
            onClick={() => setPagoLocal((v) => !v)}
          >
            {rotuloAcaoPago(celula.tipo, pagoLocal)}
          </Botao>

          {recorrente ? (
            <ToggleLinha
              rotulo="Aplicar em"
              titulo={aplicarEm.titulo}
              descricao={aplicarEm.descricao}
              ativo={aplicarRecorrente}
              onAlternar={() => setAplicarRecorrente((v) => !v)}
            />
          ) : null}
        </div>
      ) : null}
    </GavetaLateral>
  );
}
