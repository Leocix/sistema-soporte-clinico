"""Lanzador del API en desarrollo.

`app/main.py` no debe ejecutarse como script suelto: al hacerlo, Python lo
carga como modulo de nivel superior, el paquete `app` deja de existir para el
interprete y los imports relativos (`from .api.auth import ...`) fallan con
"attempted relative import with no known parent package".

Este archivo vive en la raiz de `backend-api/`, de modo que al ejecutarlo el
directorio que contiene el paquete `app` queda en el path de importacion y
uvicorn puede resolver la aplicacion por su ruta de modulo.

    python run.py                # equivalente a: uvicorn app.main:app --reload
"""
from __future__ import annotations

import uvicorn

from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        # Cadena y no el objeto: es lo que permite la recarga en caliente.
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=not settings.es_produccion,
        log_level="info",
    )
