"""Verificacion de HU04 - grupo familiar y corroboracion de la toma (RF09).

Lo que se protege aqui no es una pantalla sino una afirmacion del estudio: que
una toma corroborada vale mas como evidencia que una autorreportada. Eso solo
es cierto si el sistema garantiza que quien corrobora acompana de verdad a ese
paciente, que da fe de un evento que el paciente ya declaro y que lo hace
cuando todavia podia haberlo presenciado. Cada una de esas tres condiciones
tiene su prueba.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.db.models import Acompanante, EstadoAcompanante, RegistroAdherencia

# Misma clave que reparte conftest a las cuentas de prueba.
CLAVE = "Consultorio2026"

INVITACION = {"nombre_invitado": "Rosa Vasquez", "parentesco": "hijo"}


def _invitar(client, cab_paciente, **campos) -> dict:
    respuesta = client.post(
        "/api/familiares/invitaciones",
        json={**INVITACION, **campos},
        headers=cab_paciente,
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def _registrar_familiar(client, codigo: str, correo="rosa.vasquez@correo.pe") -> dict:
    respuesta = client.post(
        "/api/familiares/registro",
        json={
            "codigo": codigo,
            "nombres": "Rosa",
            "apellidos": "Vasquez",
            "correo": correo,
            "contrasena": CLAVE,
        },
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def _familiar(client, cab_paciente) -> dict:
    """Cabecera de un acompanante ya vinculado al paciente de las pruebas."""
    codigo = _invitar(client, cab_paciente)["codigo_invitacion"]
    token = _registrar_familiar(client, codigo)["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _toma_cumplida(client, cab_paciente, medicamento="Losartan 50 mg") -> str:
    """Registra una toma de hoy y devuelve su identificador."""
    programada = datetime.now(timezone.utc) - timedelta(hours=1)
    respuesta = client.post(
        "/api/adherencia/registros",
        json={
            "medicamento": medicamento,
            "dosis": "1 tableta",
            "fecha_hora_programada": programada.isoformat(),
            "fecha_hora_registro": programada.isoformat(),
            "estado": "tomada",
        },
        headers=cab_paciente,
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()["id_registro"]


# --- Invitacion -------------------------------------------------------------


def test_el_paciente_invita_y_recibe_un_codigo(client, cab_paciente):
    cuerpo = _invitar(client, cab_paciente)

    assert cuerpo["estado"] == "invitado"
    assert cuerpo["nombre"] == "Rosa Vasquez"
    assert len(cuerpo["codigo_invitacion"]) == 8
    # El codigo se dicta en voz alta: no debe contener caracteres ambiguos.
    assert not set(cuerpo["codigo_invitacion"]) & set("O0I1")
    assert cuerpo["expira_en"] is not None


def test_el_medico_no_invita_al_grupo_familiar(client, cab_medico):
    """La iniciativa es del paciente: es su consentimiento, no una vigilancia."""
    respuesta = client.post(
        "/api/familiares/invitaciones", json=INVITACION, headers=cab_medico
    )
    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "PERMISO_DENEGADO"


def test_el_grupo_se_limita_a_cinco_personas(client, cab_paciente):
    for i in range(5):
        _invitar(client, cab_paciente, nombre_invitado=f"Familiar {i}")

    respuesta = client.post(
        "/api/familiares/invitaciones", json=INVITACION, headers=cab_paciente
    )
    assert respuesta.status_code == 409
    assert client.get("/api/familiares", headers=cab_paciente).json().__len__() == 5


# --- Alta del acompanante ---------------------------------------------------


def test_el_codigo_crea_la_cuenta_y_la_vincula(client, cab_paciente, db_session):
    codigo = _invitar(client, cab_paciente)["codigo_invitacion"]
    cuerpo = _registrar_familiar(client, codigo)

    assert cuerpo["usuario"]["rol"] == "familiar"
    assert cuerpo["access_token"]

    vinculo = db_session.query(Acompanante).one()
    assert vinculo.estado is EstadoAcompanante.ACTIVO
    assert vinculo.id_usuario is not None
    assert vinculo.fecha_vinculacion is not None


def test_sin_codigo_valido_no_se_crea_ninguna_cuenta(client):
    """No hay registro abierto: la invitacion es la unica puerta de alta."""
    respuesta = client.post(
        "/api/familiares/registro",
        json={
            "codigo": "ZZZZZZZZ",
            "nombres": "Intruso",
            "apellidos": "Cualquiera",
            "correo": "intruso@correo.pe",
            "contrasena": CLAVE,
        },
    )
    assert respuesta.status_code == 404


def test_un_codigo_solo_se_canjea_una_vez(client, cab_paciente):
    codigo = _invitar(client, cab_paciente)["codigo_invitacion"]
    _registrar_familiar(client, codigo)

    segundo = client.post(
        "/api/familiares/registro",
        json={
            "codigo": codigo,
            "nombres": "Otra",
            "apellidos": "Persona",
            "correo": "otra@correo.pe",
            "contrasena": CLAVE,
        },
    )
    assert segundo.status_code == 404


def test_una_invitacion_vencida_no_sirve(client, cab_paciente, db_session):
    _invitar(client, cab_paciente)
    vinculo = db_session.query(Acompanante).one()
    vinculo.expira_en = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()

    respuesta = client.post(
        "/api/familiares/registro",
        json={
            "codigo": vinculo.codigo_invitacion,
            "nombres": "Rosa",
            "apellidos": "Vasquez",
            "correo": "rosa.vasquez@correo.pe",
            "contrasena": CLAVE,
        },
    )
    assert respuesta.status_code == 404


def test_el_correo_repetido_se_rechaza_solo_tras_validar_el_codigo(
    client, cab_paciente
):
    """El orden de las comprobaciones evita enumerar cuentas registradas.

    Con el orden inverso, cualquiera podria averiguar que direcciones existen
    en el sistema probando correos sin tener invitacion alguna.
    """
    sin_codigo = client.post(
        "/api/familiares/registro",
        json={
            "codigo": "ZZZZZZZZ",
            "nombres": "Quien",
            "apellidos": "Sea",
            "correo": "jose.vasquez@correo.pe",  # cuenta existente
            "contrasena": CLAVE,
        },
    )
    assert sin_codigo.status_code == 404  # no revela que el correo existe

    codigo = _invitar(client, cab_paciente)["codigo_invitacion"]
    con_codigo = client.post(
        "/api/familiares/registro",
        json={
            "codigo": codigo,
            "nombres": "Quien",
            "apellidos": "Sea",
            "correo": "jose.vasquez@correo.pe",
            "contrasena": CLAVE,
        },
    )
    assert con_codigo.status_code == 409


# --- Corroboracion ----------------------------------------------------------


def test_el_familiar_ve_y_corrobora_la_toma_reportada(client, cab_paciente):
    cab_familiar = _familiar(client, cab_paciente)
    id_registro = _toma_cumplida(client, cab_paciente)

    pendientes = client.get("/api/familiares/tomas-por-confirmar", headers=cab_familiar)
    assert pendientes.status_code == 200
    assert [t["id_registro"] for t in pendientes.json()] == [id_registro]
    assert pendientes.json()[0]["paciente"] == "Jose Vasquez"

    confirmacion = client.post(
        f"/api/familiares/tomas/{id_registro}/confirmacion", headers=cab_familiar
    )
    assert confirmacion.status_code == 200
    assert confirmacion.json()["corroborada"] is True
    assert confirmacion.json()["confirmada_por"] == "Rosa Vasquez"

    # Ya corroborada, sale de la lista de pendientes.
    despues = client.get("/api/familiares/tomas-por-confirmar", headers=cab_familiar)
    assert despues.json() == []


def test_una_toma_no_se_corrobora_dos_veces(client, cab_paciente):
    cab_familiar = _familiar(client, cab_paciente)
    id_registro = _toma_cumplida(client, cab_paciente)

    client.post(f"/api/familiares/tomas/{id_registro}/confirmacion", headers=cab_familiar)
    repetida = client.post(
        f"/api/familiares/tomas/{id_registro}/confirmacion", headers=cab_familiar
    )

    assert repetida.status_code == 409
    assert repetida.json()["codigo"] == "CONFLICTO"


def test_no_se_corrobora_una_omision(client, cab_paciente, db_session):
    """Una omision es una declaracion contra el propio interes: no necesita
    testigo, y admitirlo permitiria a un familiar avalar incumplimientos."""
    cab_familiar = _familiar(client, cab_paciente)
    programada = datetime.now(timezone.utc) - timedelta(hours=2)
    creacion = client.post(
        "/api/adherencia/registros",
        json={
            "medicamento": "Enalapril 10 mg",
            "fecha_hora_programada": programada.isoformat(),
            "estado": "omitida",
            "motivo_omision": "Olvido",
        },
        headers=cab_paciente,
    )
    assert creacion.status_code == 201

    respuesta = client.post(
        f"/api/familiares/tomas/{creacion.json()['id_registro']}/confirmacion",
        headers=cab_familiar,
    )
    assert respuesta.status_code == 409
    assert "cumplidas" in respuesta.json()["mensaje"]


def test_fuera_de_plazo_no_se_puede_corroborar(client, cab_paciente, db_session):
    """Quien da fe de una dosis debe haberla podido presenciar."""
    cab_familiar = _familiar(client, cab_paciente)
    id_registro = _toma_cumplida(client, cab_paciente)

    registro = db_session.query(RegistroAdherencia).filter_by(
        id_registro=id_registro
    ).one()
    registro.fecha_hora_programada = datetime.now(timezone.utc) - timedelta(days=5)
    db_session.commit()

    respuesta = client.post(
        f"/api/familiares/tomas/{id_registro}/confirmacion", headers=cab_familiar
    )
    assert respuesta.status_code == 409
    assert "plazo" in respuesta.json()["mensaje"].lower()

    # Y tampoco figura ya entre las pendientes.
    pendientes = client.get("/api/familiares/tomas-por-confirmar", headers=cab_familiar)
    assert pendientes.json() == []


def test_el_familiar_no_corrobora_tomas_de_un_paciente_ajeno(
    client, cab_medico, cab_paciente
):
    cab_familiar = _familiar(client, cab_paciente)

    # Una ficha de otro paciente, con su propia toma registrada por el medico.
    otra = client.post(
        "/api/pacientes",
        json={
            "nombres": "Ana", "apellidos": "Reyes Torres",
            "edad": 70, "sexo": "F", "diagnostico": "hta",
            "comorbilidades": 1, "numero_farmacos": 6, "tomas_dia": 4,
            "controles_programados_6m": 6, "controles_perdidos_6m": 1,
        },
        headers=cab_medico,
    ).json()

    programada = datetime.now(timezone.utc) - timedelta(hours=1)
    ajena = client.post(
        "/api/adherencia/registros",
        json={
            "id_paciente": otra["id_paciente"],
            "medicamento": "Metformina 850 mg",
            "fecha_hora_programada": programada.isoformat(),
            "fecha_hora_registro": programada.isoformat(),
            "estado": "tomada",
        },
        headers=cab_medico,
    ).json()

    respuesta = client.post(
        f"/api/familiares/tomas/{ajena['id_registro']}/confirmacion",
        headers=cab_familiar,
    )
    assert respuesta.status_code == 403

    # Ni aparece entre lo que puede confirmar.
    pendientes = client.get("/api/familiares/tomas-por-confirmar", headers=cab_familiar)
    assert ajena["id_registro"] not in [t["id_registro"] for t in pendientes.json()]


# --- Limites del perfil de acompanante --------------------------------------


def test_el_familiar_no_registra_tomas(client, cab_paciente):
    """Corroborar no es reportar: el acompanante da fe, no declara por otro."""
    cab_familiar = _familiar(client, cab_paciente)
    programada = datetime.now(timezone.utc)

    respuesta = client.post(
        "/api/adherencia/registros",
        json={
            "medicamento": "Losartan 50 mg",
            "fecha_hora_programada": programada.isoformat(),
            "fecha_hora_registro": programada.isoformat(),
            "estado": "tomada",
        },
        headers=cab_familiar,
    )
    assert respuesta.status_code in (400, 403)


def test_el_familiar_no_accede_a_la_ficha_clinica(client, cab_paciente, datos):
    cab_familiar = _familiar(client, cab_paciente)

    ficha = client.get(
        f"/api/pacientes/{datos['ficha'].id_paciente}", headers=cab_familiar
    )
    assert ficha.status_code == 403
    assert client.get("/api/pacientes", headers=cab_familiar).status_code == 403


def test_el_familiar_ve_a_quien_acompana(client, cab_paciente):
    cab_familiar = _familiar(client, cab_paciente)
    _toma_cumplida(client, cab_paciente)

    respuesta = client.get("/api/familiares/mis-pacientes", headers=cab_familiar)
    assert respuesta.status_code == 200

    (paciente,) = respuesta.json()
    assert paciente["nombre"] == "Jose Vasquez"
    assert paciente["parentesco"] == "hijo"
    assert paciente["tomas_por_confirmar"] == 1
    # La vista del acompanante no incluye la ficha clinica.
    assert "diagnostico" not in paciente


def test_el_paciente_no_usa_las_rutas_del_acompanante(client, cab_paciente):
    assert (
        client.get("/api/familiares/mis-pacientes", headers=cab_paciente).status_code
        == 403
    )


# --- Retirada ---------------------------------------------------------------


def test_retirar_una_invitacion_pendiente_anula_su_codigo(client, cab_paciente):
    invitacion = _invitar(client, cab_paciente)

    baja = client.delete(
        f"/api/familiares/{invitacion['id_acompanante']}", headers=cab_paciente
    )
    assert baja.status_code == 200
    assert client.get("/api/familiares", headers=cab_paciente).json() == []

    # El codigo emitido deja de servir para crear una cuenta.
    respuesta = client.post(
        "/api/familiares/registro",
        json={
            "codigo": invitacion["codigo_invitacion"],
            "nombres": "Rosa", "apellidos": "Vasquez",
            "correo": "rosa.vasquez@correo.pe", "contrasena": CLAVE,
        },
    )
    assert respuesta.status_code == 404


def test_retirar_a_un_acompanante_activo_conserva_sus_corroboraciones(
    client, cab_paciente, db_session
):
    """La pertenencia termina; el testimonio ya dado forma parte de la traza."""
    cab_familiar = _familiar(client, cab_paciente)
    id_registro = _toma_cumplida(client, cab_paciente)
    client.post(f"/api/familiares/tomas/{id_registro}/confirmacion", headers=cab_familiar)

    grupo = client.get("/api/familiares", headers=cab_paciente).json()
    assert grupo[0]["tomas_corroboradas"] == 1

    baja = client.delete(
        f"/api/familiares/{grupo[0]['id_acompanante']}", headers=cab_paciente
    )
    assert baja.status_code == 200

    vinculo = db_session.query(Acompanante).one()
    assert vinculo.estado is EstadoAcompanante.REVOCADO

    registro = db_session.query(RegistroAdherencia).filter_by(
        id_registro=id_registro
    ).one()
    assert registro.id_confirmante is not None
    assert registro.corroborada is True

    # Y el acompanante retirado pierde el acceso de inmediato.
    assert (
        client.get(
            "/api/familiares/tomas-por-confirmar", headers=cab_familiar
        ).json()
        == []
    )
