"""Inferencia del modelo predictivo de incumplimiento terapeutico (RF04).

Carga el pipeline serializado por `ml-pipeline/src/train_evaluate.py` y calcula
la probabilidad de que un paciente incumpla su tratamiento antes de la proxima
cita, que es lo que el diagnostico (OE1) identifico como ausente: hoy el
incumplimiento se detecta cuando el paciente ya se descompenso.

El artefacto contiene el pipeline **completo** —imputacion, codificacion,
escalado y clasificador—, de modo que la inferencia aplique exactamente las
mismas transformaciones que el entrenamiento. Enviar aqui una fila cruda y
dejar que el pipeline la transforme es lo que evita el desfase entre
entrenamiento y servicio.

Riesgos gestionados
-------------------
1. **Modelo ausente o ilegible.** El servicio arranca igual y responde 503 en
   las rutas de prediccion; el resto del sistema —auditoria, registro de
   tomas— sigue operativo. Un fallo del componente inteligente no puede dejar
   sin servicio a la consulta clinica.
2. **Procedencia de los datos.** La ficha del modelo viaja con el artefacto y
   se devuelve en cada prediccion. Un resultado obtenido con datos simulados no
   puede presentarse como si viniera de historias clinicas reales.
3. **Alcance de la salida.** La respuesta es una probabilidad de riesgo con los
   factores que mas pesan en el modelo, no un diagnostico. Quien decide es el
   medico.
4. **Ficha incompleta.** Las variables faltantes las imputa el propio pipeline
   con los estadisticos aprendidos en el entrenamiento; la respuesta informa
   cuantas se imputaron para que el medico module su confianza.
"""
from __future__ import annotations

import json
import logging
from datetime import date
from functools import lru_cache
from pathlib import Path

from ..core.config import settings
from ..core.exceptions import ModeloNoDisponibleError
from ..db.models import Paciente

log = logging.getLogger("cdss.ml")

# Variables que el pipeline espera, en la forma cruda del Anexo n.o 04. El
# orden no importa: el preprocesador selecciona por nombre de columna.
NUMERICAS = [
    "edad",
    "tiempo_enfermedad_anios",
    "comorbilidades",
    "numero_farmacos",
    "tomas_dia",
    "controles_programados_6m",
    "controles_perdidos_6m",
    "carga_terapeutica",
    "tasa_inasistencia",
    "cronicidad_relativa",
]
CATEGORICAS = ["nivel_educativo", "sexo", "convivencia", "apoyo_familiar", "diagnostico"]

# Umbrales de la banda de riesgo. El umbral alto es configurable porque define
# a cuantos pacientes alcanza el medico a contactar antes de la cita.
UMBRAL_MEDIO = 0.40


class Prediccion:
    """Resultado de una inferencia."""

    def __init__(
        self,
        probabilidad: float,
        nivel: str,
        factores: list[dict],
        variables_imputadas: list[str],
        ficha_modelo: dict,
    ) -> None:
        self.probabilidad = probabilidad
        self.nivel = nivel
        self.factores = factores
        self.variables_imputadas = variables_imputadas
        self.ficha_modelo = ficha_modelo


def _ruta_modelo() -> Path:
    ruta = Path(settings.model_path)
    if not ruta.is_absolute():
        # La ruta se declara relativa a la raiz de `backend-api`, no al
        # directorio desde el que se lanzo el proceso.
        ruta = (Path(__file__).resolve().parents[2] / ruta).resolve()
    return ruta


@lru_cache(maxsize=1)
def _cargar():
    """Carga el pipeline y su ficha una sola vez por proceso.

    Se cachea a proposito: deserializar en cada peticion multiplicaria la
    latencia y comprometeria la meta de RNF02 (respuesta <= 2 s).
    """
    ruta = _ruta_modelo()
    if not ruta.exists():
        raise ModeloNoDisponibleError(
            "El modelo predictivo aun no esta disponible en el servidor."
        )

    try:
        import joblib

        pipeline = joblib.load(ruta)
    except Exception as exc:  # pragma: no cover - depende del entorno
        log.exception("no se pudo cargar el modelo desde %s", ruta)
        raise ModeloNoDisponibleError(
            "El modelo predictivo no se pudo cargar. Reporte la incidencia al soporte."
        ) from exc

    ficha_ruta = ruta.with_suffix(".json")
    ficha = {}
    if ficha_ruta.exists():
        try:
            ficha = json.loads(ficha_ruta.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            log.warning("la ficha del modelo en %s no es JSON valido", ficha_ruta)

    log.info(
        "modelo cargado algoritmo=%s origen=%s",
        ficha.get("algoritmo", "desconocido"),
        ficha.get("origen_datos", "desconocido"),
    )
    return pipeline, ficha


def modelo_disponible() -> bool:
    """Indica si hay un modelo cargable, sin lanzar excepciones."""
    try:
        _cargar()
        return True
    except ModeloNoDisponibleError:
        return False


def ficha_del_modelo() -> dict:
    """Procedencia y desempeno del modelo en servicio."""
    _, ficha = _cargar()
    return ficha


def _derivar(paciente: Paciente) -> dict:
    """Reconstruye las variables derivadas tal como las define el pipeline.

    Deben calcularse igual que en `preprocess.py`: una formula distinta aqui
    produciria predicciones sobre variables que el modelo nunca vio.
    """
    tiempo = paciente.tiempo_enfermedad_anios
    tiempo = float(tiempo) if tiempo is not None else None

    return {
        "carga_terapeutica": paciente.numero_farmacos * paciente.tomas_dia,
        "tasa_inasistencia": (
            paciente.controles_perdidos_6m / paciente.controles_programados_6m
            if paciente.controles_programados_6m
            else None
        ),
        "cronicidad_relativa": (
            tiempo / (paciente.edad / 10) if tiempo is not None and paciente.edad else None
        ),
        "tiempo_enfermedad_anios": tiempo,
    }


def _fila(paciente: Paciente) -> tuple[dict, list[str]]:
    """Convierte la ficha clinica en la fila cruda que espera el pipeline."""
    derivadas = _derivar(paciente)

    fila = {
        "edad": paciente.edad,
        "comorbilidades": paciente.comorbilidades,
        "numero_farmacos": paciente.numero_farmacos,
        "tomas_dia": paciente.tomas_dia,
        "controles_programados_6m": paciente.controles_programados_6m,
        "controles_perdidos_6m": paciente.controles_perdidos_6m,
        **derivadas,
        "sexo": paciente.sexo.value,
        "diagnostico": paciente.diagnostico.value,
        "nivel_educativo": (
            paciente.nivel_educativo.value if paciente.nivel_educativo else None
        ),
        "convivencia": paciente.convivencia.value if paciente.convivencia else None,
        # En el Anexo n.o 04 se registra como si/no.
        "apoyo_familiar": (
            None if paciente.apoyo_familiar is None
            else ("si" if paciente.apoyo_familiar else "no")
        ),
    }

    # El pipeline imputa lo que falta, pero el medico debe saber sobre cuanta
    # informacion ausente se construyo la prediccion.
    imputadas = sorted(k for k, v in fila.items() if v is None)
    return fila, imputadas


def _nivel(probabilidad: float) -> str:
    if probabilidad >= settings.umbral_riesgo_alto:
        return "alto"
    if probabilidad >= UMBRAL_MEDIO:
        return "medio"
    return "bajo"


def _factores(ficha: dict, fila: dict, maximo: int = 5) -> list[dict]:
    """Variables que mas pesan en el modelo, con el valor de este paciente.

    La importancia es **global**: mide cuanto depende el modelo de cada
    variable, no cuanto aporto cada una a esta prediccion concreta. La
    atribucion individual con SHAP corresponde a RF06.
    """
    factores = []
    for entrada in ficha.get("factores_influyentes", [])[:maximo]:
        variable = entrada["variable"]
        valor = fila.get(variable)
        factores.append(
            {
                "variable": variable,
                "importancia": entrada["importancia"],
                "valor_paciente": None if valor is None else round(float(valor), 2)
                if isinstance(valor, (int, float))
                else valor,
            }
        )
    return factores


def predecir(paciente: Paciente) -> Prediccion:
    """Probabilidad de incumplimiento terapeutico del paciente indicado."""
    pipeline, ficha = _cargar()
    fila, imputadas = _fila(paciente)

    try:
        import numpy as np
        import pandas as pd

        # Los campos opcionales llegan como `None`, pero los imputadores de
        # scikit-learn solo reconocen `NaN` como valor ausente: un `None` en
        # una columna categorica hace que el codificador lo trate como una
        # categoria desconocida y aborte. Como la mayoria de las fichas tiene
        # algun opcional sin completar, la conversion no es un detalle: sin
        # ella la prediccion fallaria para casi todos los pacientes.
        marco = pd.DataFrame([{
            columna: (np.nan if valor is None else valor)
            for columna, valor in fila.items()
        }])
        probabilidad = float(pipeline.predict_proba(marco)[0][1])
    except Exception as exc:  # pragma: no cover - depende del artefacto
        log.exception("fallo la inferencia para el paciente %s", paciente.codigo_anonimizado)
        raise ModeloNoDisponibleError(
            "No se pudo calcular la prediccion para este paciente."
        ) from exc

    return Prediccion(
        probabilidad=round(probabilidad, 4),
        nivel=_nivel(probabilidad),
        factores=_factores(ficha, fila),
        variables_imputadas=imputadas,
        ficha_modelo={
            "algoritmo": ficha.get("algoritmo", "desconocido"),
            "entrenado_el": ficha.get("entrenado_el", date.min.isoformat()),
            "origen_datos": ficha.get("origen_datos", "desconocido"),
            "datos_reales": bool(ficha.get("datos_reales", False)),
            "aucroc_validacion_cruzada": ficha.get("aucroc_validacion_cruzada"),
        },
    )
