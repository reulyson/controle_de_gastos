"""Teste de integração da grade de controle vazia."""

from decimal import Decimal


def test_grade_controle_inicial_vazia(cliente):
    carteiras = cliente.get("/api/v1/carteiras").json()
    assert len(carteiras) >= 1
    cid = carteiras[0]["id"]
    resposta = cliente.get(
        f"/api/v1/carteiras/{cid}/anos/2025/grade-controle",
        params={"mes": 6},
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["linhas"] == []
    assert corpo["mes_selecionado"] == 6
    ind = corpo["indicadores"]
    assert Decimal(ind["receitas"]) == Decimal("0.00")
    assert Decimal(ind["despesas"]) == Decimal("0.00")
    assert Decimal(ind["saldo_caixa"]) == Decimal("0.00")
    assert Decimal(ind["cheque_livre"]) == Decimal("0.00")
    assert len(corpo["meses"]) == 12


def test_bootstrap_carteira_e_conta(cliente):
    resposta = cliente.get("/api/v1/carteiras")
    assert resposta.status_code == 200
    carteiras = resposta.json()
    assert len(carteiras) == 1
    assert "limite_cheque" in carteiras[0]
    assert "saldo_inicial" in carteiras[0]
