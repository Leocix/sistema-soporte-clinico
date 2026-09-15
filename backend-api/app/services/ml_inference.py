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


def _cliente() -> httpx.Client:
    """Cliente HTTP hacia el microservicio. Las pruebas lo sustituyen."""
    return httpx.Client(
        base_url=settings.ml_service_url,
        headers={"X-Clave-Servicio": settings.ml_service_clave},
        timeout=settings.ml_service_timeout,
    )


def _pedir(metodo: str, ruta: str, **kwargs) -> dict:
    try:
        with _cliente() as cliente:
            respuesta = cliente.request(metodo, ruta, **kwargs)
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


def predecir_lote(pacientes: list[Paciente]) -> dict[str, tuple[float, str]]:
    """Probabilidad y nivel por codigo anonimizado, sin SHAP (para reportes)."""
    if not pacientes:
        return {}
    cuerpo = _pedir("POST", "/predicciones/lote",
                    json={"fichas": [ficha_para_modelo(p) for p in pacientes]})
    return {p["codigo_anonimizado"]: (p["probabilidad"], p["nivel"]) for p in cuerpo["predicciones"]}
