"""Arma los anexos de pruebas a partir de la evidencia.

    python armar_anexos.py

- Caja negra: completa `plantilla_caja_negra.md` con los resultados de la
  última ejecución (`caja_negra/resultados_caja_negra.csv`) y las fechas de
  las ejecuciones conservadas, y escribe `Pruebas_caja_negra.md`.
- Ambos anexos se convierten a Word con el formato del informe (Times New
  Roman, negro) mediante `herramientas/md_a_anexo.py`.

Las tablas de resultados no se escriben a mano: salen del CSV que produce el
script de pruebas, de modo que el anexo no puede contradecir la evidencia.
"""
from __future__ import annotations

import csv
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
NEGRA = AQUI / "caja_negra"
CONVERSOR = AQUI.parent / "herramientas" / "md_a_anexo.py"

GRUPOS = OrderedDict([
    ("RF01", "RF01 · Autenticación con perfil diferenciado"),
    ("RF02", "RF02 · Registro y gestión del paciente polimedicado"),
    ("RF03", "RF03 · Registro de tomas y ventana de registro"),
    ("RF04", "RF04 y RF06 · Predicción de riesgo y explicación (componente de IA)"),
    ("RF05", "RF05 · Alertas tempranas"),
    ("RF07", "RF07 · Reportes generales"),
    ("RF09", "RF09 · Acompañamiento familiar"),
    ("RF10", "RF10 · Recuperación de contraseña"),
    ("RNF01", "RNF01 · Seguridad y protección"),
    ("RNF02", "RNF02 · Desempeño"),
    ("Descarga", "Descarga de la aplicación"),
])


def fecha(archivo: Path) -> str:
    primera = archivo.read_text(encoding="utf-8").splitlines()[0]
    return primera.split("·")[0].replace("Ejecución:", "").strip()


def celda(texto: str) -> str:
    return texto.replace("|", "/").replace("\n", " ").strip()


def tablas_caja_negra() -> tuple[str, str]:
    with open(NEGRA / "resultados_caja_negra.csv", encoding="utf-8-sig") as f:
        filas = list(csv.DictReader(f))
    por_grupo: dict[str, list[dict]] = OrderedDict((g, []) for g in GRUPOS)
    for fila in filas:
        clave = fila["Requisito"].split()[0]
        por_grupo.setdefault(clave, []).append(fila)

    partes = []
    for clave, lista in por_grupo.items():
        if not lista:
            continue
        partes.append(f"### {GRUPOS.get(clave, clave)}\n")
        partes.append("| ID | Técnica | Caso y entrada | Resultado esperado | Resultado obtenido | Estado |")
        partes.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for f in lista:
            caso = f"{f['Caso']}. *Entrada:* {f['Entrada']}"
            partes.append("| " + " | ".join(celda(x) for x in (
                f["ID"], f["Técnica"], caso, f["Resultado esperado"], f["Resultado obtenido"], f["Estado"])) + " |")
        partes.append("")

    total = len(filas)
    conformes = sum(f["Estado"] == "Conforme" for f in filas)
    tecnicas: dict[str, int] = {}
    for f in filas:
        base = f["Técnica"].split(" (")[0]
        tecnicas[base] = tecnicas.get(base, 0) + 1
    resumen = [
        f"Se ejecutaron **{total} casos automatizados**: **{conformes} conformes** y "
        f"**{total - conformes} no conformes**. A ellos se suman 10 casos manuales de la "
        "aplicación móvil (apartado 6), también conformes.",
        "",
        "| Técnica | Casos |",
        "| :--- | :---: |",
        *[f"| {t} | {n} |" for t, n in sorted(tecnicas.items(), key=lambda x: -x[1])],
    ]
    return "\n".join(resumen), "\n".join(partes)


def convertir(md: Path, docx: str) -> None:
    subprocess.run([sys.executable, str(CONVERSOR), str(md), docx], check=True)


def main() -> int:
    resumen, tablas = tablas_caja_negra()
    texto = (AQUI / "plantilla_caja_negra.md").read_text(encoding="utf-8")
    texto = (texto.replace("{{RESUMEN}}", resumen).replace("{{TABLAS}}", tablas)
             .replace("{{FECHA}}", fecha(NEGRA / "resultados_caja_negra.md"))
             .replace("{{FECHA_1}}", fecha(NEGRA / "ejecucion_1_resultados.md"))
             .replace("{{FECHA_2}}", fecha(NEGRA / "ejecucion_2_resultados.md")))
    destino = AQUI / "Pruebas_caja_negra.md"
    destino.write_text(texto, encoding="utf-8")
    convertir(destino, "Anexo_24_Pruebas_caja_negra.docx")
    convertir(AQUI / "Pruebas_caja_blanca.md", "Anexo_25_Pruebas_caja_blanca.docx")
    return 0


if __name__ == "__main__":
    sys.exit(main())
