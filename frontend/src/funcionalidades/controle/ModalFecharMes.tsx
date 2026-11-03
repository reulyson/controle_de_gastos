import { Botao } from '@/compartilhado/ui/Botao';
import { formatarMesCompleto } from '@/compartilhado/formatacao';

interface ModalFecharMesProps {
  aberto: boolean;
  mes: number;
  ano: number;
  carregando?: boolean;
  onConfirmar: () => void;
  onCancelar: () => void;
}

export function ModalFecharMes({
  aberto,
  mes,
  ano,
  carregando,
  onConfirmar,
  onCancelar,
}: ModalFecharMesProps) {
  if (!aberto) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" onClick={onCancelar} />
      <div className="relative w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
        <span className="material-symbols-outlined text-4xl text-fin-teal-600">event_available</span>
        <h3 className="mt-3 text-lg font-bold text-slate-800">Fechar mês</h3>
        <p className="mt-2 text-sm text-slate-600">
          Confirma o fechamento de {formatarMesCompleto(mes)}/{ano}? Lançamentos pendentes continuarão
          visíveis, mas o mês será marcado como fechado.
        </p>
        <div className="mt-6 flex justify-end gap-2">
          <Botao variante="secundario" onClick={onCancelar}>
            Cancelar
          </Botao>
          <Botao carregando={carregando} onClick={onConfirmar}>
            Fechar mês
          </Botao>
        </div>
      </div>
    </div>
  );
}
