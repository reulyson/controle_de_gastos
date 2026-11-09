import { formatarMoedaInput, mascararMoedaDigitacao } from '@/compartilhado/formatacao';
import { useEffect, useState } from 'react';

interface CampoMoedaProps {
  id: string;
  label: string;
  valor: number | null;
  onChange: (valor: number | null) => void;
  disabled?: boolean;
  obrigatorio?: boolean;
  placeholder?: string;
}

/**
 * Input monetário BRL com máscara em tempo real (só dígitos → 3.482,29).
 */
export function CampoMoeda({
  id,
  label,
  valor,
  onChange,
  disabled = false,
  obrigatorio = false,
  placeholder = '0,00',
}: CampoMoedaProps) {
  const [texto, setTexto] = useState(() =>
    valor !== null && Number.isFinite(valor) ? formatarMoedaInput(valor) : '',
  );

  useEffect(() => {
    setTexto(valor !== null && Number.isFinite(valor) ? formatarMoedaInput(valor) : '');
  }, [valor]);

  return (
    <div>
      <label className="fin-label" htmlFor={id}>
        {label}
        {obrigatorio ? ' *' : ''}
      </label>
      <input
        id={id}
        className="fin-input tabular-nums"
        inputMode="numeric"
        disabled={disabled}
        required={obrigatorio}
        placeholder={placeholder}
        value={texto}
        onChange={(e) => {
          const { texto: mascarado, valor: n } = mascararMoedaDigitacao(e.target.value);
          setTexto(mascarado);
          onChange(n);
        }}
        onBlur={() => {
          if (valor === null) {
            setTexto('');
            return;
          }
          setTexto(formatarMoedaInput(valor));
        }}
      />
    </div>
  );
}
