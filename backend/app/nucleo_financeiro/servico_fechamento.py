"""Fechamento mensal e carry-over de saldo."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dominio.dinheiro import decimal_de
from app.dominio.enumeracoes import StatusFechamento
from app.modulos.modelos import (
    Despesa,
    DespesaMensal,
    FechamentoMensal,
    FechamentoPendencia,
    Receita,
    ReceitaMensal,
)
from app.nucleo_financeiro.servico_calculos import ServicoCalculos


class ServicoFechamento:
    """Fecha competência propagando saldo e registrando pendências."""

    def __init__(self, sessao: Session, carteira_id: int) -> None:
        self._sessao = sessao
        self._carteira_id = carteira_id
        self._calculos = ServicoCalculos(sessao, carteira_id)

    def status_meses(self, conta_id: int, ano: int) -> list[dict]:
        """Lista status aberto/fechado dos 12 meses."""
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

    def fechar_mes(self, ano: int, mes: int) -> FechamentoMensal:
        conta = self._calculos.obter_conta()
        existente = self._sessao.scalar(
            select(FechamentoMensal).where(
                FechamentoMensal.conta_id == conta.id,
                FechamentoMensal.ano == ano,
                FechamentoMensal.mes == mes,
            )
        )
        if existente is not None and existente.status == StatusFechamento.FECHADO:
            raise ValueError("Competência já fechada")

        saldo_inicial = self._calculos.saldo_inicial_competencia(ano, mes)
        totais = self._calculos.totais_competencia(ano, mes)
        saldo_final = decimal_de(totais.saldo_caixa)

        if existente is None:
            fechamento = FechamentoMensal(
                conta_id=conta.id,
                ano=ano,
                mes=mes,
                saldo_inicial=saldo_inicial,
                saldo_final=saldo_final,
                status=StatusFechamento.FECHADO,
            )
            self._sessao.add(fechamento)
        else:
            fechamento = existente
            fechamento.saldo_inicial = saldo_inicial
            fechamento.saldo_final = saldo_final
            fechamento.status = StatusFechamento.FECHADO

        self._sessao.flush()
        self._registrar_pendencias(fechamento, ano, mes)

        prox = self._proxima_competencia(ano, mes)
        self._garantir_fechamento_proximo(conta.id, prox[0], prox[1], saldo_final)

        self._sessao.commit()
        self._sessao.refresh(fechamento)
        return fechamento

    def _registrar_pendencias(self, fechamento: FechamentoMensal, ano: int, mes: int) -> None:
        cid = self._carteira_id
        for despesa in self._sessao.scalars(
            select(DespesaMensal)
            .join(Despesa)
            .where(
                DespesaMensal.ano == ano,
                DespesaMensal.mes == mes,
                DespesaMensal.pago.is_(False),
                Despesa.carteira_id == cid,
            )
        ):
            self._sessao.add(
                FechamentoPendencia(
                    fechamento_id=fechamento.id,
                    referencia_tipo="despesa_mensal",
                    referencia_id=despesa.id,
                    descricao=f"Despesa pendente #{despesa.id}",
                    valor=decimal_de(despesa.valor),
                )
            )
        for receita in self._sessao.scalars(
            select(ReceitaMensal)
            .join(Receita)
            .where(
                ReceitaMensal.ano == ano,
                ReceitaMensal.mes == mes,
                ReceitaMensal.recebido.is_(False),
                Receita.carteira_id == cid,
            )
        ):
            self._sessao.add(
                FechamentoPendencia(
                    fechamento_id=fechamento.id,
                    referencia_tipo="receita_mensal",
                    referencia_id=receita.id,
                    descricao=f"Receita pendente #{receita.id}",
                    valor=decimal_de(receita.valor),
                )
            )

    def _garantir_fechamento_proximo(
        self,
        conta_id: int,
        ano: int,
        mes: int,
        saldo_inicial: Decimal,
    ) -> None:
        proximo = self._sessao.scalar(
            select(FechamentoMensal).where(
                FechamentoMensal.conta_id == conta_id,
                FechamentoMensal.ano == ano,
                FechamentoMensal.mes == mes,
            )
        )
        if proximo is None:
            self._sessao.add(
                FechamentoMensal(
                    conta_id=conta_id,
                    ano=ano,
                    mes=mes,
                    saldo_inicial=decimal_de(saldo_inicial),
                    saldo_final=decimal_de(saldo_inicial),
                    status=StatusFechamento.ABERTO,
                )
            )
        else:
            proximo.saldo_inicial = decimal_de(saldo_inicial)

    def reabrir_mes(self, ano: int, mes: int) -> None:
        conta = self._calculos.obter_conta()
        fechamento = self._sessao.scalar(
            select(FechamentoMensal).where(
                FechamentoMensal.conta_id == conta.id,
                FechamentoMensal.ano == ano,
                FechamentoMensal.mes == mes,
            )
        )
        if fechamento is None or fechamento.status != StatusFechamento.FECHADO:
            raise ValueError("Competência não está fechada")
        fechamento.status = StatusFechamento.ABERTO
        for pend in list(fechamento.pendencias):
            self._sessao.delete(pend)
        self._sessao.commit()

    @staticmethod
    def _proxima_competencia(ano: int, mes: int) -> tuple[int, int]:
        if mes == 12:
            return ano + 1, 1
        return ano, mes + 1
