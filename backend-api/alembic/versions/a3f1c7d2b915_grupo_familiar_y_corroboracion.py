"""Grupo familiar de acompanamiento y corroboracion de la toma (RF09).

Anade:

  * el perfil ``familiar`` al catalogo de roles;
  * la tabla ``acompanantes``, que modela invitacion y pertenencia como dos
    momentos de la misma fila;
  * dos columnas en ``registros_adherencia`` para el testimonio del
    acompanante sobre una toma ya reportada por el paciente.

Ninguna es destructiva: las tomas existentes quedan con ``id_confirmante``
nulo, que es exactamente lo que son —eventos con una sola fuente— y asi
seguiran figurando en el analisis.

Revision ID: a3f1c7d2b915
Revises: 69aaccd38fe7
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "a3f1c7d2b915"
down_revision = "69aaccd38fe7"
branch_labels = None
depends_on = None


PARENTESCO = ("conyuge", "hijo", "hermano", "cuidador", "otro")
ESTADO_ACOMPANANTE = ("invitado", "activo", "revocado")


def _es_postgres() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def upgrade() -> None:
    # --- 1. El rol nuevo -----------------------------------------------
    # En PostgreSQL el rol es un tipo enumerado nativo y hay que ampliarlo
    # antes de que ninguna fila lo use. Desde PostgreSQL 12 ADD VALUE puede
    # ejecutarse dentro de la transaccion de la migracion siempre que el valor
    # no se utilice en esa misma transaccion, que es el caso: aqui solo se
    # declara. SQLite guarda el enumerado como texto y no necesita nada.
    if _es_postgres():
        op.execute("ALTER TYPE rol_usuario ADD VALUE IF NOT EXISTS 'familiar'")

    parentesco = sa.Enum(*PARENTESCO, name="parentesco_acompanante")
    estado = sa.Enum(*ESTADO_ACOMPANANTE, name="estado_acompanante")

    # --- 2. La tabla del grupo familiar ---------------------------------
    op.create_table(
        "acompanantes",
        sa.Column("id_acompanante", sa.String(length=36), nullable=False),
        sa.Column("id_paciente", sa.String(length=36), nullable=False),
        # Nulo mientras la invitacion no se canjea: la fila existe antes que la
        # cuenta del familiar.
        sa.Column("id_usuario", sa.String(length=36), nullable=True),
        sa.Column("nombre_invitado", sa.String(length=120), nullable=False),
        sa.Column("parentesco", parentesco, nullable=False),
        sa.Column("estado", estado, nullable=False),
        sa.Column("codigo_invitacion", sa.String(length=12), nullable=False),
        sa.Column("expira_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_invitacion", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_vinculacion", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id_acompanante"),
        sa.ForeignKeyConstraint(
            ["id_paciente"], ["pacientes.id_paciente"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["id_usuario"], ["usuarios.id_usuario"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint(
            "id_paciente", "id_usuario", name="uq_acompanante_paciente_usuario"
        ),
        sa.CheckConstraint(
            "(estado = 'invitado' AND id_usuario IS NULL) "
            "OR (estado <> 'invitado' AND id_usuario IS NOT NULL)",
            name="ck_acompanante_vinculo_coherente",
        ),
    )
    op.create_index(
        "ix_acompanantes_id_paciente", "acompanantes", ["id_paciente"], unique=False
    )
    op.create_index(
        "ix_acompanantes_codigo_invitacion",
        "acompanantes",
        ["codigo_invitacion"],
        unique=True,
    )
    op.create_index(
        "ix_acompanante_paciente_estado",
        "acompanantes",
        ["id_paciente", "estado"],
        unique=False,
    )

    # --- 3. La corroboracion sobre el evento de toma ---------------------
    # Se declara la clave ajena junto a la columna: en SQLite el modo por lotes
    # rehace la tabla y la arrastra consigo, mientras que un create_foreign_key
    # suelto no tendria efecto sobre ese motor.
    with op.batch_alter_table("registros_adherencia") as lote:
        lote.add_column(
            sa.Column("id_confirmante", sa.String(length=36), nullable=True)
        )
        lote.add_column(
            sa.Column("fecha_confirmacion", sa.DateTime(timezone=True), nullable=True)
        )
        lote.create_foreign_key(
            "fk_registro_confirmante",
            "usuarios",
            ["id_confirmante"],
            ["id_usuario"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("registros_adherencia") as lote:
        lote.drop_constraint("fk_registro_confirmante", type_="foreignkey")
        lote.drop_column("fecha_confirmacion")
        lote.drop_column("id_confirmante")

    op.drop_index("ix_acompanante_paciente_estado", table_name="acompanantes")
    op.drop_index("ix_acompanantes_codigo_invitacion", table_name="acompanantes")
    op.drop_index("ix_acompanantes_id_paciente", table_name="acompanantes")
    op.drop_table("acompanantes")

    if _es_postgres():
        sa.Enum(name="estado_acompanante").drop(op.get_bind(), checkfirst=True)
        sa.Enum(name="parentesco_acompanante").drop(op.get_bind(), checkfirst=True)

    # El valor 'familiar' del enumerado de roles no se retira: PostgreSQL no
    # admite quitar un valor de un tipo enumerado sin recrearlo, y dejarlo
    # declarado es inocuo mientras ninguna fila lo use.
