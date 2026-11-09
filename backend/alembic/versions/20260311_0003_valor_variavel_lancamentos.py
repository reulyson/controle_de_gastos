"""valor_variavel em receitas e despesas.

Revision ID: 20260311_0003
Revises: 20260311_0002
Create Date: 2026-03-11
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260311_0003"
down_revision = "20260311_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("receitas") as batch:
        batch.add_column(
            sa.Column(
                "valor_variavel",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
    with op.batch_alter_table("despesas") as batch:
        batch.add_column(
            sa.Column(
                "valor_variavel",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("despesas") as batch:
        batch.drop_column("valor_variavel")
    with op.batch_alter_table("receitas") as batch:
        batch.drop_column("valor_variavel")
