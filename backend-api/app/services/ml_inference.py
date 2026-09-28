"""Cliente del microservicio de inferencia (RF04, RF06).

El modelo ya no corre dentro del API: vive en `ml-service`, un servicio
independiente que se puede reentrenar o escalar sin tocar la parte
transaccional (RNF06). Este modulo es la unica puerta hacia el: arma la ficha
anonimizada del paciente, la envia por REST con la clave de servicio y traduce
la respuesta.

Riesgos gestionados
-------------------
1. **Microservicio caido o lento.** Cualquier fallo de red, tiempo agotado o
   respuesta inesperada se convierte en `ModeloNoDisponibleError` (503): la
   ficha y la auditoria siguen funcionando sin la tarjeta de riesgo.
2. **Datos personales.** Al microservicio solo viajan las variables del Anexo
   n.o 04 y el codigo anonimizado; nunca nombres, documentos ni contactos.
3. **Procedencia.** La ficha del modelo (algoritmo, datos reales o de
   demostracion) viaja en cada prediccion y la interfaz la muestra.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

import httpx

from ..core.config import settings
from ..core.exceptions import ModeloNoDisponibleError
from ..db.models import Paciente

log = logging.getLogger("cdss.ml")


@dataclass
class Prediccion:
    probabilidad: float
    nivel: str
    factores: list[dict]
    variables_imputadas: list[str]
    ficha_modelo: dict
    valor_base: float | None = None
    contribuciones: list[dict] = field(default_factory=list)


_cliente_compartido: httpx.Client | None = None


def _cliente() -> httpx.Client:
    """Cliente HTTP hacia el microservicio. Las pruebas lo sustituyen.

    Se reutiliza entre peticiones: abrir una conexion nueva por cada prediccion
    anade el saludo TCP y TLS a cada consulta, y el panel pide predicciones de
    todos los pacientes cada vez que se abre la bandeja o un reporte.
    """
    global _cliente_compartido
    if _cliente_compartido is None or _cliente_compartido.is_closed:
        _cliente_compartido = httpx.Client(
            base_url=settings.ml_service_url,
            headers={"X-Clave-Servicio": settings.ml_service_clave},
            timeout=settings.ml_service_timeout,
        )
    return _cliente_compartido


def _pedir(metodo: str, ruta: str, **kwargs) -> dict:
    try:
        respuesta = _cliente().request(metodo, ruta, **kwargs)
    except httpx.HTTPError as exc:
        log.warning("microservicio_inalcanzable ruta=%s error=%s", ruta, exc)
        raise ModeloNoDisponibleError() from exc

    if respuesta.status_code != 200:
        log.warning("microservicio_respondio ruta=%s estado=%s", ruta, respuesta.status_code)
        raise ModeloNoDisponibleError()
    return respuesta.json()


def ficha_para_modelo(paciente: Paciente) -> dict:
    """Variables del Anexo n.o 04 con el codigo anonimizado, sin identidad."""
    tiempo = paciente.tiempo_enfermedad_anios
    return {
        "codigo_anonimizado": paciente.codigo_anonimizado,
        "edad": paciente.edad,
        "sexo": paciente.sexo.value,
        "diagnostico": paciente.diagnostico.value,
        "nivel_educativo": paciente.nivel_educativo.value if paciente.nivel_educativo else None,
        "convivencia": paciente.convivencia.value if paciente.convivencia else None,
        "apoyo_familiar": paciente.apoyo_familiar,
        "tiempo_enfermedad_anios": float(tiempo) if tiempo is not None else None,
        "comorbilidades": paciente.comorbilidades,
        "numero_farmacos": paciente.numero_farmacos,
        "tomas_dia": paciente.tomas_dia,
        "controles_programados_6m": paciente.controles_programados_6m,
        "controles_perdidos_6m": paciente.controles_perdidos_6m,
    }


def ficha_del_modelo() -> dict:
    return _pedir("GET", "/modelo")


def modelo_disponible() -> bool:
    try:
        ficha_del_modelo()
        return True
    except ModeloNoDisponibleError:
        return False


def predecir(paciente: Paciente) -> Prediccion:
    """Probabilidad y explicacion SHAP de un paciente."""
    cuerpo = _pedir("POST", "/predicciones", json=ficha_para_modelo(paciente))

    valores = {c["variable"]: c["valor_paciente"] for c in cuerpo["contribuciones"]}
    factores = [
        {"variable": f["variable"], "importancia": f["importancia"],
         "valor_paciente": valores.get(f["variable"])}
        for f in cuerpo["factores_globales"]
    ]
    return Prediccion(
        probabilidad=cuerpo["probabilidad"],
        nivel=cuerpo["nivel"],
        factores=factores,
        variables_imputadas=cuerpo["variables_imputadas"],
        ficha_modelo=cuerpo["modelo"],
        valor_base=cuerpo.get("valor_base"),
        contribuciones=cuerpo["contribuciones"],
    )


# Predicciones recientes de las vistas que recorren a todos los pacientes
# —reportes y bandeja de alertas—. La clave incluye la fecha de actualizacion
# de la ficha, de modo que editar a un paciente invalida su entrada al
# instante; el plazo cubre el caso contrario, el de dos aperturas seguidas de
# la misma pantalla. La ficha individual nunca usa esta cache: ahi el medico
# mira a un paciente concreto y la prediccion se calcula de nuevo.
VIGENCIA_CACHE_S = 60.0
_cache_lote: dict[tuple[str, str], tuple[float, tuple[float, str]]] = {}


def _clave(paciente: Paciente) -> tuple[str, str]:
    actualizacion = paciente.fecha_actualizacion
    return paciente.codigo_anonimizado, actualizacion.isoformat() if actualizacion else ""


def limpiar_cache() -> None:
    """Olvida las predicciones guardadas (lo usan las pruebas)."""
    _cache_lote.clear()


def predecir_lote(pacientes: list[Paciente]) -> dict[str, tuple[float, str]]:
    """Probabilidad y nivel por codigo anonimizado, sin SHAP (para reportes)."""
    if not pacientes:
        return {}

    ahora = time.monotonic()
    conocidos: dict[str, tuple[float, str]] = {}
    pendientes: list[Paciente] = []
    for paciente in pacientes:
        guardado = _cache_lote.get(_clave(paciente))
        if guardado is not None and ahora - guardado[0] < VIGENCIA_CACHE_S:
            conocidos[paciente.codigo_anonimizado] = guardado[1]
        else:
            pendientes.append(paciente)

    if pendientes:
        cuerpo = _pedir("POST", "/predicciones/lote",
                        json={"fichas": [ficha_para_modelo(p) for p in pendientes]})
        recientes = {
            p["codigo_anonimizado"]: (p["probabilidad"], p["nivel"])
            for p in cuerpo["predicciones"]
        }
        for paciente in pendientes:
            prediccion = recientes.get(paciente.codigo_anonimizado)
            if prediccion is not None:
                _cache_lote[_clave(paciente)] = (ahora, prediccion)
        conocidos.update(recientes)

    return conocidos
