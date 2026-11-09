"""Auth seguro e multi-carteira."""


def test_login_erro_uniforme(cliente):
    cadastro = cliente.post(
        "/api/v1/auth/cadastro",
        json={"email": "a@example.com", "nome": "A", "senha": "senha12345"},
    )
    assert cadastro.status_code == 201
    inexistente = cliente.post(
        "/api/v1/auth/login",
        json={"email": "naoexiste@example.com", "senha": "senha12345"},
    )
    senha_errada = cliente.post(
        "/api/v1/auth/login",
        json={"email": "a@example.com", "senha": "erradaaaaa"},
    )
    assert inexistente.status_code == 401
    assert senha_errada.status_code == 401
    assert inexistente.json()["detail"] == senha_errada.json()["detail"]


def test_senha_fraca_rejeitada(cliente):
    resp = cliente.post(
        "/api/v1/auth/cadastro",
        json={"email": "fraco@example.com", "nome": "F", "senha": "123"},
    )
    assert resp.status_code == 422


def test_carteira_padrao_exclusiva(cliente, usuario_autenticado):
    headers = usuario_autenticado["headers"]
    segunda = cliente.post(
        "/api/v1/carteiras",
        headers=headers,
        json={"nome": "Secundária", "padrao": True},
    )
    assert segunda.status_code == 201
    assert segunda.json()["padrao"] is True
    lista = cliente.get("/api/v1/carteiras", headers=headers).json()
    padroes = [c for c in lista if c["padrao"]]
    assert len(padroes) == 1
    assert padroes[0]["id"] == segunda.json()["id"]


def test_isolamento_entre_usuarios(cliente, usuario_autenticado):
    from app.nucleo.rate_limit import limpar_rate_limits

    headers_a = usuario_autenticado["headers"]
    cid_a = usuario_autenticado["carteira_id"]
    limpar_rate_limits()
    outro = cliente.post(
        "/api/v1/auth/cadastro",
        json={"email": "outro@example.com", "nome": "Outro", "senha": "senha12345"},
    )
    assert outro.status_code == 201, outro.text
    headers_b = {"Authorization": f"Bearer {outro.json()['access_token']}"}
    carteira_b = cliente.post(
        "/api/v1/carteiras",
        headers=headers_b,
        json={"nome": "B"},
    )
    assert carteira_b.status_code == 201
    vazamento = cliente.get(f"/api/v1/carteiras/{cid_a}/anos/2025/grade-controle", headers=headers_b)
    assert vazamento.status_code == 404
    lista_a = cliente.get("/api/v1/carteiras", headers=headers_a).json()
    assert all(c["id"] != carteira_b.json()["id"] for c in lista_a)


def test_cartao_final4_e_ajuste_limite(cliente, usuario_autenticado):
    headers = usuario_autenticado["headers"]
    cid = usuario_autenticado["carteira_id"]
    criar = cliente.post(
        "/api/v1/cartoes",
        headers=headers,
        json={
            "carteira_id": cid,
            "nome": "Visa",
            "bandeira": "Visa",
            "final_4": "4821",
            "limite": "5000.00",
            "dia_fechamento": 1,
            "dia_vencimento": 10,
        },
    )
    assert criar.status_code == 201, criar.text
    cartao = criar.json()
    assert cartao["final_4"] == "4821"
    assert cartao["limite"] == "5000.00"
    patch = cliente.patch(
        f"/api/v1/cartoes/{cartao['id']}",
        headers=headers,
        json={"limite": "7500.00"},
    )
    assert patch.status_code == 200
    assert patch.json()["limite"] == "7500.00"
