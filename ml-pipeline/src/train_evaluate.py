"""Comparacion de algoritmos predictivos del incumplimiento terapeutico.

Fase *Modeling* de CRISP-DM (Sprint 2-3). Responde al OE3: determinar el
algoritmo con mayor capacidad predictiva comparando Regresion Logistica,
Random Forest, XGBoost y SVM con validacion cruzada estratificada de cinco
pliegues, y reportando exactitud, sensibilidad, especificidad, F1-score y
AUCROC.

Decision metodologica central
-----------------------------
El balanceo con SMOTE va DENTRO del pipeline de validacion cruzada, no antes.
`preprocess.py` deja un conjunto de entrenamiento ya balanceado que sirve para
ajustar un modelo final, pero usarlo tal cual en validacion cruzada invalidaria
las metricas: al sintetizar las muestras sobre el conjunto completo, los puntos
generados por interpolacion acaban repartidos entre los pliegues de
entrenamiento y los de validacion, de modo que el modelo evalua casos derivados
de los que ya vio. El AUCROC resultante seria optimista y la comparacion entre
algoritmos, invalida.

Por eso este script parte del dataset **crudo** y arma un pipeline
`imblearn` —imputacion, codificacion, escalado, SMOTE y clasificador— que
`cross_validate` reajusta por completo en cada pliegue. El conjunto de prueba
se aparta antes de todo y nunca se balancea: conserva la prevalencia real del
consultorio, que es sobre la que operara el sistema.

Uso
---
    python src/train_evaluate.py --entrada data/raw/dataset_clinico.csv
    python src/train_evaluate.py --generar-muestra 300   # verificacion del flujo
    python src/train_evaluate.py --sin-busqueda          # sin ajuste de hiperparametros
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import warnings
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    make_scorer,
    recall_score,
    roc_auc_score,
)
from sklearn.inspection import permutation_importance
from sklearn.base import clone
from sklearn.model_selection import (
    GridSearchCV,
    StratifiedKFold,
    cross_val_predict,
    cross_validate,
)
from sklearn.svm import SVC

sys.path.insert(0, str(Path(__file__).resolve().parent))

import preprocess  # noqa: E402  (el esquema cambia con --perfil; se lee al usarlo)
from preprocess import (  # noqa: E402
    COL_OBJETIVO,
    DIR_MODELOS,
    DIR_PROCESSED,
    DIR_RAW,
    SEMILLA,
    cargar_datos,
    construir_preprocesador,
    derivar_variables,
    dividir_estratificado,
    generar_muestra_sintetica,
    limpiar,
    validar_esquema,
    ReporteDePreparacion,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("train_evaluate")

# Meta fijada en la hipotesis del proyecto de investigacion.
META_AUCROC = 0.80

# Umbral con el que se convierte la probabilidad en decision para McNemar.
UMBRAL_DECISION = 0.5

# Etiqueta con la que se marca un modelo entrenado sobre datos simulados.
ORIGEN_SIMULADO = "conjunto de demostracion simulado"

# Los artefactos del perfil reducido llevan sufijo propio: el microservicio
# carga risk_model_v1.pkl y espera el esquema completo del consultorio, de modo
# que un modelo entrenado con la ENDES no debe ocupar ese nombre.
SUFIJO_PERFIL = {"clinico": "", "endes": "_endes"}
ORIGEN_ENDES = "ENDES (INEI), microdatos publicos"


# ---------------------------------------------------------------------------
# Metricas
# ---------------------------------------------------------------------------
def especificidad(y_verdadero, y_predicho) -> float:
    """Proporcion de adherentes correctamente identificados como tales.

    scikit-learn no la trae como metrica: es la sensibilidad de la clase
    negativa, y se calcula desde la matriz de confusion.
    """
    matriz = confusion_matrix(y_verdadero, y_predicho, labels=[0, 1])
    vn, fp = matriz[0, 0], matriz[0, 1]
    return float(vn / (vn + fp)) if (vn + fp) else 0.0


METRICAS = {
    "exactitud": "accuracy",
    "sensibilidad": "recall",
    "especificidad": make_scorer(especificidad),
    "f1": "f1",
    "aucroc": "roc_auc",
}


# ---------------------------------------------------------------------------
# Algoritmos candidatos (Tabla 9 del pre informe)
# ---------------------------------------------------------------------------
def catalogo_de_modelos(incluir_xgboost: bool = True) -> dict:
    """Estimadores y sus rejillas de hiperparametros.

    XGBoost se declara aparte porque es la unica dependencia que puede faltar
    en un entorno recien creado; si no esta instalado se avisa y la comparacion
    continua con los otros tres en lugar de abortar.
    """
    modelos = {
        "Regresion Logistica": (
            LogisticRegression(max_iter=1000, random_state=SEMILLA),
            {"clf__C": [0.01, 0.1, 1, 10], "clf__penalty": ["l2"]},
        ),
        "Random Forest": (
            RandomForestClassifier(random_state=SEMILLA, n_jobs=-1),
            {
                "clf__n_estimators": [200, 500],
                "clf__max_depth": [None, 8, 12],
                "clf__min_samples_leaf": [1, 3, 5],
            },
        ),
        "SVM (RBF)": (
            # `probability=True` es necesario para el AUCROC; encarece el
            # ajuste, pero con el tamano de muestra del estudio es asumible.
            SVC(kernel="rbf", probability=True, random_state=SEMILLA),
            {"clf__C": [0.1, 1, 10], "clf__gamma": ["scale", 0.01]},
        ),
    }

    if not incluir_xgboost:
        log.info("XGBoost excluido a peticion: el modelo resultante no lo necesitara.")
        return modelos

    try:
        from xgboost import XGBClassifier
    except ImportError:
        log.warning(
            "XGBoost no esta instalado; se compara sin el. "
            "Instalelo con: pip install -r requirements.txt"
        )
        return modelos

    modelos["XGBoost"] = (
        XGBClassifier(
            random_state=SEMILLA,
            eval_metric="logloss",
            tree_method="hist",
        ),
        {
            "clf__n_estimators": [200, 400],
            "clf__learning_rate": [0.05, 0.1],
            "clf__max_depth": [3, 5, 7],
        },
    )
    return modelos


@dataclass
class ResultadoModelo:
    """Desempeno de un algoritmo en validacion cruzada y en prueba."""

    nombre: str
    hiperparametros: dict = field(default_factory=dict)
    # Media y desviacion estandar entre pliegues.
    cv: dict = field(default_factory=dict)
    # Metricas sobre el conjunto de prueba independiente.
    prueba: dict = field(default_factory=dict)

    @property
    def aucroc_cv(self) -> float:
        return self.cv.get("aucroc", {}).get("media", 0.0)

    @property
    def sensibilidad_cv(self) -> float:
        return self.cv.get("sensibilidad", {}).get("media", 0.0)


# ---------------------------------------------------------------------------
# Evaluacion
# ---------------------------------------------------------------------------
def construir_pipeline(numericas: list[str], estimador):
    """Encadena preparacion, balanceo y clasificador en un solo objeto.

    Al ser un unico estimador, `cross_validate` lo reajusta entero en cada
    pliegue: el imputador, el codificador, el escalador y SMOTE se calculan
    solo con la porcion de entrenamiento del pliegue. Es lo que evita la fuga
    de informacion descrita en la cabecera del modulo.
    """
    from imblearn.pipeline import Pipeline as PipelineImb
    from imblearn.over_sampling import SMOTE

    return PipelineImb(
        steps=[
            ("prep", construir_preprocesador(numericas)),
            ("smote", SMOTE(random_state=SEMILLA)),
            ("clf", estimador),
        ]
    )


def _resumen_de_pliegues(puntuaciones: dict) -> dict:
    """Media y desviacion estandar de cada metrica entre los pliegues."""
    return {
        nombre: {
            "media": round(float(np.mean(puntuaciones[f"test_{nombre}"])), 4),
            "desviacion": round(float(np.std(puntuaciones[f"test_{nombre}"])), 4),
        }
        for nombre in METRICAS
    }


def evaluar_modelo(
    nombre: str,
    estimador,
    rejilla: dict,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    numericas: list[str],
    pliegues: int,
    con_busqueda: bool,
) -> tuple[ResultadoModelo, object]:
    """Ajusta el modelo y lo evalua con validacion cruzada estratificada."""
    particion = StratifiedKFold(n_splits=pliegues, shuffle=True, random_state=SEMILLA)
    pipeline = construir_pipeline(numericas, estimador)

    if con_busqueda and rejilla:
        # La busqueda tambien se hace dentro de la validacion cruzada, de modo
        # que los hiperparametros no se elijan mirando datos de validacion.
        busqueda = GridSearchCV(
            pipeline,
            rejilla,
            scoring="roc_auc",
            cv=particion,
            n_jobs=-1,
            refit=True,
        )
        busqueda.fit(X_train, y_train)
        pipeline = busqueda.best_estimator_
        hiperparametros = {
            k.replace("clf__", ""): v for k, v in busqueda.best_params_.items()
        }
        log.info("%s: mejores hiperparametros %s", nombre, hiperparametros)
    else:
        hiperparametros = {}

    puntuaciones = cross_validate(
        pipeline,
        X_train,
        y_train,
        cv=particion,
        scoring=METRICAS,
        n_jobs=-1,
        error_score="raise",
    )

    resultado = ResultadoModelo(
        nombre=nombre,
        hiperparametros=hiperparametros,
        cv=_resumen_de_pliegues(puntuaciones),
    )
    log.info(
        "%-22s AUCROC %.4f (+/-%.4f)  sensibilidad %.4f",
        nombre,
        resultado.aucroc_cv,
        resultado.cv["aucroc"]["desviacion"],
        resultado.sensibilidad_cv,
    )

    pipeline.fit(X_train, y_train)
    return resultado, pipeline


def evaluar_en_prueba(pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """Metricas sobre el conjunto apartado, con la prevalencia real."""
    predicho = pipeline.predict(X_test)
    probabilidad = pipeline.predict_proba(X_test)[:, 1]

    return {
        "exactitud": round(float(accuracy_score(y_test, predicho)), 4),
        "sensibilidad": round(float(recall_score(y_test, predicho, zero_division=0)), 4),
        "especificidad": round(especificidad(y_test, predicho), 4),
        "f1": round(float(f1_score(y_test, predicho, zero_division=0)), 4),
        "aucroc": round(float(roc_auc_score(y_test, probabilidad)), 4),
    }


def fondo_de_referencia(pipeline, X_train: pd.DataFrame, n_grupos: int = 12) -> dict:
    """Pacientes de referencia contra los que SHAP mide cada contribucion.

    SHAP explica una prediccion comparandola con lo que el modelo diria de un
    paciente "tipico". En lugar de guardar fichas reales del entrenamiento
    —que con datos del consultorio serian registros clinicos dentro del
    repositorio—, se guardan los centroides de k-medias en el espacio ya
    preparado (imputado, codificado y escalado). Resumen la poblacion sin
    corresponder a ningun paciente concreto.
    """
    from sklearn.cluster import KMeans

    preparador = pipeline.named_steps["prep"]
    matriz = preparador.transform(X_train)
    grupos = min(n_grupos, len(matriz))
    kmedias = KMeans(n_clusters=grupos, n_init=10, random_state=SEMILLA).fit(matriz)
    return {
        "columnas_preparadas": [str(c) for c in preparador.get_feature_names_out()],
        "centroides": [[round(float(v), 6) for v in fila] for fila in kmedias.cluster_centers_],
    }


def importancia_de_variables(pipeline, X_test, y_test, n_repeticiones: int = 20) -> list[dict]:
    """Importancia por permutacion de cada variable del Anexo n.o 04.

    Mide cuanto empeora el AUCROC al barajar una variable: si al desordenarla
    el modelo pierde capacidad, esa variable le importaba. Es agnostica al
    algoritmo, lo que resulta necesario aqui porque el ganador puede ser un SVM
    con nucleo radial, que no expone coeficientes interpretables.

    Es una importancia **global** del modelo, no una descomposicion por
    paciente. La atribucion individual con SHAP corresponde a RF06, en el
    Sprint 3; hasta entonces el microservicio informa estos factores dejando
    claro su alcance, en lugar de presentar como personal algo que no lo es.
    """
    resultado = permutation_importance(
        pipeline, X_test, y_test,
        scoring="roc_auc", n_repeats=n_repeticiones,
        random_state=SEMILLA, n_jobs=-1,
    )
    factores = [
        {
            "variable": columna,
            "importancia": round(float(media), 4),
            "desviacion": round(float(desviacion), 4),
        }
        for columna, media, desviacion in zip(
            X_test.columns, resultado.importances_mean, resultado.importances_std
        )
    ]
    factores.sort(key=lambda f: f["importancia"], reverse=True)
    return factores


# ---------------------------------------------------------------------------
# Seleccion y contraste estadistico
# ---------------------------------------------------------------------------
def seleccionar_mejor(
    ordenados: list[ResultadoModelo], contraste: dict | None = None
) -> ResultadoModelo:
    """Mayor AUCROC; ante empate estadistico, mayor sensibilidad.

    `ordenados` va de mayor a menor AUCROC. `contraste` es la prueba de DeLong
    entre las AUCROC de los dos primeros. Si no encuentra diferencia
    significativa, el AUCROC no basta para preferir a uno y decide la
    sensibilidad: el error clinicamente costoso es el falso negativo —un
    paciente en riesgo que el sistema no detecta y que por tanto no recibe la
    alerta temprana—.
    """
    primero = ordenados[0]
    if len(ordenados) < 2 or not contraste:
        return primero
    p_valor = contraste.get("p_valor")
    empate = p_valor is None or p_valor >= 0.05
    segundo = ordenados[1]
    if empate and segundo.sensibilidad_cv > primero.sensibilidad_cv:
        return segundo
    return primero


def _delong(y_verdadero, puntajes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """AUCROC de uno o varios modelos y su matriz de covarianza (DeLong).

    Implementacion rapida de Sun y Xu (2014) del metodo de DeLong et al.
    (1988). `puntajes` tiene una fila por modelo, evaluados sobre los mismos
    pacientes: por eso las AUCROC estan correlacionadas y la covarianza entre
    ellas no puede ignorarse al compararlas.
    """
    from scipy.stats import rankdata

    y = np.asarray(y_verdadero).astype(int)
    puntajes = np.atleast_2d(np.asarray(puntajes, dtype=float))
    positivos, negativos = puntajes[:, y == 1], puntajes[:, y == 0]
    m, n = positivos.shape[1], negativos.shape[1]

    rx = np.vstack([rankdata(fila) for fila in positivos])
    ry = np.vstack([rankdata(fila) for fila in negativos])
    rz = np.vstack([rankdata(fila) for fila in np.hstack([positivos, negativos])])

    aucs = rz[:, :m].sum(axis=1) / (m * n) - (m + 1.0) / (2.0 * n)
    v01 = (rz[:, :m] - rx) / n
    v10 = 1.0 - (rz[:, m:] - ry) / m
    covarianza = np.atleast_2d(np.cov(v01)) / m + np.atleast_2d(np.cov(v10)) / n
    return aucs, covarianza


def intervalo_auc(y_verdadero, probabilidad) -> dict:
    """AUCROC con su intervalo de confianza al 95 % y contraste frente al azar.

    El contraste frente a 0,5 delimita lo que el resultado demuestra: una
    AUCROC baja pero significativamente mayor que 0,5 indica que las variables
    contienen señal, aunque insuficiente para la meta.
    """
    from scipy.stats import norm

    aucs, cov = _delong(y_verdadero, probabilidad)
    auc, ee = float(aucs[0]), float(np.sqrt(cov[0, 0]))
    z = (auc - 0.5) / ee if ee > 0 else float("inf")
    return {
        "aucroc": round(auc, 4),
        "error_estandar": round(ee, 4),
        "ic95": [round(max(0.0, auc - 1.96 * ee), 4), round(min(1.0, auc + 1.96 * ee), 4)],
        "p_valor_frente_al_azar": round(float(norm.sf(z)), 6),
    }


def prueba_delong(y_verdadero, probabilidad_a, probabilidad_b) -> dict:
    """Contrasta si dos modelos difieren en AUCROC sobre los mismos pacientes.

    Es la prueba que corresponde a un criterio de seleccion basado en AUCROC:
    compara la capacidad de ordenar a los pacientes por riesgo, sin depender
    de ningun umbral. McNemar, en cambio, compara aciertos con un umbral fijo,
    y responde a otra pregunta (ver `prueba_mcnemar`).
    """
    from scipy.stats import norm

    aucs, cov = _delong(y_verdadero, np.vstack([probabilidad_a, probabilidad_b]))
    diferencia = float(aucs[0] - aucs[1])
    varianza = float(cov[0, 0] + cov[1, 1] - 2 * cov[0, 1])
    ee = float(np.sqrt(max(varianza, 0.0)))
    if ee == 0:
        p = 1.0 if diferencia == 0 else 0.0
        z = None
    else:
        z = diferencia / ee
        p = float(2 * norm.sf(abs(z)))

    significativo = p < 0.05
    return {
        "prueba": "DeLong (AUCROC correlacionadas)",
        "aucroc_a": round(float(aucs[0]), 4),
        "aucroc_b": round(float(aucs[1]), 4),
        "diferencia": round(diferencia, 4),
        "ic95_diferencia": [round(diferencia - 1.96 * ee, 4), round(diferencia + 1.96 * ee, 4)],
        "estadistico_z": None if z is None else round(z, 4),
        "p_valor": round(p, 4),
        "p_valor_completo": p,
        "interpretacion": (
            "Las AUCROC difieren de forma estadisticamente significativa (p < 0,05)."
            if significativo
            else "Sin evidencia de diferencia entre las AUCROC (p >= 0,05); "
            "la eleccion entre ambos se decide por la sensibilidad."
        ),
    }


def prueba_mcnemar(y_verdadero, prediccion_a, prediccion_b) -> dict:
    """Contrasta si dos clasificadores difieren en sus aciertos con un umbral.

    Compara solo los casos discordantes: aquellos que un modelo clasifica bien
    y el otro mal. Con pocos discordantes se usa la version binomial exacta,
    que no depende de la aproximacion asintotica de la chi-cuadrado.

    No decide la seleccion: el criterio es el AUCROC y su contraste es DeLong.
    McNemar se reporta como complemento, porque responde a algo que el AUCROC
    no dice: si los dos modelos, con el umbral de decision, alertarian sobre
    los mismos pacientes o sobre pacientes distintos.
    """
    from scipy.stats import binomtest, chi2

    acierta_a = np.asarray(prediccion_a) == np.asarray(y_verdadero)
    acierta_b = np.asarray(prediccion_b) == np.asarray(y_verdadero)

    b = int(np.sum(acierta_a & ~acierta_b))  # solo A acierta
    c = int(np.sum(~acierta_a & acierta_b))  # solo B acierta
    discordantes = b + c

    if discordantes == 0:
        return {
            "discordantes": 0,
            "prueba": "no aplicable",
            "p_valor": None,
            "interpretacion": "Ambos modelos aciertan y fallan en los mismos casos.",
        }

    if discordantes < 25:
        p = float(binomtest(b, discordantes, 0.5).pvalue)
        prueba = "binomial exacta"
        estadistico = None
    else:
        # Correccion de continuidad de Edwards.
        estadistico = float((abs(b - c) - 1) ** 2 / discordantes)
        p = float(chi2.sf(estadistico, df=1))
        prueba = "chi-cuadrado con correccion de continuidad"

    significativo = p < 0.05
    return {
        "discordantes": discordantes,
        "solo_acierta_a": b,
        "solo_acierta_b": c,
        "prueba": prueba,
        "estadistico": None if estadistico is None else round(estadistico, 4),
        "p_valor": round(p, 4),
        "interpretacion": (
            "Diferencia estadisticamente significativa (p < 0,05)."
            if significativo
            else "Sin evidencia de diferencia significativa (p >= 0,05); "
            "la eleccion entre ambos se decide por la sensibilidad."
        ),
    }


# ---------------------------------------------------------------------------
# Salidas
# ---------------------------------------------------------------------------
def tabla_markdown(resultados: list[ResultadoModelo], mejor: str) -> str:
    """Tabla comparativa lista para pegar en el pre informe."""
    lineas = [
        "| Algoritmo | Exactitud | Sensibilidad | Especificidad | F1-score | AUCROC |",
        "| :--- | :---: | :---: | :---: | :---: | :---: |",
    ]
    for r in sorted(resultados, key=lambda x: x.aucroc_cv, reverse=True):
        marca = " **(seleccionado)**" if r.nombre == mejor else ""
        celdas = []
        for metrica in ("exactitud", "sensibilidad", "especificidad", "f1", "aucroc"):
            m = r.cv[metrica]
            celdas.append(f"{m['media']:.3f} ± {m['desviacion']:.3f}")
        lineas.append(f"| {r.nombre}{marca} | " + " | ".join(celdas) + " |")
    return "\n".join(lineas)


def guardar_artefactos(
    resultados: list[ResultadoModelo],
    mejor: ResultadoModelo,
    pipeline_ganador,
    contraste: dict,
    contexto: dict,
    sufijo: str = "",
) -> None:
    import joblib

    DIR_MODELOS.mkdir(parents=True, exist_ok=True)
    DIR_PROCESSED.mkdir(parents=True, exist_ok=True)

    # El pipeline incluye la preparacion: en inferencia recibe la fila cruda y
    # aplica exactamente las mismas transformaciones del entrenamiento.
    ruta_modelo = DIR_MODELOS / f"risk_model{sufijo}_v1.pkl"
    joblib.dump(pipeline_ganador, ruta_modelo)

    # La procedencia viaja con el modelo. El microservicio la lee y la devuelve
    # en cada prediccion, de modo que un resultado obtenido con datos simulados
    # no pueda presentarse como si viniera de historias clinicas reales.
    ficha = {
        "algoritmo": mejor.nombre,
        "hiperparametros": mejor.hiperparametros,
        "entrenado_el": date.today().isoformat(),
        "origen_datos": contexto["origen_datos"],
        "datos_reales": contexto["origen_datos"] != ORIGEN_SIMULADO,
        "filas_entrenamiento": contexto["filas_entrenamiento"],
        "aucroc_validacion_cruzada": mejor.aucroc_cv,
        "sensibilidad_validacion_cruzada": mejor.sensibilidad_cv,
        "metricas_prueba": mejor.prueba,
        "cumple_meta_aucroc": mejor.aucroc_cv >= META_AUCROC,
        "semilla": SEMILLA,
        # Importancia global del modelo, no atribucion por paciente.
        "factores_influyentes": contexto["factores"],
        # Referencia de la explicacion individual con SHAP (RF06).
        "fondo_shap": contexto["fondo_shap"],
    }
    ruta_ficha = DIR_MODELOS / f"risk_model{sufijo}_v1.json"
    ruta_ficha.write_text(
        json.dumps(ficha, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    log.info("Ficha del modelo guardada en %s", ruta_ficha)

    reporte = {
        "fecha": date.today().isoformat(),
        "semilla": SEMILLA,
        **contexto,
        "modelo_seleccionado": mejor.nombre,
        "cumple_meta_aucroc": mejor.aucroc_cv >= META_AUCROC,
        "meta_aucroc": META_AUCROC,
        # Contraste que decide la seleccion: DeLong sobre las AUCROC.
        "contraste_auc_delong": contraste,
        "resultados": [asdict(r) for r in resultados],
    }
    ruta_reporte = DIR_PROCESSED / f"reporte_modelado{sufijo}.json"
    ruta_reporte.write_text(
        json.dumps(reporte, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    ruta_tabla = DIR_PROCESSED / f"tabla_comparativa{sufijo}.md"
    ruta_tabla.write_text(
        "# Comparacion de algoritmos (validacion cruzada estratificada de "
        f"{contexto['pliegues']} pliegues)\n\n"
        + tabla_markdown(resultados, mejor.nombre)
        + "\n",
        encoding="utf-8",
    )

    log.info("Modelo guardado en %s", ruta_modelo)
    log.info("Reporte guardado en %s", ruta_reporte)
    log.info("Tabla comparativa guardada en %s", ruta_tabla)


# ---------------------------------------------------------------------------
# Orquestacion
# ---------------------------------------------------------------------------
def ejecutar(
    ruta_entrada: Path,
    test_size: float = 0.20,
    pliegues: int = 5,
    con_busqueda: bool = True,
    incluir_xgboost: bool = True,
    origen_datos: str = "extraccion documental (Anexo n.o 04)",
    sufijo: str = "",
) -> tuple[list[ResultadoModelo], ResultadoModelo]:
    reporte_prep = ReporteDePreparacion()

    df = cargar_datos(ruta_entrada)
    validar_esquema(df)
    df = limpiar(df, reporte_prep)
    df = derivar_variables(df, reporte_prep)

    numericas = [*preprocess.NUMERICAS, *reporte_prep.caracteristicas_derivadas]
    X = df[[*numericas, *preprocess.ORDINALES, *preprocess.NOMINALES]]
    y = df[COL_OBJETIVO]

    conteo = y.value_counts().sort_index()
    if conteo.min() < pliegues:
        raise ValueError(
            f"La clase minoritaria tiene {conteo.min()} casos y no admite "
            f"{pliegues} pliegues estratificados. Amplie la extraccion del "
            f"Anexo n.o 04 o reduzca --pliegues."
        )

    X_train, X_test, y_train, y_test = dividir_estratificado(X, y, test_size)
    log.info(
        "Particion estratificada: %d entrenamiento / %d prueba | clases %s",
        len(X_train),
        len(X_test),
        conteo.to_dict(),
    )

    resultados: list[ResultadoModelo] = []
    pipelines: dict[str, object] = {}

    for nombre, (estimador, rejilla) in catalogo_de_modelos(incluir_xgboost).items():
        resultado, pipeline = evaluar_modelo(
            nombre, estimador, rejilla, X_train, y_train,
            numericas, pliegues, con_busqueda,
        )
        resultado.prueba = evaluar_en_prueba(pipeline, X_test, y_test)
        resultados.append(resultado)
        pipelines[nombre] = pipeline

    ordenados = sorted(
        resultados, key=lambda r: (r.aucroc_cv, r.sensibilidad_cv), reverse=True
    )

    # El contraste entre los dos mejores se hace sobre las predicciones fuera
    # de pliegue del ENTRENAMIENTO, no sobre el conjunto de prueba. Si la
    # prueba interviniera en la seleccion, dejaria de ser una estimacion
    # independiente del desempeño del modelo elegido.
    contraste_decisiones: dict = {"prueba": "no aplicable"}
    if len(ordenados) >= 2:
        primero, segundo = ordenados[0], ordenados[1]
        particion = StratifiedKFold(n_splits=pliegues, shuffle=True, random_state=SEMILLA)
        fuera_de_pliegue = {
            r.nombre: cross_val_predict(
                clone(pipelines[r.nombre]), X_train, y_train,
                cv=particion, method="predict_proba", n_jobs=-1,
            )[:, 1]
            for r in (primero, segundo)
        }
        contraste = prueba_delong(
            y_train, fuera_de_pliegue[primero.nombre], fuera_de_pliegue[segundo.nombre]
        )
        contraste_decisiones = prueba_mcnemar(
            y_train,
            (fuera_de_pliegue[primero.nombre] >= UMBRAL_DECISION).astype(int),
            (fuera_de_pliegue[segundo.nombre] >= UMBRAL_DECISION).astype(int),
        )
        for c in (contraste, contraste_decisiones):
            c["modelo_a"] = primero.nombre
            c["modelo_b"] = segundo.nombre
            c["datos"] = "predicciones fuera de pliegue del conjunto de entrenamiento"
        contraste_decisiones["umbral"] = UMBRAL_DECISION
        log.info("DeLong %s vs %s: diferencia %.4f, p = %.4f",
                 primero.nombre, segundo.nombre, contraste["diferencia"], contraste["p_valor"])
    else:
        contraste = {"prueba": "no aplicable", "interpretacion": "Un solo modelo."}

    mejor = seleccionar_mejor(ordenados, contraste)
    log.info("Modelo seleccionado: %s", mejor.nombre)

    # Desempeño del elegido en la prueba reservada, con su intervalo: es la
    # unica cifra que el conjunto de prueba aporta, y la aporta una sola vez.
    auc_prueba = intervalo_auc(
        y_test, pipelines[mejor.nombre].predict_proba(X_test)[:, 1]
    )
    log.info("AUCROC en prueba: %.4f (IC95 %s); p frente al azar = %.6f",
             auc_prueba["aucroc"], auc_prueba["ic95"], auc_prueba["p_valor_frente_al_azar"])

    log.info("Calculando la importancia de las variables por permutacion...")
    factores = importancia_de_variables(pipelines[mejor.nombre], X_test, y_test)
    log.info(
        "Variables mas influyentes: %s",
        ", ".join(f["variable"] for f in factores[:4]),
    )

    guardar_artefactos(
        resultados,
        mejor,
        pipelines[mejor.nombre],
        contraste,
        {
            "filas_analizadas": int(len(df)),
            "filas_entrenamiento": int(len(X_train)),
            "filas_prueba": int(len(X_test)),
            "distribucion_clases": {str(k): int(v) for k, v in conteo.items()},
            "pliegues": pliegues,
            "busqueda_de_hiperparametros": con_busqueda,
            "algoritmos_comparados": len(resultados),
            "origen_datos": origen_datos,
            "perfil": preprocess.PERFIL_ACTUAL,
            "variables": list(X.columns),
            "contraste_decisiones_mcnemar": contraste_decisiones,
            "aucroc_prueba_con_intervalo": auc_prueba,
            "factores": factores,
            "fondo_shap": fondo_de_referencia(pipelines[mejor.nombre], X_train),
        },
        sufijo=sufijo,
    )
    return resultados, mejor


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Comparacion de algoritmos predictivos del incumplimiento (OE3)."
    )
    parser.add_argument("--entrada", type=Path, default=DIR_RAW / "dataset_clinico.csv")
    parser.add_argument("--test-size", type=float, default=0.20)
    parser.add_argument("--pliegues", type=int, default=5)
    parser.add_argument(
        "--sin-busqueda", action="store_true",
        help="Omite el ajuste de hiperparametros y usa los valores por defecto.",
    )
    parser.add_argument(
        "--sin-xgboost", action="store_true",
        help="Excluye XGBoost; produce un modelo que no lo necesita en produccion.",
    )
    parser.add_argument(
        "--generar-muestra", type=int, metavar="N",
        help="Genera N filas sinteticas y ejecuta sobre ellas (solo prueba tecnica).",
    )
    parser.add_argument(
        "--perfil", choices=list(preprocess.PERFILES), default="clinico",
        help="Esquema de variables segun la fuente: 'clinico' para la ficha del "
             "Anexo n.o 04, 'endes' para los microdatos del INEI. El perfil "
             "reducido escribe sus artefactos con el sufijo _endes.",
    )
    args = parser.parse_args(argv)

    preprocess.aplicar_perfil(args.perfil)

    # La consola de Windows usa cp1252 por defecto y rompe el simbolo +/- de
    # la tabla. Los archivos generados ya se escriben en UTF-8.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    entrada = args.entrada
    origen = ORIGEN_ENDES if args.perfil == "endes" else "extraccion documental (Anexo n.o 04)"
    if args.generar_muestra:
        entrada = generar_muestra_sintetica(
            args.generar_muestra, DIR_RAW / "demostracion_simulada.csv"
        )
        origen = ORIGEN_SIMULADO

    # Las rejillas incluyen combinaciones que algunos modelos descartan; los
    # avisos de convergencia no aportan nada al reporte.
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)

    try:
        resultados, mejor = ejecutar(
            entrada, args.test_size, args.pliegues,
            con_busqueda=not args.sin_busqueda,
            incluir_xgboost=not args.sin_xgboost,
            origen_datos=origen,
            sufijo=SUFIJO_PERFIL[args.perfil],
        )
    except (FileNotFoundError, ValueError) as exc:
        log.error("%s", exc)
        return 1

    print("\n--- Comparacion de algoritmos (validacion cruzada estratificada) ---\n")
    print(tabla_markdown(resultados, mejor.nombre))
    print(f"\nModelo seleccionado: {mejor.nombre}")
    print(f"AUCROC en validacion cruzada: {mejor.aucroc_cv:.4f} "
          f"(meta >= {META_AUCROC})")
    print(f"AUCROC en el conjunto de prueba: {mejor.prueba['aucroc']:.4f}")

    ruta = DIR_PROCESSED / f"reporte_modelado{SUFIJO_PERFIL[args.perfil]}.json"
    reporte = json.loads(ruta.read_text(encoding="utf-8"))
    d = reporte["contraste_auc_delong"]
    if "diferencia" in d:
        print(f"\nDeLong {d['modelo_a']} vs {d['modelo_b']} (fuera de pliegue): "
              f"diferencia {d['diferencia']:+.4f}, IC95 {d['ic95_diferencia']}, "
              f"p = {d['p_valor']:.4f}")
        m = reporte["contraste_decisiones_mcnemar"]
        print(f"McNemar con umbral {m.get('umbral')}: {m.get('discordantes')} discordantes, "
              f"p = {m.get('p_valor')}")
    a = reporte["aucroc_prueba_con_intervalo"]
    print(f"AUCROC en prueba con IC95: {a['aucroc']} {a['ic95']}; "
          f"p frente al azar = {a['p_valor_frente_al_azar']}")

    if mejor.aucroc_cv < META_AUCROC:
        print(
            "\nATENCION: ningun algoritmo alcanza la meta de AUCROC >= "
            f"{META_AUCROC} fijada en la hipotesis. Antes de reportarlo revise "
            "el tamano de la muestra y la calidad de las variables extraidas."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
