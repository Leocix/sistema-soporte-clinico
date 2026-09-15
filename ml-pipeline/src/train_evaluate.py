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
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_validate
from sklearn.svm import SVC

sys.path.insert(0, str(Path(__file__).resolve().parent))

from preprocess import (  # noqa: E402
    COL_OBJETIVO,
    DIR_MODELOS,
    DIR_PROCESSED,
    DIR_RAW,
    NOMINALES,
    NUMERICAS,
    ORDINALES,
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

# Etiqueta con la que se marca un modelo entrenado sobre datos simulados.
ORIGEN_SIMULADO = "conjunto de demostracion simulado"


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

    `ordenados` va de mayor a menor AUCROC. Si la prueba de McNemar entre los
    dos primeros no encuentra diferencia significativa, el AUCROC no basta para
    preferir a uno y decide la sensibilidad: el error clinicamente costoso es
    el falso negativo —un paciente en riesgo que el sistema no detecta y que
    por tanto no recibe la alerta temprana—.
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


def prueba_mcnemar(y_verdadero, prediccion_a, prediccion_b) -> dict:
    """Contrasta si dos clasificadores difieren en sus aciertos.

    Compara solo los casos discordantes: aquellos que un modelo clasifica bien
    y el otro mal. Con pocos discordantes se usa la version binomial exacta,
    que no depende de la aproximacion asintotica de la chi-cuadrado.
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
) -> None:
    import joblib

    DIR_MODELOS.mkdir(parents=True, exist_ok=True)
    DIR_PROCESSED.mkdir(parents=True, exist_ok=True)

    # El pipeline incluye la preparacion: en inferencia recibe la fila cruda y
    # aplica exactamente las mismas transformaciones del entrenamiento.
    ruta_modelo = DIR_MODELOS / "risk_model_v1.pkl"
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
    (DIR_MODELOS / "risk_model_v1.json").write_text(
        json.dumps(ficha, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    log.info("Ficha del modelo guardada en %s", DIR_MODELOS / "risk_model_v1.json")

    reporte = {
        "fecha": date.today().isoformat(),
        "semilla": SEMILLA,
        **contexto,
        "modelo_seleccionado": mejor.nombre,
        "cumple_meta_aucroc": mejor.aucroc_cv >= META_AUCROC,
        "meta_aucroc": META_AUCROC,
        "contraste_dos_mejores": contraste,
        "resultados": [asdict(r) for r in resultados],
    }
    ruta_reporte = DIR_PROCESSED / "reporte_modelado.json"
    ruta_reporte.write_text(
        json.dumps(reporte, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    ruta_tabla = DIR_PROCESSED / "tabla_comparativa.md"
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
) -> tuple[list[ResultadoModelo], ResultadoModelo]:
    reporte_prep = ReporteDePreparacion()

    df = cargar_datos(ruta_entrada)
    validar_esquema(df)
    df = limpiar(df, reporte_prep)
    df = derivar_variables(df, reporte_prep)

    numericas = [*NUMERICAS, *reporte_prep.caracteristicas_derivadas]
    X = df[[*numericas, *ORDINALES, *NOMINALES]]
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

    if len(ordenados) >= 2:
        primero, segundo = ordenados[0], ordenados[1]
        contraste = prueba_mcnemar(
            y_test,
            pipelines[primero.nombre].predict(X_test),
            pipelines[segundo.nombre].predict(X_test),
        )
        contraste["modelo_a"] = primero.nombre
        contraste["modelo_b"] = segundo.nombre
    else:
        contraste = {"prueba": "no aplicable", "interpretacion": "Un solo modelo."}

    mejor = seleccionar_mejor(ordenados, contraste)
    log.info("Modelo seleccionado: %s", mejor.nombre)

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
            "factores": factores,
            "fondo_shap": fondo_de_referencia(pipelines[mejor.nombre], X_train),
        },
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
    args = parser.parse_args(argv)

    # La consola de Windows usa cp1252 por defecto y rompe el simbolo +/- de
    # la tabla. Los archivos generados ya se escriben en UTF-8.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    entrada = args.entrada
    origen = "extraccion documental (Anexo n.o 04)"
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

    if mejor.aucroc_cv < META_AUCROC:
        print(
            "\nATENCION: ningun algoritmo alcanza la meta de AUCROC >= "
            f"{META_AUCROC} fijada en la hipotesis. Antes de reportarlo revise "
            "el tamano de la muestra y la calidad de las variables extraidas."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
