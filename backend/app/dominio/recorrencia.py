"""Geração de ocorrências mensais a partir de recorrência."""

from dataclasses import dataclass
from decimal import Decimal

from app.dominio.competencia import Competencia
from app.dominio.dinheiro import decimal_de
from app.dominio.enumeracoes import TipoRecorrencia


@dataclass(frozen=True, slots=True)
class OcorrenciaRecorrente:
    """Uma ocorrência gerada para um lançamento.

    Attributes:
        competencia: Mês/ano da ocorrência.
        valor: Valor da parcela ou repetição.
        indice: Número sequencial (1 para única).
    """

    competencia: Competencia
    valor: Decimal
    indice: int = 1


def gerar_ocorrencias(
    tipo: TipoRecorrencia,
    valor: Decimal,
    competencia_inicio: Competencia,
    quantidade_meses: int | None = None,
) -> list[OcorrenciaRecorrente]:
    """Gera ocorrências únicas ou mensais.

    Args:
        tipo: UNICA ou MENSAL.
        valor: Valor de cada ocorrência.
        competencia_inicio: Primeira competência.
        quantidade_meses: Para MENSAL, quantos meses gerar (padrão 12).

    Returns:
        list[OcorrenciaRecorrente]: Lista de ocorrências geradas.
    """
    valor_q = decimal_de(valor)
    if tipo == TipoRecorrencia.UNICA:
        return [
            OcorrenciaRecorrente(competencia=competencia_inicio, valor=valor_q, indice=1),
        ]

    meses = quantidade_meses if quantidade_meses is not None else 12
    if meses < 1:
        msg = "quantidade_meses deve ser >= 1"
        raise ValueError(msg)

    ocorrencias: list[OcorrenciaRecorrente] = []
    comp = competencia_inicio
    for indice in range(1, meses + 1):
        ocorrencias.append(OcorrenciaRecorrente(competencia=comp, valor=valor_q, indice=indice))
        comp = comp.proxima()
    return ocorrencias
