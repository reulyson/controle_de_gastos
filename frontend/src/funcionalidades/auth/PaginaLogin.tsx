import { useState, type FormEvent } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '@/compartilhado/contexto/ContextoAuth';
import { Botao } from '@/compartilhado/ui/Botao';

export function PaginaLogin() {
  const { autenticado, carregando, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [erro, setErro] = useState<string | null>(null);
  const [pendente, setPendente] = useState(false);

  if (!carregando && autenticado) {
    return <Navigate to="/" replace />;
  }

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErro(null);
    setPendente(true);
    try {
      await login(email.trim(), senha);
      navigate('/', { replace: true });
    } catch (err) {
      setErro(err instanceof Error ? err.message : 'Falha no login');
    } finally {
      setPendente(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-100 via-slate-50 to-teal-50/40 px-4">
      <form onSubmit={onSubmit} className="fin-panel w-full max-w-md space-y-4 p-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">FinFlow</h1>
          <p className="text-sm text-slate-500">Entrar na conta</p>
        </div>
        <div>
          <label className="fin-label" htmlFor="login-email">
            E-mail
          </label>
          <input
            id="login-email"
            className="fin-input"
            type="email"
            autoComplete="username"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="fin-label" htmlFor="login-senha">
            Senha
          </label>
          <input
            id="login-senha"
            className="fin-input"
            type="password"
            autoComplete="current-password"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            required
          />
        </div>
        {erro ? <p className="text-sm text-rose-600">{erro}</p> : null}
        <Botao type="submit" className="w-full" carregando={pendente}>
          Entrar
        </Botao>
        <p className="text-center text-sm text-slate-500">
          Novo por aqui?{' '}
          <Link className="font-semibold text-fin-teal-700 hover:underline" to="/cadastro">
            Cadastro
          </Link>
        </p>
      </form>
    </div>
  );
}
