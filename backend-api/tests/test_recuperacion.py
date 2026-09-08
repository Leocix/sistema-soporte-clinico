"""Verificacion del restablecimiento de la contrasena (RF10).

Lo que se protege aqui es doble. Por un lado que la recuperacion funcione: sin
ella un paciente de zona rural que olvida su clave tiene que viajar al
consultorio. Por otro, que no se convierta en una puerta: un enlace de
recuperacion es una credencial con la que se entra en una cuenta ajena, y toda
la superficie que anade —el mensaje de respuesta, la caducidad, el reuso—
tiene su prueba.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

import pytest

from app.core.config import settings
from app.db.models import Restablecimiento, Usuario

CLAVE_NUEVA = "ClaveNueva2026"
CORREO_PACIENTE = "jose.vasquez@correo.pe"


@pytest.fixture()
def con_correo(monkeypatch):
    """Simula un servicio con servidor de correo configurado.

    No se envia nada: se sustituye el emisor por una lista donde queda lo que
    se habria mandado. Las pruebas no deben depender de una red ni dejar
    mensajes en ningun buzon.
    """
    monkeypatch.setattr(settings, "smtp_host", "smtp.pruebas", raising=False)
    monkeypatch.setattr(settings, "smtp_remitente", "no-responder@pruebas", raising=False)
    monkeypatch.setattr(settings, "frontend_url", "https://panel.pruebas", raising=False)

    enviados: list[dict] = []

    def _emisor(destino, nombre, enlace):
        enviados.append({"destino": destino, "nombre": nombre, "enlace": enlace})
        return True

    monkeypatch.setattr("app.api.auth.enviar_restablecimiento", _emisor)
    return enviados


def _testigo(enlace: str) -> str:
    return enlace.split("?t=", 1)[1]


def _pedir(client, correo=CORREO_PACIENTE):
    return client.post("/api/auth/recuperacion", json={"correo": correo})


def _entrar(client, contrasena, correo=CORREO_PACIENTE, perfil="paciente"):
    return client.post(
        "/api/auth/login",
        json={"correo": correo, "contrasena": contrasena, "perfil": perfil},
    )


# --- Recorrido completo -----------------------------------------------------


def test_el_enlace_permite_fijar_una_contrasena_nueva(client, datos, con_correo):
    solicitud = _pedir(client)
    assert solicitud.status_code == 202
    assert solicitud.json()["correo_habilitado"] is True

    # El mensaje sale hacia la direccion de la cuenta, no hacia la que se pidio.
    assert len(con_correo) == 1
    assert con_correo[0]["destino"] == CORREO_PACIENTE
    assert con_correo[0]["enlace"].startswith("https://panel.pruebas/restablecer?t=")

    confirmacion = client.post(
        "/api/auth/recuperacion/confirmar",
        json={
            "testigo": _testigo(con_correo[0]["enlace"]),
            "contrasena": CLAVE_NUEVA,
        },
    )
    assert confirmacion.status_code == 200

    assert _entrar(client, CLAVE_NUEVA).status_code == 200
    # Y la anterior deja de servir.
    assert _entrar(client, "Consultorio2026").status_code == 401


def test_el_testigo_no_se_guarda_en_claro(client, datos, con_correo, db_session):
    """De la credencial solo se persiste su resumen, como con las contrasenas."""
    _pedir(client)
    testigo = _testigo(con_correo[0]["enlace"])

    permiso = db_session.query(Restablecimiento).one()
    assert permiso.hash_testigo != testigo
    assert permiso.hash_testigo == hashlib.sha256(testigo.encode()).hexdigest()


# --- No enumeracion de cuentas ---------------------------------------------


def test_la_respuesta_es_identica_exista_o_no_la_cuenta(client, datos, con_correo):
    """Contestar distinto convertiria la ruta en un buscador de correos."""
    existente = _pedir(client)
    inexistente = _pedir(client, "nadie@ninguna-parte.pe")

    assert existente.status_code == inexistente.status_code == 202
    assert existente.json() == inexistente.json()
    # Pero solo se envio un mensaje.
    assert len(con_correo) == 1


def test_sin_servidor_de_correo_se_dirige_al_consultorio(client, datos, monkeypatch):
    """Prometer un mensaje que nadie enviara es peor que no ofrecerlo."""
    monkeypatch.setattr(settings, "smtp_host", "", raising=False)

    respuesta = _pedir(client)

    assert respuesta.status_code == 202
    assert respuesta.json()["correo_habilitado"] is False
    assert "consultorio" in respuesta.json()["mensaje"]


# --- Vigencia del permiso ---------------------------------------------------


def test_un_enlace_solo_sirve_una_vez(client, datos, con_correo):
    _pedir(client)
    testigo = _testigo(con_correo[0]["enlace"])

    primera = client.post(
        "/api/auth/recuperacion/confirmar",
        json={"testigo": testigo, "contrasena": CLAVE_NUEVA},
    )
    assert primera.status_code == 200

    segunda = client.post(
        "/api/auth/recuperacion/confirmar",
        json={"testigo": testigo, "contrasena": "OtraClave2026"},
    )
    assert segunda.status_code == 404
    # La contrasena sigue siendo la que fijo el primer canje.
    assert _entrar(client, CLAVE_NUEVA).status_code == 200


def test_un_enlace_vencido_no_sirve(client, datos, con_correo, db_session):
    """Un enlace vive en una bandeja de correo que puede quedar abierta."""
    _pedir(client)
    permiso = db_session.query(Restablecimiento).one()
    permiso.expira_en = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()

    respuesta = client.post(
        "/api/auth/recuperacion/confirmar",
        json={
            "testigo": _testigo(con_correo[0]["enlace"]),
            "contrasena": CLAVE_NUEVA,
        },
    )
    assert respuesta.status_code == 404


def test_pedir_uno_nuevo_anula_el_anterior(client, datos, con_correo):
    """Quien no recuerda si ya lo pidio lo pide dos veces; no deben valer los dos."""
    _pedir(client)
    _pedir(client)
    assert len(con_correo) == 2

    viejo = client.post(
        "/api/auth/recuperacion/confirmar",
        json={
            "testigo": _testigo(con_correo[0]["enlace"]),
            "contrasena": CLAVE_NUEVA,
        },
    )
    assert viejo.status_code == 404

    nuevo = client.post(
        "/api/auth/recuperacion/confirmar",
        json={
            "testigo": _testigo(con_correo[1]["enlace"]),
            "contrasena": CLAVE_NUEVA,
        },
    )
    assert nuevo.status_code == 200


def test_un_testigo_inventado_no_abre_nada(client, datos, con_correo):
    respuesta = client.post(
        "/api/auth/recuperacion/confirmar",
        json={"testigo": "n" * 43, "contrasena": CLAVE_NUEVA},
    )
    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "RECURSO_NO_ENCONTRADO"


def test_una_cuenta_desactivada_no_recibe_enlace(client, datos, con_correo, db_session):
    cuenta = db_session.query(Usuario).filter(Usuario.correo == CORREO_PACIENTE).one()
    cuenta.activo = False
    db_session.commit()

    respuesta = _pedir(client)

    assert respuesta.status_code == 202  # misma respuesta que siempre
    assert con_correo == []


# --- Calidad de la contrasena nueva ----------------------------------------


def test_la_contrasena_nueva_debe_tener_ocho_caracteres(client, datos, con_correo):
    _pedir(client)
    respuesta = client.post(
        "/api/auth/recuperacion/confirmar",
        json={"testigo": _testigo(con_correo[0]["enlace"]), "contrasena": "corta"},
    )

    assert respuesta.status_code == 422
    assert any(d["campo"] == "contrasena" for d in respuesta.json()["detalles"])


def test_se_rechazan_los_espacios_de_los_bordes(client, datos, con_correo):
    """El teclado del telefono anade un espacio al completar palabras."""
    _pedir(client)
    respuesta = client.post(
        "/api/auth/recuperacion/confirmar",
        json={
            "testigo": _testigo(con_correo[0]["enlace"]),
            "contrasena": "ClaveNueva2026 ",
        },
    )

    assert respuesta.status_code == 422
    assert "espacios" in respuesta.text


# --- Alcance del perfil -----------------------------------------------------


def test_el_medico_tambien_recupera_su_acceso(client, datos, con_correo):
    respuesta = _pedir(client, "milko.ugaz@consultorio.pe")
    assert respuesta.status_code == 202
    assert len(con_correo) == 1

    client.post(
        "/api/auth/recuperacion/confirmar",
        json={
            "testigo": _testigo(con_correo[0]["enlace"]),
            "contrasena": CLAVE_NUEVA,
        },
    )
    assert (
        _entrar(client, CLAVE_NUEVA, "milko.ugaz@consultorio.pe", "medico").status_code
        == 200
    )


def test_recuperar_no_cambia_el_perfil_de_la_cuenta(client, datos, con_correo):
    """El enlace devuelve el acceso; no concede permisos que no se tenian."""
    _pedir(client)
    client.post(
        "/api/auth/recuperacion/confirmar",
        json={
            "testigo": _testigo(con_correo[0]["enlace"]),
            "contrasena": CLAVE_NUEVA,
        },
    )

    # Con la contrasena nueva sigue siendo paciente, no medico.
    assert _entrar(client, CLAVE_NUEVA, CORREO_PACIENTE, "medico").status_code == 401
    assert _entrar(client, CLAVE_NUEVA).json()["usuario"]["rol"] == "paciente"
