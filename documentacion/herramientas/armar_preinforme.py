"""Arma el Word final del pre informe sobre el documento editado por el autor.

    python armar_preinforme.py

Parte de `SCRUM_GUZMÁN_LEONARDO.docx` —el Word que el autor edita a mano— y
escribe `SCRUM_GUZMÁN_LEONARDO_entrega.docx` sin tocar el original:

- conserva la carátula, la información general, el índice automático y los
  anexos que el autor armó con sus imágenes;
- retira de la información general el «Estado del avance» y la «Convención de
  lectura», que no forman parte del formato institucional;
- reemplaza el cuerpo (Resultados y Referencias) por el de
  `Pre_informe_final.md`;
- agrega los anexos que faltaban, con el mismo estilo de título y de pie que
  los del autor, y deja todo en Times New Roman negro;
- actualiza el índice con Word, si está instalado.
"""
from __future__ import annotations

import re
import sys
from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm
from docx.text.paragraph import Paragraph

AQUI = Path(__file__).resolve().parent
DOC = AQUI.parent
sys.path.insert(0, str(AQUI))
from md_a_docx import _fijar_fuente, convertir  # noqa: E402

PREINFORME = DOC / "01_preinforme"
BASE = PREINFORME / "SCRUM_GUZMÁN_LEONARDO.docx"
DESTINO = PREINFORME / "SCRUM_GUZMÁN_LEONARDO_entrega.docx"
MARKDOWN = PREINFORME / "Pre_informe_final.md"
CAPTURAS = DOC / "05_manual" / "capturas"
FECHA = "3 de noviembre de 2026"

# Anexos de imágenes: (número, título, [(captura, «a) Título.», descripción)]).
ANEXOS_CAPTURAS = {
    14: ("Capturas de las alertas tempranas y su cierre", [
        ("w19_alertas.png", "Bandeja de alertas tempranas.",
         "El médico ve, sin revisar paciente por paciente, a quién debe contactar antes del "
         "próximo control, con el motivo y la cifra que sustenta cada alerta (RF05)."),
        ("w20_alerta_nota.png", "Registro de lo actuado.",
         "El médico anota qué hizo con el paciente y marca la alerta como atendida o como no aplicable."),
        ("w21_alertas_atendidas.png", "Alertas atendidas.",
         "La alerta sale de las pendientes y conserva la nota del médico como evidencia de la intervención."),
    ]),
    15: ("Capturas del control de acceso y de las validaciones", [
        ("w02_acceso_error.png", "Acceso denegado.",
         "Ante credenciales incorrectas el sistema responde con un mensaje que no revela si falló "
         "el correo o la contraseña (RNF01)."),
        ("w09_alta_validaciones.png", "Validaciones de la ficha.",
         "El formulario rechaza a un paciente con menos de cinco fármacos o con más controles perdidos "
         "que programados y explica junto a cada campo qué corregir; el dato no entra al conjunto de datos."),
        ("w23_baja_confirmar.png", "Confirmación de una acción delicada.",
         "Dar de baja a un paciente exige confirmación; su historial de tomas se conserva."),
    ]),
}

# Anexos a partir de Markdown: (número, título, archivo).
ANEXOS_MD = [
    (19, "Expediente de juicio de expertos", DOC / "02_instrumentos" / "Expediente_Expertos.md"),
    (20, "Descripción de actividades, técnicas y herramientas de desarrollo",
     PREINFORME / "anexos" / "Anexo_20_Actividades_tecnicas_herramientas.md"),
    (21, "Productos, artefactos y entregables del desarrollo",
     PREINFORME / "anexos" / "Anexo_21_Productos_artefactos.md"),
    (22, "Evidencia del modelo: comparación de algoritmos y ficha de procedencia",
     PREINFORME / "anexos" / "Anexo_22_Evidencia_modelo.md"),
    (23, "Manual de usuario del sistema", DOC / "05_manual" / "Manual_de_usuario.md"),
    (24, "Pruebas de caja negra", DOC / "07_pruebas" / "Pruebas_caja_negra.md"),
    (25, "Pruebas de caja blanca", DOC / "07_pruebas" / "Pruebas_caja_blanca.md"),
    (26, "Matriz de consistencia del proyecto", PREINFORME / "anexos" / "Anexo_26_Matriz_consistencia.md"),
]


def texto(doc, el) -> str:
    return Paragraph(el, doc).text.strip() if el.tag.endswith("}p") else ""


def estilo(doc, el) -> str:
    return Paragraph(el, doc).style.name if el.tag.endswith("}p") else ""


def hijos(doc):
    return [h for h in doc.element.body.iterchildren() if not h.tag.endswith("}sectPr")]


def agregado(doc, funcion) -> list:
    """Ejecuta `funcion`, que escribe al final del documento, y devuelve lo que añadió."""
    # Por posición y no por identidad: lxml crea un objeto Python nuevo cada vez
    # que se recorre el árbol, de modo que `id()` no sirve para reconocer un
    # elemento. Lo que `funcion` escribe queda siempre al final del cuerpo.
    antes = len(hijos(doc))
    funcion()
    nuevos = hijos(doc)[antes:]
    for el in nuevos:
        uniformar_elemento(doc, el)
    return nuevos


def uniformar_elemento(doc, el) -> None:
    for r in el.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r"):
        from docx.text.run import Run
        _fijar_fuente(Run(r, Paragraph(el, doc) if el.tag.endswith("}p") else None))


def mover_antes(elementos, destino) -> None:
    for el in elementos:
        destino.addprevious(el)


def degradar_titulos(md: str) -> str:
    """Quita el primer título y convierte los demás en párrafos en negrita.

    Los títulos de un anexo no deben entrar en el índice del informe: el
    índice lista «Anexo N°…», no las secciones internas de cada anexo.
    """
    lineas = md.splitlines()
    salida, primero = [], True
    for linea in lineas:
        m = re.match(r"^(#{1,4})\s+(.*)$", linea.strip())
        if m:
            if primero:
                primero = False
                continue
            salida.extend(["", f"**{m.group(2).replace('**', '')}**", ""])
        else:
            salida.append(linea)
    return "\n".join(salida)


def _renumerar(texto_original: str) -> str:
    def correr(m: re.Match) -> str:
        n = int(m.group(2))
        if n <= 2:
            return m.group(0)
        # Los títulos escriben «Anexo N°7»; el texto, «Anexo n.° 07».
        return m.group(1) + (str(n - 1) if "N°" in m.group(1) else str(n - 1).zfill(2))
    return REFERENCIA_ANEXO.sub(correr, texto_original)


# «Anexo N°3:» en los títulos y «Anexo n.° 04» en el texto de los anexos.
REFERENCIA_ANEXO = re.compile(r"(Anexos? (?:N°|n\.° ?))(\d{1,2})")


def retirar_anexo_de_similitud(doc) -> None:
    """Quita el Anexo N°2 (informe de similitud) y corre los números siguientes.

    El informe de similitud no forma parte de este entregable. Se retira su
    título y su contenido, hasta el título del anexo siguiente, y cada anexo
    posterior y cada referencia a él bajan un número.
    """
    lista = hijos(doc)
    inicio = next(i for i, el in enumerate(lista) if texto(doc, el).startswith("Anexo N°2:"))
    fin = next(i for i, el in enumerate(lista) if i > inicio and texto(doc, el).startswith("Anexo N°3:"))
    for el in lista[inicio:fin]:
        doc.element.body.remove(el)

    anexos = next(i for i, el in enumerate(hijos(doc))
                  if estilo(doc, el) == "Heading 1" and texto(doc, el).upper() == "ANEXOS")
    for el in hijos(doc)[anexos:]:
        for p in el.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
            parrafo = Paragraph(p, doc)
            nuevo = _renumerar(parrafo.text)
            if nuevo == parrafo.text:
                continue
            # Word parte el número entre varios runs («Anexo N°1» + «0»), de
            # modo que el texto se reúne en el primer run con contenido.
            con_texto = [r for r in parrafo.runs if r.text]
            con_texto[0].text = nuevo
            for r in con_texto[1:]:
                r.text = ""


def main() -> int:
    doc = Document(str(BASE))
    cuerpo = doc.element.body
    lista = hijos(doc)

    # --- Información general: fecha y elementos ajenos al formato ------------
    for el in lista:
        if re.fullmatch(r"\d{1,2} de \w+ de \d{4}", texto(doc, el)):
            p = Paragraph(el, doc)
            p.runs[0].text = FECHA
            for r in p.runs[1:]:
                r.text = ""
            break
    estado = next(i for i, el in enumerate(lista) if texto(doc, el) == "Estado del avance")
    indice = next(i for i, el in enumerate(lista) if el.tag.endswith("}sdt") and i > estado)
    for el in lista[estado:indice]:
        cuerpo.remove(el)

    # --- Cuerpo: se retira el anterior y se escribe el del Markdown -----------
    lista = hijos(doc)
    resultados = next(i for i, el in enumerate(lista)
                      if estilo(doc, el) == "Heading 1" and texto(doc, el).endswith("RESULTADOS"))
    anexos = next(i for i, el in enumerate(lista)
                  if estilo(doc, el) == "Heading 1" and texto(doc, el).upper() == "ANEXOS")
    seccion_anexos = lista[anexos:]
    for el in lista[resultados:]:
        cuerpo.remove(el)

    md = MARKDOWN.read_text(encoding="utf-8")
    md = md[md.index("# I. RESULTADOS"):md.index("# ANEXOS")]
    agregado(doc, lambda: convertir(doc, md))

    sect = cuerpo.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sectPr")
    for el in seccion_anexos:
        sect.addprevious(el)

    # Un párrafo con estilo de título que solo contiene una imagen entra al
    # índice automático con la imagen dentro. Se le da el estilo normal.
    for el in hijos(doc):
        if (estilo(doc, el).startswith("Heading") and not texto(doc, el)
                and el.findall(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing")):
            p = Paragraph(el, doc)
            p.style = doc.styles["Normal"]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    retirar_anexo_de_similitud(doc)

    # --- Modelos de formato tomados de los anexos del autor -------------------
    lista = hijos(doc)
    titulo_modelo = next(el for el in lista if texto(doc, el).startswith("Anexo N°13"))
    pie_modelo = next(el for el in lista if texto(doc, el).startswith("a) Pantalla de acceso"))
    antes_del_16 = next(el for el in lista if texto(doc, el).startswith("Anexo N°16"))

    def titulo(numero: int, nombre: str):
        el = deepcopy(titulo_modelo)
        p = Paragraph(el, doc)
        p.runs[0].text = f"Anexo N°{numero}: {nombre}"
        for r in p.runs[1:]:
            r.text = ""
        for dibujo in el.findall(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing"):
            dibujo.getparent().remove(dibujo)
        uniformar_elemento(doc, el)
        return el

    def pie(letra: str, rotulo: str, descripcion: str):
        el = deepcopy(pie_modelo)
        p = Paragraph(el, doc)
        p.runs[0].text = f"{letra}) {rotulo}"
        p.runs[1].text = f" {descripcion}" if len(p.runs) > 1 else ""
        for r in p.runs[2:]:
            r.text = ""
        uniformar_elemento(doc, el)
        return el

    def salto():
        def escribir():
            doc.add_page_break()
        return agregado(doc, escribir)

    def anexo_capturas(numero: int):
        nombre, figuras = ANEXOS_CAPTURAS[numero]
        bloque = salto() + [titulo(numero, nombre)]
        for k, (archivo, rotulo, descripcion) in enumerate(figuras):
            def imagen(archivo=archivo):
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.add_run().add_picture(str(CAPTURAS / archivo), width=Cm(15))
            bloque += agregado(doc, imagen)
            bloque.append(pie("abcdefgh"[k], rotulo, descripcion))
        return bloque

    def anexo_md(numero: int, nombre: str, archivo: Path):
        contenido = degradar_titulos(archivo.read_text(encoding="utf-8"))
        return salto() + [titulo(numero, nombre)] + agregado(
            doc, lambda: convertir(doc, contenido, base=archivo.parent))

    # Anexos 14 y 15 entre el 13 y el 16, donde el autor dejó el hueco.
    for numero in (14, 15):
        mover_antes(anexo_capturas(numero), antes_del_16)

    # Anexos 19 a 26 al final.
    for numero, nombre, archivo in ANEXOS_MD:
        bloque = anexo_md(numero, nombre, archivo)
        for el in bloque:
            sect.addprevious(el)

    doc.save(str(DESTINO))
    print(f"Generado: {DESTINO.name}")

    try:
        import win32com.client  # type: ignore
    except ImportError:
        print("Sin pywin32: abra el Word y actualice el índice (F9).")
        return 0
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    try:
        documento = word.Documents.Open(str(DESTINO))
        for i in range(1, documento.TablesOfContents.Count + 1):
            documento.TablesOfContents(i).Update()
        documento.Save()
        paginas = documento.ComputeStatistics(2)
        documento.Close()
        print(f"Índice actualizado · {paginas} páginas")
    finally:
        word.Quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
