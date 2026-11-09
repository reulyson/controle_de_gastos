"""Geração de linhas mensais a partir de receitas/despesas recorrentes."""

from decimal import Decimal
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dominio.competencia import Competencia
from app.dominio.enumeracoes import TipoRecorrencia
from app.dominio.recorrencia import OcorrenciaRecorrente, gerar_ocorrencias
from app.modulos.modelos import Despesa, DespesaMensal, Receita, ReceitaMensal

TipoLancamento = Literal["receita", "despesa"]


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
        """Gera receitas_mensais para receita cadastrada."""
        return self._gerar_mensais("receita", receita_id, ano_inicio, mes_inicio, meses)

    def gerar_despesas_mensais(
        self,
        despesa_id: int,
        ano_inicio: int,
        mes_inicio: int,
        meses: int | None = None,
    ) -> list[DespesaMensal]:
        """Gera despesas_mensais para despesa cadastrada."""
        return self._gerar_mensais("despesa", despesa_id, ano_inicio, mes_inicio, meses)

    def _obter_lancamento(
        self,
        tipo: TipoLancamento,
        lancamento_id: int,
    ) -> Receita | Despesa:
        if tipo == "receita":
            entidade = self._sessao.get(Receita, lancamento_id)
            rotulo = "Receita"
        else:
            entidade = self._sessao.get(Despesa, lancamento_id)
            rotulo = "Despesa"
        if entidade is None:
            raise ValueError(f"{rotulo} não encontrada")
        return entidade

    def _buscar_mensal_existente(
        self,
        tipo: TipoLancamento,
        lancamento_id: int,
        oc: OcorrenciaRecorrente,
    ) -> ReceitaMensal | DespesaMensal | None:
        if tipo == "receita":
            return self._sessao.scalar(
                select(ReceitaMensal).where(
                    ReceitaMensal.receita_id == lancamento_id,
                    ReceitaMensal.ano == oc.competencia.ano,
                    ReceitaMensal.mes == oc.competencia.mes,
                )
            )
        return self._sessao.scalar(
            select(DespesaMensal).where(
                DespesaMensal.despesa_id == lancamento_id,
                DespesaMensal.ano == oc.competencia.ano,
                DespesaMensal.mes == oc.competencia.mes,
            )
        )

    def _nova_linha_mensal(
        self,
        tipo: TipoLancamento,
        lancamento_id: int,
        oc: OcorrenciaRecorrente,
    ) -> ReceitaMensal | DespesaMensal:
        if tipo == "receita":
            return ReceitaMensal(
                receita_id=lancamento_id,
                ano=oc.competencia.ano,
                mes=oc.competencia.mes,
                valor=oc.valor,
            )
        return DespesaMensal(
            despesa_id=lancamento_id,
            ano=oc.competencia.ano,
            mes=oc.competencia.mes,
            valor=oc.valor,
        )

    def _gerar_mensais(
        self,
        tipo: TipoLancamento,
        lancamento_id: int,
        ano_inicio: int,
        mes_inicio: int,
        meses: int | None,
    ) -> list[ReceitaMensal] | list[DespesaMensal]:
        entidade = self._obter_lancamento(tipo, lancamento_id)
        ocorrencias = gerar_ocorrencias(
            TipoRecorrencia(entidade.recorrencia),
            Decimal(str(entidade.valor)),
            Competencia(ano=ano_inicio, mes=mes_inicio),
            meses,
            valor_variavel=bool(entidade.valor_variavel),
        )
        criadas: list[ReceitaMensal] | list[DespesaMensal] = []
        for oc in ocorrencias:
            existente = self._buscar_mensal_existente(tipo, lancamento_id, oc)
            if existente:
                criadas.append(existente)
                continue
            linha = self._nova_linha_mensal(tipo, lancamento_id, oc)
            self._sessao.add(linha)
            criadas.append(linha)
        self._sessao.commit()
        return criadas
