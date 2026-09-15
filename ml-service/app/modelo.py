"""Carga del modelo, prediccion y explicacion individual con SHAP.

El artefacto que produce `ml-pipeline/src/train_evaluate.py` contiene el
pipeline completo (preparacion + SMOTE + clasificador). Aqui se le entrega la
fila cruda de la ficha y aplica las mismas transformaciones del entrenamiento.

Explicacion con SHAP (RF06)
---------------------------
SHAP reparte la diferencia entre la probabilidad del paciente y la del
paciente de referencia entre sus variables, de forma que las contribuciones
sumen exactamente esa diferencia. Se calcula en el espacio ya preparado
(imputado, codificado y escalado) con el explicador por permutaciones, que es
agnostico al algoritmo: el ganador puede ser un SVM, que no tiene coeficientes
interpretables. Las columnas de una misma variable categorica (por ejemplo,
`convivencia_solo`) se suman para devolver una contribucion por variable del
Anexo n.o 04.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from .config import settings
from .esquemas import Contribucion, FactorGlobal, FichaEntrada, FichaModelo, Prediccion

log = logging.getLogger("cdss.ml")

RAIZ = Path(__file__).resolve().parents[1]


class ModeloNoDisponible(Exception):
    """El artefacto no existe o no se pudo cargar."""


@dataclass
class ModeloCargado:
    pipeline: object
    ficha: dict

    @property
    def columnas_entrada(self) -> list[str]:
        return list(self.pipeline.named_steps["prep"].feature_names_in_)


def _ruta_modelo() -> Path:
    ruta = Path(settings.model_path)
    return ruta if ruta.is_absolute() else (RAIZ / ruta).resolve()


@lru_cache(maxsize=1)
def cargar() -> ModeloCargado:
    """Carga el modelo una sola vez por proceso (RNF02)."""
    ruta = _ruta_modelo()
    if not ruta.exists():
        raise ModeloNoDisponible(f"No existe el modelo en {ruta}.")
    try:
        import joblib

        pipeline = joblib.load(ruta)
    except Exception as exc:  # pragma: no cover - depende del entorno
        log.exception("no se pudo cargar el modelo desde %s", ruta)
        raise ModeloNoDisponible("El modelo no se pudo cargar.") from exc

    ruta_ficha = ruta.with_suffix(".json")
    ficha = json.loads(ruta_ficha.read_text(encoding="utf-8")) if ruta_ficha.exists() else {}
    log.info("modelo_cargado algoritmo=%s origen=%s",
             ficha.get("algoritmo"), ficha.get("origen_datos"))
    return ModeloCargado(pipeline=pipeline, ficha=ficha)


def ficha_publica(modelo: ModeloCargado) -> FichaModelo:
    f = modelo.ficha
    return FichaModelo(
        algoritmo=f.get("algoritmo", "desconocido"),
        entrenado_el=f.get("entrenado_el", ""),
        origen_datos=f.get("origen_datos", "desconocido"),
        datos_reales=bool(f.get("datos_reales", False)),
        aucroc_validacion_cruzada=f.get("aucroc_validacion_cruzada"),
    )


# ---------------------------------------------------------------------------
# De la ficha a la fila del modelo
# ---------------------------------------------------------------------------
def derivar(ficha: FichaEntrada) -> dict:
    """Variables derivadas, con las mismas formulas que `preprocess.py`."""
    tiempo = ficha.tiempo_enfermedad_anios
    return {
        "carga_terapeutica": ficha.numero_farmacos * ficha.tomas_dia,
        "tasa_inasistencia": (
            ficha.controles_perdidos_6m / ficha.controles_programados_6m
            if ficha.controles_programados_6m else None
        ),
        "cronicidad_relativa": tiempo / (ficha.edad / 10) if tiempo is not None else None,
    }


def construir_fila(ficha: FichaEntrada) -> dict:
    fila = {
        "edad": ficha.edad,
        "tiempo_enfermedad_anios": ficha.tiempo_enfermedad_anios,
        "comorbilidades": ficha.comorbilidades,
        "numero_farmacos": ficha.numero_farmacos,
        "tomas_dia": ficha.tomas_dia,
        "controles_programados_6m": ficha.controles_programados_6m,
        "controles_perdidos_6m": ficha.controles_perdidos_6m,
        **derivar(ficha),
        "sexo": ficha.sexo,
        "diagnostico": ficha.diagnostico,
        "nivel_educativo": ficha.nivel_educativo,
        "convivencia": ficha.convivencia,
        # En el Anexo n.o 04 se registra como si/no.
        "apoyo_familiar": None if ficha.apoyo_familiar is None
        else ("si" if ficha.apoyo_familiar else "no"),
    }
    return fila


def _marco(modelo: ModeloCargado, filas: list[dict]) -> pd.DataFrame:
    # Los imputadores de scikit-learn solo reconocen NaN como ausente.
    marco = pd.DataFrame([
        {c: (np.nan if f.get(c) is None else f.get(c)) for c in modelo.columnas_entrada}
        for f in filas
    ])
    return marco


def nivel(probabilidad: float) -> str:
    if probabilidad >= settings.umbral_riesgo_alto:
        return "alto"
    if probabilidad >= settings.umbral_riesgo_medio:
        return "medio"
    return "bajo"


# ---------------------------------------------------------------------------
# SHAP
# ---------------------------------------------------------------------------
def _variable_de_columna(columna: str, variables: list[str]) -> str:
    """`convivencia_solo` -> `convivencia`; `edad` -> `edad`."""
    if columna in variables:
        return columna
    candidatas = [v for v in variables if columna.startswith(v + "_")]
    return max(candidatas, key=len) if candidatas else columna


def explicar(modelo: ModeloCargado, marco: pd.DataFrame) -> tuple[float, dict[str, float]]:
    """Valor base y contribucion SHAP por variable para UNA fila."""
    import shap

    fondo = modelo.ficha.get("fondo_shap")
    if not fondo:
        raise ModeloNoDisponible("El modelo no incluye referencia para SHAP.")

    preparador = modelo.pipeline.named_steps["prep"]
    clasificador = modelo.pipeline.named_steps["clf"]
    columnas = list(preparador.get_feature_names_out())
    if columnas != fondo["columnas_preparadas"]:
        raise ModeloNoDisponible("La referencia SHAP no corresponde a este modelo.")

    x = np.asarray(preparador.transform(marco), dtype=float)
    referencia = np.asarray(fondo["centroides"], dtype=float)

    def probabilidad(matriz):
        return clasificador.predict_proba(matriz)[:, 1]

    explicador = shap.PermutationExplainer(
        probabilidad, shap.maskers.Independent(referencia, max_samples=len(referencia)), seed=42,
    )
    evaluaciones = max(settings.evaluaciones_shap, 2 * len(columnas) + 1)
    resultado = explicador(x, max_evals=evaluaciones, silent=True)

    variables = modelo.columnas_entrada
    por_variable: dict[str, float] = {}
    for columna, valor in zip(columnas, resultado.values[0]):
        clave = _variable_de_columna(columna, variables)
        por_variable[clave] = por_variable.get(clave, 0.0) + float(valor)
    return float(np.ravel(resultado.base_values)[0]), por_variable


# ---------------------------------------------------------------------------
# Prediccion
# ---------------------------------------------------------------------------
def _redondear(valor):
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        return round(float(valor), 2)
    return valor


def predecir(fichas: list[FichaEntrada], con_explicacion: bool) -> list[Prediccion]:
    modelo = cargar()
    filas = [construir_fila(f) for f in fichas]
    marco = _marco(modelo, filas)
    probabilidades = modelo.pipeline.predict_proba(marco)[:, 1]

    globales = [
        FactorGlobal(variable=f["variable"], importancia=f["importancia"])
        for f in modelo.ficha.get("factores_influyentes", [])[:5]
    ]
    publica = ficha_publica(modelo)

    salida = []
    for i, (ficha, fila) in enumerate(zip(fichas, filas)):
        probabilidad = float(probabilidades[i])
        base, contribuciones = None, []
        if con_explicacion:
            base, por_variable = explicar(modelo, marco.iloc[[i]])
            contribuciones = sorted(
                (
                    Contribucion(variable=v, valor_paciente=_redondear(fila.get(v)),
                                 contribucion=round(c, 4))
                    for v, c in por_variable.items()
                ),
                key=lambda c: abs(c.contribucion), reverse=True,
            )
            base = round(base, 4)
        salida.append(Prediccion(
            codigo_anonimizado=ficha.codigo_anonimizado,
            probabilidad=round(probabilidad, 4),
            nivel=nivel(probabilidad),
            variables_imputadas=sorted(k for k, v in fila.items() if v is None),
            valor_base=base,
            contribuciones=contribuciones,
            factores_globales=globales,
            modelo=publica,
        ))
    return salida
