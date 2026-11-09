"""Categorias por usuario + tipo_carteira.

Revision ID: 20260311_0002
Revises: 20251103_0001
Create Date: 2026-03-11
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260311_0002"
down_revision = "20251103_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("carteiras") as batch:
        batch.add_column(
            sa.Column(
                "tipo_carteira",
                sa.String(length=20),
                nullable=False,
                server_default="pessoal",
            )
        )

    with op.batch_alter_table("categorias") as batch:
        batch.add_column(sa.Column("usuario_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_categorias_usuario_id",
            "usuarios",
            ["usuario_id"],
            ["id"],
        )
        batch.drop_constraint("uq_categoria_nome_tipo", type_="unique")
        batch.create_unique_constraint(
            "uq_categoria_nome_usuario",
            ["nome", "usuario_id"],
        )
        batch.create_index("ix_categorias_usuario_id", ["usuario_id"])


def downgrade() -> None:
    with op.batch_alter_table("categorias") as batch:
        batch.drop_index("ix_categorias_usuario_id")
        batch.drop_constraint("uq_categoria_nome_usuario", type_="unique")
        batch.create_unique_constraint("uq_categoria_nome_tipo", ["nome", "tipo"])
        batch.drop_constraint("fk_categorias_usuario_id", type_="foreignkey")
        batch.drop_column("usuario_id")

    with op.batch_alter_table("carteiras") as batch:
        batch.drop_column("tipo_carteira")
