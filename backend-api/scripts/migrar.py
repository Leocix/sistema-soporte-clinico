"""Aplica las migraciones al arrancar, con reintentos.

El servicio ejecuta `alembic upgrade head` antes de levantar el API. Si en ese
instante la base gestionada no responde —el nombre todavia no resuelve en la
red del proveedor, la base acaba de reiniciarse o hay un corte de segundos— el
despliegue completo falla y el sistema queda caido hasta que alguien lo
reintenta a mano. Eso ocurrio en produccion (incidencia I-22).

Aqui se reintenta con espera creciente antes de rendirse. Si el fallo no es de
conexion —una migracion mal escrita, por ejemplo— no se reintenta: repetir algo
que esta roto solo retrasa el diagnostico.

    python scripts/migrar.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from sqlalchemy.exc import InterfaceError, OperationalError  # noqa: E402

from app.core.config import settings  # noqa: E402

# Cuatro intentos cubren un minuto largo de indisponibilidad, que es el orden
# de magnitud de un reinicio del proveedor gestionado.
ESPERAS = (5, 15, 30)


def _pista(error: Exception) -> str:
    """Traduce el fallo a lo que hay que revisar."""
    texto = str(error).lower()
    if "translate host name" in texto or "name or service not known" in texto:
        return (
            "El nombre del servidor no se pudo resolver. Si se repite, revise en "
            "el panel de la base de datos que el servicio siga activo y que "
            "DATABASE_URL no tenga espacios ni saltos de linea."
        )
    if "password authentication" in texto or "authentication failed" in texto:
        return "Usuario o contrasena incorrectos en DATABASE_URL."
    if "does not exist" in texto:
        return "La base de datos indicada en DATABASE_URL no existe."
    if "timeout" in texto or "timed out" in texto:
        return "La base no respondio a tiempo; puede estar arrancando."
    return "Revise DATABASE_URL y el estado del servicio de base de datos."


def migrar() -> int:
    configuracion = Config(str(RAIZ / "alembic.ini"))
    configuracion.set_main_option("script_location", str(RAIZ / "alembic"))

    destino = settings.database_url.split("@")[-1]  # sin usuario ni contrasena
    for intento, espera in enumerate((*ESPERAS, None), start=1):
        try:
            print(f"Aplicando migraciones (intento {intento}) sobre {destino}", flush=True)
            command.upgrade(configuracion, "head")
            print("Esquema al dia.", flush=True)
            return 0
        except (OperationalError, InterfaceError) as error:
            print(f"No se pudo conectar: {_pista(error)}", file=sys.stderr, flush=True)
            if espera is None:
                print("Se agotaron los intentos de conexion.", file=sys.stderr)
                return 1
            print(f"Nuevo intento en {espera} s...", file=sys.stderr, flush=True)
            time.sleep(espera)
    return 1


if __name__ == "__main__":
    sys.exit(migrar())
