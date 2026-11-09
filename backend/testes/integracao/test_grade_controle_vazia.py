"""Teste de integração da grade de controle vazia."""

from decimal import Decimal


def test_grade_controle_inicial_vazia(cliente, usuario_autenticado):
    cid = usuario_autenticado["carteira_id"]
    headers = usuario_autenticado["headers"]
    resposta = cliente.get(
        f"/api/v1/carteiras/{cid}/anos/2025/grade-controle",
        params={"mes": 6},
        headers=headers,
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


def test_carteira_criada_pelo_usuario(cliente, usuario_autenticado):
    headers = usuario_autenticado["headers"]
    resposta = cliente.get("/api/v1/carteiras", headers=headers)
    assert resposta.status_code == 200
    carteiras = resposta.json()
    assert len(carteiras) == 1
    assert carteiras[0]["padrao"] is True
    assert "limite_cheque" in carteiras[0]
    assert "saldo_inicial" in carteiras[0]
