"""Genera el script DDL de PostgreSQL a partir de los modelos SQLAlchemy.

Produce `schema_postgresql.sql`, pensado para abrirlo y ejecutarlo en DBeaver
cuando se quiere crear el esquema a mano —por ejemplo, para inspeccionar la
estructura o levantar una base de trabajo— sin depender de Alembic.

La fuente de verdad del esquema siguen siendo los modelos y las migraciones:
este archivo es una proyeccion de ellos, no un artefacto que se edite aparte.

    python scripts/generar_ddl.py
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from sqlalchemy import Enum as SAEnum  # noqa: E402
from sqlalchemy.dialects.postgresql.base import PGDialect  # noqa: E402
from sqlalchemy.schema import CreateIndex, CreateTable  # noqa: E402

from app.db.database import Base  # noqa: E402
from app.db import models  # noqa: E402,F401  (registra las tablas en el metadata)

SALIDA = RAIZ / "schema_postgresql.sql"

CABECERA = f"""-- ---------------------------------------------------------------------------
-- Sistema de soporte clinico con aprendizaje automatico para prevenir el
-- incumplimiento terapeutico en hipertensos y diabeticos polimedicados.
-- Consultorio medico Milko Ugaz Zegarra - Chiclayo.
--
-- Esquema relacional del nucleo funcional (RF01-RF03).
-- Generado automaticamente desde los modelos SQLAlchemy el {date.today():%d/%m/%Y}
-- por scripts/generar_ddl.py. NO editar a mano: modificar los modelos y
-- regenerar, o crear una migracion de Alembic.
-- ---------------------------------------------------------------------------

"""


def _tipos_enumerados(dialecto: PGDialect) -> list[str]:
    """PostgreSQL exige declarar los tipos enumerados antes de las tablas."""
    vistos: dict[str, list[str]] = {}
    for tabla in Base.metadata.sorted_tables:
        for columna in tabla.columns:
            if isinstance(columna.type, SAEnum) and columna.type.name:
                vistos.setdefault(columna.type.name, list(columna.type.enums))

    sentencias = []
    for nombre, valores in vistos.items():
        literales = ", ".join(f"'{v}'" for v in valores)
        sentencias.append(f"CREATE TYPE {nombre} AS ENUM ({literales});")
    return sentencias


def generar() -> str:
    dialecto = PGDialect()
    partes: list[str] = [CABECERA]

    partes.append("-- === Tipos enumerados del dominio clinico ===\n")
    partes.extend(f"{s}\n" for s in _tipos_enumerados(dialecto))
    partes.append("\n")

    for tabla in Base.metadata.sorted_tables:
        partes.append(f"-- === Tabla: {tabla.name} ===\n")
        ddl = str(CreateTable(tabla).compile(dialect=dialecto)).strip()
        partes.append(f"{ddl};\n\n")
        for indice in sorted(tabla.indexes, key=lambda i: i.name or ""):
            idx = str(CreateIndex(indice).compile(dialect=dialecto)).strip()
            partes.append(f"{idx};\n")
        partes.append("\n")

    return "".join(partes)


if __name__ == "__main__":
    SALIDA.write_text(generar(), encoding="utf-8")
    print(f"DDL de PostgreSQL escrito en {SALIDA}")
