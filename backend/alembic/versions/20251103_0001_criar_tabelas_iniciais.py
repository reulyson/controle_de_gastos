"""Cria todas as tabelas iniciais do FinFlow.

Revision ID: 20251103_0001
Revises:
Create Date: 2025-11-03

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20251103_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

MONETARIO = sa.Numeric(14, 2)


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "carteiras",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("limite_cheque_especial_total", MONETARIO, nullable=False),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome", "tipo", name="uq_categoria_nome_tipo"),
    )
    op.create_table(
        "contas_financeiras",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("carteira_id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("saldo_inicial", MONETARIO, nullable=False),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.ForeignKeyConstraint(["carteira_id"], ["carteiras.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("carteira_id"),
    )
    op.create_table(
        "receitas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=True),
        sa.Column("descricao", sa.String(length=255), nullable=False),
        sa.Column("valor", MONETARIO, nullable=False),
        sa.Column("recorrencia", sa.String(length=20), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "despesas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=True),
        sa.Column("descricao", sa.String(length=255), nullable=False),
        sa.Column("valor", MONETARIO, nullable=False),
        sa.Column("recorrencia", sa.String(length=20), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cartoes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("carteira_id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("dia_fechamento", sa.Integer(), nullable=False),
        sa.Column("dia_vencimento", sa.Integer(), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["carteira_id"], ["carteiras.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "fechamentos_mensais",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("conta_id", sa.Integer(), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.Column("saldo_inicial", MONETARIO, nullable=False),
        sa.Column("saldo_final", MONETARIO, nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(["conta_id"], ["contas_financeiras.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("conta_id", "ano", "mes", name="uq_fechamento_conta_mes"),
    )
    op.create_table(
        "pagamentos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("conta_id", sa.Integer(), nullable=False),
        sa.Column("descricao", sa.String(length=255), nullable=False),
        sa.Column("valor_total", MONETARIO, nullable=False),
        sa.Column("data_pagamento", sa.Date(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.ForeignKeyConstraint(["conta_id"], ["contas_financeiras.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "receitas_mensais",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("receita_id", sa.Integer(), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.Column("valor", MONETARIO, nullable=False),
        sa.Column("recebido", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["receita_id"], ["receitas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("receita_id", "ano", "mes", name="uq_receita_mensal"),
    )
    op.create_table(
        "despesas_mensais",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("despesa_id", sa.Integer(), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.Column("valor", MONETARIO, nullable=False),
        sa.Column("pago", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["despesa_id"], ["despesas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("despesa_id", "ano", "mes", name="uq_despesa_mensal"),
    )
    op.create_table(
        "compras_cartao",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cartao_id", sa.Integer(), nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=True),
        sa.Column("descricao", sa.String(length=255), nullable=False),
        sa.Column("valor_total", MONETARIO, nullable=False),
        sa.Column("tipo_compra", sa.String(length=20), nullable=False),
        sa.Column("data_compra", sa.Date(), nullable=False),
        sa.Column("parcelas_total", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["cartao_id"], ["cartoes.id"]),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "faturas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cartao_id", sa.Integer(), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.Column("valor_total", MONETARIO, nullable=False),
        sa.Column("paga", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["cartao_id"], ["cartoes.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cartao_id", "ano", "mes", name="uq_fatura_cartao_mes"),
    )
    op.create_table(
        "fechamento_pendencias",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("fechamento_id", sa.Integer(), nullable=False),
        sa.Column("referencia_tipo", sa.String(length=40), nullable=False),
        sa.Column("referencia_id", sa.Integer(), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("valor", MONETARIO, nullable=False),
        sa.ForeignKeyConstraint(["fechamento_id"], ["fechamentos_mensais.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "pagamentos_rateios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pagamento_id", sa.Integer(), nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=True),
        sa.Column("despesa_mensal_id", sa.Integer(), nullable=True),
        sa.Column("valor", MONETARIO, nullable=False),
        sa.Column("descricao", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.id"]),
        sa.ForeignKeyConstraint(["despesa_mensal_id"], ["despesas_mensais.id"]),
        sa.ForeignKeyConstraint(["pagamento_id"], ["pagamentos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "parcelas_cartao",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("compra_id", sa.Integer(), nullable=False),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("valor", MONETARIO, nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["compra_id"], ["compras_cartao.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "pagamentos_fatura",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("fatura_id", sa.Integer(), nullable=False),
        sa.Column("valor", MONETARIO, nullable=False),
        sa.Column("data_pagamento", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["fatura_id"], ["faturas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "fatura_itens",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("fatura_id", sa.Integer(), nullable=False),
        sa.Column("descricao", sa.String(length=255), nullable=False),
        sa.Column("valor", MONETARIO, nullable=False),
        sa.Column("tipo_compra", sa.String(length=20), nullable=False),
        sa.Column("parcela_id", sa.Integer(), nullable=True),
        sa.Column("marcado_pago", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["fatura_id"], ["faturas.id"]),
        sa.ForeignKeyConstraint(["parcela_id"], ["parcelas_cartao.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("fatura_itens")
    op.drop_table("pagamentos_fatura")
    op.drop_table("parcelas_cartao")
    op.drop_table("pagamentos_rateios")
    op.drop_table("fechamento_pendencias")
    op.drop_table("faturas")
    op.drop_table("compras_cartao")
    op.drop_table("despesas_mensais")
    op.drop_table("receitas_mensais")
    op.drop_table("pagamentos")
    op.drop_table("fechamentos_mensais")
    op.drop_table("cartoes")
    op.drop_table("despesas")
    op.drop_table("receitas")
    op.drop_table("contas_financeiras")
    op.drop_table("categorias")
    op.drop_table("carteiras")
    op.drop_table("usuarios")
