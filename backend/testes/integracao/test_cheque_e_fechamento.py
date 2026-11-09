"""Testes de bloqueio por cheque e saldo encadeado no fechamento."""

from decimal import Decimal


def _criar_despesa_mensal(cliente, headers, carteira_id, valor: str = "1000.00") -> int:
    desp = cliente.post(
        "/api/v1/despesas",
        headers=headers,
        json={
            "carteira_id": carteira_id,
            "descricao": "Teste cheque",
            "valor": valor,
            "recorrencia": "unica",
            "mes_referencia": 3,
            "ano_referencia": 2025,
        },
    )
    assert desp.status_code == 201, desp.text
    grade = cliente.get(
        f"/api/v1/carteiras/{carteira_id}/anos/2025/grade-controle",
        params={"mes": 3},
        headers=headers,
    ).json()
    linhas = [l for l in grade["linhas"] if l["secao"] == "DESPESAS"]
    assert linhas
    cel = next(c for c in linhas[0]["celulas"] if c["mes"] == 3)
    return int(cel["referencia_id"])


def test_bloqueio_cheque_especial(cliente, usuario_autenticado):
    headers = usuario_autenticado["headers"]
    cid = usuario_autenticado["carteira_id"]
    cliente.patch(
        f"/api/v1/carteiras/{cid}",
        headers=headers,
        json={"limite_cheque": "100.00", "saldo_inicial": "0.00"},
    )
    dm_id = _criar_despesa_mensal(cliente, headers, cid, "500.00")
    resposta = cliente.post(
        "/api/v1/pagamentos",
        headers=headers,
        json={
            "tipo": "despesa",
            "referencia_id": str(dm_id),
            "mes": 3,
            "ano": 2025,
            "pago": True,
        },
    )
    assert resposta.status_code == 422


def test_fechamento_saldo_encadeado(cliente, usuario_autenticado):
    headers = usuario_autenticado["headers"]
    cid = usuario_autenticado["carteira_id"]
    cliente.patch(
        f"/api/v1/carteiras/{cid}",
        headers=headers,
        json={"limite_cheque": "5000.00", "saldo_inicial": "1000.00"},
    )
    cliente.post(
        "/api/v1/receitas",
        headers=headers,
        json={
            "carteira_id": cid,
            "descricao": "Salário",
            "valor": "200.00",
            "recorrencia": "unica",
            "mes_referencia": 1,
            "ano_referencia": 2025,
        },
    )
    grade = cliente.get(
        f"/api/v1/carteiras/{cid}/anos/2025/grade-controle",
        params={"mes": 1},
        headers=headers,
    ).json()
    cel = grade["linhas"][0]["celulas"][0]
    cliente.post(
        "/api/v1/pagamentos",
        headers=headers,
        json={
            "tipo": "receita",
            "referencia_id": cel["referencia_id"],
            "mes": 1,
            "ano": 2025,
            "pago": True,
        },
    )
    fechar = cliente.post(
        f"/api/v1/carteiras/{cid}/fechamentos",
        headers=headers,
        json={"mes": 1, "ano": 2025},
    )
    assert fechar.status_code == 204
    grade_fev = cliente.get(
        f"/api/v1/carteiras/{cid}/anos/2025/grade-controle",
        params={"mes": 2},
        headers=headers,
    ).json()
    saldo_fev = Decimal(grade_fev["indicadores"]["saldo_caixa"])
    assert saldo_fev == Decimal("1200.00")
