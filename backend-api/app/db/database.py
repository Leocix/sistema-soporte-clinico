"""Capa de acceso a datos: motor, sesion y base declarativa.

Capa de datos de la arquitectura (Fig. 5): PostgreSQL gestionado con
conexion cifrada en transito (sslmode=require) y respaldos cifrados
AES-256 (RNF01). En entorno local se admite SQLite para poder ejecutar las
pruebas del sprint sin infraestructura externa.
"""
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from ..core.config import settings


class Base(DeclarativeBase):
    """Base declarativa comun a todos los modelos del dominio clinico."""


_es_sqlite = settings.database_url.startswith("sqlite")

engine = create_engine(
    settings.database_url,
    # SQLite (solo local) necesita desactivar la comprobacion de hilo.
    connect_args={"check_same_thread": False} if _es_sqlite else {},
    # pool_pre_ping evita servir conexiones caidas tras una desconexion del
    # proveedor gestionado; contribuye a la disponibilidad objetivo (RNF04).
    pool_pre_ping=True,
    **(
        {}
        if _es_sqlite
        else {
            "pool_size": settings.db_pool_size,
            "max_overflow": settings.db_max_overflow,
            "pool_recycle": settings.db_pool_recycle_seconds,
        }
    ),
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    """Dependencia de FastAPI: entrega una sesion y garantiza su cierre."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
