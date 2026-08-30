"""Preparacion de datos del modelo predictivo de incumplimiento terapeutico.

Fase *Data Preparation* de CRISP-DM (Sprint 2, semanas 3-4). Automatiza el
recorrido que va desde la ficha de recoleccion en bruto (Anexo n.o 04) hasta
las matrices listas para la fase de *Modeling*:

    raw/dataset_clinico.csv
        -> validacion de esquema y criterios de elegibilidad
        -> saneamiento de valores fuera de rango
        -> ingenieria de caracteristicas
        -> particion estratificada entrenamiento / prueba
        -> imputacion de nulos + codificacion + escalado (ajustados en train)
        -> balanceo de clases con SMOTE (solo en train)
        -> processed/*.csv + preprocesador serializado + reporte JSON

Decision metodologica central
-----------------------------
La particion estratificada se ejecuta ANTES de imputar, codificar y balancear.
El imputador, el codificador y el escalador se ajustan unicamente con el
subconjunto de entrenamiento, y SMOTE se aplica tambien solo a ese
subconjunto. Si se balanceara el conjunto completo, las muestras sinteticas
derivadas de registros de prueba se filtrarian al entrenamiento y las metricas
(AUCROC, sensibilidad, F1-score) quedarian infladas, invalidando la
comparacion de algoritmos exigida por OE3.

Uso
---
    python src/preprocess.py --entrada data/raw/dataset_clinico.csv
    python src/preprocess.py --generar-muestra 200   # verificacion del flujo
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("preprocess")

RAIZ = Path(__file__).resolve().parents[1]
DIR_RAW = RAIZ / "data" / "raw"
DIR_PROCESSED = RAIZ / "data" / "processed"
DIR_MODELOS = RAIZ / "models"

# ---------------------------------------------------------------------------
# Esquema del Anexo n.o 04 (dimensiones del modelo de adherencia de la OMS)
# ---------------------------------------------------------------------------
COL_ID = "codigo_paciente"
COL_OBJETIVO = "incumplimiento"

NUMERICAS = [
    "edad",                       # dimension paciente
    "tiempo_enfermedad_anios",    # dimension enfermedad
    "comorbilidades",             # dimension enfermedad
    "numero_farmacos",            # dimension terapia
    "tomas_dia",                  # dimension terapia
    "controles_programados_6m",   # dimension sistema de salud
    "controles_perdidos_6m",      # dimension sistema de salud
]
ORDINALES = {"nivel_socioeconomico": ["bajo", "medio", "alto"]}
NOMINALES = ["sexo", "aseguramiento", "zona_residencia", "diagnostico"]

# El puntaje de Morisky es la fuente de la variable objetivo (0 = adherente,
# 1 = incumplimiento). No se usa como predictor: hacerlo introduciria fuga de
# informacion, pues determina por completo la etiqueta.
COL_MORISKY = "puntaje_morisky"

COLUMNAS_REQUERIDAS = [COL_ID, *NUMERICAS, *ORDINALES, *NOMINALES, COL_OBJETIVO]

# Rangos plausibles: un valor fuera de rango se marca como nulo y se imputa,
# en lugar de descartar al paciente y perder el resto de sus variables.
RANGOS_VALIDOS = {
    "edad": (18, 120),
    "tiempo_enfermedad_anios": (0, 80),
    "comorbilidades": (0, 15),
    "numero_farmacos": (0, 30),
    "tomas_dia": (1, 20),
    "controles_programados_6m": (0, 30),
    "controles_perdidos_6m": (0, 30),
}

CATEGORIAS_VALIDAS = {
    "sexo": ["M", "F"],
    "nivel_socioeconomico": ["bajo", "medio", "alto"],
    "aseguramiento": ["sis", "essalud", "ninguno"],
    "zona_residencia": ["urbana", "rural"],
    "diagnostico": ["hta", "dm2", "ambas"],
}

MIN_FARMACOS_POLIMEDICADO = 5
SEMILLA = 42


@dataclass
class ReporteDePreparacion:
    """Trazabilidad de cada transformacion, adjuntable como evidencia."""

    filas_originales: int = 0
    duplicados_eliminados: int = 0
    excluidos_por_elegibilidad: int = 0
    excluidos_sin_objetivo: int = 0
    filas_finales: int = 0
    valores_fuera_de_rango: dict = field(default_factory=dict)
    nulos_por_columna: dict = field(default_factory=dict)
    porcentaje_nulos_total: float = 0.0
    caracteristicas_derivadas: list = field(default_factory=list)
    distribucion_clases_original: dict = field(default_factory=dict)
    ratio_desbalance_original: float = 0.0
    filas_entrenamiento_antes_smote: int = 0
    filas_entrenamiento_despues_smote: int = 0
    muestras_sinteticas_generadas: int = 0
    distribucion_clases_train_balanceado: dict = field(default_factory=dict)
    filas_prueba: int = 0
    n_caracteristicas_finales: int = 0
    nombres_caracteristicas: list = field(default_factory=list)

    def a_json(self, ruta: Path) -> None:
        ruta.write_text(
            json.dumps(self.__dict__, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        log.info("Reporte de preparacion guardado en %s", ruta)


# ---------------------------------------------------------------------------
# 1. Carga y validacion
# ---------------------------------------------------------------------------
def cargar_datos(ruta: Path) -> pd.DataFrame:
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontro el dataset en {ruta}. Extraiga los registros con la "
            f"ficha del Anexo n.o 04 o ejecute --generar-muestra para una prueba "
            f"del flujo."
        )
    df = pd.read_csv(ruta)
    log.info("Dataset cargado: %d filas x %d columnas", len(df), df.shape[1])
    return df


def validar_esquema(df: pd.DataFrame) -> None:
    faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in df.columns]
    if faltantes:
        raise ValueError(
            "El dataset no cumple el esquema del Anexo n.o 04. "
            f"Columnas faltantes: {', '.join(faltantes)}"
        )
    log.info("Esquema validado contra el Anexo n.o 04 (%d variables)", len(COLUMNAS_REQUERIDAS))


# ---------------------------------------------------------------------------
# 2. Limpieza
# ---------------------------------------------------------------------------
def limpiar(df: pd.DataFrame, reporte: ReporteDePreparacion) -> pd.DataFrame:
    reporte.filas_originales = len(df)
    df = df.copy()

    # 2.1 Un paciente, una fila. Se conserva la extraccion mas reciente.
    antes = len(df)
    df = df.drop_duplicates(subset=[COL_ID], keep="last")
    reporte.duplicados_eliminados = antes - len(df)

    # 2.2 Normalizacion de texto: minusculas y sin espacios sobrantes.
    for col in [*ORDINALES, *NOMINALES]:
        df[col] = df[col].astype("string").str.strip().str.lower()
    if "sexo" in df.columns:
        df["sexo"] = df["sexo"].str.upper()

    # 2.3 Categorias no previstas -> nulo (se imputan mas adelante).
    for col, validas in CATEGORIAS_VALIDAS.items():
        invalidas = ~df[col].isin(validas) & df[col].notna()
        if invalidas.any():
            reporte.valores_fuera_de_rango[col] = int(invalidas.sum())
            df.loc[invalidas, col] = pd.NA

    # 2.4 Valores numericos fuera del rango plausible -> nulo.
    for col, (minimo, maximo) in RANGOS_VALIDOS.items():
        df[col] = pd.to_numeric(df[col], errors="coerce")
        fuera = ((df[col] < minimo) | (df[col] > maximo)) & df[col].notna()
        if fuera.any():
            reporte.valores_fuera_de_rango[col] = (
                reporte.valores_fuera_de_rango.get(col, 0) + int(fuera.sum())
            )
            df.loc[fuera, col] = np.nan

    # 2.5 Se devuelven las categoricas a dtype object con np.nan: los
    #     imputadores de scikit-learn no interpretan el pd.NA de las columnas
    #     de tipo "string".
    for col in [*ORDINALES, *NOMINALES]:
        df[col] = df[col].astype(object).where(df[col].notna(), np.nan)

    # 2.6 Incoherencia clinica: no se puede faltar a mas controles de los
    #     programados. Se anula el dato erroneo, no el paciente.
    incoherentes = df["controles_perdidos_6m"] > df["controles_programados_6m"]
    if incoherentes.any():
        reporte.valores_fuera_de_rango["controles_perdidos_6m_incoherentes"] = int(
            incoherentes.sum()
        )
        df.loc[incoherentes, "controles_perdidos_6m"] = np.nan

    # 2.7 Criterio de elegibilidad del Anexo n.o 04: polimedicacion.
    antes = len(df)
    df = df[df["numero_farmacos"].fillna(0) >= MIN_FARMACOS_POLIMEDICADO]
    reporte.excluidos_por_elegibilidad = antes - len(df)

    # 2.8 Sin etiqueta no hay aprendizaje supervisado posible.
    antes = len(df)
    df[COL_OBJETIVO] = pd.to_numeric(df[COL_OBJETIVO], errors="coerce")
    df = df[df[COL_OBJETIVO].isin([0, 1])]
    reporte.excluidos_sin_objetivo = antes - len(df)
    df[COL_OBJETIVO] = df[COL_OBJETIVO].astype(int)

    reporte.filas_finales = len(df)
    log.info(
        "Limpieza: %d -> %d filas (duplicados=%d, no elegibles=%d, sin objetivo=%d)",
        reporte.filas_originales,
        reporte.filas_finales,
        reporte.duplicados_eliminados,
        reporte.excluidos_por_elegibilidad,
        reporte.excluidos_sin_objetivo,
    )
    if df.empty:
        raise ValueError("No quedaron registros validos tras la limpieza.")
    return df.reset_index(drop=True)


def perfilar_nulos(df: pd.DataFrame, reporte: ReporteDePreparacion) -> None:
    """Documenta la ausencia de datos antes de imputar (evidencia de OE1/OE3)."""
    columnas = [*NUMERICAS, *ORDINALES, *NOMINALES]
    nulos = df[columnas].isna().sum()
    reporte.nulos_por_columna = {
        c: {"n": int(n), "porcentaje": round(100 * n / len(df), 2)}
        for c, n in nulos.items()
        if n > 0
    }
    reporte.porcentaje_nulos_total = round(
        100 * float(nulos.sum()) / (len(df) * len(columnas)), 2
    )
    log.info(
        "Valores faltantes: %.2f %% de las celdas; %d variables afectadas",
        reporte.porcentaje_nulos_total,
        len(reporte.nulos_por_columna),
    )


# ---------------------------------------------------------------------------
# 3. Ingenieria de caracteristicas
# ---------------------------------------------------------------------------
def derivar_variables(df: pd.DataFrame, reporte: ReporteDePreparacion) -> pd.DataFrame:
    """Deriva indicadores que la literatura asocia al incumplimiento.

    Las tres variables construidas expresan la carga terapeutica y la
    desvinculacion del seguimiento, dos de los factores de incumplimiento
    priorizados en el diagnostico del consultorio (OE1).
    """
    df = df.copy()

    # Complejidad del regimen: dosis diarias totales que el paciente maneja.
    df["carga_terapeutica"] = df["numero_farmacos"] * df["tomas_dia"]
    # Fraccion de controles a los que el paciente no asistio.
    df["tasa_inasistencia"] = np.where(
        df["controles_programados_6m"] > 0,
        df["controles_perdidos_6m"] / df["controles_programados_6m"],
        np.nan,
    )
    # Anios de enfermedad por decada de vida: cronicidad relativa a la edad.
    df["cronicidad_relativa"] = df["tiempo_enfermedad_anios"] / (df["edad"] / 10)

    derivadas = ["carga_terapeutica", "tasa_inasistencia", "cronicidad_relativa"]
    reporte.caracteristicas_derivadas = derivadas
    log.info("Caracteristicas derivadas: %s", ", ".join(derivadas))
    return df


# ---------------------------------------------------------------------------
# 4. Preprocesador reutilizable en inferencia
# ---------------------------------------------------------------------------
def construir_preprocesador(numericas: list[str]) -> ColumnTransformer:
    """Imputacion + codificacion + escalado en un unico artefacto serializable.

    Se serializa junto al modelo para que la inferencia en produccion (RF04)
    aplique exactamente la misma transformacion que el entrenamiento; de lo
    contrario se produce el desfase entre entrenamiento y servicio.
    """
    # Mediana: robusta ante los valores extremos de conteo de farmacos.
    rama_numerica = Pipeline(
        [("imputar", SimpleImputer(strategy="median")),
         # El escalado es indispensable para SVM y Regresion Logistica; es
         # inocuo para Random Forest y XGBoost, que son invariantes a escala.
         ("escalar", StandardScaler())]
    )
    rama_ordinal = Pipeline(
        [("imputar", SimpleImputer(strategy="most_frequent")),
         ("codificar", OrdinalEncoder(categories=[ORDINALES["nivel_socioeconomico"]]))]
    )
    rama_nominal = Pipeline(
        [("imputar", SimpleImputer(strategy="most_frequent")),
         ("codificar", OneHotEncoder(handle_unknown="ignore", drop="if_binary",
                                     sparse_output=False))]
    )
    return ColumnTransformer(
        [
            ("num", rama_numerica, numericas),
            ("ord", rama_ordinal, list(ORDINALES)),
            ("nom", rama_nominal, NOMINALES),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


# ---------------------------------------------------------------------------
# 5. Particion y balanceo
# ---------------------------------------------------------------------------
def dividir_estratificado(
    X: pd.DataFrame, y: pd.Series, test_size: float
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Particion estratificada: conserva la prevalencia real en ambos lados."""
    return train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=SEMILLA, shuffle=True
    )


def balancear_con_smote(
    X_train: np.ndarray, y_train: pd.Series, reporte: ReporteDePreparacion
) -> tuple[np.ndarray, np.ndarray]:
    """Aplica SMOTE sobre el conjunto de entrenamiento ya transformado.

    La clase minoritaria del problema es el incumplimiento, justamente la que
    el sistema debe detectar. Sin balanceo, un clasificador puede alcanzar una
    exactitud alta prediciendo siempre "adherente" y una sensibilidad cercana a
    cero, resultado inservible como alerta temprana (RF05).
    """
    try:
        from imblearn.over_sampling import SMOTE
    except ImportError as exc:  # pragma: no cover - dependencia declarada
        raise SystemExit(
            "Falta la dependencia imbalanced-learn. Instale con:\n"
            "    pip install -r requirements.txt"
        ) from exc

    conteo = y_train.value_counts().to_dict()
    minoritaria = min(conteo.values())
    reporte.filas_entrenamiento_antes_smote = int(len(y_train))

    # k_neighbors no puede superar el numero de vecinos disponibles en la
    # clase minoritaria; con muestras pequenas se ajusta a la baja.
    k = max(1, min(5, minoritaria - 1))
    if minoritaria < 2:
        raise ValueError(
            "La clase minoritaria tiene menos de 2 casos en entrenamiento; "
            "SMOTE no es aplicable. Amplie la extraccion del Anexo n.o 04."
        )
    if k < 5:
        log.warning("Clase minoritaria pequena (%d): k_neighbors ajustado a %d", minoritaria, k)

    X_bal, y_bal = SMOTE(random_state=SEMILLA, k_neighbors=k).fit_resample(X_train, y_train)

    reporte.filas_entrenamiento_despues_smote = int(len(y_bal))
    reporte.muestras_sinteticas_generadas = int(len(y_bal) - len(y_train))
    reporte.distribucion_clases_train_balanceado = {
        str(k_): int(v) for k_, v in pd.Series(y_bal).value_counts().sort_index().items()
    }
    log.info(
        "SMOTE: %d -> %d filas de entrenamiento (%d sinteticas); distribucion %s",
        reporte.filas_entrenamiento_antes_smote,
        reporte.filas_entrenamiento_despues_smote,
        reporte.muestras_sinteticas_generadas,
        reporte.distribucion_clases_train_balanceado,
    )
    return X_bal, np.asarray(y_bal)


# ---------------------------------------------------------------------------
# 6. Orquestacion
# ---------------------------------------------------------------------------
def ejecutar_pipeline(
    ruta_entrada: Path, test_size: float = 0.20, aplicar_smote: bool = True
) -> ReporteDePreparacion:
    import joblib

    reporte = ReporteDePreparacion()

    df = cargar_datos(ruta_entrada)
    validar_esquema(df)
    df = limpiar(df, reporte)
    perfilar_nulos(df, reporte)
    df = derivar_variables(df, reporte)

    numericas = [*NUMERICAS, *reporte.caracteristicas_derivadas]
    X = df[[*numericas, *ORDINALES, *NOMINALES]]
    y = df[COL_OBJETIVO]

    conteo = y.value_counts().sort_index()
    reporte.distribucion_clases_original = {str(k): int(v) for k, v in conteo.items()}
    reporte.ratio_desbalance_original = round(float(conteo.max() / conteo.min()), 2)
    log.info(
        "Distribucion de la variable objetivo: %s (ratio %.2f:1)",
        reporte.distribucion_clases_original,
        reporte.ratio_desbalance_original,
    )

    X_train, X_test, y_train, y_test = dividir_estratificado(X, y, test_size)
    log.info("Particion estratificada: %d entrenamiento / %d prueba", len(X_train), len(X_test))

    # El preprocesador se ajusta SOLO con entrenamiento; el conjunto de prueba
    # unicamente se transforma, evitando la fuga de informacion.
    preprocesador = construir_preprocesador(numericas)
    X_train_t = preprocesador.fit_transform(X_train)
    X_test_t = preprocesador.transform(X_test)
    nombres = list(preprocesador.get_feature_names_out())

    if aplicar_smote:
        X_train_t, y_train_final = balancear_con_smote(X_train_t, y_train, reporte)
    else:
        y_train_final = np.asarray(y_train)
        reporte.filas_entrenamiento_antes_smote = len(y_train)
        reporte.filas_entrenamiento_despues_smote = len(y_train)
        log.warning("SMOTE desactivado: el conjunto de entrenamiento queda desbalanceado.")

    reporte.filas_prueba = int(len(y_test))
    reporte.n_caracteristicas_finales = len(nombres)
    reporte.nombres_caracteristicas = nombres

    DIR_PROCESSED.mkdir(parents=True, exist_ok=True)
    DIR_MODELOS.mkdir(parents=True, exist_ok=True)

    train_out = pd.DataFrame(X_train_t, columns=nombres)
    train_out[COL_OBJETIVO] = y_train_final
    test_out = pd.DataFrame(X_test_t, columns=nombres)
    test_out[COL_OBJETIVO] = np.asarray(y_test)

    train_out.to_csv(DIR_PROCESSED / "train_balanceado.csv", index=False)
    test_out.to_csv(DIR_PROCESSED / "test.csv", index=False)
    joblib.dump(preprocesador, DIR_MODELOS / "preprocesador_v1.pkl")
    reporte.a_json(DIR_PROCESSED / "reporte_preparacion.json")

    log.info("Artefactos escritos en %s y %s", DIR_PROCESSED, DIR_MODELOS)
    return reporte


# ---------------------------------------------------------------------------
# Utilidad de verificacion del flujo (NO es dato clinico)
# ---------------------------------------------------------------------------
def generar_muestra_sintetica(n: int, ruta: Path) -> Path:
    """Genera un CSV artificial para comprobar que el flujo corre de extremo a
    extremo antes de disponer de la extraccion real.

    ADVERTENCIA: los datos son simulados. Sirven unicamente para verificar el
    codigo del pipeline; ningun resultado obtenido con ellos puede reportarse
    como hallazgo de la investigacion.
    """
    rng = np.random.default_rng(SEMILLA)
    farmacos = rng.integers(5, 12, n)
    tomas = rng.integers(2, 9, n)
    programados = rng.integers(2, 9, n)
    perdidos = np.minimum(rng.poisson(1.2, n), programados)

    # Etiqueta generada con una relacion latente entre carga terapeutica,
    # inasistencia y edad, mas ruido, para producir clases desbalanceadas.
    logit = (
        -4.2
        + 0.18 * farmacos
        + 0.12 * tomas
        + 1.9 * (perdidos / np.maximum(programados, 1))
        + 0.02 * rng.integers(40, 90, n)
        + rng.normal(0, 0.6, n)
    )
    objetivo = (1 / (1 + np.exp(-logit)) > 0.62).astype(int)

    df = pd.DataFrame(
        {
            COL_ID: [f"P-{i:03d}" for i in range(1, n + 1)],
            "edad": rng.integers(40, 90, n),
            "sexo": rng.choice(["M", "F"], n),
            "nivel_socioeconomico": rng.choice(["bajo", "medio", "alto"], n, p=[0.5, 0.35, 0.15]),
            "aseguramiento": rng.choice(["sis", "essalud", "ninguno"], n),
            "zona_residencia": rng.choice(["urbana", "rural"], n, p=[0.7, 0.3]),
            "diagnostico": rng.choice(["hta", "dm2", "ambas"], n, p=[0.4, 0.25, 0.35]),
            "tiempo_enfermedad_anios": np.round(rng.gamma(3, 2.2, n), 1),
            "comorbilidades": rng.integers(0, 5, n),
            "numero_farmacos": farmacos,
            "tomas_dia": tomas,
            "controles_programados_6m": programados,
            "controles_perdidos_6m": perdidos,
            COL_MORISKY: rng.integers(0, 5, n),
            COL_OBJETIVO: objetivo,
        }
    )

    # Se inyectan nulos y valores fuera de rango para ejercitar la limpieza.
    for col, frac in [("nivel_socioeconomico", 0.08), ("tiempo_enfermedad_anios", 0.12),
                      ("zona_residencia", 0.05)]:
        df.loc[df.sample(frac=frac, random_state=SEMILLA).index, col] = None
    df.loc[df.sample(n=max(1, n // 50), random_state=7).index, "edad"] = 999

    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False)
    log.warning("Muestra SINTETICA de %d filas escrita en %s (no usar en resultados)", n, ruta)
    return ruta


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Preparacion de datos (CRISP-DM) del modelo de incumplimiento terapeutico."
    )
    parser.add_argument(
        "--entrada", type=Path, default=DIR_RAW / "dataset_clinico.csv",
        help="CSV extraido con la ficha del Anexo n.o 04.",
    )
    parser.add_argument(
        "--test-size", type=float, default=0.20,
        help="Proporcion reservada para prueba (por defecto 0.20).",
    )
    parser.add_argument(
        "--sin-smote", action="store_true",
        help="Omite el balanceo; util para medir el efecto del desbalance.",
    )
    parser.add_argument(
        "--generar-muestra", type=int, metavar="N",
        help="Genera N filas sinteticas y ejecuta el flujo sobre ellas (solo prueba tecnica).",
    )
    args = parser.parse_args(argv)

    entrada = args.entrada
    if args.generar_muestra:
        entrada = generar_muestra_sintetica(
            args.generar_muestra, DIR_RAW / "SINTETICO_NO_USAR_EN_RESULTADOS.csv"
        )

    try:
        reporte = ejecutar_pipeline(entrada, args.test_size, aplicar_smote=not args.sin_smote)
    except (FileNotFoundError, ValueError) as exc:
        log.error("%s", exc)
        return 1

    print("\n--- Resumen de la preparacion de datos ---")
    print(f"Filas validas .................. {reporte.filas_finales}")
    print(f"Celdas faltantes imputadas ..... {reporte.porcentaje_nulos_total} %")
    print(f"Distribucion original .......... {reporte.distribucion_clases_original} "
          f"(ratio {reporte.ratio_desbalance_original}:1)")
    print(f"Entrenamiento tras SMOTE ....... {reporte.filas_entrenamiento_despues_smote} "
          f"{reporte.distribucion_clases_train_balanceado}")
    print(f"Prueba (sin balancear) ......... {reporte.filas_prueba}")
    print(f"Caracteristicas finales ........ {reporte.n_caracteristicas_finales}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
