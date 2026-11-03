"""Imagen con la salida de la última ejecución de la caja negra.

    python evidencia.py

Se construye desde `resultados_caja_negra.csv`, el mismo archivo que escribe el
script de pruebas, de modo que la imagen no puede mostrar otra cosa que lo que
la ejecución registró.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

AQUI = Path(__file__).resolve().parent


def main() -> None:
    with open(AQUI / "resultados_caja_negra.csv", encoding="utf-8-sig") as f:
        filas = list(csv.DictReader(f))
    cabecera = (AQUI / "resultados_caja_negra.md").read_text(encoding="utf-8").splitlines()[:2]
    lineas = [f"$ python ejecutar_caja_negra.py --ui", ""]
    for f in filas:
        marca = "OK " if f["Estado"] == "Conforme" else "NO "
        lineas.append(f"  {marca} {f['ID']:<6} {f['Caso'][:78]}")
    total = len(filas)
    ok = sum(f["Estado"] == "Conforme" for f in filas)
    lineas += ["", f"{ok}/{total} conformes.", *cabecera]

    fig = plt.figure(figsize=(8.6, 0.155 * len(lineas) + 0.5), facecolor="#1e1e1e")
    for k, linea in enumerate(lineas):
        color = "#7ee787" if linea.strip().startswith("OK") else (
            "#ff7b72" if linea.strip().startswith("NO") else "#e6edf3")
        fig.text(0.015, 1 - (k + 1.3) / (len(lineas) + 1.5), linea, va="center", fontsize=6.6,
                 family="DejaVu Sans Mono", color=color)
    destino = AQUI / "evidencia"
    destino.mkdir(exist_ok=True)
    fig.savefig(destino / "salida_ejecucion_final.png", dpi=190, facecolor=fig.get_facecolor(),
                bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    print("Generada:", destino / "salida_ejecucion_final.png")


if __name__ == "__main__":
    main()
