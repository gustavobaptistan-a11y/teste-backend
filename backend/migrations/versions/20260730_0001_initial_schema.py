"""initial schema

Revision ID: 20260730_0001
Revises:
Create Date: 2026-07-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260730_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("senha_hash", sa.Text(), nullable=False),
        sa.Column("permissao", sa.String(length=50), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "clientes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("telefone", sa.String(length=50), nullable=False),
        sa.Column("empresa", sa.String(length=255), nullable=True),
        sa.Column("origem", sa.String(length=120), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_clientes_nome", "clientes", ["nome"])
    op.create_index("ix_clientes_empresa", "clientes", ["empresa"])

    op.create_table(
        "leads",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("titulo", sa.String(length=255), nullable=False),
        sa.Column("cliente_nome", sa.String(length=255), nullable=False),
        sa.Column("valor", sa.Numeric(12, 2), nullable=False),
        sa.Column("etapa", sa.String(length=80), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
    )
    op.create_index("ix_leads_cliente_nome", "leads", ["cliente_nome"])
    op.create_index("ix_leads_etapa", "leads", ["etapa"])


def downgrade() -> None:
    op.drop_index("ix_leads_etapa", table_name="leads")
    op.drop_index("ix_leads_cliente_nome", table_name="leads")
    op.drop_table("leads")
    op.drop_index("ix_clientes_empresa", table_name="clientes")
    op.drop_index("ix_clientes_nome", table_name="clientes")
    op.drop_table("clientes")
    op.drop_table("usuarios")
