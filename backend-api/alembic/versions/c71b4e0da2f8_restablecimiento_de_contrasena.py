"""Restablecimiento de la contrasena por correo (RF10).

Crea la tabla ``restablecimientos``, que guarda el resumen SHA-256 del testigo
que viaja en el enlace —nunca el testigo—, su caducidad y el momento en que se
consumio.

Revision ID: c71b4e0da2f8
Revises: a3f1c7d2b915
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "c71b4e0da2f8"
down_revision = "a3f1c7d2b915"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "restablecimientos",
        sa.Column("id_restablecimiento", sa.String(length=36), nullable=False),
        sa.Column("id_usuario", sa.String(length=36), nullable=False),
        # 64 caracteres: el SHA-256 en hexadecimal.
        sa.Column("hash_testigo", sa.String(length=64), nullable=False),
        sa.Column("expira_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("usado_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fecha_solicitud", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id_restablecimiento"),
        sa.ForeignKeyConstraint(
            ["id_usuario"], ["usuarios.id_usuario"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_restablecimientos_id_usuario",
        "restablecimientos",
        ["id_usuario"],
        unique=False,
    )
    # Unico: el testigo identifica un permiso concreto y la busqueda del canje
    # entra siempre por aqui.
    op.create_index(
        "ix_restablecimientos_hash_testigo",
        "restablecimientos",
        ["hash_testigo"],
        unique=True,
    )
    op.create_index(
        "ix_restablecimiento_usuario_uso",
        "restablecimientos",
        ["id_usuario", "usado_en"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_restablecimiento_usuario_uso", table_name="restablecimientos")
    op.drop_index("ix_restablecimientos_hash_testigo", table_name="restablecimientos")
    op.drop_index("ix_restablecimientos_id_usuario", table_name="restablecimientos")
    op.drop_table("restablecimientos")
