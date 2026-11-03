"""Cálculos agregados de receitas, despesas e caixa."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dominio.cheque import cheque_livre
from app.dominio.dinheiro import ZERO, decimal_de, somar
from app.dominio.resumo import TotaisCompetencia, consolidar_totais
from app.modulos.modelos import (
    Carteira,
    Categoria,
    ContaFinanceira,
    Despesa,
    DespesaMensal,
    Pagamento,
    Receita,
    ReceitaMensal,
)


class ServicoCalculos:
    """Consolida totais e indicadores por competência."""

    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def obter_conta_unica(self) -> ContaFinanceira:
        """Retorna a conta de caixa (bootstrap garante uma).

        Returns:
            ContaFinanceira: Conta principal.

        Raises:
            RuntimeError: Se não houver conta.
        """
        conta = self._sessao.scalar(select(ContaFinanceira).limit(1))
        if conta is None:
            msg = "Conta financeira não encontrada"
            raise RuntimeError(msg)
        return conta

    def obter_carteira(self) -> Carteira:
        """Retorna carteira principal.

        Returns:
            Carteira: Primeira carteira cadastrada.
        """
        carteira = self._sessao.scalar(select(Carteira).limit(1))
        if carteira is None:
            msg = "Carteira não encontrada"
            raise RuntimeError(msg)
        return carteira

    def saldo_inicial_competencia(self, ano: int, mes: int) -> Decimal:
        """Saldo inicial do mês (fechamento anterior ou saldo_inicial da conta).

        Args:
            ano: Ano de referência.
            mes: Mês de referência.

        Returns:
            Decimal: Saldo de abertura.
        """
        from app.modulos.modelos import FechamentoMensal

        conta = self.obter_conta_unica()
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

    def totais_competencia(self, ano: int, mes: int) -> TotaisCompetencia:
        """Calcula totais de receita, despesa, pago e caixa.

        Args:
            ano: Ano.
            mes: Mês.

        Returns:
            TotaisCompetencia: Agregados do período.
        """
        saldo_inicial = self.saldo_inicial_competencia(ano, mes)

        receitas = self._sessao.scalars(
            select(ReceitaMensal.valor).where(ReceitaMensal.ano == ano, ReceitaMensal.mes == mes)
        ).all()
        despesas = self._sessao.scalars(
            select(DespesaMensal.valor).where(DespesaMensal.ano == ano, DespesaMensal.mes == mes)
        ).all()

        conta = self.obter_conta_unica()
        pagamentos = self._sessao.scalars(
            select(Pagamento.valor_total).where(
                Pagamento.conta_id == conta.id,
                Pagamento.data_pagamento >= f"{ano:04d}-{mes:02d}-01",
            )
        ).all()

        receitas_recebidas = self._sessao.scalars(
            select(ReceitaMensal.valor).where(
                ReceitaMensal.ano == ano,
                ReceitaMensal.mes == mes,
                ReceitaMensal.recebido.is_(True),
            )
        ).all()
        despesas_pagas = self._sessao.scalars(
            select(DespesaMensal.valor).where(
                DespesaMensal.ano == ano,
                DespesaMensal.mes == mes,
                DespesaMensal.pago.is_(True),
            )
        ).all()

        totais = consolidar_totais(
            [decimal_de(v) for v in receitas],
            [decimal_de(v) for v in despesas],
            [decimal_de(v) for v in pagamentos],
            saldo_inicial,
        )
        totais.saldo_caixa = totais.calcular_saldo_caixa(
            saldo_inicial,
            sum((decimal_de(v) for v in receitas_recebidas), ZERO),
            sum((decimal_de(v) for v in despesas_pagas), ZERO),
        )
        return totais

    def indicadores(self, ano: int, mes: int) -> dict[str, Decimal]:
        """Indicadores auxiliares para grade de controle (legado).

        Args:
            ano: Ano.
            mes: Mês.

        Returns:
            dict: cheque_livre, saldo_caixa, total_orcado, etc.
        """
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
        """Indicadores no formato esperado pelo frontend.

        Args:
            ano: Ano.
            mes: Mês.

        Returns:
            dict: saldo_caixa, cheque_livre, receitas, despesas, orcado, pendencias.
        """
        totais = self.totais_competencia(ano, mes)
        carteira = self.obter_carteira()
        pend_rec = self._sessao.scalars(
            select(ReceitaMensal.valor).where(
                ReceitaMensal.ano == ano,
                ReceitaMensal.mes == mes,
                ReceitaMensal.recebido.is_(False),
            )
        ).all()
        pend_desp = self._sessao.scalars(
            select(DespesaMensal.valor).where(
                DespesaMensal.ano == ano,
                DespesaMensal.mes == mes,
                DespesaMensal.pago.is_(False),
            )
        ).all()
        pendencias = somar(
            *(decimal_de(v) for v in pend_rec),
            *(decimal_de(v) for v in pend_desp),
        )
        return {
            "saldo_caixa": totais.saldo_caixa,
            "cheque_livre": cheque_livre(carteira.limite_cheque_especial_total, totais.saldo_caixa),
            "receitas": totais.total_receita,
            "despesas": totais.total_despesa,
            "orcado": totais.total_orcado,
            "pendencias": pendencias,
        }

    def relatorio_anual(self, ano: int) -> dict:
        """Resumo mensal e por categoria para relatório.

        Args:
            ano: Ano de referência.

        Returns:
            dict: meses e por_categoria.
        """
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
        for rm in self._sessao.scalars(
            select(ReceitaMensal).where(ReceitaMensal.ano == ano)
        ).all():
            rec = self._sessao.get(Receita, rm.receita_id)
            cat_id = rec.categoria_id if rec else None
            nome = categorias[cat_id].nome if cat_id and cat_id in categorias else "Sem categoria"
            chave = (nome, "receita")
            agregado[chave] = agregado.get(chave, ZERO) + decimal_de(rm.valor)
        for dm in self._sessao.scalars(
            select(DespesaMensal).where(DespesaMensal.ano == ano)
        ).all():
            desp = self._sessao.get(Despesa, dm.despesa_id)
            cat_id = desp.categoria_id if desp else None
            nome = categorias[cat_id].nome if cat_id and cat_id in categorias else "Sem categoria"
            chave = (nome, "despesa")
            agregado[chave] = agregado.get(chave, ZERO) + decimal_de(dm.valor)
        for (nome, tipo), valor in sorted(agregado.items(), key=lambda x: x[0][0]):
            por_categoria.append({"nome": nome, "valor": valor, "tipo": tipo})
        return {"meses": meses, "por_categoria": por_categoria}
