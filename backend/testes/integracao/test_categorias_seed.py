"""Seed e API de categorias sistema vs pessoal."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modulos.modelos import Categoria
from app.nucleo.seed_categorias import CATEGORIAS_PADRAO, garantir_categorias_padrao


def test_seed_cria_15_e_nao_duplica(sessao: Session) -> None:
    sistema = sessao.scalars(select(Categoria).where(Categoria.usuario_id.is_(None))).all()
    assert len(sistema) == len(CATEGORIAS_PADRAO)
    assert {c.nome for c in sistema} == set(CATEGORIAS_PADRAO)
    assert garantir_categorias_padrao(sessao) == 0


def test_listar_cria_pessoal_e_protege_sistema(
    cliente: TestClient, usuario_autenticado: dict
) -> None:
    headers = usuario_autenticado["headers"]
    lista = cliente.get("/api/v1/categorias", headers=headers)
    assert lista.status_code == 200
    dados = lista.json()
    assert len(dados) >= len(CATEGORIAS_PADRAO)
    padrao = [c for c in dados if c["origem"] == "padrao"]
    assert {c["nome"] for c in padrao} == set(CATEGORIAS_PADRAO)

    criar = cliente.post(
        "/api/v1/categorias",
        headers=headers,
        json={"nome": "Academia"},
    )
    assert criar.status_code == 201
    assert criar.json()["origem"] == "pessoal"
    pessoal_id = criar.json()["id"]

    lista2 = cliente.get("/api/v1/categorias", headers=headers).json()
    assert any(c["id"] == pessoal_id and c["origem"] == "pessoal" for c in lista2)

    sistema_id = next(c["id"] for c in lista2 if c["origem"] == "padrao")
    bloqueio = cliente.delete(f"/api/v1/categorias/{sistema_id}", headers=headers)
    assert bloqueio.status_code == 403

    ok = cliente.delete(f"/api/v1/categorias/{pessoal_id}", headers=headers)
    assert ok.status_code == 204
