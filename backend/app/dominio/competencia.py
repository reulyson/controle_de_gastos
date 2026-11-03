"""Representação e validação de competência (ano/mês)."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Competencia:
    """Par ano/mês de referência financeira.

    Attributes:
        ano: Ano calendário (>= 2000).
        mes: Mês entre 1 e 12.
    """

    ano: int
    mes: int

    def __post_init__(self) -> None:
        if self.ano < 2000:
            msg = "Ano inválido"
            raise ValueError(msg)
        if not 1 <= self.mes <= 12:
            msg = "Mês deve estar entre 1 e 12"
            raise ValueError(msg)

    def proxima(self) -> "Competencia":
        """Retorna a competência imediatamente seguinte.

        Returns:
            Competencia: Mês seguinte ou janeiro do ano seguinte.
        """
        if self.mes == 12:
            return Competencia(ano=self.ano + 1, mes=1)
        return Competencia(ano=self.ano, mes=self.mes + 1)

    def chave(self) -> str:
        """Identificador estável YYYY-MM.

        Returns:
            str: Chave de competência.
        """
        return f"{self.ano:04d}-{self.mes:02d}"
