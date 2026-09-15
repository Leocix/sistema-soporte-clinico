"""Verificacion del alta del acceso movil desde el panel (RF01/RF02).

Sin esta ruta el circuito quedaba roto en un punto que no se ve en ningun
diagrama: el medico daba de alta la ficha con su correo y no tenia forma de
decirle al paciente con que contrasena entrar. La cuenta solo podia crearla un
script en el servidor.
"""
from __future__ import annotations

from app.core.security import verify_password
from app.db.models import Paciente, Rol, Usuario

FICHA = {
    "nombres": "Ana Maria",
    "apellidos": "Reyes Torres",
    "correo": "ana.reyes@correo.pe",
    "edad": 72,
    "sexo": "F",
    "diagnostico": "hta",
    "lista_comorbilidades": ["dislipidemia", "obesidad", "artrosis"],
    "numero_farmacos": 9,
    "tomas_dia": 6,
    "controles_programados_6m": 6,
    "controles_perdidos_6m": 2,
}


def _alta(client, cab_medico, **campos) -> dict:
    respuesta = client.post(
        "/api/pacientes", json={**FICHA, **campos}, headers=cab_medico
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def _generar(client, cab_medico, id_paciente):
    return client.post(f"/api/pacientes/{id_paciente}/acceso", headers=cab_medico)


def _entrar(client, correo, clave):
    return client.post(
        "/api/auth/login",
        json={"correo": correo, "contrasena": clave, "perfil": "paciente"},
    )


# --- Alta del acceso --------------------------------------------------------


def test_el_medico_genera_el_acceso_y_el_paciente_entra(client, cab_medico):
    ficha = _alta(client, cab_medico)
    assert ficha["tiene_acceso_movil"] is False

    respuesta = _generar(client, cab_medico, ficha["id_paciente"])
    assert respuesta.status_code == 201, respuesta.text

    cuerpo = respuesta.json()
    assert cuerpo["creada"] is True
    assert cuerpo["correo"] == "ana.reyes@correo.pe"
    assert cuerpo["nombre_completo"] == "Ana Maria Reyes Torres"
    assert len(cuerpo["contrasena_temporal"]) == 10
    # Se dicta por telefono: no debe llevar caracteres que se confundan.
    assert not set(cuerpo["contrasena_temporal"]) & set("Ol0I1")

    # La credencial recien entregada sirve de verdad.
    assert _entrar(client, cuerpo["correo"], cuerpo["contrasena_temporal"]).status_code == 200


def test_la_ficha_declara_que_ya_tiene_acceso(client, cab_medico):
    ficha = _alta(client, cab_medico)
    _generar(client, cab_medico, ficha["id_paciente"])

    consulta = client.get(f"/api/pacientes/{ficha['id_paciente']}", headers=cab_medico)
    assert consulta.json()["tiene_acceso_movil"] is True


def test_la_contrasena_no_queda_recuperable(client, cab_medico, db_session):
    """En la base solo queda el hash: ni el medico ni el administrador la ven."""
    ficha = _alta(client, cab_medico)
    clave = _generar(client, cab_medico, ficha["id_paciente"]).json()["contrasena_temporal"]

    cuenta = db_session.query(Usuario).filter(
        Usuario.correo == "ana.reyes@correo.pe"
    ).one()
    assert clave not in cuenta.hash_contrasena
    assert verify_password(clave, cuenta.hash_contrasena)


# --- Restablecimiento -------------------------------------------------------


def test_volver_a_generarlo_cambia_la_contrasena_y_no_duplica_la_cuenta(
    client, cab_medico, db_session
):
    """Dar acceso y volver a darlo son el mismo gesto en la consulta."""
    ficha = _alta(client, cab_medico)
    primera = _generar(client, cab_medico, ficha["id_paciente"]).json()

    segunda_respuesta = _generar(client, cab_medico, ficha["id_paciente"])
    assert segunda_respuesta.status_code == 201
    segunda = segunda_respuesta.json()

    assert segunda["creada"] is False
    assert segunda["contrasena_temporal"] != primera["contrasena_temporal"]

    # Una sola cuenta, y solo vale la ultima contrasena entregada.
    assert db_session.query(Usuario).filter(
        Usuario.correo == "ana.reyes@correo.pe"
    ).count() == 1
    assert _entrar(client, primera["correo"], primera["contrasena_temporal"]).status_code == 401
    assert _entrar(client, segunda["correo"], segunda["contrasena_temporal"]).status_code == 200


def test_el_correo_corregido_en_la_ficha_se_traslada_a_la_cuenta(
    client, cab_medico
):
    """El medico puede corregir el correo despues de haber creado el acceso."""
    ficha = _alta(client, cab_medico)
    _generar(client, cab_medico, ficha["id_paciente"])

    client.patch(
        f"/api/pacientes/{ficha['id_paciente']}",
        json={"correo": "ana.corregido@correo.pe"},
        headers=cab_medico,
    )
    nueva = _generar(client, cab_medico, ficha["id_paciente"]).json()

    assert nueva["correo"] == "ana.corregido@correo.pe"
    assert _entrar(client, "ana.corregido@correo.pe", nueva["contrasena_temporal"]).status_code == 200


# --- Condiciones que lo impiden ---------------------------------------------


def test_sin_correo_en_la_ficha_no_hay_acceso(client, cab_medico):
    ficha = _alta(client, cab_medico, correo=None)

    respuesta = _generar(client, cab_medico, ficha["id_paciente"])

    assert respuesta.status_code == 409
    assert "correo" in respuesta.json()["mensaje"].lower()


def test_un_paciente_dado_de_baja_no_recibe_acceso(client, cab_medico):
    ficha = _alta(client, cab_medico)
    client.delete(f"/api/pacientes/{ficha['id_paciente']}", headers=cab_medico)

    respuesta = _generar(client, cab_medico, ficha["id_paciente"])

    assert respuesta.status_code == 409
    assert "baja" in respuesta.json()["mensaje"].lower()


def test_un_correo_que_ya_es_de_otra_cuenta_se_rechaza(client, cab_medico, datos):
    """El correo del paciente de la ficha existente ya tiene cuenta propia."""
    ficha = _alta(client, cab_medico, correo="jose.vasquez@correo.pe")

    respuesta = _generar(client, cab_medico, ficha["id_paciente"])

    assert respuesta.status_code == 409
    assert "otra cuenta" in respuesta.json()["mensaje"].lower()


# --- Quien puede hacerlo ----------------------------------------------------


def test_solo_el_medico_tratante_genera_el_acceso(
    client, cab_medico, cab_otro_medico, cab_paciente
):
    ficha = _alta(client, cab_medico)

    ajeno = _generar(client, cab_otro_medico, ficha["id_paciente"])
    assert ajeno.status_code == 403

    propio_paciente = _generar(client, cab_paciente, ficha["id_paciente"])
    assert propio_paciente.status_code == 403

    assert client.post(f"/api/pacientes/{ficha['id_paciente']}/acceso").status_code == 401
