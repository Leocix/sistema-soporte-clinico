"""Identidad del paciente: nombres, apellidos, documento, correo y telefono.

La seudonimizacion protege el conjunto de datos que alimenta al modelo, no la
ficha clinica: el medico necesita saber a quien llamar cuando el sistema marca
un riesgo alto. Estos campos viven en la historia clinica y quedan fuera de la
exportacion hacia el pipeline de aprendizaje automatico, que sigue recibiendo
unicamente `codigo_anonimizado`.

`nombres` y `apellidos` son obligatorios, pero la tabla ya tiene filas: anadir
una columna NOT NULL sin valor por defecto fallaria sobre ellas. Se sigue el
recorrido habitual —anadir con valor por defecto, rellenar, retirar el valor
por defecto— para que la migracion se aplique sin detener el servicio y sin
dejar el valor por defecto en el esquema definitivo.

Revision ID: 69aaccd38fe7
Revises: 172087203693
Create Date: 2026-09-05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "69aaccd38fe7"
down_revision: Union[str, Sequence[str], None] = "172087203693"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Marca deliberadamente visible: si aparece en el panel, esa ficha se creo
# antes de que la identidad fuera obligatoria y hay que completarla.
RELLENO = "(por registrar)"


def upgrade() -> None:
    # --- Campos opcionales: se anaden directamente ---
    op.add_column("pacientes", sa.Column("documento_identidad", sa.String(length=20), nullable=True))
    op.add_column("pacientes", sa.Column("correo", sa.String(length=180), nullable=True))
    op.add_column("pacientes", sa.Column("telefono", sa.String(length=25), nullable=True))
    op.create_index("ix_pacientes_documento_identidad", "pacientes", ["documento_identidad"])

    # --- Campos obligatorios: anadir con relleno, luego retirar el relleno ---
    op.add_column(
        "pacientes",
        sa.Column("nombres", sa.String(length=120), nullable=False, server_default=RELLENO),
    )
    op.add_column(
        "pacientes",
        sa.Column("apellidos", sa.String(length=120), nullable=False, server_default=RELLENO),
    )

    # El valor por defecto cumplio su funcion al rellenar las filas existentes;
    # se retira para que toda alta futura tenga que aportar el dato.
    #
    # SQLite no implementa ALTER COLUMN, asi que el cambio va en modo `batch`:
    # Alembic recrea la tabla a partir del esquema reflejado. Las restricciones
    # CHECK del estudio se declaran explicitamente porque la reflexion de
    # SQLite no siempre las recupera, y perderlas dejaria la base sin el
    # criterio de polimedicacion.
    restricciones = [
        sa.CheckConstraint("numero_farmacos >= 5", name="ck_paciente_polimedicado"),
        sa.CheckConstraint("edad >= 18 AND edad <= 120", name="ck_paciente_edad_valida"),
        sa.CheckConstraint(
            "puntaje_morisky IS NULL OR (puntaje_morisky >= 0 AND puntaje_morisky <= 4)",
            name="ck_paciente_morisky_rango",
        ),
        sa.CheckConstraint(
            "controles_perdidos_6m <= controles_programados_6m",
            name="ck_paciente_controles_coherentes",
        ),
    ]
    with op.batch_alter_table("pacientes", table_args=restricciones) as batch:
        batch.alter_column("nombres", server_default=None)
        batch.alter_column("apellidos", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_pacientes_documento_identidad", table_name="pacientes")
    op.drop_column("pacientes", "telefono")
    op.drop_column("pacientes", "correo")
    op.drop_column("pacientes", "documento_identidad")
    op.drop_column("pacientes", "apellidos")
    op.drop_column("pacientes", "nombres")
