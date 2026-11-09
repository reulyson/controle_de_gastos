import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useCarteira } from '@/compartilhado/contexto/ContextoCarteira';
import { idComoTexto } from '@/compartilhado/formatacao';
import { Botao } from '@/compartilhado/ui/Botao';

export function PaginaEscolherPadrao() {
  const { carteiras, precisaEscolherPadrao, definirPadrao, carregando } = useCarteira();
  const [escolhida, setEscolhida] = useState(
    carteiras[0] ? idComoTexto(carteiras[0].id) : '',
  );
  const [pendente, setPendente] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  if (!carregando && !precisaEscolherPadrao) {
    return <Navigate to="/" replace />;
  }

  const confirmar = async () => {
    if (!escolhida) return;
    setPendente(true);
    setErro(null);
    try {
      await definirPadrao(escolhida);
    } catch (err) {
      setErro(err instanceof Error ? err.message : 'Não foi possível definir o padrão');
    } finally {
      setPendente(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-100 via-slate-50 to-teal-50/40 px-4">
      <div className="fin-panel w-full max-w-lg space-y-4 p-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Qual carteira é a padrão?</h1>
          <p className="text-sm text-slate-500">Escolha qual usar no app</p>
        </div>
        <ul className="space-y-2">
          {carteiras.map((c) => {
            const id = idComoTexto(c.id);
            return (
              <li key={id}>
                <label className="flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 px-4 py-3 hover:bg-slate-50">
                  <input
                    type="radio"
                    name="padrao"
                    checked={escolhida === id}
                    onChange={() => setEscolhida(id)}
                  />
                  <span className="font-medium text-slate-800">{c.nome}</span>
                </label>
              </li>
            );
          })}
        </ul>
        {erro ? <p className="text-sm text-rose-600">{erro}</p> : null}
        <Botao className="w-full" carregando={pendente} onClick={() => void confirmar()}>
          Confirmar padrão
        </Botao>
      </div>
    </div>
  );
}
