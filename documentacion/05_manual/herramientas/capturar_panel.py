"""Capturas anotadas del panel medico para el manual de usuario.

    python capturar_panel.py            (con la variable CLAVE_DEMO definida)

Requiere el sistema corriendo en modo local (http://localhost:5173) con los
datos de demostracion, y Playwright con Microsoft Edge (`pip install
playwright pillow`; usa el Edge instalado, no descarga navegadores).

Recorre el panel como lo haria el medico y guarda en `../capturas/` una imagen
por paso, con numeros rojos sobre los elementos que el manual menciona. Si la
interfaz cambia antes de la entrega, basta con volver a ejecutarlo.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from playwright.sync_api import Page, sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
URL = "http://localhost:5173"
DESTINO = Path(__file__).resolve().parents[1] / "capturas"
ROJO = (217, 45, 32)
ESCALA = 1  # device_scale_factor de la pagina


def _fuente(tam: int) -> ImageFont.FreeTypeFont:
    for nombre in ("arialbd.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(nombre, tam)
        except OSError:
            continue
    return ImageFont.load_default()


def capturar(pagina: Page, nombre: str, marcas: list = (), recorte=None, margen: int = 24,
             ocultar: list = ()) -> None:
    """Guarda la captura `nombre` con marcas numeradas.

    `marcas` es una lista de localizadores; cada uno recibe un numero (1, 2...).
    `recorte` es un localizador cuya caja delimita la imagen (o None: pantalla).
    `ocultar` son localizadores cuyo contenido se difumina (p. ej., contrasenas).
    """
    pagina.wait_for_timeout(350)
    ruta = DESTINO / f"{nombre}.png"
    pagina.screenshot(path=str(ruta), full_page=True)
    img = Image.open(ruta).convert("RGB")

    for loc in ocultar:
        caja = loc.bounding_box()
        if caja:
            x, y, w, h = (int(v) for v in (caja["x"], caja["y"] + pagina.evaluate("scrollY"), caja["width"], caja["height"]))
            zona = img.crop((x, y, x + w, y + h)).filter(ImageFilter.GaussianBlur(9))
            img.paste(zona, (x, y))

    dibujo = ImageDraw.Draw(img)
    fuente = _fuente(17)
    desplazamiento = pagina.evaluate("scrollY")
    for numero, loc in enumerate(marcas, start=1):
        caja = loc.bounding_box()
        if not caja:
            print(f"   aviso: la marca {numero} de {nombre} no esta visible")
            continue
        x, y = caja["x"], caja["y"] + desplazamiento
        w, h = caja["width"], caja["height"]
        dibujo.rounded_rectangle((x - 4, y - 4, x + w + 4, y + h + 4), radius=6, outline=ROJO, width=3)
        r = 14
        cx, cy = x - 4, y - 4
        dibujo.ellipse((cx - r, cy - r, cx + r, cy + r), fill=ROJO, outline=(255, 255, 255), width=2)
        texto = str(numero)
        tw, th = dibujo.textbbox((0, 0), texto, font=fuente)[2:]
        dibujo.text((cx - tw / 2, cy - th / 2 - 2), texto, fill=(255, 255, 255), font=fuente)

    if recorte is not None:
        caja = recorte.bounding_box()
        if caja:
            x0 = max(0, int(caja["x"]) - margen)
            y0 = max(0, int(caja["y"] + desplazamiento) - margen)
            x1 = min(img.width, int(caja["x"] + caja["width"]) + margen)
            y1 = min(img.height, int(caja["y"] + desplazamiento + caja["height"]) + margen)
            # Un modal mas alto que la ventana se desplaza por dentro: lo que
            # queda bajo el borde inferior no se ve y no debe recortarse.
            y1 = min(y1, int(desplazamiento + pagina.viewport_size["height"]))
            img = img.crop((x0, y0, x1, y1))
    else:
        # Sin recorte: la parte visible de la ventana, no la pagina entera.
        alto = pagina.viewport_size["height"]
        img = img.crop((0, desplazamiento, img.width, min(img.height, desplazamiento + alto)))
    img.save(ruta)
    print(f"   {ruta.name}")


def _contenedor(pagina: Page, texto: str):
    """Tarjeta o seccion que contiene un titulo dado."""
    return pagina.get_by_text(texto, exact=True).first.locator(
        "xpath=ancestor::*[self::section or self::article or self::aside or self::form"
        " or contains(@class,'tarjeta') or contains(@class,'seccion') or contains(@class,'modal')][1]"
    )


def recorrer(pagina: Page, clave: str) -> None:
    # --- 2. Acceso -----------------------------------------------------------
    pagina.goto(URL)
    pagina.wait_for_load_state("networkidle")
    capturar(pagina, "w01_acceso", [
        pagina.locator("input[name=correo]"), pagina.locator("input[name=contrasena]"),
        pagina.get_by_role("button", name="Mostrar contraseña"),
        pagina.get_by_role("button", name="Ingresar"), pagina.get_by_text("¿Olvidó su contraseña?"),
    ])

    pagina.fill("input[name=correo]", "milko.ugaz@consultorio.pe")
    pagina.fill("input[name=contrasena]", "contrasena-incorrecta")
    pagina.get_by_role("button", name="Ingresar").click()
    pagina.wait_for_timeout(1200)
    capturar(pagina, "w02_acceso_error", [pagina.locator(".mensaje--error, [role=alert]").first])

    pagina.get_by_text("¿Olvidó su contraseña?").click()
    pagina.wait_for_load_state("networkidle")
    capturar(pagina, "w03_recuperar", [
        pagina.locator("input[type=email]"), pagina.get_by_role("button", name="Enviarme el enlace"),
    ])

    pagina.goto(URL + "/restablecer?t=enlace-de-ejemplo")
    pagina.wait_for_load_state("networkidle")
    capturar(pagina, "w04_restablecer", [pagina.locator("input[type=password]").first,
                                         pagina.locator("input[type=password]").nth(1),
                                         pagina.locator("button[type=submit]")])

    pagina.goto(URL)
    pagina.fill("input[name=correo]", "milko.ugaz@consultorio.pe")
    pagina.fill("input[name=contrasena]", clave)
    pagina.get_by_role("button", name="Ingresar").click()
    pagina.wait_for_url("**/panel")
    pagina.wait_for_load_state("networkidle")
    pagina.wait_for_timeout(800)
    # Version sin anotaciones, para la caratula.
    pagina.screenshot(path=str(DESTINO / "portada_panel.png"))

    # --- 3. Pantalla principal ---------------------------------------------------
    capturar(pagina, "w05_panel", [
        pagina.locator("nav[aria-label='Secciones del panel']"),
        pagina.locator("[aria-label='Indicadores generales']"),
        pagina.get_by_placeholder("Nombre o código"), pagina.locator("select").first,
        pagina.get_by_role("button", name="Registrar paciente"),
        pagina.get_by_role("link", name="Ver ficha").first,
        pagina.get_by_role("button", name="Cerrar sesión"),
    ])

    # --- 4.5 Busqueda y filtro --------------------------------------------------------
    pagina.get_by_placeholder("Nombre o código").fill("P-002")
    pagina.wait_for_timeout(600)
    capturar(pagina, "w06_busqueda", [pagina.get_by_placeholder("Nombre o código"),
                                      pagina.locator("table tbody tr").first])
    pagina.get_by_placeholder("Nombre o código").fill("")
    pagina.locator("select").first.select_option(label="Diabetes tipo 2")
    pagina.wait_for_timeout(600)
    capturar(pagina, "w07_filtro", [pagina.locator("select").first])
    pagina.locator("select").first.select_option(label="Todos")

    # --- 4.1 Alta de un paciente -----------------------------------------------------
    pagina.get_by_role("button", name="Registrar paciente").click()
    pagina.wait_for_timeout(700)
    modal = pagina.locator(".modal__panel").first
    capturar(pagina, "w08_alta_vacia", [
        pagina.locator("input[name=nombres]"), pagina.locator("input[name=apellidos]"),
        pagina.locator("input[name=documento_identidad]"), pagina.locator("input[name=telefono]"),
        pagina.locator("input[name=correo]"), pagina.locator("input[name=codigo_anonimizado]"),
    ], recorte=modal)

    # Validaciones: intentar guardar con datos imposibles.
    pagina.fill("input[name=nombres]", "Ana")
    pagina.fill("input[name=apellidos]", "Torres Díaz")
    pagina.fill("input[name=edad]", "64")
    pagina.fill("input[name=numero_farmacos]", "3")
    pagina.fill("input[name=controles_programados_6m]", "4")
    pagina.fill("input[name=controles_perdidos_6m]", "6")
    pagina.get_by_role("button", name="Registrar paciente").last.click()
    pagina.wait_for_timeout(700)
    pagina.locator("input[name=numero_farmacos]").scroll_into_view_if_needed()
    capturar(pagina, "w09_alta_validaciones", [
        pagina.locator("input[name=numero_farmacos]"), pagina.locator("input[name=tomas_dia]"),
        pagina.locator("input[name=controles_perdidos_6m]"),
    ], recorte=modal)

    # Datos correctos.
    pagina.fill("input[name=documento_identidad]", "45781236")
    pagina.fill("input[name=telefono]", "987654321")
    pagina.fill("input[name=correo]", "ana.torres@correo.pe")
    pagina.locator("select[name=sexo]").select_option(label="Femenino")
    pagina.locator("select[name=diagnostico]").select_option(label="Ambas")
    pagina.fill("input[name=tiempo_enfermedad_anios]", "8")
    pagina.locator(".campo--casilla input").nth(0).check()
    pagina.locator(".campo--casilla input").nth(1).check()
    pagina.fill("input[name=numero_farmacos]", "7")
    pagina.fill("input[name=tomas_dia]", "4")
    pagina.locator("select[name=nivel_educativo]").select_option(label="Secundaria")
    pagina.locator("select[name=convivencia]").select_option(label="Vive acompañado")
    pagina.locator("select[name=apoyo_familiar]").select_option(index=1)
    pagina.fill("input[name=controles_programados_6m]", "6")
    pagina.fill("input[name=controles_perdidos_6m]", "2")
    pagina.fill("input[name=puntaje_morisky]", "2")
    pagina.locator("select[name=incumplimiento_basal]").select_option(label="Incumplimiento")
    pagina.locator("input[name=edad]").scroll_into_view_if_needed()
    capturar(pagina, "w10_alta_clinica", [
        pagina.locator("input[name=edad]"), pagina.locator("select[name=diagnostico]"),
        pagina.locator(".comorbilidades").first, pagina.locator("input[name=numero_farmacos]"),
        pagina.locator("input[name=tomas_dia]"),
    ], recorte=modal)
    pagina.get_by_role("button", name="Registrar paciente").last.scroll_into_view_if_needed()
    capturar(pagina, "w11_alta_contexto", [
        pagina.locator("select[name=nivel_educativo]"), pagina.locator("select[name=convivencia]"),
        pagina.locator("select[name=apoyo_familiar]"), pagina.locator("input[name=controles_programados_6m]"),
        pagina.locator("input[name=puntaje_morisky]"),
        pagina.get_by_role("button", name="Registrar paciente").last,
    ], recorte=modal)
    pagina.get_by_role("button", name="Registrar paciente").last.click()
    pagina.wait_for_timeout(1500)
    capturar(pagina, "w12_alta_confirmada", [pagina.locator(".mensaje--exito").first])

    # --- Ficha del paciente P-001 -------------------------------------------------------
    pagina.get_by_placeholder("Nombre o código").fill("P-001")
    pagina.wait_for_timeout(500)
    pagina.get_by_role("link", name="Ver ficha").first.click()
    pagina.wait_for_load_state("networkidle")
    pagina.wait_for_timeout(2500)
    capturar(pagina, "w13_ficha", [
        pagina.get_by_role("button", name="Editar ficha"), pagina.get_by_role("button", name="Dar de baja"),
        pagina.get_by_text("Riesgo predicho por el modelo", exact=False).first,
    ])
    tarjeta = pagina.locator("section.alerta").first
    tarjeta.scroll_into_view_if_needed()
    capturar(pagina, "w14_riesgo_shap", [
        pagina.locator(".prediccion__valor").first, pagina.locator(".prediccion__factores").first,
    ], recorte=tarjeta)
    # El historial es ancho: se amplia la ventana solo para esta captura, para
    # que la columna Testigo quede a la vista.
    pagina.set_viewport_size({"width": 1800, "height": 1000})
    pagina.wait_for_timeout(500)
    historial = pagina.locator(".tarjeta:has(h3:has-text('Historial de tomas'))").first
    historial.scroll_into_view_if_needed()
    capturar(pagina, "w15_historial", [
        pagina.locator("th:has-text('Retraso')").first, pagina.locator("th:has-text('Estado')").first,
        pagina.locator("th:has-text('Testigo')").first,
    ], recorte=historial)
    pagina.set_viewport_size({"width": 1366, "height": 860})
    pagina.wait_for_timeout(300)

    acceso = pagina.locator("section:has(> h3:has-text('Acceso a la aplicación móvil')), .tarjeta:has(h3:has-text('Acceso a la aplicación móvil'))").last
    acceso.scroll_into_view_if_needed()
    capturar(pagina, "w16_acceso_movil", [acceso.get_by_role("button").first], recorte=acceso)

    # --- 4.3 Edicion -------------------------------------------------------------------
    pagina.get_by_role("button", name="Editar ficha").click()
    pagina.wait_for_timeout(700)
    formulario = pagina.locator(".modal__panel").first
    pagina.fill("input[name=tomas_dia]", "6")
    pagina.locator("input[name=tomas_dia]").scroll_into_view_if_needed()
    capturar(pagina, "w17_edicion", [pagina.locator("input[name=codigo_anonimizado]"),
                                     pagina.locator("input[name=tomas_dia]")], recorte=formulario)
    pagina.locator("button[type=submit]").last.click()
    pagina.wait_for_timeout(2000)
    pagina.evaluate("window.scrollTo(0, 0)")
    capturar(pagina, "w18_edicion_guardada", [pagina.locator(".mensaje--exito").first])

    # --- Alertas ---------------------------------------------------------------------
    pagina.get_by_role("link", name="Alertas tempranas").click()
    pagina.wait_for_load_state("networkidle")
    pagina.wait_for_timeout(1500)
    capturar(pagina, "w19_alertas", [
        pagina.locator("select").first, pagina.get_by_role("link").filter(has_text="P-0").first,
        pagina.get_by_role("button", name="Registrar lo que hice").first,
    ])
    pagina.get_by_role("button", name="Registrar lo que hice").first.click()
    pagina.wait_for_timeout(600)
    pagina.locator("textarea").first.fill(
        "Se le llamó por teléfono y se reforzó la pauta; control adelantado al viernes.")
    nota = pagina.locator("li.alerta-tarjeta:has(textarea)").first
    capturar(pagina, "w20_alerta_nota", [
        pagina.locator("textarea").first, pagina.get_by_role("button", name="Atendida").first,
        pagina.get_by_role("button", name="No aplica").first,
    ], recorte=nota, margen=60)
    pagina.get_by_role("button", name="Atendida").first.click()
    pagina.wait_for_timeout(1500)
    pagina.locator("select").first.select_option(label="Atendidas")
    pagina.wait_for_timeout(1200)
    capturar(pagina, "w21_alertas_atendidas", [pagina.locator("select").first])

    # --- Reportes ---------------------------------------------------------------------
    pagina.get_by_role("link", name="Reportes generales").click()
    pagina.wait_for_load_state("networkidle")
    pagina.wait_for_timeout(1500)
    capturar(pagina, "w22_reportes", [
        pagina.locator("select").first, pagina.get_by_role("button", name="Exportar CSV"),
        pagina.locator("[aria-label='Indicadores generales']"),
    ])

    # --- 4.4 Baja ---------------------------------------------------------------------
    pagina.get_by_role("link", name="Panel de auditoría").click()
    pagina.wait_for_load_state("networkidle")
    pagina.get_by_placeholder("Nombre o código").fill("P-006")
    pagina.wait_for_timeout(500)
    pagina.get_by_role("link", name="Ver ficha").first.click()
    pagina.wait_for_load_state("networkidle")
    pagina.wait_for_timeout(1500)
    pagina.get_by_role("button", name="Dar de baja").click()
    pagina.wait_for_timeout(500)
    capturar(pagina, "w23_baja_confirmar", [pagina.get_by_role("button", name="Sí, dar de baja"),
                                            pagina.get_by_role("button", name="Cancelar").first])
    pagina.get_by_role("button", name="Sí, dar de baja").click()
    pagina.wait_for_url("**/panel")
    pagina.wait_for_timeout(1200)
    capturar(pagina, "w24_baja_hecha", [pagina.locator(".mensaje--exito").first])

    pagina.get_by_role("button", name="Cerrar sesión").click()
    pagina.wait_for_timeout(800)


def main() -> int:
    parser = argparse.ArgumentParser(description="Capturas anotadas del panel medico.")
    parser.add_argument("--clave", default=os.environ.get("CLAVE_DEMO"),
                        help="Contrasena de las cuentas de demostracion (o variable CLAVE_DEMO).")
    args = parser.parse_args()
    if not args.clave:
        parser.error("indique --clave o la variable CLAVE_DEMO")
    DESTINO.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        navegador = p.chromium.launch(channel="msedge")
        pagina = navegador.new_page(viewport={"width": 1366, "height": 860}, device_scale_factor=ESCALA)
        try:
            recorrer(pagina, args.clave)
        finally:
            navegador.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
