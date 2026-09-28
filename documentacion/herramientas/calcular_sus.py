"""Calcula el puntaje de la escala SUS a partir de las respuestas (OE5).

La escala SUS [Brooke, 1996] tiene diez afirmaciones que se responden de 1
(totalmente en desacuerdo) a 5 (totalmente de acuerdo). El puntaje **no** es el
promedio de las respuestas: los impares aportan (respuesta - 1), los pares
aportan (5 - respuesta), y la suma se multiplica por 2,5 para llevarla a una
escala de 0 a 100. Hacerlo a mano es la forma habitual de equivocarse.

    python calcular_sus.py ../02_instrumentos/Respuestas_SUS.csv

El archivo lleva una fila por participante:

    participante,perfil,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10
    M-01,medico,4,2,5,1,4,2,5,1,4,2

Devuelve el puntaje de cada participante, el promedio por perfil y el promedio
general, con su interpretacion y la comparacion con la meta del proyecto
(>= 80 puntos).
"""
from __future__ import annotations

import argparse
import csv
import statistics
import sys
from pathlib import Path

META = 80.0
AFIRMACIONES = 10


def puntaje(respuestas: list[int]) -> float:
    """Puntaje SUS de un participante, de 0 a 100."""
    if len(respuestas) != AFIRMACIONES:
        raise ValueError(f"Se esperaban {AFIRMACIONES} respuestas y llegaron {len(respuestas)}.")
    if any(r < 1 or r > 5 for r in respuestas):
        raise ValueError("Cada respuesta va de 1 a 5.")

    suma = 0
    for posicion, respuesta in enumerate(respuestas, start=1):
        suma += (respuesta - 1) if posicion % 2 else (5 - respuesta)
    return suma * 2.5


def interpretar(valor: float) -> str:
    """Interpretacion habitual del puntaje SUS."""
    if valor >= 85:
        return "excelente"
    if valor >= 72:
        return "bueno"
    if valor >= 51:
        return "aceptable"
    return "deficiente"


def leer(ruta: Path) -> list[dict]:
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        filas = list(csv.DictReader(archivo))
    if not filas:
        raise ValueError("El archivo no tiene respuestas.")

    participantes = []
    for numero, fila in enumerate(filas, start=2):
        try:
            respuestas = [int(fila[f"p{i}"]) for i in range(1, AFIRMACIONES + 1)]
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"Fila {numero}: faltan respuestas o no son numeros ({error}).") from error
        participantes.append({
            "participante": fila.get("participante", f"fila {numero}"),
            "perfil": (fila.get("perfil") or "sin perfil").strip().lower(),
            "puntaje": puntaje(respuestas),
        })
    return participantes


def informe(participantes: list[dict]) -> str:
    lineas = ["| Participante | Perfil | Puntaje SUS | Interpretación |",
              "| :--- | :--- | :---: | :--- |"]
    for p in participantes:
        lineas.append(f"| {p['participante']} | {p['perfil']} | {p['puntaje']:.1f} | "
                      f"{interpretar(p['puntaje'])} |")

    perfiles = sorted({p["perfil"] for p in participantes})
    if len(perfiles) > 1:
        lineas.append("")
        lineas.append("| Perfil | Participantes | Promedio |")
        lineas.append("| :--- | :---: | :---: |")
        for perfil in perfiles:
            puntajes = [p["puntaje"] for p in participantes if p["perfil"] == perfil]
            lineas.append(f"| {perfil} | {len(puntajes)} | {statistics.mean(puntajes):.1f} |")

    todos = [p["puntaje"] for p in participantes]
    promedio = statistics.mean(todos)
    lineas.append("")
    lineas.append(f"**Promedio general: {promedio:.1f} puntos** ({interpretar(promedio)}); "
                  f"meta del proyecto: {META:.0f}. "
                  f"{'Se alcanza.' if promedio >= META else 'No se alcanza.'}")
    if len(todos) > 1:
        lineas.append(f"Rango: {min(todos):.1f} – {max(todos):.1f}; "
                      f"desviación estándar: {statistics.stdev(todos):.1f}.")
    return "\n".join(lineas)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Puntaje SUS a partir de las respuestas (OE5).")
    parser.add_argument("archivo", type=Path, help="CSV con una fila por participante.")
    args = parser.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    try:
        participantes = leer(args.archivo)
    except (OSError, ValueError) as error:
        print(f"No se pudo calcular: {error}", file=sys.stderr)
        return 1

    print(informe(participantes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
