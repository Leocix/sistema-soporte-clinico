"""Punto de entrada del API Gateway del sistema de soporte clinico.

Capa de logica / servicios de la arquitectura de microservicios (Fig. 5 del
proyecto de investigacion). Concentra tres responsabilidades transversales:

  1. CORS controlado para el panel medico React + Vite desplegado en Vercel.
  2. Middlewares de seguridad y observabilidad (cabeceras endurecidas, host
     confiable, compresion, identificador de traza por peticion) -> RNF01.
  3. Manejo global de excepciones, de modo que ningun fallo no controlado
     tumbe el servicio ni exponga detalles internos -> RNF01 y RNF04.

Ejecucion local:
    uvicorn app.main:app --reload --port 8000
"""
from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from .api.adherencia import router as adherencia_router
from .api.auth import router as auth_router
from .api.familiares import router as familiares_router
from .api.pacientes import router as pacientes_router
from .api.prediccion import router as prediccion_router
from .core.config import settings
from .core.exceptions import register_exception_handlers
from .db.database import Base, engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("cdss.api")


# ---------------------------------------------------------------------------
# Ciclo de vida
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Prepara y libera los recursos compartidos del proceso."""
    # En local se crea el esquema directamente para agilizar las pruebas del
    # sprint; en desarrollo y produccion el esquema lo gobierna Alembic, que
    # mantiene el historial de migraciones de la base clinica.
    if not settings.es_produccion and settings.database_url.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
        logger.info("esquema_local_verificado motor=sqlite")

    logger.info(
        "api_iniciada version=%s entorno=%s", settings.app_version, settings.environment
    )
    yield
    engine.dispose()
    logger.info("api_detenida conexiones_liberadas=true")


# ---------------------------------------------------------------------------
# Middlewares propios
# ---------------------------------------------------------------------------
class TrazaPeticionMiddleware(BaseHTTPMiddleware):
    """Asigna un identificador y mide la latencia de cada peticion.

    El identificador se propaga al cuerpo de los errores y al log del
    servidor, lo que permite correlacionar un fallo reportado por el medico
    con su traza sin exponer informacion interna al cliente. La latencia
    registrada es la evidencia base de las pruebas de rendimiento (RNF02:
    tiempo de respuesta <= 2 s).
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        inicio = time.perf_counter()
        respuesta = await call_next(request)
        duracion_ms = (time.perf_counter() - inicio) * 1000

        respuesta.headers["X-Request-ID"] = request_id
        respuesta.headers["X-Tiempo-Respuesta-ms"] = f"{duracion_ms:.1f}"
        logger.info(
            "peticion metodo=%s ruta=%s estado=%s ms=%.1f traza=%s",
            request.method,
            request.url.path,
            respuesta.status_code,
            duracion_ms,
            request_id,
        )
        return respuesta


class CabecerasSeguridadMiddleware(BaseHTTPMiddleware):
    """Endurece las cabeceras de toda respuesta (RNF01).

    Evita el rastreo del tipo MIME, el enmarcado del panel clinico en sitios
    de terceros y la fuga de rutas por el encabezado Referer. HSTS solo se
    emite en produccion, donde el trafico viaja siempre sobre TLS.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        respuesta = await call_next(request)
        respuesta.headers.setdefault("X-Content-Type-Options", "nosniff")
        respuesta.headers.setdefault("X-Frame-Options", "DENY")
        respuesta.headers.setdefault("Referrer-Policy", "no-referrer")
        respuesta.headers.setdefault(
            "Permissions-Policy", "geolocation=(), microphone=(), camera=()"
        )
        # El API solo devuelve JSON: se prohibe cualquier recurso incrustado.
        respuesta.headers.setdefault(
            "Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'"
        )
        # Los datos de salud no deben quedar en caches intermedias.
        respuesta.headers.setdefault("Cache-Control", "no-store")
        if settings.es_produccion:
            respuesta.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )
        return respuesta


# ---------------------------------------------------------------------------
# Instancia de la aplicacion
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API del sistema de soporte clinico con aprendizaje automatico para "
        "prevenir el incumplimiento terapeutico en pacientes hipertensos y "
        "diabeticos polimedicados del consultorio medico Milko Ugaz Zegarra. "
        "Expone los servicios de autenticacion (RF01), gestion de pacientes "
        "(RF02), registro de adherencia (RF03) y, desde el Sprint 3, la "
        "inferencia del modelo predictivo con explicabilidad SHAP (RF04, RF06)."
    ),
    lifespan=lifespan,
    # La documentacion interactiva se publica solo fuera de produccion.
    docs_url=None if settings.es_produccion else "/docs",
    redoc_url=None if settings.es_produccion else "/redoc",
    openapi_url=None if settings.es_produccion else "/openapi.json",
)

# El orden importa: el ultimo middleware registrado es el mas externo, por lo
# que CORS se anade al final para que sus cabeceras acompanen tambien a las
# respuestas de error generadas por los manejadores globales.
app.add_middleware(CabecerasSeguridadMiddleware)
app.add_middleware(TrazaPeticionMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1024)

if settings.allowed_hosts_list != ["*"]:
    # Mitiga la inyeccion de encabezado Host en el despliegue gestionado.
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts_list)

app.add_middleware(
    CORSMiddleware,
    # Origenes fijos: entorno local y dominio de produccion del panel medico.
    allow_origins=settings.cors_origins_list,
    # Vercel genera un subdominio por despliegue de vista previa; se autorizan
    # por expresion regular en lugar de enumerarlos uno a uno.
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID", "X-Tiempo-Respuesta-ms"],
    max_age=600,
)

# Manejadores globales de excepciones (RNF04).
register_exception_handlers(app)

# Routers del sistema. Todos comparten el prefijo /api y el mismo contrato de
# errores; las alertas tempranas (RF05) se incorporan en el Sprint 3.
app.include_router(auth_router)
app.include_router(pacientes_router)
app.include_router(adherencia_router)
app.include_router(familiares_router)
app.include_router(prediccion_router)


# ---------------------------------------------------------------------------
# Endpoints de servicio
# ---------------------------------------------------------------------------
@app.get("/", tags=["Servicio"], summary="Identificacion del servicio")
def raiz() -> dict:
    return {
        "servicio": settings.app_name,
        "version": settings.app_version,
        "entorno": settings.environment,
    }


@app.get("/health", tags=["Servicio"], summary="Sonda de disponibilidad")
def health() -> dict:
    """Sonda usada por el balanceador de carga para retirar replicas caidas
    (RNF04: disponibilidad objetivo >= 99 %)."""
    return {"estado": "ok", "version": settings.app_version}
