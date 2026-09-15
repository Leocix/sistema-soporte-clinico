"""Variables de la ficha ajustadas a una clinica privada.

  * Sustituye nivel socioeconomico, aseguramiento y zona de residencia —que en
    una clinica privada apenas varian entre pacientes— por nivel educativo,
    convivencia y apoyo familiar en la toma.
  * Anade la lista de comorbilidades concretas. La columna ``comorbilidades``
    se conserva como total, que es la variable que usa el modelo.

Es destructiva para las tres columnas retiradas: sus valores no tienen
equivalente en las nuevas variables.

Revision ID: d4e8a1b6c3f7
Revises: c71b4e0da2f8
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "d4e8a1b6c3f7"
down_revision = "c71b4e0da2f8"
branch_labels = None
depends_on = None

NIVEL_EDUCATIVO = ("sin_estudios", "primaria", "secundaria", "superior")
CONVIVENCIA = ("solo", "acompanado")


def _es_postgres() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def _enum(valores: tuple[str, ...], nombre: str):
    """En PostgreSQL el tipo se crea aparte, una sola vez, y la columna solo lo
    referencia; en SQLite el enumerado es texto con restriccion."""
    if _es_postgres():
        tipo = postgresql.ENUM(*valores, name=nombre, create_type=False)
        postgresql.ENUM(*valores, name=nombre).create(op.get_bind(), checkfirst=True)
        return tipo
    return sa.Enum(*valores, name=nombre)


def upgrade() -> None:
    nivel = _enum(NIVEL_EDUCATIVO, "nivel_educativo")
    convivencia = _enum(CONVIVENCIA, "convivencia")

    with op.batch_alter_table("pacientes") as tabla:
        tabla.add_column(sa.Column("nivel_educativo", nivel, nullable=True))
        tabla.add_column(sa.Column("convivencia", convivencia, nullable=True))
        tabla.add_column(sa.Column("apoyo_familiar", sa.Boolean(), nullable=True))
        tabla.add_column(sa.Column(
            "lista_comorbilidades", sa.JSON(), nullable=False, server_default="[]"
        ))
        tabla.drop_column("nivel_socioeconomico")
        tabla.drop_column("aseguramiento")
        tabla.drop_column("zona_residencia")

    if _es_postgres():
        for tipo in ("nivel_socioeconomico", "aseguramiento_salud", "zona_residencia"):
            op.execute(f"DROP TYPE IF EXISTS {tipo}")


def downgrade() -> None:
    nse = _enum(("bajo", "medio", "alto"), "nivel_socioeconomico")
    aseg = _enum(("sis", "essalud", "ninguno"), "aseguramiento_salud")
    zona = _enum(("urbana", "rural"), "zona_residencia")

    with op.batch_alter_table("pacientes") as tabla:
        tabla.add_column(sa.Column("nivel_socioeconomico", nse, nullable=True))
        tabla.add_column(sa.Column("aseguramiento", aseg, nullable=True))
        tabla.add_column(sa.Column("zona_residencia", zona, nullable=True))
        tabla.drop_column("lista_comorbilidades")
        tabla.drop_column("apoyo_familiar")
        tabla.drop_column("convivencia")
        tabla.drop_column("nivel_educativo")

    if _es_postgres():
        op.execute("DROP TYPE IF EXISTS nivel_educativo")
        op.execute("DROP TYPE IF EXISTS convivencia")
