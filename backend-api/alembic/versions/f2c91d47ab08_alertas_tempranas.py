"""Alertas tempranas de riesgo para el medico (RF05).

Crea la tabla ``alertas``, con el motivo redactado, el valor que disparo la
regla y el desenlace que registro el medico. No es destructiva.

Revision ID: f2c91d47ab08
Revises: d4e8a1b6c3f7
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "f2c91d47ab08"
down_revision = "d4e8a1b6c3f7"
branch_labels = None
depends_on = None

TIPO = ("riesgo_predicho", "omisiones_seguidas", "adherencia_baja")
ESTADO = ("abierta", "atendida", "descartada", "resuelta")


def _es_postgres() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def _enum(valores: tuple[str, ...], nombre: str):
    if _es_postgres():
        postgresql.ENUM(*valores, name=nombre).create(op.get_bind(), checkfirst=True)
        return postgresql.ENUM(*valores, name=nombre, create_type=False)
    return sa.Enum(*valores, name=nombre)


def upgrade() -> None:
    op.create_table(
        "alertas",
        sa.Column("id_alerta", sa.String(length=36), nullable=False),
        sa.Column("id_paciente", sa.String(length=36), nullable=False),
        sa.Column("tipo", _enum(TIPO, "tipo_alerta"), nullable=False),
        sa.Column("estado", _enum(ESTADO, "estado_alerta"), nullable=False),
        sa.Column("motivo", sa.String(length=300), nullable=False),
        sa.Column("valor", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("fecha_creacion", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_cierre", sa.DateTime(timezone=True), nullable=True),
        sa.Column("nota_cierre", sa.Text(), nullable=True),
        sa.Column("id_medico_cierre", sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint("id_alerta"),
        sa.ForeignKeyConstraint(["id_paciente"], ["pacientes.id_paciente"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["id_medico_cierre"], ["usuarios.id_usuario"], ondelete="SET NULL"),
    )
    op.create_index("ix_alertas_id_paciente", "alertas", ["id_paciente"])
    op.create_index("ix_alerta_paciente_estado", "alertas", ["id_paciente", "estado"])


def downgrade() -> None:
    op.drop_index("ix_alerta_paciente_estado", table_name="alertas")
    op.drop_index("ix_alertas_id_paciente", table_name="alertas")
    op.drop_table("alertas")
    if _es_postgres():
        op.execute("DROP TYPE IF EXISTS tipo_alerta")
        op.execute("DROP TYPE IF EXISTS estado_alerta")
