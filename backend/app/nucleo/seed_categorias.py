"""Seed idempotente de categorias padrão do sistema."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dominio.enumeracoes import TipoCategoria
from app.modulos.modelos import Categoria

CATEGORIAS_PADRAO: tuple[str, ...] = (
    "Salário",
    "Freelance / Extra",
    "Rendimentos",
    "Moradia",
    "Contas",
    "Alimentação",
    "Transporte",
    "Saúde",
    "Educação",
    "Assinaturas",
    "Pessoal / Lazer",
    "Mercado",
    "Delivery",
    "Compras gerais",
    "Outros",
)


def garantir_categorias_padrao(sessao: Session) -> int:
    """Garante as categorias sistema (usuario_id NULL). Retorna quantas criou."""
    criadas = 0
    existentes = {
        c.nome
        for c in sessao.scalars(
            select(Categoria).where(Categoria.usuario_id.is_(None))
        ).all()
    }
    for nome in CATEGORIAS_PADRAO:
        if nome in existentes:
            continue
        sessao.add(
            Categoria(
                nome=nome,
                tipo=TipoCategoria.AMBOS.value,
                usuario_id=None,
            )
        )
        criadas += 1
        existentes.add(nome)
    return criadas
