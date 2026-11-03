"""Conjunto externo de entrenamiento a partir de la ENDES (INEI, Peru).

La extraccion documental del Anexo n.o 04 es la fuente definitiva del estudio,
pero mientras se realiza, la comparacion de algoritmos exigida por el OE3 no
tiene con que ejecutarse sobre datos reales. Este modulo resuelve ese bloqueo:
descarga los microdatos publicos de la Encuesta Demografica y de Salud Familiar
y los traduce al esquema que `preprocess.py` ya sabe leer.

    python src/endes.py --anios 2014-2017
    python src/preprocess.py --perfil endes --entrada data/raw/endes_adherencia.csv
    python src/train_evaluate.py --perfil endes --entrada data/raw/endes_adherencia.csv

Que se toma de la encuesta
--------------------------
Del modulo de salud (CSALUD01), aplicado a una persona de 15 anos o mas
seleccionada al azar en cada hogar:

===============  ==========================================================
QS23, QSSEXO     edad y sexo
QS24, QS25N      nivel educativo alcanzado
QS102 / QS109    diagnostico medico de hipertension / de diabetes
QS103U-C         tiempo transcurrido desde el diagnostico de hipertension
QS110U-C         tiempo transcurrido desde el diagnostico de diabetes
QS104 / QS111    compro medicamentos para controlar la enfermedad
QS106 / QS113    **los tomo tal cual se lo indico el medico**  -> etiqueta
QS900, QS901     peso y talla medidos -> indice de masa corporal
QS700A-I         cuestionario PHQ-9 de sintomas depresivos
QS304, QS25C1-6  catarata y limitaciones funcionales
===============  ==========================================================

Del modulo del hogar (RECH0) se toma HV012, el numero de residentes
habituales, del que se deriva si la persona vive sola o acompanada.

Que NO cubre la encuesta
------------------------
Cinco variables del Anexo n.o 04 no existen en la ENDES: `numero_farmacos`,
`tomas_dia`, `controles_programados_6m`, `controles_perdidos_6m` y
`apoyo_familiar`. Por eso el conjunto resultante se procesa con el perfil
reducido `endes` y NO sustituye al modelo del consultorio: sirve para validar
la metodologia de comparacion sobre datos reales y para fijar una linea base
nacional. El criterio de elegibilidad por polimedicacion tampoco puede
aplicarse, de modo que la poblacion es mas amplia que la del estudio.

Por que el rango por defecto llega hasta 2017
---------------------------------------------
A partir de 2018 el INEI dejo de publicar QS103U-C y QS110U-C: las columnas
siguen en el archivo pero vienen vacias. Incluir esos anios multiplica la
muestra, a costa de imputar la mitad de `tiempo_enfermedad_anios`. El rango
2014-2017 la trae completa en el 99 % de los casos, que es lo defendible ante
un jurado; `--anios 2014-2019` queda disponible para quien prefiera tamano.

Procedencia de los codigos de descarga
--------------------------------------
El portal de microdatos entrega los modulos en
`descarga/SPSS/<encuesta>-Modulo<modulo>.zip`. Los codigos del CATALOGO se
consultaron uno a uno en `cambiaPeriodo.asp` del propio portal; a partir de
2020 el INEI renumero los modulos (salud 414 -> 1640, hogar 64 -> 1629).
"""
from __future__ import annotations

import argparse
import logging
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("endes")

RAIZ = Path(__file__).resolve().parents[1]
DIR_RAW = RAIZ / "data" / "raw"
DIR_CACHE = RAIZ / "data" / "externo" / "endes"

BASE_DESCARGA = "https://proyectos.inei.gob.pe/iinei/srienaho/descarga/SPSS"

# anio -> (codigo de encuesta, modulo de salud, modulo del hogar)
CATALOGO: dict[int, tuple[int, int, int]] = {
    2014: (441, 414, 64),
    2015: (504, 414, 64),
    2016: (548, 414, 64),
    2017: (605, 414, 64),
    2018: (638, 414, 64),
    2019: (691, 414, 64),
    2020: (739, 1640, 1629),
    2021: (760, 1640, 1629),
    2022: (786, 1640, 1629),
    2023: (910, 1640, 1629),
    2024: (968, 1640, 1629),
    2025: (1038, 1640, 1629),
}

# Codigo 8 = "No sabe / no recuerda" en toda la encuesta. No es un "no": se
# trata como dato ausente para no inventar una respuesta que el informante
# explicitamente no dio.
NO_SABE = 8.0

COLUMNAS_SALUD = [
    "HHID", "QSNUMERO", "QS23", "QSSEXO", "QS24", "QS25N",
    "QS102", "QS103U", "QS103C", "QS104", "QS106",
    "QS109", "QS110U", "QS110C", "QS111", "QS113",
    "QS900", "QS901", "QS902", "QS304",
    "QS25C1", "QS25C2", "QS25C3", "QS25C4", "QS25C5", "QS25C6",
    "QS700A", "QS700B", "QS700C", "QS700D", "QS700E",
    "QS700F", "QS700G", "QS700H", "QS700I",
]
COLUMNAS_HOGAR = ["HHID", "HV012", "HV009"]

ITEMS_PHQ9 = ["QS700A", "QS700B", "QS700C", "QS700D", "QS700E",
              "QS700F", "QS700G", "QS700H", "QS700I"]
# Punto de corte habitual del PHQ-9 para sintomatologia depresiva moderada.
CORTE_PHQ9 = 10
ITEMS_LIMITACION = ["QS25C1", "QS25C2", "QS25C3", "QS25C4", "QS25C5", "QS25C6"]
IMC_OBESIDAD = 30.0


# ---------------------------------------------------------------------------
# Descarga
# ---------------------------------------------------------------------------
def ruta_modulo(anio: int, modulo: int, dir_cache: Path) -> Path:
    encuesta = CATALOGO[anio][0]
    return dir_cache / f"{encuesta}-Modulo{modulo}.zip"


def descargar(anio: int, modulo: int, dir_cache: Path) -> Path:
    """Descarga un modulo si no esta en la cache y devuelve su ruta."""
    destino = ruta_modulo(anio, modulo, dir_cache)
    if destino.exists() and zipfile.is_zipfile(destino):
        log.info("%d modulo %d: ya descargado (%.1f MB)", anio, modulo,
                 destino.stat().st_size / 1e6)
        return destino

    url = f"{BASE_DESCARGA}/{CATALOGO[anio][0]}-Modulo{modulo}.zip"
    destino.parent.mkdir(parents=True, exist_ok=True)
    log.info("%d modulo %d: descargando de %s", anio, modulo, url)
    parcial = destino.with_suffix(".parcial")
    try:
        peticion = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(peticion, timeout=300) as respuesta, \
                parcial.open("wb") as archivo:
            while bloque := respuesta.read(1 << 20):
                archivo.write(bloque)
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        parcial.unlink(missing_ok=True)
        raise RuntimeError(
            f"No se pudo descargar el modulo {modulo} de {anio} ({error}). "
            f"Compruebe la conexion o descarguelo a mano desde "
            f"https://proyectos.inei.gob.pe/microdatos/ y dejelo en {destino}."
        ) from error

    # El portal responde 200 con una pagina de error cuando el codigo no
    # existe; sin esta comprobacion el fallo aparecería mucho despues.
    if not zipfile.is_zipfile(parcial):
        parcial.unlink(missing_ok=True)
        raise RuntimeError(
            f"Lo descargado para {anio} modulo {modulo} no es un ZIP. "
            f"Es probable que el INEI haya cambiado el codigo de encuesta; "
            f"consultelo en https://proyectos.inei.gob.pe/microdatos/"
        )
    parcial.replace(destino)
    log.info("%d modulo %d: %.1f MB", anio, modulo, destino.stat().st_size / 1e6)
    return destino


def leer_sav(zip_modulo: Path, sufijo: str, columnas: list[str]) -> pd.DataFrame:
    """Lee el .sav cuyo nombre termina en `sufijo` dentro del ZIP del modulo."""
    try:
        import pyreadstat
    except ImportError as exc:  # pragma: no cover - dependencia declarada
        raise SystemExit(
            "Falta la dependencia pyreadstat, necesaria para leer los archivos "
            "SPSS del INEI. Instale con:\n    pip install -r requirements.txt"
        ) from exc

    with zipfile.ZipFile(zip_modulo) as zf:
        nombres = [n for n in zf.namelist() if n.upper().endswith(sufijo.upper())]
        if not nombres:
            raise RuntimeError(
                f"{zip_modulo.name} no contiene ningun archivo {sufijo}. "
                f"Contiene: {', '.join(zf.namelist())}"
            )
        destino = zip_modulo.parent / zip_modulo.stem
        ruta = destino / nombres[0]
        if not ruta.exists():
            zf.extract(nombres[0], destino)

    disponibles = set(pyreadstat.read_sav(ruta, metadataonly=True)[1].column_names)
    faltantes = [c for c in columnas if c not in disponibles]
    if faltantes:
        log.warning("%s no trae %s; esas variables quedaran vacias",
                    ruta.name, ", ".join(faltantes))
    df, _ = pyreadstat.read_sav(ruta, usecols=[c for c in columnas if c in disponibles])
    for columna in faltantes:
        df[columna] = np.nan
    return df


# ---------------------------------------------------------------------------
# Traduccion al esquema del Anexo n.o 04
# ---------------------------------------------------------------------------
def _nivel_educativo(fila: pd.Series) -> str | float:
    if fila["QS24"] == 2:  # nunca asistio a la escuela
        return "sin_estudios"
    nivel = fila["QS25N"]
    if pd.isna(nivel):
        return np.nan
    return {0: "sin_estudios", 1: "primaria", 2: "secundaria",
            3: "superior", 4: "superior", 5: "superior"}.get(int(nivel), np.nan)


def _anios_desde(unidad: float, cantidad: float) -> float:
    """Convierte el par unidad/cantidad de la ENDES a anios."""
    if pd.isna(unidad) or pd.isna(cantidad) or unidad == NO_SABE:
        return np.nan
    if unidad == 1:      # meses, cuando hace menos de dos anios
        return round(cantidad / 12, 2)
    if unidad == 2:      # anios
        return float(cantidad)
    return np.nan


def _imc(peso: float, talla: float, resultado: float) -> float:
    if resultado != 1 or pd.isna(peso) or pd.isna(talla) or talla <= 0:
        return np.nan
    # El INEI codifica la ausencia con valores centinela muy altos.
    if peso > 300 or talla > 250 or talla < 100:
        return np.nan
    return peso / (talla / 100) ** 2


def _comorbilidades(fila: pd.Series) -> float:
    """Cuenta las condiciones concurrentes que la encuesta permite establecer.

    No incluye la hipertension ni la diabetes: esas dos viajan en la variable
    `diagnostico`, igual que en la ficha del consultorio. El recuento es un
    minimo verificable, no el total real de comorbilidades del paciente.
    """
    total = 0

    imc = _imc(fila["QS900"], fila["QS901"], fila["QS902"])
    if not pd.isna(imc) and imc >= IMC_OBESIDAD:
        total += 1

    phq9 = fila[ITEMS_PHQ9]
    if phq9.notna().all() and phq9.sum() >= CORTE_PHQ9:
        total += 1

    if fila["QS304"] == 1:  # catarata diagnosticada
        total += 1

    # Las seis dificultades funcionales cuentan como una sola condicion: la
    # ficha del consultorio registra "limitacion funcional", no cada sentido.
    if any(fila[item] == 1 for item in ITEMS_LIMITACION):
        total += 1

    return float(total)


def _incumplimiento(fila: pd.Series, amplia: bool) -> float:
    """Variable objetivo a partir de las preguntas QS106 (HTA) y QS113 (DM).

    Definicion estricta (por defecto): incumple quien compro el medicamento y
    declara no haberlo tomado como se lo indico el medico. Es el constructo que
    mide el test de Morisky y el que predice el sistema.

    Definicion amplia: suma a la anterior a quien ni siquiera compro el
    medicamento. Reproduce el criterio del analisis nacional publicado sobre
    esta misma encuesta, util para contrastar la prevalencia.
    """
    respuestas = [fila["QS106"], fila["QS113"]]
    if amplia:
        for compro in (fila["QS104"], fila["QS111"]):
            if compro == 2:
                return 1.0
    if any(r == 2 for r in respuestas):
        return 1.0
    if any(r == 1 for r in respuestas):
        return 0.0
    return np.nan


def construir_anio(anio: int, dir_cache: Path, amplia: bool) -> pd.DataFrame:
    """Devuelve las filas utilizables de un anio de la encuesta."""
    _, mod_salud, mod_hogar = CATALOGO[anio]
    salud = leer_sav(descargar(anio, mod_salud, dir_cache), "CSALUD01.sav", COLUMNAS_SALUD)
    hogar = leer_sav(descargar(anio, mod_hogar, dir_cache), "RECH0.SAV", COLUMNAS_HOGAR)

    # La clave del hogar llega con espacios de relleno en unos anios y sin
    # ellos en otros; sin normalizarla el cruce devuelve cero coincidencias.
    for tabla in (salud, hogar):
        tabla["HHID"] = tabla["HHID"].astype(str).str.strip()
    hogar = hogar.drop_duplicates(subset=["HHID"], keep="first")

    df = salud.merge(hogar, on="HHID", how="left")

    hta = df["QS102"] == 1
    dm = df["QS109"] == 1
    df = df[hta | dm].copy()
    if df.empty:
        return df

    hta, dm = df["QS102"] == 1, df["QS109"] == 1

    salida = pd.DataFrame(index=df.index)
    salida["codigo_paciente"] = (
        "ENDES-" + str(anio) + "-" + df["HHID"].astype(str) + "-"
        + df["QSNUMERO"].fillna(0).astype(int).astype(str)
    )
    salida["edad"] = df["QS23"]
    salida["sexo"] = df["QSSEXO"].map({1.0: "M", 2.0: "F"})
    salida["nivel_educativo"] = df.apply(_nivel_educativo, axis=1)
    salida["convivencia"] = np.where(
        df["HV012"].fillna(df["HV009"]).isna(), None,
        np.where(df["HV012"].fillna(df["HV009"]) <= 1, "solo", "acompanado"),
    )
    salida["diagnostico"] = np.select(
        [hta & dm, hta, dm], ["ambas", "hta", "dm2"], default=None
    )

    anios_hta = df.apply(lambda f: _anios_desde(f["QS103U"], f["QS103C"]), axis=1)
    anios_dm = df.apply(lambda f: _anios_desde(f["QS110U"], f["QS110C"]), axis=1)
    # Con ambos diagnosticos manda el mas antiguo: es el que marca el tiempo
    # que la persona lleva conviviendo con un tratamiento cronico.
    salida["tiempo_enfermedad_anios"] = pd.concat([anios_hta, anios_dm], axis=1).max(axis=1)

    salida["comorbilidades"] = df.apply(_comorbilidades, axis=1)
    salida["incumplimiento"] = df.apply(lambda f: _incumplimiento(f, amplia), axis=1)
    salida["anio_encuesta"] = anio

    antes = len(salida)
    salida = salida[salida["incumplimiento"].notna()]
    log.info("%d: %d diagnosticados, %d con respuesta de adherencia (%d sin dato)",
             anio, antes, len(salida), antes - len(salida))

    if not salida.empty and salida["tiempo_enfermedad_anios"].notna().sum() == 0:
        log.warning(
            "%d no publica el tiempo desde el diagnostico: esas %d filas "
            "tendran que imputarse.", anio, len(salida),
        )
    return salida


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _rango(texto: str) -> list[int]:
    anios: list[int] = []
    for parte in texto.split(","):
        parte = parte.strip()
        if "-" in parte:
            desde, hasta = (int(x) for x in parte.split("-", 1))
            anios.extend(range(desde, hasta + 1))
        elif parte:
            anios.append(int(parte))
    desconocidos = [a for a in anios if a not in CATALOGO]
    if desconocidos:
        raise argparse.ArgumentTypeError(
            f"Sin codigo de descarga para {desconocidos}. "
            f"Anios disponibles: {min(CATALOGO)}-{max(CATALOGO)}."
        )
    return sorted(set(anios))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Descarga la ENDES y la traduce al esquema del Anexo n.o 04."
    )
    parser.add_argument("--anios", type=_rango, default=_rango("2014-2017"),
                        help="Anios a incluir, p. ej. 2014-2017 o 2018,2019. "
                             "Desde 2018 no se publica el tiempo desde el "
                             "diagnostico.")
    parser.add_argument("--etiqueta", choices=["estricta", "amplia"], default="estricta",
                        help="estricta: compro el medicamento y no lo tomo como se "
                             "le indico. amplia: suma a quien no lo compro.")
    parser.add_argument("--salida", type=Path, default=DIR_RAW / "endes_adherencia.csv")
    parser.add_argument("--cache", type=Path, default=DIR_CACHE,
                        help="Carpeta donde se guardan los ZIP del INEI.")
    args = parser.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    try:
        partes = [construir_anio(a, args.cache, args.etiqueta == "amplia")
                  for a in args.anios]
    except RuntimeError as error:
        log.error("%s", error)
        return 1

    df = pd.concat([p for p in partes if not p.empty], ignore_index=True)
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.salida, index=False)

    incumplen = int(df["incumplimiento"].sum())
    print(f"\n--- ENDES {args.anios[0]}-{args.anios[-1]} "
          f"(etiqueta {args.etiqueta}) ---")
    print(f"Pacientes con diagnostico y respuesta ... {len(df)}")
    print(f"Incumplimiento ......................... {incumplen} "
          f"({100 * incumplen / len(df):.1f} %)")
    print("Diagnostico ............................ "
          + ", ".join(f"{k}={v}" for k, v in df["diagnostico"].value_counts().items()))
    print(f"\nEscrito en {args.salida}")
    print(
        "\nNo cubiertas por la encuesta: numero_farmacos, tomas_dia, "
        "controles_programados_6m,\ncontroles_perdidos_6m y apoyo_familiar. "
        "Procese con el perfil reducido:\n"
        f"    python src/preprocess.py --perfil endes --entrada {args.salida}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
