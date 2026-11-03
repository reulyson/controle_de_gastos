import type { CelulaGrade } from '@/compartilhado/api/tipos';
import { formatarMesCompleto, formatarMoeda } from '@/compartilhado/formatacao';
import { GavetaLateral } from '@/compartilhado/ui/GavetaLateral';

interface GavetaDetalheCelulaProps {
  celula: CelulaGrade | null;
  rotuloLinha?: string;
  onFechar: () => void;
}

export function GavetaDetalheCelula({ celula, rotuloLinha, onFechar }: GavetaDetalheCelulaProps) {
  return (
    <GavetaLateral aberta={celula !== null} titulo="Detalhe da célula" onFechar={onFechar}>
      {celula ? (
        <dl className="space-y-4 text-sm">
          <div>
            <dt className="fin-label">Linha</dt>
            <dd className="font-semibold text-slate-800">{rotuloLinha ?? celula.linha_id}</dd>
          </div>
          <div>
            <dt className="fin-label">Período</dt>
            <dd>{formatarMesCompleto(celula.mes)}</dd>
          </div>
          <div>
            <dt className="fin-label">Valor</dt>
            <dd className="text-lg font-bold text-fin-teal-700">{formatarMoeda(celula.valor)}</dd>
          </div>
          {celula.orcado !== undefined ? (
            <div>
              <dt className="fin-label">Orçado</dt>
              <dd>{formatarMoeda(celula.orcado)}</dd>
            </div>
          ) : null}
          <div>
            <dt className="fin-label">Status</dt>
            <dd>{celula.pago ? 'Pago' : 'Pendente'}</dd>
          </div>
          <div>
            <dt className="fin-label">Tipo</dt>
            <dd className="capitalize">{celula.tipo}</dd>
          </div>
        </dl>
      ) : null}
    </GavetaLateral>
  );
}
