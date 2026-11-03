"""Genera el icono de la aplicacion «Mi tratamiento» en todas las densidades.

    python app-movil/herramientas/generar_icono.py

Dibuja el logo por codigo, sin depender de archivos de imagen externos: una
capsula en diagonal (el tratamiento) con una marca de verificacion (la toma
registrada), sobre el azul de la marca (Tema.primario, #17608F).

Produce dos formatos:
- `mipmap-*/ic_launcher.png`: icono clasico, para Android anterior a 8.
- `mipmap-anydpi-v26/ic_launcher.xml` + `drawable-*/ic_launcher_foreground.png`:
  icono adaptativo. Sin el, Android 8 o superior encoge el icono clasico
  dentro de un circulo blanco.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

RES = Path(__file__).resolve().parents[1] / "android" / "app" / "src" / "main" / "res"
AZUL = (23, 96, 143, 255)        # #17608F, Tema.primario
AZUL_CLARO = (143, 193, 227, 255)
BLANCO = (255, 255, 255, 255)
VERDE = (18, 112, 74, 255)       # #12704A, Tema.exito

LIENZO = 1024  # se dibuja grande y se reduce: los bordes quedan suaves


def dibujar_logo(escala: float = 1.0, fondo: bool = True) -> Image.Image:
    """Logo completo en un lienzo de LIENZO x LIENZO px."""
    base = Image.new("RGBA", (LIENZO, LIENZO), (0, 0, 0, 0))
    if fondo:
        ImageDraw.Draw(base).rounded_rectangle((0, 0, LIENZO, LIENZO), radius=230, fill=AZUL)

    # Capsula: se dibuja horizontal y se rota.
    capa = Image.new("RGBA", (LIENZO, LIENZO), (0, 0, 0, 0))
    c = LIENZO / 2
    largo, ancho = 600 * escala, 250 * escala
    caja = (c - largo / 2, c - ancho / 2, c + largo / 2, c + ancho / 2)
    d = ImageDraw.Draw(capa)
    d.rounded_rectangle(caja, radius=ancho / 2, fill=BLANCO)
    mascara = Image.new("L", (LIENZO, LIENZO), 0)
    ImageDraw.Draw(mascara).rounded_rectangle(caja, radius=ancho / 2, fill=255)
    derecha = Image.new("L", (LIENZO, LIENZO), 0)
    ImageDraw.Draw(derecha).rectangle((c, 0, LIENZO, LIENZO), fill=255)
    tinte = Image.new("RGBA", (LIENZO, LIENZO), AZUL_CLARO)
    capa.paste(tinte, (0, 0), Image.composite(derecha, Image.new("L", (LIENZO, LIENZO), 0), mascara))
    capa = capa.rotate(45, resample=Image.BICUBIC, center=(c, c))
    base.alpha_composite(capa)

    # Insignia de verificacion, abajo a la derecha.
    r = 175 * escala
    cx, cy = c + 255 * escala, c + 255 * escala
    d = ImageDraw.Draw(base)
    d.ellipse((cx - r - 22 * escala, cy - r - 22 * escala, cx + r + 22 * escala, cy + r + 22 * escala),
              fill=AZUL if fondo else (0, 0, 0, 0))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=VERDE)
    grosor = int(52 * escala)
    puntos = [(cx - 85 * escala, cy + 2 * escala), (cx - 22 * escala, cy + 68 * escala),
              (cx + 95 * escala, cy - 62 * escala)]
    d.line(puntos, fill=BLANCO, width=grosor, joint="curve")
    for x, y in (puntos[0], puntos[-1]):
        d.ellipse((x - grosor / 2, y - grosor / 2, x + grosor / 2, y + grosor / 2), fill=BLANCO)
    return base


CLASICO = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
ADAPTATIVO = {"mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432}


def main() -> None:
    clasico = dibujar_logo(escala=0.82, fondo=True)
    for densidad, px in CLASICO.items():
        destino = RES / f"mipmap-{densidad}" / "ic_launcher.png"
        clasico.resize((px, px), Image.LANCZOS).save(destino)

    # Primer plano adaptativo: el arte debe caber en la zona segura central
    # (66 de los 108 dp), porque cada fabricante recorta el borde a su forma.
    primer_plano = dibujar_logo(escala=0.52, fondo=False)
    for densidad, px in ADAPTATIVO.items():
        carpeta = RES / f"drawable-{densidad}"
        carpeta.mkdir(exist_ok=True)
        primer_plano.resize((px, px), Image.LANCZOS).save(carpeta / "ic_launcher_foreground.png")

    (RES / "mipmap-anydpi-v26").mkdir(exist_ok=True)
    (RES / "mipmap-anydpi-v26" / "ic_launcher.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
        '    <background android:drawable="@color/ic_launcher_background"/>\n'
        '    <foreground android:drawable="@drawable/ic_launcher_foreground"/>\n'
        '</adaptive-icon>\n',
        encoding="utf-8",
    )
    (RES / "values" / "ic_launcher_background.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<resources>\n    <color name="ic_launcher_background">#17608F</color>\n</resources>\n',
        encoding="utf-8",
    )
    # Vista previa para documentacion y para revisarlo sin compilar.
    clasico.resize((512, 512), Image.LANCZOS).save(Path(__file__).with_name("icono_512.png"))
    print("Icono generado en todas las densidades.")


if __name__ == "__main__":
    main()
