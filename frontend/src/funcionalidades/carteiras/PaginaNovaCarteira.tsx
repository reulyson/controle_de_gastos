import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '@/compartilhado/api/servicos';
import { chavesConsulta } from '@/compartilhado/api/chavesConsulta';
import type { TipoCarteira } from '@/compartilhado/api/tipos';
import { useCarteira } from '@/compartilhado/contexto/ContextoCarteira';
import { formatarTitulo } from '@/compartilhado/formatacao';
import { Botao } from '@/compartilhado/ui/Botao';
import { CampoMoeda } from '@/compartilhado/ui/CampoMoeda';

const TIPOS: { valor: TipoCarteira; rotulo: string }[] = [
  { valor: 'pessoal', rotulo: 'Pessoal' },
  { valor: 'empresarial', rotulo: 'Empresarial' },
  { valor: 'conjunto', rotulo: 'Conjunto' },
];

export function PaginaNovaCarteira() {
  const { carteiras } = useCarteira();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [nome, setNome] = useState('Principal');
  const [tipo, setTipo] = useState<TipoCarteira>('pessoal');
  const [temSaldo, setTemSaldo] = useState(false);
  const [saldo, setSaldo] = useState<number | null>(null);
  const [temCheque, setTemCheque] = useState(false);
  const [limite, setLimite] = useState<number | null>(null);
  const [comoPadrao, setComoPadrao] = useState(true);

  const jaTem = carteiras.length > 0;

  const criar = useMutation({
    mutationFn: () =>
      api.carteiras.criar({
        nome: formatarTitulo(nome),
        tipo_carteira: tipo,
        limite_cheque: temCheque ? (limite ?? 0) : 0,
        saldo_inicial: temSaldo ? (saldo ?? 0) : 0,
        padrao: jaTem ? comoPadrao : true,
      }),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: chavesConsulta.carteiras.todas });
      navigate('/', { replace: true });
    },
  });

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!nome.trim()) return;
    criar.mutate();
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-100 via-slate-50 to-teal-50/40 px-4">
      <form onSubmit={onSubmit} className="fin-panel w-full max-w-lg space-y-4 p-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Criar carteira</h1>
          <p className="text-sm text-slate-500">
            {jaTem
              ? 'Nova carteira para sua conta'
              : 'Primeira carteira vira padrão automaticamente'}
          </p>
        </div>
        <div>
          <label className="fin-label" htmlFor="nome-carteira">
            Nome
          </label>
          <input
            id="nome-carteira"
            className="fin-input"
            value={nome}
            onChange={(e) => setNome(e.target.value)}
            required
          />
        </div>

        <fieldset className="space-y-2">
          <legend className="fin-label">Tipo de carteira</legend>
          <div className="flex flex-wrap gap-3">
            {TIPOS.map((t) => (
              <label key={t.valor} className="flex items-center gap-2 text-sm text-slate-700">
                <input
                  type="radio"
                  name="tipo-carteira"
                  checked={tipo === t.valor}
                  onChange={() => setTipo(t.valor)}
                />
                {t.rotulo}
              </label>
            ))}
          </div>
        </fieldset>

        <fieldset className="space-y-2">
          <legend className="fin-label">Tem saldo inicial?</legend>
          <div className="flex gap-4">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="radio"
                name="tem-saldo"
                checked={!temSaldo}
                onChange={() => {
                  setTemSaldo(false);
                  setSaldo(null);
                }}
              />
              Não
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="radio"
                name="tem-saldo"
                checked={temSaldo}
                onChange={() => setTemSaldo(true)}
              />
              Sim
            </label>
          </div>
          {temSaldo ? (
            <CampoMoeda
              id="saldo-inicial-nova"
              label="Valor do saldo inicial"
              valor={saldo}
              onChange={setSaldo}
            />
          ) : null}
        </fieldset>

        <fieldset className="space-y-2">
          <legend className="fin-label">Vai usar cheque especial?</legend>
          <div className="flex gap-4">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="radio"
                name="tem-cheque"
                checked={!temCheque}
                onChange={() => {
                  setTemCheque(false);
                  setLimite(null);
                }}
              />
              Não
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="radio"
                name="tem-cheque"
                checked={temCheque}
                onChange={() => setTemCheque(true)}
              />
              Sim
            </label>
          </div>
          {temCheque ? (
            <CampoMoeda
              id="limite-cheque-nova"
              label="Limite do cheque especial"
              valor={limite}
              onChange={setLimite}
            />
          ) : null}
        </fieldset>

        {jaTem ? (
          <label className="flex items-center gap-2 text-sm text-slate-700">
            <input
              type="checkbox"
              checked={comoPadrao}
              onChange={(e) => setComoPadrao(e.target.checked)}
            />
            Definir como carteira padrão
          </label>
        ) : null}
        {criar.error instanceof Error ? (
          <p className="text-sm text-rose-600">{criar.error.message}</p>
        ) : null}
        <div className={`flex gap-2 ${jaTem ? '' : 'flex-col'}`}>
          {jaTem ? (
            <Botao
              type="button"
              variante="secundario"
              className="flex-1"
              onClick={() => navigate(-1)}
            >
              Cancelar
            </Botao>
          ) : null}
          <Botao
            type="submit"
            className={jaTem ? 'flex-1' : 'w-full'}
            carregando={criar.isPending}
            disabled={!nome.trim()}
          >
            Criar e continuar
          </Botao>
        </div>
      </form>
    </div>
  );
}
