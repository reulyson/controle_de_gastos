"""Montagem da grade de controle anual."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.dominio.dinheiro import ZERO, decimal_de, somar
from app.dominio.enumeracoes import StatusFechamento
from app.modulos.modelos import (
    Cartao,
    Despesa,
    DespesaMensal,
    FechamentoMensal,
    Fatura,
    Receita,
    ReceitaMensal,
)
from app.nucleo_financeiro.servico_calculos import ServicoCalculos


class ServicoGrade:
    """Constrói payload da grade de controle para o frontend."""

    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao
        self._calculos = ServicoCalculos(sessao)

    def montar(
        self,
        carteira_id: int,
        ano: int,
        mes_selecionado: int,
    ) -> dict:
        """Monta grade completa com 12 células por linha.

        Args:
            carteira_id: ID da carteira.
            ano: Ano da grade.
            mes_selecionado: Mês em foco nos indicadores.

        Returns:
            dict: Estrutura compatível com GradeControle do frontend.
        """
        conta = self._calculos.obter_conta_unica()
        indicadores = self._calculos.indicadores_mes(ano, mes_selecionado)
        mes_fechado = self._mes_fechado(conta.id, ano, mes_selecionado)
        linhas = (
            self._linhas_receitas(ano)
            + self._linhas_despesas(ano)
            + self._linhas_cartoes(carteira_id, ano)
        )
        totais = self._totais_anuais(ano, mes_selecionado)
        meses = self._status_meses(conta.id, ano)
        return {
            "ano": ano,
            "mes_selecionado": mes_selecionado,
            "mes_fechado": mes_fechado,
            "indicadores": indicadores,
            "linhas": linhas,
            "totais": totais,
            "meses": meses,
            "pendencias_herdadas": [],
        }

    def _mes_fechado(self, conta_id: int, ano: int, mes: int) -> bool:
        fechamento = self._sessao.scalar(
            select(FechamentoMensal).where(
                FechamentoMensal.conta_id == conta_id,
                FechamentoMensal.ano == ano,
                FechamentoMensal.mes == mes,
            )
        )
        return fechamento is not None and fechamento.status == StatusFechamento.FECHADO

    def _status_meses(self, conta_id: int, ano: int) -> list[dict]:
        fechamentos = {
            f.mes: f.status
            for f in self._sessao.scalars(
                select(FechamentoMensal).where(
                    FechamentoMensal.conta_id == conta_id,
                    FechamentoMensal.ano == ano,
                )
            )
        }
        return [
            {
                "mes": m,
                "status": "fechado"
                if fechamentos.get(m) == StatusFechamento.FECHADO
                else "aberto",
            }
            for m in range(1, 13)
        ]

    def _preencher_celulas(
        self,
        linha_id: str,
        tipo: str,
        por_mes: dict[int, tuple[int, Decimal, bool]],
    ) -> list[dict]:
        celulas = []
        total = ZERO
        for m in range(1, 13):
            if m in por_mes:
                ref_id, valor, pago = por_mes[m]
                total = somar(total, valor)
                celulas.append(
                    {
                        "id": str(ref_id),
                        "linha_id": linha_id,
                        "mes": m,
                        "valor": valor,
                        "pago": pago,
                        "tipo": tipo,
                        "referencia_id": str(ref_id),
                    }
                )
            else:
                celulas.append(
                    {
                        "id": f"{linha_id}-{m}",
                        "linha_id": linha_id,
                        "mes": m,
                        "valor": Decimal("0.00"),
                        "pago": False,
                        "tipo": tipo,
                        "referencia_id": None,
                    }
                )
        return celulas, total

    def _linhas_receitas(self, ano: int) -> list[dict]:
        receitas = self._sessao.scalars(
            select(Receita)
            .where(Receita.ativo.is_(True))
            .options(joinedload(Receita.mensais))
        ).unique().all()
        linhas: list[dict] = []
        for receita in receitas:
            linha_id = str(receita.id)
            por_mes: dict[int, tuple[int, Decimal, bool]] = {}
            for rm in receita.mensais:
                if rm.ano == ano:
                    por_mes[rm.mes] = (rm.id, decimal_de(rm.valor), rm.recebido)
            celulas, total = self._preencher_celulas(linha_id, "receita", por_mes)
            linhas.append(
                {
                    "id": linha_id,
                    "secao": "RECEITAS",
                    "rotulo": receita.descricao,
                    "celulas": celulas,
                    "total_anual": total,
                }
            )
        return linhas

    def _linhas_despesas(self, ano: int) -> list[dict]:
        despesas = self._sessao.scalars(
            select(Despesa)
            .where(Despesa.ativo.is_(True))
            .options(joinedload(Despesa.mensais))
        ).unique().all()
        linhas: list[dict] = []
        for despesa in despesas:
            linha_id = str(despesa.id)
            por_mes: dict[int, tuple[int, Decimal, bool]] = {}
            for dm in despesa.mensais:
                if dm.ano == ano:
                    por_mes[dm.mes] = (dm.id, decimal_de(dm.valor), dm.pago)
            celulas, total = self._preencher_celulas(linha_id, "despesa", por_mes)
            linhas.append(
                {
                    "id": linha_id,
                    "secao": "DESPESAS",
                    "rotulo": despesa.descricao,
                    "celulas": celulas,
                    "total_anual": total,
                }
            )
        return linhas

    def _linhas_cartoes(self, carteira_id: int, ano: int) -> list[dict]:
        cartoes = self._sessao.scalars(
            select(Cartao).where(Cartao.carteira_id == carteira_id, Cartao.ativo.is_(True))
        ).all()
        linhas: list[dict] = []
        for cartao in cartoes:
            linha_id = str(cartao.id)
            por_mes: dict[int, tuple[int, Decimal, bool]] = {}
            faturas = self._sessao.scalars(
                select(Fatura).where(Fatura.cartao_id == cartao.id, Fatura.ano == ano)
            ).all()
            for fat in faturas:
                por_mes[fat.mes] = (cartao.id, decimal_de(fat.valor_total), fat.paga)
            celulas, total = self._preencher_celulas(linha_id, "cartao", por_mes)
            for cel in celulas:
                if cel["referencia_id"] is None and cel["valor"] == Decimal("0.00"):
                    cel["referencia_id"] = linha_id
            linhas.append(
                {
                    "id": linha_id,
                    "secao": "CARTOES",
                    "rotulo": cartao.nome,
                    "celulas": celulas,
                    "total_anual": total,
                }
            )
        return linhas

    def _totais_anuais(self, ano: int, mes_caixa: int) -> dict:
        receitas_ano = self._sessao.scalars(
            select(ReceitaMensal.valor).where(ReceitaMensal.ano == ano)
        ).all()
        despesas_ano = self._sessao.scalars(
            select(DespesaMensal.valor).where(DespesaMensal.ano == ano)
        ).all()
        total_receita = somar(*(decimal_de(v) for v in receitas_ano)) if receitas_ano else ZERO
        total_despesa = somar(*(decimal_de(v) for v in despesas_ano)) if despesas_ano else ZERO
        comp = self._calculos.totais_competencia(ano, mes_caixa)
        return {
            "total_receita": total_receita,
            "total_despesa": total_despesa,
            "total_orcado": decimal_de(total_despesa - total_receita),
            "total_pago": comp.total_pago,
            "caixa": comp.saldo_caixa,
        }
