"""Pendências = despesas não pagas de meses fechados anteriores."""

from decimal import Decimal


def test_pendencias_so_apos_fechamento(cliente, usuario_autenticado):
    headers = usuario_autenticado["headers"]
    cid = usuario_autenticado["carteira_id"]
    cliente.patch(
        f"/api/v1/carteiras/{cid}",
        headers=headers,
        json={"limite_cheque": "5000.00", "saldo_inicial": "0.00"},
    )

    criada = cliente.post(
        "/api/v1/despesas",
        headers=headers,
        json={
            "carteira_id": cid,
            "descricao": "Conta atrasada",
            "valor": "200.00",
            "recorrencia": "unica",
            "mes_referencia": 1,
            "ano_referencia": 2025,
        },
    )
    assert criada.status_code == 201, criada.text

    grade_jan = cliente.get(
        f"/api/v1/carteiras/{cid}/anos/2025/grade-controle",
        params={"mes": 1},
        headers=headers,
    ).json()
    assert Decimal(str(grade_jan["indicadores"]["pendencias"])) == Decimal("0.00")

    fechar = cliente.post(
        f"/api/v1/carteiras/{cid}/fechamentos",
        headers=headers,
        json={"mes": 1, "ano": 2025},
    )
    assert fechar.status_code == 204, fechar.text

    grade_fev = cliente.get(
        f"/api/v1/carteiras/{cid}/anos/2025/grade-controle",
        params={"mes": 2},
        headers=headers,
    ).json()
    assert Decimal(str(grade_fev["indicadores"]["pendencias"])) == Decimal("200.00")
    assert "total_pago" in grade_fev["indicadores"]

    grade_jan_fechado = cliente.get(
        f"/api/v1/carteiras/{cid}/anos/2025/grade-controle",
        params={"mes": 1},
        headers=headers,
    ).json()
    # Pendências só de competências anteriores à visão — jan não inclui a si mesma.
    assert Decimal(str(grade_jan_fechado["indicadores"]["pendencias"])) == Decimal("0.00")
