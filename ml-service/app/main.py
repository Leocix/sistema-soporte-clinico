"""Microservicio de inferencia del modelo predictivo (RF04, RF06).

Separado del API central, como establece la arquitectura de microservicios del
proyecto: se puede reentrenar, reemplazar o escalar sin tocar la parte
transaccional del sistema (RNF06). Solo lo consume el API central, que le
envia las variables del Anexo n.o 04 con el codigo anonimizado.

    GET  /health                 disponibilidad (publica, para Render)
    GET  /modelo                 procedencia y desempeno del modelo
    POST /predicciones           probabilidad + explicacion SHAP de un paciente
    POST /predicciones/lote      probabilidades de varios pacientes, sin SHAP
"""
from __future__ import annotations

import hmac
import logging
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse

from . import modelo as servicio
from .config import settings
from .esquemas import FichaEntrada, FichaModelo, PeticionLote, Prediccion, RespuestaLote

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
log = logging.getLogger("cdss.ml")

if settings.es_produccion and not settings.clave_servicio:
    raise RuntimeError("CLAVE_SERVICIO es obligatoria en produccion.")


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Carga el modelo y SHAP al arrancar, no en la primera consulta del medico.

    La primera explicacion SHAP tarda unos 5 s (importacion y compilacion
    interna); se ejecuta una con una ficha de ejemplo para que no la pague la
    primera ficha que abra el medico tras un despliegue.
    """
    try:
        ejemplo = FichaEntrada(
            codigo_anonimizado="CALENTAR", edad=65, sexo="F", diagnostico="hta",
            comorbilidades=1, numero_farmacos=5, tomas_dia=3,
            controles_programados_6m=6, controles_perdidos_6m=1,
        )
        servicio.predecir([ejemplo], con_explicacion=True)
        log.info("modelo_y_shap_listos")
    except servicio.ModeloNoDisponible as exc:
        log.warning("arranque_sin_modelo motivo=%s", exc)
    yield


app = FastAPI(
    lifespan=lifespan,
    title=settings.app_name,
    version=settings.app_version,
    docs_url=None if settings.es_produccion else "/docs",
    redoc_url=None,
    openapi_url=None if settings.es_produccion else "/openapi.json",
)


@app.middleware("http")
async def medir(request: Request, call_next):
    inicio = time.perf_counter()
    respuesta = await call_next(request)
    ms = (time.perf_counter() - inicio) * 1000
    respuesta.headers["X-Tiempo-Respuesta-ms"] = f"{ms:.1f}"
    respuesta.headers["Cache-Control"] = "no-store"
    log.info("peticion ruta=%s estado=%s ms=%.1f", request.url.path, respuesta.status_code, ms)
    return respuesta


@app.exception_handler(servicio.ModeloNoDisponible)
async def _sin_modelo(_: Request, exc: servicio.ModeloNoDisponible):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"codigo": "MODELO_NO_DISPONIBLE", "mensaje": str(exc)},
    )


def verificar_clave(x_clave_servicio: str = Header(default="")) -> None:
    """Solo el API central, que conoce la clave, puede pedir predicciones."""
    if settings.clave_servicio and not hmac.compare_digest(
        x_clave_servicio, settings.clave_servicio
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Clave de servicio invalida.")


@app.get("/health")
def salud() -> dict:
    return {"estado": "ok", "version": settings.app_version}


@app.get("/modelo", response_model=FichaModelo, dependencies=[Depends(verificar_clave)])
def ficha_del_modelo() -> FichaModelo:
    return servicio.ficha_publica(servicio.cargar())


@app.post("/predicciones", response_model=Prediccion, dependencies=[Depends(verificar_clave)])
def predecir(ficha: FichaEntrada) -> Prediccion:
    return servicio.predecir([ficha], con_explicacion=True)[0]


@app.post("/predicciones/lote", response_model=RespuestaLote, dependencies=[Depends(verificar_clave)])
def predecir_lote(peticion: PeticionLote) -> RespuestaLote:
    return RespuestaLote(predicciones=servicio.predecir(peticion.fichas, con_explicacion=False))
