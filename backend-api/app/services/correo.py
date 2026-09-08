"""Envio de correo saliente (RF10).

Se usa para una sola cosa: hacer llegar el enlace de restablecimiento de la
contrasena. Se implementa con ``smtplib`` de la biblioteca estandar y no con un
servicio propietario, de modo que el consultorio pueda usar el proveedor que
tenga —el correo del propio consultorio, una cuenta de Gmail con contrasena de
aplicacion, o un servicio transaccional— cambiando cinco variables de entorno y
sin tocar el codigo.

El modulo **nunca propaga una excepcion** hacia el endpoint. Un fallo de SMTP
—servidor caido, credenciales caducadas, buzon inexistente— tiene que quedar en
el registro del servidor, no en la respuesta: si el API contestara distinto
segun el envio prosperase o no, cualquiera podria averiguar que direcciones
estan dadas de alta pidiendo restablecimientos.
"""
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from ..core.config import settings

logger = logging.getLogger("cdss.correo")

ASUNTO = "Recupere el acceso a Mi tratamiento"


def _cuerpo(nombre: str, enlace: str, minutos: int) -> tuple[str, str]:
    """Version en texto plano y version en HTML del mensaje."""
    texto = (
        f"Hola, {nombre}:\n\n"
        "Alguien pidio restablecer la contrasena de su cuenta del consultorio "
        "medico Milko Ugaz Zegarra.\n\n"
        "Abra este enlace para escribir una contrasena nueva:\n"
        f"{enlace}\n\n"
        f"El enlace vence en {minutos} minutos y solo puede usarse una vez.\n\n"
        "Si no fue usted quien lo pidio, no haga nada: su contrasena actual "
        "sigue siendo valida.\n"
    )

    html = f"""\
<html><body style="font-family:system-ui,Segoe UI,Arial,sans-serif;
                   font-size:16px;color:#1c2733;line-height:1.5">
  <p>Hola, {nombre}:</p>
  <p>Alguien pidi&oacute; restablecer la contrase&ntilde;a de su cuenta del
     consultorio m&eacute;dico Milko Ugaz Zegarra.</p>
  <p style="margin:26px 0">
    <a href="{enlace}"
       style="background:#17608F;color:#fff;text-decoration:none;
              padding:14px 26px;border-radius:8px;display:inline-block;
              font-weight:600">Escribir una contrase&ntilde;a nueva</a>
  </p>
  <p style="color:#5C6B82;font-size:15px">
    El enlace vence en {minutos} minutos y solo puede usarse una vez.<br>
    Si no fue usted quien lo pidi&oacute;, no haga nada: su contrase&ntilde;a
    actual sigue siendo v&aacute;lida.
  </p>
</body></html>"""

    return texto, html


def enviar_restablecimiento(destino: str, nombre: str, enlace: str) -> bool:
    """Envia el enlace de restablecimiento. Devuelve si salio o no.

    El valor devuelto sirve para el registro del servidor, no para decidir la
    respuesta al cliente, que es siempre la misma.
    """
    if not settings.correo_configurado:
        logger.warning(
            "Se pidio un restablecimiento pero no hay servidor de correo "
            "configurado; el mensaje no se envio."
        )
        return False

    minutos = settings.minutos_vigencia_restablecimiento
    texto, html = _cuerpo(nombre, enlace, minutos)

    mensaje = EmailMessage()
    mensaje["Subject"] = ASUNTO
    mensaje["From"] = settings.smtp_remitente
    mensaje["To"] = destino
    mensaje.set_content(texto)
    mensaje.add_alternative(html, subtype="html")

    try:
        # El puerto 465 habla TLS desde el saludo inicial; el 587 empieza en
        # claro y asciende con STARTTLS. Es la unica diferencia de trato y la
        # decide el propio numero de puerto, sin una variable mas que explicar.
        if settings.smtp_port == 465:
            servidor = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=15)
        else:
            servidor = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15)

        with servidor:
            if settings.smtp_port != 465:
                servidor.starttls()
            if settings.smtp_usuario:
                servidor.login(settings.smtp_usuario, settings.smtp_contrasena)
            servidor.send_message(mensaje)

        logger.info("Enlace de restablecimiento enviado.")
        return True

    except Exception:  # noqa: BLE001 - cualquier fallo de correo se absorbe
        # Sin la direccion ni el enlace: este registro puede acabar en un
        # servicio de terceros.
        logger.exception("No se pudo enviar el enlace de restablecimiento.")
        return False
