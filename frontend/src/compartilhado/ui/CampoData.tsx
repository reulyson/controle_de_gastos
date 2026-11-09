interface CampoDataProps {
  id: string;
  label: string;
  valor: string;
  onChange: (valor: string) => void;
  obrigatorio?: boolean;
}

export function CampoData({
  id,
  label,
  valor,
  onChange,
  obrigatorio = false,
}: CampoDataProps) {
  return (
    <div>
      <label className="fin-label" htmlFor={id}>
        {label}
        {obrigatorio ? ' *' : ''}
      </label>
      <input
        id={id}
        type="date"
        className="fin-input"
        value={valor}
        required={obrigatorio}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}
