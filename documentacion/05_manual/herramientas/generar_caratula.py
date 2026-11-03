"""Carátula del manual de usuario, como imagen A4.

    python generar_caratula.py

Compone el logo de la aplicación y dos capturas reales (panel y celular) sobre
una franja con los colores del sistema. Los textos se editan en DATOS; la
imagen resultante (`../capturas/caratula.png`) la inserta `armar_manual.py`
como primera página del Word.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).resolve().parent
CAPTURAS = AQUI.parent / "capturas"
LOGO = AQUI.parents[2] / "app-movil" / "herramientas" / "icono_512.png"

DATOS = {
    "sistema": "CDSS Adherencia  ·  Mi tratamiento",
    "titulo": "MANUAL DE USUARIO",
    "subtitulo": ("Sistema de soporte a la decisión clínica para la prevención del "
                  "incumplimiento terapéutico en pacientes hipertensos y diabéticos "
                  "polimedicados"),
    "roles": [("Médico", "Panel web"), ("Paciente y familiar", "Aplicación móvil"),
              ("Encargado del sistema", "Modo local y desplegado")],
    # Las capturas de la portada van sin anotaciones; las genera
    # `capturar_panel.py` (portada_panel.png) y una captura del emulador
    # (portada_movil.png).
    "pie": ["Versión 1.0  ·  Noviembre de 2026",
            "Consultorio médico Milko Ugaz Zegarra  ·  Chiclayo",
            "Elaborado por Leonardo Guzmán Salazar"],
}

ANCHO, ALTO = 1654, 2339          # A4 a 200 ppp
AZUL_OSCURO = (11, 46, 74)
AZUL = (23, 96, 143)
CELESTE = (125, 190, 230)
VERDE = (34, 160, 107)
TINTA = (24, 33, 45)
GRIS = (96, 108, 122)


def fuente(tam: int, negrita: bool = False) -> ImageFont.FreeTypeFont:
    nombres = ("timesbd.ttf", "georgiab.ttf") if negrita else ("times.ttf", "georgia.ttf")
    for nombre in (*nombres, "DejaVuSerif-Bold.ttf" if negrita else "DejaVuSerif.ttf"):
        try:
            return ImageFont.truetype(nombre, tam)
        except OSError:
            continue
    return ImageFont.load_default()


def envolver(dibujo, texto, letra, ancho_max):
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = f"{actual} {palabra}".strip()
        if dibujo.textlength(prueba, font=letra) <= ancho_max:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    return lineas + [actual]


def sombra(base: Image.Image, caja, radio: int, desenfoque: int = 28, opacidad: int = 110):
    capa = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(capa).rounded_rectangle(caja, radius=radio, fill=(0, 0, 0, opacidad))
    base.alpha_composite(capa.filter(ImageFilter.GaussianBlur(desenfoque)))


def esquinas(img: Image.Image, radio: int) -> Image.Image:
    mascara = Image.new("L", img.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, 0, *img.size), radius=radio, fill=255)
    img = img.convert("RGBA")
    img.putalpha(mascara)
    return img


def main() -> int:
    lienzo = Image.new("RGBA", (ANCHO, ALTO), (255, 255, 255, 255))
    d = ImageDraw.Draw(lienzo)

    # Franja superior en degradado, con un borde inferior en diagonal suave.
    alto_franja = 1420
    for y in range(alto_franja):
        t = y / alto_franja
        color = tuple(int(AZUL_OSCURO[i] + (AZUL[i] - AZUL_OSCURO[i]) * t) for i in range(3))
        d.line([(0, y), (ANCHO, y)], fill=color)
    d.polygon([(0, alto_franja), (ANCHO, alto_franja - 160), (ANCHO, alto_franja)], fill="white")
    # Círculos decorativos, muy tenues.
    adorno = Image.new("RGBA", lienzo.size, (0, 0, 0, 0))
    da = ImageDraw.Draw(adorno)
    da.ellipse((1050, -260, 1900, 590), outline=(255, 255, 255, 40), width=6)
    da.ellipse((1180, -120, 1760, 460), outline=(255, 255, 255, 28), width=4)
    lienzo.alpha_composite(adorno)

    # Logo y nombre del sistema.
    margen = 130
    logo = Image.open(LOGO).convert("RGBA").resize((150, 150), Image.LANCZOS)
    lienzo.alpha_composite(logo, (margen, 130))
    d.text((margen + 185, 168), DATOS["sistema"], font=fuente(46, True), fill="white")
    d.text((margen + 185, 230), "Consultorio médico Milko Ugaz Zegarra",
           font=fuente(34), fill=CELESTE)

    # Título y subtítulo.
    d.text((margen, 370), DATOS["titulo"], font=fuente(128, True), fill="white")
    d.rectangle((margen, 530, margen + 220, 540), fill=VERDE)
    y = 585
    for linea in envolver(d, DATOS["subtitulo"], fuente(44), ANCHO - 2 * margen):
        d.text((margen, y), linea, font=fuente(44), fill=(225, 238, 248))
        y += 58

    # Computadora con el panel.
    panel = Image.open(CAPTURAS / "portada_panel.png").convert("RGB")
    ancho_pantalla = 1040
    panel = panel.resize((ancho_pantalla, int(panel.height * ancho_pantalla / panel.width)), Image.LANCZOS)
    x0, y0 = 120, 860
    marco = (x0 - 22, y0 - 22, x0 + ancho_pantalla + 22, y0 + panel.height + 22)
    sombra(lienzo, (marco[0], marco[1] + 30, marco[2], marco[3] + 40), 30)
    d.rounded_rectangle(marco, radius=26, fill=(30, 36, 44))
    lienzo.alpha_composite(esquinas(panel, 8), (x0, y0))
    base_y = marco[3]
    d.rounded_rectangle((marco[0] - 70, base_y, marco[2] + 70, base_y + 34), radius=14, fill=(205, 211, 219))
    d.rounded_rectangle((marco[0] + 380, base_y, marco[2] - 380, base_y + 12), radius=6, fill=(170, 177, 188))

    # Celular con la pantalla «Hoy».
    movil = Image.open(CAPTURAS / "portada_movil.png").convert("RGB")
    ancho_movil = 370
    movil = movil.resize((ancho_movil, int(movil.height * ancho_movil / movil.width)), Image.LANCZOS)
    mx, my = 1150, 760
    cuerpo = (mx - 18, my - 18, mx + ancho_movil + 18, my + movil.height + 18)
    sombra(lienzo, (cuerpo[0] + 10, cuerpo[1] + 40, cuerpo[2] + 10, cuerpo[3] + 40), 54)
    d.rounded_rectangle(cuerpo, radius=56, fill=(18, 22, 28))
    lienzo.alpha_composite(esquinas(movil, 40), (mx, my))

    # Tarjetas de los tres perfiles.
    y_roles = 1745
    ancho_tarjeta = (ANCHO - 2 * margen - 2 * 40) // 3
    for i, (rol, medio) in enumerate(DATOS["roles"]):
        x = margen + i * (ancho_tarjeta + 40)
        caja = (x, y_roles, x + ancho_tarjeta, y_roles + 220)
        sombra(lienzo, (caja[0], caja[1] + 12, caja[2], caja[3] + 12), 22, 18, 50)
        d.rounded_rectangle(caja, radius=22, fill="white", outline=(222, 230, 238), width=2)
        d.rounded_rectangle((x, y_roles, x + 14, y_roles + 220), radius=7, fill=(AZUL, VERDE, AZUL_OSCURO)[i])
        d.text((x + 44, y_roles + 30), f"Sección {i + 2}", font=fuente(30), fill=GRIS)
        lineas = envolver(d, rol, fuente(40, True), ancho_tarjeta - 70)
        for j, linea in enumerate(lineas):
            d.text((x + 44, y_roles + 72 + j * 46), linea, font=fuente(40, True), fill=TINTA)
        d.text((x + 44, y_roles + 82 + len(lineas) * 46), medio, font=fuente(30), fill=AZUL)

    # Pie.
    d.line([(margen, 2060), (ANCHO - margen, 2040)], fill=(222, 230, 238), width=3)
    for k, linea in enumerate(DATOS["pie"]):
        letra = fuente(40, True) if k == 0 else fuente(36)
        d.text((margen, 2095 + k * 58), linea, font=letra, fill=TINTA if k == 0 else GRIS)

    destino = CAPTURAS / "caratula.png"
    lienzo.convert("RGB").save(destino, optimize=True)
    print(f"Generada: {destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
