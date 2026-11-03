"""Geração de linhas mensais a partir de receitas/despesas recorrentes."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dominio.competencia import Competencia
from app.dominio.enumeracoes import TipoRecorrencia
from app.dominio.recorrencia import gerar_ocorrencias
from app.modulos.modelos import Despesa, DespesaMensal, Receita, ReceitaMensal


class ServicoRecorrencia:
    """Materializa ocorrências mensais no banco."""

    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def gerar_receitas_mensais(
        self,
        receita_id: int,
        ano_inicio: int,
        mes_inicio: int,
        meses: int | None = None,
    ) -> list[ReceitaMensal]:
        """Gera receitas_mensais para receita cadastrada.

        Args:
            receita_id: ID da receita.
            ano_inicio: Competência inicial.
            mes_inicio: Mês inicial.
            meses: Quantidade de meses (mensal).

        Returns:
            list[ReceitaMensal]: Linhas criadas ou existentes.
        """
        receita = self._sessao.get(Receita, receita_id)
        if receita is None:
            msg = "Receita não encontrada"
            raise ValueError(msg)

        tipo = TipoRecorrencia(receita.recorrencia)
        ocorrencias = gerar_ocorrencias(
            tipo,
            Decimal(str(receita.valor)),
            Competencia(ano=ano_inicio, mes=mes_inicio),
            meses,
        )
        criadas: list[ReceitaMensal] = []
        for oc in ocorrencias:
            existente = self._sessao.scalar(
                select(ReceitaMensal).where(
                    ReceitaMensal.receita_id == receita_id,
                    ReceitaMensal.ano == oc.competencia.ano,
                    ReceitaMensal.mes == oc.competencia.mes,
                )
            )
            if existente:
                criadas.append(existente)
                continue
            linha = ReceitaMensal(
                receita_id=receita_id,
                ano=oc.competencia.ano,
                mes=oc.competencia.mes,
                valor=oc.valor,
            )
            self._sessao.add(linha)
            criadas.append(linha)
        self._sessao.commit()
        return criadas

    def gerar_despesas_mensais(
        self,
        despesa_id: int,
        ano_inicio: int,
        mes_inicio: int,
        meses: int | None = None,
    ) -> list[DespesaMensal]:
        """Gera despesas_mensais para despesa cadastrada.

        Args:
            despesa_id: ID da despesa.
            ano_inicio: Competência inicial.
            mes_inicio: Mês inicial.
            meses: Quantidade de meses.

        Returns:
            list[DespesaMensal]: Linhas criadas ou existentes.
        """
        despesa = self._sessao.get(Despesa, despesa_id)
        if despesa is None:
            msg = "Despesa não encontrada"
            raise ValueError(msg)

        tipo = TipoRecorrencia(despesa.recorrencia)
        ocorrencias = gerar_ocorrencias(
            tipo,
            Decimal(str(despesa.valor)),
            Competencia(ano=ano_inicio, mes=mes_inicio),
            meses,
        )
        criadas: list[DespesaMensal] = []
        for oc in ocorrencias:
            existente = self._sessao.scalar(
                select(DespesaMensal).where(
                    DespesaMensal.despesa_id == despesa_id,
                    DespesaMensal.ano == oc.competencia.ano,
                    DespesaMensal.mes == oc.competencia.mes,
                )
            )
            if existente:
                criadas.append(existente)
                continue
            linha = DespesaMensal(
                despesa_id=despesa_id,
                ano=oc.competencia.ano,
                mes=oc.competencia.mes,
                valor=oc.valor,
            )
            self._sessao.add(linha)
            criadas.append(linha)
        self._sessao.commit()
        return criadas
