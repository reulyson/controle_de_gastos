"""Testes de domínio: resumo, cheque e recorrência."""

from decimal import Decimal

import pytest

from app.dominio.cheque import cheque_livre
from app.dominio.competencia import Competencia
from app.dominio.dinheiro import decimal_de
from app.dominio.enumeracoes import TipoRecorrencia
from app.dominio.liquidacao import SaldoInsuficienteError, validar_pagamento_com_cheque
from app.dominio.recorrencia import gerar_ocorrencias
from app.dominio.resumo import consolidar_totais


def test_consolidar_totais_saldo_caixa():
    totais = consolidar_totais(
        receitas=[Decimal("1000.00"), Decimal("200.50")],
        despesas=[Decimal("800.00")],
        pagos=[Decimal("300.00")],
        saldo_inicial=Decimal("100.00"),
    )
    assert totais.total_receita == decimal_de("1200.50")
    assert totais.total_despesa == decimal_de("800.00")
    assert totais.total_orcado == decimal_de("-400.50")
    assert totais.total_pago == decimal_de("300.00")
    assert totais.saldo_caixa == decimal_de("1000.50")


def test_cheque_livre_com_saldo_negativo():
    livre = cheque_livre(Decimal("500.00"), Decimal("-150.00"))
    assert livre == decimal_de("350.00")


def test_validar_pagamento_bloqueia_abaixo_limite():
    with pytest.raises(SaldoInsuficienteError):
        validar_pagamento_com_cheque(
            saldo_atual=Decimal("-400.00"),
            valor_pagamento=Decimal("200.00"),
            limite_cheque_especial=Decimal("500.00"),
        )


def test_gerar_ocorrencias_mensais():
    ocs = gerar_ocorrencias(
        TipoRecorrencia.MENSAL,
        Decimal("100.00"),
        Competencia(2025, 1),
        quantidade_meses=3,
    )
    assert len(ocs) == 3
    assert ocs[0].competencia == Competencia(2025, 1)
    assert ocs[2].competencia == Competencia(2025, 3)
