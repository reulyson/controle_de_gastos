import { useState, type FormEvent } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '@/compartilhado/contexto/ContextoAuth';
import { Botao } from '@/compartilhado/ui/Botao';

export function PaginaCadastro() {
  const { autenticado, carregando, cadastrar } = useAuth();
  const navigate = useNavigate();
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [confirma, setConfirma] = useState('');
  const [erro, setErro] = useState<string | null>(null);
  const [pendente, setPendente] = useState(false);

  if (!carregando && autenticado) {
    return <Navigate to="/carteiras/nova" replace />;
  }

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErro(null);
    if (senha !== confirma) {
      setErro('As senhas não conferem');
      return;
    }
    if (senha.length < 8) {
      setErro('Senha deve ter no mínimo 8 caracteres');
      return;
    }
    setPendente(true);
    try {
      await cadastrar(nome.trim(), email.trim(), senha);
      navigate('/carteiras/nova', { replace: true });
    } catch (err) {
      setErro(err instanceof Error ? err.message : 'Falha no cadastro');
    } finally {
      setPendente(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-100 via-slate-50 to-teal-50/40 px-4">
      <form onSubmit={onSubmit} className="fin-panel w-full max-w-md space-y-4 p-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Criar conta</h1>
          <p className="text-sm text-slate-500">E-mail e senha (mín. 8 caracteres)</p>
        </div>
        <div>
          <label className="fin-label" htmlFor="cad-nome">
            Nome
          </label>
          <input
            id="cad-nome"
            className="fin-input"
            autoComplete="name"
            value={nome}
            onChange={(e) => setNome(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="fin-label" htmlFor="cad-email">
            E-mail
          </label>
          <input
            id="cad-email"
            className="fin-input"
            type="email"
            autoComplete="username"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="fin-label" htmlFor="cad-senha">
            Senha
          </label>
          <input
            id="cad-senha"
            className="fin-input"
            type="password"
            autoComplete="new-password"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            required
            minLength={8}
            maxLength={128}
          />
        </div>
        <div>
          <label className="fin-label" htmlFor="cad-confirma">
            Confirmar senha
          </label>
          <input
            id="cad-confirma"
            className="fin-input"
            type="password"
            autoComplete="new-password"
            value={confirma}
            onChange={(e) => setConfirma(e.target.value)}
            required
          />
        </div>
        {erro ? <p className="text-sm text-rose-600">{erro}</p> : null}
        <Botao type="submit" className="w-full" carregando={pendente}>
          Cadastrar
        </Botao>
        <p className="text-center text-sm text-slate-500">
          Já tem conta?{' '}
          <Link className="font-semibold text-fin-teal-700 hover:underline" to="/login">
            Entrar
          </Link>
        </p>
      </form>
    </div>
  );
}
