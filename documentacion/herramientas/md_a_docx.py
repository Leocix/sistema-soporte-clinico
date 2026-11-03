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
# Por defecto el pre informe al 50 %; otro corte se indica como argumento:
#     python ../herramientas/md_a_docx.py Pre_informe_65.md
ORIGEN = RAIZ / (sys.argv[1] if len(sys.argv) > 1 else "Pre_informe_final.md")
DESTINO = ORIGEN.with_suffix(".docx")

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
        # Los fragmentos de codigo NO cambian de tipografia: el documento usa
        # una sola fuente en todo el cuerpo, y una segunda familia —aunque sea
        # monoespaciada y correcta tipograficamente— rompe el formato
        # institucional. Se distinguen en cursiva, que si respeta la fuente.
        if mono:
            run.italic = True


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

    # Mínimo de cada columna: su palabra más larga debe caber entera. Sin esto
    # una columna de estado partía «Conforme» en «Conform» y «e». Se usa el
    # cuerpo de 8 a 9 puntos de las tablas (unas 0,075 pulgadas por letra) y
    # se limita, para que una ruta de archivo no se lleve media tabla.
    minimos = []
    for i in range(columnas):
        palabras = [p for f in filas if i < len(f) for p in re.split(r"[\s/]+", f[i].replace("*", "").replace("`", ""))]
        larga = max((len(p) for p in palabras), default=0)
        minimos.append(max(MIN_COL, min(larga * 0.075 + 0.14, 1.5)))

    # Se sube al mínimo lo que quede por debajo y se descuenta de las columnas
    # que tengan holgura, repitiendo hasta que todas cumplan.
    for _ in range(columnas):
        deficit = sum(m - a for a, m in zip(anchos, minimos) if a < m)
        if deficit <= 0:
            break
        holgadas = [i for i, a in enumerate(anchos) if a > minimos[i]]
        if not holgadas:
            break
        sobrante = sum(anchos[i] - minimos[i] for i in holgadas)
        for i in holgadas:
            anchos[i] -= min(deficit, sobrante) * (anchos[i] - minimos[i]) / sobrante
        anchos = [max(a, m) for a, m in zip(anchos, minimos)]

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
# Tipografía y color: una sola familia, un solo color
# ---------------------------------------------------------------------------
# El formato institucional usa Times New Roman en negro. Cualquier fuente o
# color que se cuele —la de un tema de Word, la de un encabezado heredado de la
# plantilla, la de un fragmento de codigo— se corrige al final, de una vez,
# sobre el documento ya construido. Es mas fiable que recordarlo en cada run.
FUENTE = "Times New Roman"
NEGRO = RGBColor(0, 0, 0)


def _fijar_fuente(run) -> None:
    run.font.name = FUENTE
    run.font.color.rgb = NEGRO
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(rfonts)
    # `ascii` y `hAnsi` cubren el texto latino; `cs` y `eastAsia` evitan que
    # Word sustituya la fuente en los simbolos (✔, –, «») que usan las tablas.
    for atributo in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(atributo), FUENTE)


def uniformar(doc) -> None:
    """Deja todo el documento en una sola fuente y en negro."""
    normal = doc.styles["Normal"]
    normal.font.name = FUENTE
    normal.font.color.rgb = NEGRO

    for parrafo in doc.paragraphs:
        for run in parrafo.runs:
            _fijar_fuente(run)
    for tabla in doc.tables:
        for fila in tabla.rows:
            for celda in fila.cells:
                for parrafo in celda.paragraphs:
                    for run in parrafo.runs:
                        _fijar_fuente(run)


# ---------------------------------------------------------------------------
# Conversión del cuerpo
# ---------------------------------------------------------------------------
def _ya_hay_salto(doc) -> bool:
    """Evita duplicar el salto que la plantilla ya trae al final de la portada."""
    ultimo = doc.paragraphs[-1]
    return 'w:br' in ultimo._p.xml and 'type="page"' in ultimo._p.xml


def insertar_imagen(doc, ruta: Path, pie: str) -> None:
    """Imagen centrada con su pie debajo.

    Las capturas del celular son verticales: a todo el ancho ocuparian dos
    paginas, asi que se limitan por alto y no por ancho.
    """
    from docx.shared import Cm
    from PIL import Image

    with Image.open(ruta) as img:
        ancho, alto = img.size
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    if ruta.parent.name in ("grafos", "codigo", "evidencia"):
        # Un grafo de flujo se lee por sus números y rótulos: se le da la
        # página casi entera en vez del tamaño de una captura de celular.
        alto_cm = min(19.0, 15.5 * alto / ancho)
        p.add_run().add_picture(str(ruta), height=Cm(alto_cm))
    elif alto > ancho * 1.3:
        p.add_run().add_picture(str(ruta), height=Cm(12))
    else:
        p.add_run().add_picture(str(ruta), width=Cm(min(15.5, 15.5 * ancho / 1366 + 4)))
    if pie:
        leyenda = doc.add_paragraph()
        leyenda.alignment = WD_ALIGN_PARAGRAPH.CENTER
        leyenda.paragraph_format.space_after = Pt(12)
        escribir_inline(leyenda, pie, base_cursiva=True)
        for run in leyenda.runs:
            run.font.size = Pt(10)


def _con_continuacion(lineas: list[str], i: int, texto: str) -> tuple[str, int]:
    """Une al elemento de lista las lineas sangradas que lo continuan.

    Sin esto, un paso escrito en dos lineas del Markdown salia en Word como
    dos parrafos: el numero en uno y el resto de la frase en otro.
    """
    i += 1
    partes = [texto]
    while i < len(lineas):
        linea = lineas[i]
        if not linea.strip() or not linea.startswith((" ", "\t")):
            break
        if re.match(r"^\s*([-*]\s+|\d+\.\s+)", linea):
            break
        partes.append(linea.strip())
        i += 1
    return " ".join(partes), i


def convertir(doc, markdown: str, base: Path | None = None) -> None:
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

        # Imagen: ![pie](ruta relativa al .md)
        imagen = re.match(r"^!\[(.*)\]\((.+)\)$", crudo)
        if imagen:
            insertar_imagen(doc, (base or Path.cwd()) / imagen.group(2), imagen.group(1))
            i += 1
            continue

        # Encabezados
        titulo = re.match(r"^(#{1,4})\s+(.*)$", crudo)
        if titulo:
            nivel, texto = len(titulo.group(1)), titulo.group(2)
            # Las secciones mayores (I. RESULTADOS, II. REFERENCIAS, ANEXOS)
            # empiezan en pagina nueva, como en el modelo de la Escuela.
            if nivel == 1 and doc.paragraphs and not _ya_hay_salto(doc):
                doc.add_page_break()
            p = doc.add_paragraph(style=f"Heading {nivel}")
            escribir_inline(p, texto)
            i += 1
            continue

        # Lista con viñeta
        if re.match(r"^[-*]\s+", crudo):
            texto, i = _con_continuacion(lineas, i, re.sub(r"^[-*]\s+", "", crudo))
            p = doc.add_paragraph(style="List Paragraph")
            p.paragraph_format.left_indent = Pt(24)
            escribir_inline(p, texto)
            p.runs and setattr(p.runs[0], "text", "•  " + p.runs[0].text)
            continue

        # Lista numerada
        numerada = re.match(r"^(\d+)\.\s+(.*)$", crudo)
        if numerada:
            texto, i = _con_continuacion(lineas, i, numerada.group(2))
            p = doc.add_paragraph(style="List Paragraph")
            p.paragraph_format.left_indent = Pt(24)
            escribir_inline(p, f"{numerada.group(1)}.  {texto}")
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
            if (not siguiente or siguiente.startswith(("#", "|", ">", "---", "!["))
                    or re.match(r"^([-*]\s+|\d+\.\s+)", siguiente)):
                break
            parrafo.append(siguiente)
            i += 1

        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(8)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        # El rótulo de una tabla no debe quedar solo al pie de una página.
        if parrafo[0].startswith("**Tabla "):
            p.paragraph_format.keep_with_next = True
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

    # La portada y la informacion general vienen de la plantilla; se actualizan
    # con lo que declara el Markdown. El titulo importa especialmente: el
    # formato institucional exige que identifique por nombre el lugar donde se
    # ejecuta la investigacion, y el de la plantilla decia solo "consultorio de
    # medicina interna".
    fuente = ORIGEN.read_text(encoding="utf-8")
    fecha = re.search(r"\d{1,2} de \w+ de \d{4}", fuente)
    fecha = fecha.group(0) if fecha else "08 de septiembre de 2026"
    encontrado = re.search(
        r"\*\*2\. Título del informe de tesis\*\*\s+([^\n]+)", fuente
    )
    titulo = encontrado.group(1).strip() if encontrado else None

    for hijo in hijos[:corte]:
        if not hijo.tag.endswith("}p"):
            continue
        texto = texto_de(hijo)
        if re.fullmatch(r"\d{1,2} de \w+ de \d{4}", texto):
            reemplazar_texto(hijo, fecha)
        elif texto.rstrip().rstrip(",").strip() == "Chiclayo":
            # El año NO se escribe aqui. La plantilla trae un control de
            # contenido llamado «Año de sustentación» incrustado en esta misma
            # linea, y `Paragraph.text` no lo ve porque vive dentro de un
            # `w:sdt`. Escribir «Chiclayo, 2026» dejaba el año dos veces
            # seguidas en la portada: el que escribiamos y el del control.
            reemplazar_texto(hijo, "Chiclayo, ")
        elif titulo and texto.lower().startswith("sistema de soporte clínico"):
            # Aparece dos veces: en la portada y en el punto 2 de la
            # informacion general.
            reemplazar_texto(hijo, titulo)

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

    # El indice y los anexos NO se generan desde el Markdown:
    #
    # - El indice es una tabla de contenido automatica de Word, insertada a
    #   mano en el documento. Lleva numeros de pagina y se actualiza con F9;
    #   una lista con viñetas escrita aqui la duplicaria.
    # - Los anexos se arman en Word porque son capturas e imagenes, que el
    #   Markdown no puede aportar. La relacion de anexos del Markdown queda
    #   como inventario de trabajo, no como contenido del entregable.
    cuerpo_md = md[marca:]
    inicio = cuerpo_md.find("# I. RESULTADOS")
    if inicio > 0:
        cuerpo_md = cuerpo_md[inicio:]
    fin = cuerpo_md.find("# ANEXOS")
    if fin > 0:
        cuerpo_md = cuerpo_md[:fin]

    convertir(doc, cuerpo_md)
    uniformar(doc)

    doc.save(str(DESTINO))
    print(f"Generado: {DESTINO.name}")
    d = Document(str(DESTINO))
    print(f"  párrafos: {len(d.paragraphs)} · tablas: {len(d.tables)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
