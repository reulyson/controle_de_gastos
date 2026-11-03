"""Projeção simples de fluxo de caixa por competência."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.dominio.competencia import Competencia
from app.dominio.dinheiro import decimal_de
from app.nucleo_financeiro.servico_calculos import ServicoCalculos


class ServicoFluxoCaixa:
    """Expõe série de saldos projetados."""

    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao
        self._calculos = ServicoCalculos(sessao)

    def projetar_meses(self, ano: int, mes: int, quantidade: int = 3) -> list[dict[str, Decimal | str]]:
        """Projeta saldo de caixa para competências consecutivas.

        Args:
            ano: Competência inicial.
            mes: Mês inicial.
            quantidade: Número de meses.

        Returns:
            list: Dicionários com competencia e saldo_projetado.
        """
        comp = Competencia(ano=ano, mes=mes)
        serie: list[dict[str, Decimal | str]] = []
        saldo = self._calculos.saldo_inicial_competencia(comp.ano, comp.mes)
        for _ in range(quantidade):
            totais = self._calculos.totais_competencia(comp.ano, comp.mes)
            saldo = totais.saldo_caixa
            serie.append({"competencia": comp.chave(), "saldo_projetado": decimal_de(saldo)})
            comp = comp.proxima()
        return serie
