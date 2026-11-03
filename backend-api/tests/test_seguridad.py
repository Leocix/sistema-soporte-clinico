"""Verificacion de seguridad del API (RNF01).

Son datos de salud: lo que se comprueba aqui no es que el sistema funcione,
sino que **no** haga cosas que no debe. Cada prueba corresponde a un riesgo
concreto del despliegue publico.

El cifrado del trafico (TLS) y el cifrado en reposo del gestor son garantias de
la plataforma, no del codigo: se verifican contra el servicio desplegado y
quedan documentados en `DESPLIEGUE.md`.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.db.models import Paciente, Usuario


# --- Contrasenas -------------------------------------------------------------


def test_la_contrasena_nunca_se_guarda_legible(db_session, datos):
    usuario = db_session.query(Usuario).first()

    assert usuario.hash_contrasena.startswith("$2b$")
    assert "Segura" not in usuario.hash_contrasena


def test_dos_usuarios_con_la_misma_contrasena_tienen_hash_distinto():
    """Cada hash lleva su propia sal: una tabla robada no se descifra en bloque."""
    uno, otro = hash_password("MismaClave123"), hash_password("MismaClave123")

    assert uno != otro
    assert verify_password("MismaClave123", uno)
    assert not verify_password("OtraClave123", uno)


# --- Sesion y testigo --------------------------------------------------------


def test_un_token_firmado_con_otra_clave_no_vale(client, datos):
    """Fabricar un token sin la clave del servidor no abre ninguna puerta."""
    falso = jwt.encode(
        {"sub": datos["medico"].id_usuario, "rol": "medico",
         "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        "clave-del-atacante", algorithm="HS256",
    )

    respuesta = client.get("/api/pacientes", headers={"Authorization": f"Bearer {falso}"})
    assert respuesta.status_code == 401


def test_un_token_vencido_no_vale(client, datos):
    vencido = jwt.encode(
        {"sub": datos["medico"].id_usuario, "rol": "medico",
         "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.secret_key, algorithm=settings.algorithm,
    )

    respuesta = client.get("/api/pacientes", headers={"Authorization": f"Bearer {vencido}"})
    assert respuesta.status_code == 401


def test_el_rol_del_token_no_se_puede_elevar(client, datos):
    """Un paciente que se firma a si mismo como medico sigue sin serlo: el rol
    se comprueba contra la base de datos, no solo contra el token."""
    token = jwt.encode(
        {"sub": datos["cuenta_paciente"].id_usuario, "rol": "medico",
         "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        settings.secret_key, algorithm=settings.algorithm,
    )

    respuesta = client.get("/api/pacientes", headers={"Authorization": f"Bearer {token}"})
    assert respuesta.status_code == 403


@pytest.mark.parametrize("cabecera", ["", "Bearer", "Bearer   ", "Token abc", "Bearer abc.def"])
def test_cabeceras_de_autorizacion_malformadas(client, cabecera):
    respuesta = client.get("/api/pacientes", headers={"Authorization": cabecera})
    assert respuesta.status_code == 401


# --- No revelar quien esta registrado ----------------------------------------


def test_el_acceso_no_permite_averiguar_que_correos_existen(client, datos):
    """Misma respuesta exista o no la cuenta: si no, la pantalla de acceso se
    convierte en una lista de usuarios del consultorio."""
    existente = client.post("/api/auth/login", json={
        "correo": datos["medico"].correo, "contrasena": "ClaveEquivocada123", "perfil": "medico",
    })
    inexistente = client.post("/api/auth/login", json={
        "correo": "no.existe@consultorio.pe", "contrasena": "ClaveEquivocada123", "perfil": "medico",
    })

    assert existente.status_code == inexistente.status_code == 401
    assert existente.json()["mensaje"] == inexistente.json()["mensaje"]


def test_la_recuperacion_responde_igual_exista_o_no_la_cuenta(client, datos):
    existente = client.post("/api/auth/recuperacion", json={"correo": datos["medico"].correo})
    inexistente = client.post("/api/auth/recuperacion", json={"correo": "nadie@ejemplo.pe"})

    assert existente.status_code == inexistente.status_code
    assert existente.json()["mensaje"] == inexistente.json()["mensaje"]


# --- Aislamiento de los datos clinicos ---------------------------------------


def test_un_medico_no_alcanza_los_pacientes_de_otro(client, cab_otro_medico, datos):
    """El rol no basta: la autorizacion es por paciente a cargo."""
    id_ajeno = datos["ficha"].id_paciente

    assert client.get(f"/api/pacientes/{id_ajeno}", headers=cab_otro_medico).status_code == 403
    assert client.patch(f"/api/pacientes/{id_ajeno}", json={"edad": 80},
                        headers=cab_otro_medico).status_code == 403
    assert client.get(f"/api/prediccion/pacientes/{id_ajeno}",
                      headers=cab_otro_medico).status_code == 403
    assert client.get(f"/api/adherencia/pacientes/{id_ajeno}/registros",
                      headers=cab_otro_medico).status_code == 403


def test_el_paciente_no_accede_a_las_vistas_del_medico(client, cab_paciente):
    for ruta in ("/api/pacientes", "/api/reportes/general", "/api/alertas",
                 "/api/prediccion/estado"):
        assert client.get(ruta, headers=cab_paciente).status_code == 403, ruta


def test_la_busqueda_no_ejecuta_lo_que_le_escriban(client, cab_medico, datos):
    """Los parametros viajan como valores, no como SQL: la tabla sigue ahi."""
    respuesta = client.get("/api/pacientes", params={"busqueda": "'; DROP TABLE pacientes;--"},
                           headers=cab_medico)

    assert respuesta.status_code == 200
    assert respuesta.json()["items"] == []
    assert client.get("/api/pacientes", headers=cab_medico).json()["total"] == 1


# --- Lo que sale del servidor ------------------------------------------------


def test_los_errores_no_filtran_la_estructura_interna(client, cab_medico):
    respuesta = client.get("/api/pacientes/no-existe", headers=cab_medico)
    cuerpo = respuesta.text.lower()

    assert respuesta.status_code == 404
    for filtracion in ("traceback", "select ", "sqlalchemy", "password", "c:\\\\"):
        assert filtracion not in cuerpo
    # En su lugar, un identificador con el que pedir soporte.
    assert respuesta.json()["id_traza"]


def test_las_respuestas_llevan_las_cabeceras_de_seguridad(client):
    cabeceras = client.get("/health").headers

    assert cabeceras["X-Content-Type-Options"] == "nosniff"
    assert cabeceras["X-Frame-Options"] == "DENY"
    assert cabeceras["Referrer-Policy"] == "no-referrer"
    assert "frame-ancestors 'none'" in cabeceras["Content-Security-Policy"]
    # Los datos de salud no deben quedar en caches intermedias.
    assert cabeceras["Cache-Control"] == "no-store"


def test_la_documentacion_puede_cargar_swagger_y_el_api_sigue_cerrado(client):
    # Con `default-src 'none'` el navegador bloquea Swagger UI y /docs queda en blanco.
    docs = client.get("/docs").headers["Content-Security-Policy"]
    assert "https://cdn.jsdelivr.net" in docs
    assert "frame-ancestors 'none'" in docs

    api = client.get("/api/pacientes").headers["Content-Security-Policy"]
    assert api.startswith("default-src 'none'")


def test_la_ficha_del_paciente_no_viaja_con_su_contrasena(client, cab_medico, datos):
    cuerpo = client.get(f"/api/pacientes/{datos['ficha'].id_paciente}", headers=cab_medico).text

    for prohibido in ("hash_contrasena", "contrasena", "$2b$"):
        assert prohibido not in cuerpo


def test_al_microservicio_no_se_le_envian_datos_personales(db_session, datos):
    """El modelo solo necesita variables clinicas y el codigo anonimizado."""
    from app.services.ml_inference import ficha_para_modelo

    paciente = db_session.query(Paciente).first()
    enviado = ficha_para_modelo(paciente)

    assert enviado["codigo_anonimizado"] == paciente.codigo_anonimizado
    for dato in ("nombres", "apellidos", "documento_identidad", "correo", "telefono"):
        assert dato not in enviado


def test_el_esquema_rechaza_campos_no_previstos(client, cab_medico, datos):
    """Nada entra a la ficha por la puerta de atras."""
    respuesta = client.patch(f"/api/pacientes/{datos['ficha'].id_paciente}",
                             json={"id_medico_tratante": "otro-medico"}, headers=cab_medico)
    assert respuesta.status_code == 422


def test_los_errores_de_validacion_llegan_en_castellano(client, cab_medico):
    """Observación de la caja negra: Pydantic responde en inglés por defecto."""
    r = client.post("/api/pacientes", headers=cab_medico, json={
        "nombres": "Ana", "apellidos": "Reyes", "edad": 17, "sexo": "X",
        "diagnostico": "hta", "numero_farmacos": 7, "tomas_dia": 3})
    assert r.status_code == 422
    motivos = {d["campo"]: d["motivo"] for d in r.json()["detalles"]}
    assert motivos["edad"] == "Debe ser mayor o igual a 18."
    assert motivos["sexo"].startswith("Valor no permitido. Use:")
    assert " or " not in motivos["sexo"]
