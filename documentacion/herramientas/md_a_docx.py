# -*- coding: utf-8 -*-
"""Convierte el pre informe en Markdown a Word conservando el formato USAT.

No genera el documento desde cero: **parte de la plantilla institucional** que
ya trae la portada de la universidad, la sección de información general y los
estilos de encabezado del modelo entregado por la Escuela. Se conserva todo lo
anterior al índice y se sustituye el cuerpo, de modo que el formato exigido por
el subcriterio 1.6 no dependa de que yo lo reproduzca a mano.
"""
from __future__ import annotations

import re
import sys
from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

RAIZ = Path(r"C:\Users\Leona\OneDrive\Desktop\Sistema-Soporte-Clinico\documentacion\01_preinforme")
PLANTILLA = RAIZ / "Pre_informe_40.docx"
ORIGEN = RAIZ / "Pre_informe_50.md"
DESTINO = RAIZ / "Pre_informe_50.docx"

# Ancho útil de la página, en pulgadas, para repartir las columnas de las tablas.
ANCHO_UTIL = 6.3
MIN_COL = 0.62


# ---------------------------------------------------------------------------
# Texto en línea: negrita, cursiva, código y enlaces
# ---------------------------------------------------------------------------
TROZO = re.compile(
    r"(\*\*\*.+?\*\*\*|\*\*.+?\*\*|(?<!\*)\*(?!\*).+?(?<!\*)\*(?!\*)"
    r"|`[^`]+`|\[[^\]]+\]\([^)]+\))",
    re.S,
)


def escribir_inline(parrafo, texto: str, base_negrita=False, base_cursiva=False):
    """Vuelca `texto` en el párrafo respetando el marcado de Markdown."""
    for trozo in TROZO.split(texto):
        if not trozo:
            continue

        negrita, cursiva, mono = base_negrita, base_cursiva, False
        contenido = trozo

        if trozo.startswith("***") and trozo.endswith("***"):
            escribir_inline(parrafo, trozo[3:-3], True, True)
            continue
        elif trozo.startswith("**") and trozo.endswith("**"):
            # Recursivo: la negrita puede contener cursiva, y en este informe la
            # contiene a menudo (los subtitulos de sprint llevan el nombre de la
            # fase de CRISP-DM en cursiva dentro de la negrita).
            escribir_inline(parrafo, trozo[2:-2], True, base_cursiva)
            continue
        elif trozo.startswith("*") and trozo.endswith("*"):
            escribir_inline(parrafo, trozo[1:-1], base_negrita, True)
            continue
        elif trozo.startswith("`") and trozo.endswith("`"):
            contenido, mono = trozo[1:-1], True
        else:
            enlace = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", trozo)
            if enlace:
                etiqueta, url = enlace.group(1), enlace.group(2)
                # El enlace se deja legible en papel: el texto y, si aporta, la
                # dirección. Un hipervínculo azul no sirve en un documento
                # impreso, que es como se evalúa este informe.
                contenido = etiqueta if url.startswith("#") or url in etiqueta else f"{etiqueta} ({url})"

        # El marcado anidado dentro de un trozo ya resuelto se limpia.
        contenido = contenido.replace("**", "").replace("`", "")

        run = parrafo.add_run(contenido)
        run.bold = negrita or None
        run.italic = cursiva or None
        if mono:
            run.font.name = "Consolas"
            run.font.size = Pt(9.5)
            rpr = run._element.get_or_add_rPr()
            rfonts = rpr.find(qn("w:rFonts"))
            if rfonts is None:
                rfonts = rpr.makeelement(qn("w:rFonts"), {})
                rpr.append(rfonts)
            rfonts.set(qn("w:ascii"), "Consolas")
            rfonts.set(qn("w:hAnsi"), "Consolas")


# ---------------------------------------------------------------------------
# Tablas
# ---------------------------------------------------------------------------
def separar_celdas(linea: str) -> list[str]:
    return [c.strip() for c in linea.strip().strip("|").split("|")]


def es_separador(linea: str) -> bool:
    return bool(re.fullmatch(r"\|[\s:|-]+\|", linea.strip()))


def alineaciones(linea: str) -> list[int]:
    modos = []
    for celda in separar_celdas(linea):
        izq, der = celda.startswith(":"), celda.endswith(":")
        if izq and der:
            modos.append(WD_ALIGN_PARAGRAPH.CENTER)
        elif der:
            modos.append(WD_ALIGN_PARAGRAPH.RIGHT)
        else:
            modos.append(WD_ALIGN_PARAGRAPH.LEFT)
    return modos


def repartir_anchos(filas: list[list[str]], columnas: int) -> list[float]:
    """Reparte el ancho por el contenido, garantizando un mínimo a cada columna.

    Sin el mínimo, una columna corta —un número de fila, un `✔`— queda tan
    estrecha que Word parte su encabezado letra a letra, y una columna larga se
    lleva todo el ancho restante.
    """
    pesos = []
    for i in range(columnas):
        largos = [len(f[i]) for f in filas if i < len(f)]
        pesos.append(max(sum(largos) / max(len(largos), 1), max(largos or [1]) ** 0.5))

    total = sum(pesos) or 1
    anchos = [ANCHO_UTIL * p / total for p in pesos]

    # Se sube al mínimo lo que quede por debajo y se descuenta de las columnas
    # que tengan holgura, repitiendo hasta que todas cumplan.
    for _ in range(columnas):
        deficit = sum(MIN_COL - a for a in anchos if a < MIN_COL)
        if deficit <= 0:
            break
        holgadas = [i for i, a in enumerate(anchos) if a > MIN_COL]
        if not holgadas:
            break
        sobrante = sum(anchos[i] - MIN_COL for i in holgadas)
        for i in holgadas:
            anchos[i] -= deficit * (anchos[i] - MIN_COL) / sobrante
        anchos = [max(a, MIN_COL) for a in anchos]

    escala = ANCHO_UTIL / sum(anchos)
    return [a * escala for a in anchos]


def insertar_tabla(doc, bloque: list[str]) -> None:
    encabezado = separar_celdas(bloque[0])
    modos = alineaciones(bloque[1])
    cuerpo = [separar_celdas(l) for l in bloque[2:] if l.strip()]
    columnas = len(encabezado)

    tabla = doc.add_table(rows=1, cols=columnas)
    try:
        tabla.style = doc.styles["Table Grid"]
    except KeyError:
        pass
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    tabla.autofit = False

    # Una tabla ancha en vertical no cabe a 9 puntos: el registro de
    # incidencias tiene siete columnas de texto corrido y, sin bajar el cuerpo,
    # Word parte las palabras en columnas de dos caracteres.
    cuerpo_letra = Pt(8) if columnas >= 6 else Pt(9)

    def pintar(celda, texto, modo, negrita=False):
        p = celda.paragraphs[0]
        p.alignment = modo
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        escribir_inline(p, texto.replace("<br>", " "), base_negrita=negrita)
        for run in p.runs:
            run.font.size = cuerpo_letra

    for i, texto in enumerate(encabezado):
        pintar(tabla.rows[0].cells[i], texto, modos[i] if i < len(modos) else 0, negrita=True)

    for fila in cuerpo:
        celdas = tabla.add_row().cells
        for i in range(columnas):
            pintar(celdas[i], fila[i] if i < len(fila) else "", modos[i] if i < len(modos) else 0)

    from docx.shared import Inches
    anchos = repartir_anchos([encabezado] + cuerpo, columnas)
    for fila in tabla.rows:
        for i, celda in enumerate(fila.cells):
            celda.width = Inches(anchos[i])

    # Sombreado del encabezado, para que la tabla se lea de un vistazo.
    for celda in tabla.rows[0].cells:
        tcpr = celda._tc.get_or_add_tcPr()
        sombra = tcpr.makeelement(qn("w:shd"), {})
        sombra.set(qn("w:val"), "clear")
        sombra.set(qn("w:fill"), "E8EEF4")
        tcpr.append(sombra)


# ---------------------------------------------------------------------------
# Conversión del cuerpo
# ---------------------------------------------------------------------------
def convertir(doc, markdown: str) -> None:
    lineas = markdown.split("\n")
    i = 0
    while i < len(lineas):
        linea = lineas[i]
        crudo = linea.strip()

        if not crudo or crudo in {"---", "***", "___"}:
            i += 1
            continue

        # Tabla
        if crudo.startswith("|") and i + 1 < len(lineas) and es_separador(lineas[i + 1]):
            bloque = []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                bloque.append(lineas[i])
                i += 1
            insertar_tabla(doc, bloque)
            doc.add_paragraph()
            continue

        # Encabezados
        titulo = re.match(r"^(#{1,4})\s+(.*)$", crudo)
        if titulo:
            nivel, texto = len(titulo.group(1)), titulo.group(2)
            p = doc.add_paragraph(style=f"Heading {nivel}")
            escribir_inline(p, texto)
            i += 1
            continue

        # Lista con viñeta
        if re.match(r"^[-*]\s+", crudo):
            p = doc.add_paragraph(style="List Paragraph")
            p.paragraph_format.left_indent = Pt(24)
            escribir_inline(p, re.sub(r"^[-*]\s+", "", crudo))
            p.runs and setattr(p.runs[0], "text", "•  " + p.runs[0].text)
            i += 1
            continue

        # Lista numerada
        numerada = re.match(r"^(\d+)\.\s+(.*)$", crudo)
        if numerada:
            p = doc.add_paragraph(style="List Paragraph")
            p.paragraph_format.left_indent = Pt(24)
            escribir_inline(p, f"{numerada.group(1)}.  {numerada.group(2)}")
            i += 1
            continue

        # Cita
        if crudo.startswith(">"):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Pt(24)
            escribir_inline(p, crudo.lstrip("> ").strip(), base_cursiva=True)
            i += 1
            continue

        # Párrafo corriente: se unen las líneas hasta el siguiente corte.
        parrafo = [crudo]
        i += 1
        while i < len(lineas):
            siguiente = lineas[i].strip()
            if (not siguiente or siguiente.startswith(("#", "|", ">", "---"))
                    or re.match(r"^([-*]\s+|\d+\.\s+)", siguiente)):
                break
            parrafo.append(siguiente)
            i += 1

        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(8)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        escribir_inline(p, " ".join(parrafo))


# ---------------------------------------------------------------------------
# Montaje sobre la plantilla institucional
# ---------------------------------------------------------------------------
def main() -> int:
    if not PLANTILLA.exists():
        print(f"Falta la plantilla: {PLANTILLA}", file=sys.stderr)
        return 1

    doc = Document(str(PLANTILLA))
    cuerpo = doc.element.body

    # Se conserva todo lo anterior al índice —portada e información general— y
    # se retira el resto: es el cuerpo que vamos a reponer desde el Markdown.
    from docx.text.paragraph import Paragraph

    def texto_de(hijo) -> str:
        """Texto del parrafo.

        Se usa la API de python-docx y no `itertext` de lxml: sobre un `w:p` de
        OOXML, `itertext` recorre nodos que repiten el contenido y devuelve el
        texto duplicado, lo que hacia fallar en silencio las sustituciones de
        la portada.
        """
        return Paragraph(hijo, doc).text.strip()

    def reemplazar_texto(hijo, nuevo_texto: str) -> None:
        """Sustituye el texto conservando el formato del primer fragmento."""
        p = Paragraph(hijo, doc)
        if not p.runs:
            p.add_run(nuevo_texto)
            return
        p.runs[0].text = nuevo_texto
        for run in p.runs[1:]:
            run.text = ""

    hijos = list(cuerpo.iterchildren())
    corte = None
    for n, hijo in enumerate(hijos):
        if hijo.tag.endswith("}p"):
            texto = texto_de(hijo).upper()
            if texto.startswith("ÍNDICE") or texto.startswith("INDICE"):
                corte = n
                break
    if corte is None:
        print("No se encontró el ÍNDICE en la plantilla.", file=sys.stderr)
        return 1

    ultimo_parrafo = None
    for hijo in hijos[corte:]:
        # El último `sectPr` guarda márgenes y tamaño de página: no se toca.
        if hijo.tag.endswith("}sectPr"):
            continue
        cuerpo.remove(hijo)

    # Se actualiza la portada al corte que este documento evidencia.
    for hijo in hijos[:corte]:
        if not hijo.tag.endswith("}p"):
            continue
        texto = texto_de(hijo)
        if re.fullmatch(r"\d{1,2} de \w+ de \d{4}", texto):
            reemplazar_texto(hijo, "08 de septiembre de 2026")
        elif texto.rstrip().rstrip(",").strip() == "Chiclayo":
            reemplazar_texto(hijo, "Chiclayo, 2026")

    # Cuerpo nuevo: desde el índice del Markdown hasta el final.
    md = ORIGEN.read_text(encoding="utf-8")
    marca = md.find("# ÍNDICE")
    if marca < 0:
        print("No se encontró '# ÍNDICE' en el Markdown.", file=sys.stderr)
        return 1

    # El estado del avance vive en la información general del Markdown y no en
    # la plantilla; se antepone para no perderlo. En vez de crear un encabezado
    # suelto se clona el último epígrafe numerado de la plantilla —«Fecha de
    # presentación»— y se le cambia el texto: así hereda la numeración
    # automática de Word y aparece como el punto 6, en lugar de un «6.» escrito
    # a mano que se desalinearía si la plantilla cambiara.
    inicio_estado = md.find("**6. Estado del avance**")
    if 0 < inicio_estado < marca:
        modelo = None
        for hijo in hijos[:corte]:
            if hijo.tag.endswith("}p") and Paragraph(hijo, doc).style.name == "List Paragraph":
                modelo = hijo
        if modelo is not None:
            clon = deepcopy(modelo)
            # `sectPr` tiene que seguir siendo el último hijo del cuerpo: es
            # donde viven los márgenes y el tamaño de página. Un `append` lo
            # dejaría detrás y Word descartaría el párrafo sin avisar.
            cierre = cuerpo.find(qn("w:sectPr"))
            if cierre is not None:
                cierre.addprevious(clon)
            else:
                cuerpo.append(clon)
            reemplazar_texto(clon, "Estado del avance")
        else:
            convertir(doc, "#### 6. Estado del avance")
        convertir(doc, md[inicio_estado:marca].replace("**6. Estado del avance**", ""))

    convertir(doc, md[marca:])

    doc.save(str(DESTINO))
    print(f"Generado: {DESTINO.name}")
    d = Document(str(DESTINO))
    print(f"  párrafos: {len(d.paragraphs)} · tablas: {len(d.tables)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
