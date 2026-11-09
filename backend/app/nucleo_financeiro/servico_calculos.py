"""Cálculos agregados de receitas, despesas e caixa."""

from calendar import monthrange
from datetime import date
from decimal import Decimal

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.dominio.cheque import cheque_livre
from app.dominio.dinheiro import ZERO, decimal_de, somar
from app.dominio.enumeracoes import StatusFechamento
from app.dominio.resumo import TotaisCompetencia, consolidar_totais
from app.modulos.modelos import (
    Carteira,
    Categoria,
    ContaFinanceira,
    Despesa,
    DespesaMensal,
    FechamentoMensal,
    Pagamento,
    Receita,
    ReceitaMensal,
)


class ServicoCalculos:
    """Consolida totais e indicadores por competência e carteira."""

    def __init__(self, sessao: Session, carteira_id: int | None = None) -> None:
        self._sessao = sessao
        self._carteira_id = carteira_id

    def definir_carteira(self, carteira_id: int) -> None:
        self._carteira_id = carteira_id

    def obter_carteira(self, carteira_id: int | None = None) -> Carteira:
        cid = carteira_id if carteira_id is not None else self._carteira_id
        if cid is None:
            raise RuntimeError("carteira_id não informado")
        carteira = self._sessao.get(Carteira, cid)
        if carteira is None:
            raise RuntimeError("Carteira não encontrada")
        return carteira

    def obter_conta(self, carteira_id: int | None = None) -> ContaFinanceira:
        cid = carteira_id if carteira_id is not None else self._carteira_id
        if cid is None:
            raise RuntimeError("carteira_id não informado")
        conta = self._sessao.scalar(
            select(ContaFinanceira).where(ContaFinanceira.carteira_id == cid)
        )
        if conta is None:
            raise RuntimeError("Conta financeira não encontrada")
        return conta

    def obter_conta_unica(self) -> ContaFinanceira:
        """Compat: usa carteira definida no serviço."""
        return self.obter_conta()

    def saldo_inicial_competencia(self, ano: int, mes: int) -> Decimal:
        conta = self.obter_conta()
        if mes == 1:
            comp_anterior = (ano - 1, 12)
        else:
            comp_anterior = (ano, mes - 1)

        fechamento = self._sessao.scalar(
            select(FechamentoMensal).where(
                FechamentoMensal.conta_id == conta.id,
                FechamentoMensal.ano == comp_anterior[0],
                FechamentoMensal.mes == comp_anterior[1],
            )
        )
        if fechamento is not None:
            return decimal_de(fechamento.saldo_final)
        return decimal_de(conta.saldo_inicial)

    @staticmethod
    def _intervalo_mes(ano: int, mes: int) -> tuple[date, date]:
        ultimo = monthrange(ano, mes)[1]
        return date(ano, mes, 1), date(ano, mes, ultimo)

    def pendencias_meses_fechados(self, ano: int, mes: int) -> Decimal:
        """Despesas não pagas de competências fechadas anteriores à visão."""
        cid = self._carteira_id
        if cid is None:
            raise RuntimeError("carteira_id não informado")
        conta = self.obter_conta()
        valores = self._sessao.scalars(
            select(DespesaMensal.valor)
            .join(Despesa, DespesaMensal.despesa_id == Despesa.id)
            .join(
                FechamentoMensal,
                and_(
                    FechamentoMensal.ano == DespesaMensal.ano,
                    FechamentoMensal.mes == DespesaMensal.mes,
                    FechamentoMensal.conta_id == conta.id,
                ),
            )
            .where(
                Despesa.carteira_id == cid,
                DespesaMensal.pago.is_(False),
                FechamentoMensal.status == StatusFechamento.FECHADO,
                or_(
                    DespesaMensal.ano < ano,
                    and_(DespesaMensal.ano == ano, DespesaMensal.mes < mes),
                ),
            )
        ).all()
        return somar(*(decimal_de(v) for v in valores)) if valores else ZERO

    def totais_competencia(self, ano: int, mes: int) -> TotaisCompetencia:
        saldo_inicial = self.saldo_inicial_competencia(ano, mes)
        cid = self._carteira_id
        if cid is None:
            raise RuntimeError("carteira_id não informado")

        receitas = self._sessao.scalars(
            select(ReceitaMensal.valor)
            .join(Receita)
            .where(
                ReceitaMensal.ano == ano,
                ReceitaMensal.mes == mes,
                Receita.carteira_id == cid,
            )
        ).all()
        despesas = self._sessao.scalars(
            select(DespesaMensal.valor)
            .join(Despesa)
            .where(
                DespesaMensal.ano == ano,
                DespesaMensal.mes == mes,
                Despesa.carteira_id == cid,
            )
        ).all()

        conta = self.obter_conta()
        inicio, fim = self._intervalo_mes(ano, mes)
        pagamentos = self._sessao.scalars(
            select(Pagamento.valor_total).where(
                Pagamento.conta_id == conta.id,
                Pagamento.data_pagamento >= inicio,
                Pagamento.data_pagamento <= fim,
            )
        ).all()

        receitas_recebidas = self._sessao.scalars(
            select(ReceitaMensal.valor)
            .join(Receita)
            .where(
                ReceitaMensal.ano == ano,
                ReceitaMensal.mes == mes,
                ReceitaMensal.recebido.is_(True),
                Receita.carteira_id == cid,
            )
        ).all()

        total_pagamentos = (
            somar(*(decimal_de(v) for v in pagamentos)) if pagamentos else ZERO
        )
        totais = consolidar_totais(
            [decimal_de(v) for v in receitas],
            [decimal_de(v) for v in despesas],
            [decimal_de(v) for v in pagamentos],
            saldo_inicial,
        )
        # Caixa: créditos do mês (recebidos) − pagamentos com data no mês (inclui pendências).
        totais.saldo_caixa = totais.calcular_saldo_caixa(
            saldo_inicial,
            sum((decimal_de(v) for v in receitas_recebidas), ZERO),
            total_pagamentos,
        )
        return totais

    def indicadores(self, ano: int, mes: int) -> dict[str, Decimal]:
        totais = self.totais_competencia(ano, mes)
        carteira = self.obter_carteira()
        return {
            "total_receita": totais.total_receita,
            "total_despesa": totais.total_despesa,
            "total_orcado": totais.total_orcado,
            "total_pago": totais.total_pago,
            "saldo_caixa": totais.saldo_caixa,
            "cheque_livre": cheque_livre(carteira.limite_cheque_especial_total, totais.saldo_caixa),
        }

    def indicadores_mes(self, ano: int, mes: int) -> dict[str, Decimal]:
        totais = self.totais_competencia(ano, mes)
        carteira = self.obter_carteira()
        return {
            "saldo_caixa": totais.saldo_caixa,
            "cheque_livre": cheque_livre(carteira.limite_cheque_especial_total, totais.saldo_caixa),
            "receitas": totais.total_receita,
            "despesas": totais.total_despesa,
            "orcado": totais.total_orcado,
            "total_pago": totais.total_pago,
            "pendencias": self.pendencias_meses_fechados(ano, mes),
        }

    def relatorio_anual(self, ano: int) -> dict:
        meses: list[dict] = []
        for mes in range(1, 13):
            t = self.totais_competencia(ano, mes)
            meses.append(
                {
                    "mes": mes,
                    "receitas": t.total_receita,
                    "despesas": t.total_despesa,
                    "saldo": t.saldo_caixa,
                }
            )
        por_categoria: list[dict] = []
        categorias = {c.id: c for c in self._sessao.scalars(select(Categoria)).all()}
        agregado: dict[tuple[str, str], Decimal] = {}
        cid = self._carteira_id
        for rm in self._sessao.scalars(
            select(ReceitaMensal)
            .join(Receita)
            .where(ReceitaMensal.ano == ano, Receita.carteira_id == cid)
        ).all():
            rec = self._sessao.get(Receita, rm.receita_id)
            cat_id = rec.categoria_id if rec else None
            nome = categorias[cat_id].nome if cat_id and cat_id in categorias else "Sem categoria"
            chave = (nome, "receita")
            agregado[chave] = agregado.get(chave, ZERO) + decimal_de(rm.valor)
        for dm in self._sessao.scalars(
            select(DespesaMensal)
            .join(Despesa)
            .where(DespesaMensal.ano == ano, Despesa.carteira_id == cid)
        ).all():
            desp = self._sessao.get(Despesa, dm.despesa_id)
            cat_id = desp.categoria_id if desp else None
            nome = categorias[cat_id].nome if cat_id and cat_id in categorias else "Sem categoria"
            chave = (nome, "despesa")
            agregado[chave] = agregado.get(chave, ZERO) + decimal_de(dm.valor)
        for (nome, tipo), valor in sorted(agregado.items(), key=lambda x: x[0][0]):
            por_categoria.append({"nome": nome, "valor": valor, "tipo": tipo})
        return {"meses": meses, "por_categoria": por_categoria}
