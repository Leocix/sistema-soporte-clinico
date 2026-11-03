# -*- coding: utf-8 -*-
"""Convierte un anexo en Markdown a un Word independiente.

`md_a_docx.py` sirve para el pre informe: parte de la plantilla institucional y
sustituye el cuerpo a partir del indice. Los anexos son documentos sueltos y no
tienen ni plantilla ni indice, de modo que necesitan su propia entrada; lo que
comparten es el formateo, que se reutiliza tal cual.

    python ../herramientas/md_a_anexo.py ../05_manual/Manual_de_usuario.md
    python ../herramientas/md_a_anexo.py origen.md Anexo_23_Manual.docx

Sin segundo argumento el `.docx` se crea junto al `.md`, con su mismo nombre.
"""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.shared import Cm, Pt

# `md_a_docx` se importa por su formateo. Su codigo de nivel de modulo solo
# calcula rutas, y `main()` esta tras el guardia de __main__, asi que importarlo
# no genera ningun documento.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_a_docx import convertir, uniformar  # noqa: E402

FUENTE = "Times New Roman"
TAMANO = Pt(11)


def documento_base() -> Document:
    """Documento en blanco con los margenes y la fuente del informe."""
    doc = Document()
    for seccion in doc.sections:
        seccion.top_margin = Cm(2.5)
        seccion.bottom_margin = Cm(2.5)
        seccion.left_margin = Cm(3.0)
        seccion.right_margin = Cm(2.5)

    normal = doc.styles["Normal"]
    normal.font.name = FUENTE
    normal.font.size = TAMANO
    normal.paragraph_format.space_after = Pt(6)
    return doc


def main(argv: list[str] | None = None) -> int:
    argumentos = sys.argv[1:] if argv is None else argv
    if not argumentos:
        print(__doc__, file=sys.stderr)
        return 2

    origen = Path(argumentos[0]).resolve()
    if not origen.exists():
        print(f"No existe {origen}", file=sys.stderr)
        return 1

    destino = (
        origen.parent / argumentos[1] if len(argumentos) > 1 else origen.with_suffix(".docx")
    )

    doc = documento_base()
    convertir(doc, origen.read_text(encoding="utf-8"), base=origen.parent)
    uniformar(doc)

    try:
        doc.save(str(destino))
    except PermissionError:
        print(f"{destino.name} esta abierto en Word; cierrelo y repita.", file=sys.stderr)
        return 1

    generado = Document(str(destino))
    print(f"Generado: {destino.name} "
          f"({len(generado.paragraphs)} parrafos, {len(generado.tables)} tablas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
