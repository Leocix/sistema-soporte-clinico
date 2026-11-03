"""Arma el Word del manual: carátula, ficha del documento, índice y cuerpo.

    python generar_caratula.py
    python armar_manual.py

El cuerpo sale de `../Manual_de_usuario.md` con el mismo conversor del pre
informe (Times New Roman, negro). La carátula es la imagen que produce
`generar_caratula.py`, a página completa. El índice es una tabla de contenido
de Word; si Word está instalado, se actualiza sola al final para que el
documento quede con los números de página ya puestos.
"""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

AQUI = Path(__file__).resolve().parent
MANUAL = AQUI.parent
sys.path.insert(0, str(AQUI.parents[1] / "herramientas"))
from md_a_docx import convertir, escribir_inline, uniformar  # noqa: E402

ORIGEN = MANUAL / "Manual_de_usuario.md"
DESTINO = MANUAL / "Anexo_23_Manual_de_usuario.docx"
CARATULA = MANUAL / "capturas" / "caratula.png"


def _campo(parrafo, instruccion: str, texto: str = "") -> None:
    """Inserta un campo de Word (TOC, PAGE…) en el párrafo."""
    def run_con(elemento):
        r = OxmlElement("w:r")
        r.append(elemento)
        parrafo._p.append(r)

    inicio = OxmlElement("w:fldChar")
    inicio.set(qn("w:fldCharType"), "begin")
    run_con(inicio)
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruccion
    run_con(instr)
    separador = OxmlElement("w:fldChar")
    separador.set(qn("w:fldCharType"), "separate")
    run_con(separador)
    if texto:
        t = OxmlElement("w:t")
        t.text = texto
        run_con(t)
    fin = OxmlElement("w:fldChar")
    fin.set(qn("w:fldCharType"), "end")
    run_con(fin)


def _a4(seccion, margen_cm: float | None) -> None:
    seccion.page_width, seccion.page_height = Cm(21), Cm(29.7)
    if margen_cm is None:
        seccion.top_margin = seccion.bottom_margin = Cm(2.5)
        seccion.left_margin, seccion.right_margin = Cm(3.0), Cm(2.5)
    else:
        for lado in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
            setattr(seccion, lado, Cm(margen_cm))
        seccion.header_distance = seccion.footer_distance = Cm(0)


def _titulo_suelto(doc, texto: str) -> None:
    """Título centrado que no entra en el índice (no usa estilo de encabezado)."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(18)
    run = p.add_run(texto)
    run.bold = True
    run.font.size = Pt(16)


def main() -> int:
    if not CARATULA.exists():
        print("Falta la caratula: ejecute antes generar_caratula.py", file=sys.stderr)
        return 1

    markdown = ORIGEN.read_text(encoding="utf-8")
    # La primera línea (título) y la tabla de datos pasan a la ficha del
    # documento; el resto es el cuerpo, que empieza en «# 1.».
    inicio_cuerpo = markdown.index("\n# 1.")
    cabecera, cuerpo = markdown[:inicio_cuerpo], markdown[inicio_cuerpo:]
    tabla_datos = "\n".join(l for l in cabecera.splitlines() if l.startswith("|"))

    doc = Document()
    normal = doc.styles["Normal"]
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(6)

    # 1. Carátula a página completa.
    _a4(doc.sections[0], 0)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(0)
    p.add_run().add_picture(str(CARATULA), width=Cm(21), height=Cm(29.65))

    # 2. Ficha del documento e índice, ya con márgenes normales.
    seccion = doc.add_section(WD_SECTION.NEW_PAGE)
    _a4(seccion, None)
    pie = seccion.footer
    pie.is_linked_to_previous = False
    numero = pie.paragraphs[0]
    numero.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _campo(numero, "PAGE", "1")

    _titulo_suelto(doc, "FICHA DEL DOCUMENTO")
    convertir(doc, tabla_datos)
    nota = doc.add_paragraph()
    escribir_inline(nota, "Este manual está dividido en una sección por cada tipo de usuario: "
                          "**médico** (sección 2), **paciente y familiar** (sección 3) y "
                          "**encargado del sistema** (sección 4).")
    doc.add_page_break()

    _titulo_suelto(doc, "ÍNDICE")
    _campo(doc.add_paragraph(), r'TOC \o "1-2" \h \z \u',
           "Haga clic derecho aquí y elija «Actualizar campo» para ver el índice.")

    # 3. Cuerpo (cada «#» abre página nueva).
    convertir(doc, cuerpo, base=MANUAL)
    uniformar(doc)

    try:
        doc.save(str(DESTINO))
    except PermissionError:
        print(f"{DESTINO.name} está abierto en Word; ciérrelo y repita.", file=sys.stderr)
        return 1
    print(f"Generado: {DESTINO.name}")

    # 4. Índice con números de página, si Word está disponible.
    try:
        import win32com.client  # type: ignore
    except ImportError:
        print("Sin pywin32: abra el Word y actualice el índice (F9).")
        return 0
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    try:
        documento = word.Documents.Open(str(DESTINO))
        documento.TablesOfContents(1).Update()
        documento.Save()
        documento.Close()
        print("Índice actualizado.")
    finally:
        word.Quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
