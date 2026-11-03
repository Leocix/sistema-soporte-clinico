"""Manejo global y controlado de errores del API Gateway.

Sustenta RNF04 (fiabilidad: disponibilidad >= 99 %) y RNF01 (seguridad):
ninguna excepcion no controlada debe propagarse al cliente ni exponer la
traza interna, la consulta SQL o la estructura de la base de datos clinica.
Todas las respuestas de error comparten un unico contrato (`ErrorEnvelope`),
lo que permite al panel medico React y a la app Flutter tratar los fallos de
forma homogenea.
"""
from __future__ import annotations

import logging
import uuid

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("cdss.api")


# ---------------------------------------------------------------------------
# Contrato unico de error
# ---------------------------------------------------------------------------
class ErrorEnvelope(BaseModel):
    """Cuerpo estandar de toda respuesta de error del API."""

    exito: bool = False
    codigo: str = Field(..., description="Codigo estable, legible por maquina")
    mensaje: str = Field(..., description="Mensaje apto para mostrar al usuario")
    detalles: list[dict] | None = Field(
        default=None, description="Errores de validacion campo por campo"
    )
    id_traza: str = Field(..., description="Identificador para correlacionar logs")


# ---------------------------------------------------------------------------
# Mensajes de validacion en castellano
# ---------------------------------------------------------------------------
def motivo_en_castellano(err: dict) -> str:
    """Traduce el motivo de un error de Pydantic al castellano.

    Pydantic redacta en ingles («Input should be greater than or equal to
    18»). Las pruebas de caja negra mostraron que esos textos llegaban tal cual
    al usuario cuando un dato se rechazaba en el servidor. Los mensajes que
    escriben nuestros propios validadores ya estan en castellano y se respetan.
    """
    tipo = err.get("type", "")
    ctx = dict(err.get("ctx") or {})
    if "expected" in ctx:
        ctx["expected"] = str(ctx["expected"]).replace(" or ", " o ")
    plantillas = {
        "missing": "Campo obligatorio.",
        "greater_than_equal": "Debe ser mayor o igual a {ge}.",
        "greater_than": "Debe ser mayor que {gt}.",
        "less_than_equal": "Debe ser menor o igual a {le}.",
        "less_than": "Debe ser menor que {lt}.",
        "string_too_short": "Debe tener al menos {min_length} caracteres.",
        "string_too_long": "Debe tener como máximo {max_length} caracteres.",
        "too_long": "Admite como máximo {max_length} elementos.",
        "string_pattern_mismatch": "El formato no es válido.",
        "int_parsing": "Debe ser un número entero.",
        "int_from_float": "Debe ser un número entero.",
        "float_parsing": "Debe ser un número.",
        "bool_parsing": "Debe ser sí o no.",
        "datetime_parsing": "La fecha u hora no es válida.",
        "datetime_from_date_parsing": "La fecha u hora no es válida.",
        "date_parsing": "La fecha no es válida.",
        "enum": "Valor no permitido. Use: {expected}.",
        "literal_error": "Valor no permitido. Use: {expected}.",
        "extra_forbidden": "Campo no permitido.",
        "string_type": "Debe ser un texto.",
        "list_type": "Debe ser una lista.",
    }
    if tipo in plantillas:
        try:
            return plantillas[tipo].format(**ctx)
        except (KeyError, IndexError):
            return plantillas[tipo].split(" {")[0].rstrip(":.") + "."
    mensaje = err.get("msg", "").removeprefix("Value error, ")
    if "email address" in mensaje:
        return "El correo electrónico no es válido."
    return mensaje


# ---------------------------------------------------------------------------
# Excepciones de dominio
# ---------------------------------------------------------------------------
class AppError(Exception):
    """Error de negocio previsto. Se traduce a una respuesta HTTP controlada."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    codigo: str = "ERROR_APLICACION"
    mensaje: str = "No fue posible completar la operación."

    def __init__(
        self,
        mensaje: str | None = None,
        *,
        codigo: str | None = None,
        status_code: int | None = None,
        detalles: list[dict] | None = None,
    ) -> None:
        self.mensaje = mensaje or self.mensaje
        self.codigo = codigo or self.codigo
        self.status_code = status_code or self.status_code
        self.detalles = detalles
        super().__init__(self.mensaje)


class NoAutenticadoError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    codigo = "NO_AUTENTICADO"
    mensaje = "Credenciales ausentes, inválidas o expiradas."


class PermisoDenegadoError(AppError):
    """RBAC: el usuario esta autenticado pero su rol no habilita el recurso."""

    status_code = status.HTTP_403_FORBIDDEN
    codigo = "PERMISO_DENEGADO"
    mensaje = "Su perfil no tiene permisos para acceder a este recurso."


class RecursoNoEncontradoError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    codigo = "RECURSO_NO_ENCONTRADO"
    mensaje = "El recurso solicitado no existe."


class ConflictoError(AppError):
    status_code = status.HTTP_409_CONFLICT
    codigo = "CONFLICTO"
    mensaje = "El recurso ya existe o viola una restriccion de integridad."


class ModeloNoDisponibleError(AppError):
    """El microservicio de inferencia (RF04) no pudo atender la peticion.

    Se responde 503 en lugar de 500 para que el panel clinico degrade la
    vista de riesgo sin bloquear el resto de la auditoria de adherencia.
    """

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    codigo = "MODELO_NO_DISPONIBLE"
    mensaje = "El servicio de predicción de riesgo no está disponible."


# ---------------------------------------------------------------------------
# Registro de manejadores
# ---------------------------------------------------------------------------
def _id_traza(request: Request) -> str:
    return getattr(request.state, "request_id", None) or str(uuid.uuid4())


def _responder(request: Request, status_code: int, codigo: str, mensaje: str,
               detalles: list[dict] | None = None) -> JSONResponse:
    traza = _id_traza(request)
    cuerpo = ErrorEnvelope(
        codigo=codigo, mensaje=mensaje, detalles=detalles, id_traza=traza
    )
    return JSONResponse(
        status_code=status_code,
        content=cuerpo.model_dump(),
        headers={"X-Request-ID": traza},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Engancha los manejadores globales a la instancia de FastAPI."""

    @app.exception_handler(AppError)
    async def _app_error(request: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "error_negocio codigo=%s ruta=%s traza=%s",
            exc.codigo, request.url.path, _id_traza(request),
        )
        return _responder(request, exc.status_code, exc.codigo, exc.mensaje, exc.detalles)

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _responder(
            request,
            exc.status_code,
            f"HTTP_{exc.status_code}",
            str(exc.detail) if exc.detail else "Peticion no procesada.",
        )

    @app.exception_handler(RequestValidationError)
    async def _validacion(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Validacion estricta de esquemas Pydantic: se devuelve el campo y el
        # motivo, sin reflejar el valor recibido (puede contener datos de salud).
        detalles = []
        for err in exc.errors():
            # Los validadores de modelo (los que comparan varios campos entre
            # si) no apuntan a ninguna columna concreta: su `loc` es solo
            # ("body",). Se etiquetan como "general" para que el cliente no
            # muestre un nombre de campo vacio.
            campo = ".".join(str(p) for p in err.get("loc", []) if p != "body")
            detalles.append(
                {
                    "campo": campo or "general",
                    "motivo": motivo_en_castellano(err),
                    "tipo": err.get("type", ""),
                }
            )
        return _responder(
            request,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "VALIDACION_FALLIDA",
            "Los datos enviados no cumplen el esquema esperado.",
            detalles,
        )

    @app.exception_handler(IntegrityError)
    async def _integridad(request: Request, exc: IntegrityError) -> JSONResponse:
        logger.warning("violacion_integridad ruta=%s traza=%s", request.url.path, _id_traza(request))
        return _responder(
            request,
            status.HTTP_409_CONFLICT,
            "CONFLICTO",
            "La operación viola una restricción de integridad de los datos.",
        )

    @app.exception_handler(SQLAlchemyError)
    async def _bd(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        # La traza va al log del servidor; al cliente solo el identificador.
        logger.exception("fallo_base_datos ruta=%s traza=%s", request.url.path, _id_traza(request))
        return _responder(
            request,
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "BD_NO_DISPONIBLE",
            "El servicio de datos no está disponible temporalmente.",
        )

    @app.exception_handler(Exception)
    async def _no_controlado(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("error_no_controlado ruta=%s traza=%s", request.url.path, _id_traza(request))
        return _responder(
            request,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "ERROR_INTERNO",
            "Ocurrio un error interno. Reporte el identificador de traza al soporte.",
        )
