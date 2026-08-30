"""Verificacion de HU02 - gestion de pacientes polimedicados (RF02)."""
from __future__ import annotations

FICHA_VALIDA = {
    "edad": 72,
    "sexo": "F",
    "diagnostico": "hta",
    "nivel_socioeconomico": "bajo",
    "aseguramiento": "sis",
    "zona_residencia": "urbana",
    "tiempo_enfermedad_anios": 12.5,
    "comorbilidades": 3,
    "numero_farmacos": 9,
    "tomas_dia": 6,
    "controles_programados_6m": 6,
    "controles_perdidos_6m": 2,
    "puntaje_morisky": 2,
    "incumplimiento_basal": True,
}


def test_alta_persiste_y_asigna_codigo_correlativo(client, cab_medico):
    """Criterio de aceptacion: alta persistida y consultable."""
    creacion = client.post("/api/pacientes", json=FICHA_VALIDA, headers=cab_medico)
    assert creacion.status_code == 201, creacion.text

    cuerpo = creacion.json()
    assert cuerpo["codigo_anonimizado"] == "P-002"  # P-001 ya existe en el consultorio
    assert cuerpo["activo"] is True

    consulta = client.get(f"/api/pacientes/{cuerpo['id_paciente']}", headers=cab_medico)
    assert consulta.status_code == 200
    assert consulta.json()["numero_farmacos"] == 9


def test_rechaza_paciente_no_polimedicado(client, cab_medico):
    """Criterio de elegibilidad del Anexo n.o 04: minimo 5 farmacos."""
    ficha = {**FICHA_VALIDA, "numero_farmacos": 3}
    respuesta = client.post("/api/pacientes", json=ficha, headers=cab_medico)

    assert respuesta.status_code == 422
    cuerpo = respuesta.json()
    assert cuerpo["codigo"] == "VALIDACION_FALLIDA"
    assert any(d["campo"] == "numero_farmacos" for d in cuerpo["detalles"])


def test_rechaza_controles_incoherentes(client, cab_medico):
    ficha = {**FICHA_VALIDA, "controles_programados_6m": 2, "controles_perdidos_6m": 5}
    respuesta = client.post("/api/pacientes", json=ficha, headers=cab_medico)

    assert respuesta.status_code == 422
    assert "controles perdidos" in respuesta.text.lower()


def test_rechaza_campos_no_previstos(client, cab_medico):
    """La validacion estricta impide colar columnas fuera del Anexo n.o 04."""
    ficha = {**FICHA_VALIDA, "presion_arterial": "140/90"}
    respuesta = client.post("/api/pacientes", json=ficha, headers=cab_medico)
    assert respuesta.status_code == 422


def test_paciente_no_puede_dar_de_alta(client, cab_paciente):
    """RBAC: el alta de fichas es privativa del perfil medico."""
    respuesta = client.post("/api/pacientes", json=FICHA_VALIDA, headers=cab_paciente)

    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "PERMISO_DENEGADO"


def test_actualizacion_parcial_conserva_el_resto_de_la_ficha(client, cab_medico, datos):
    id_paciente = datos["ficha"].id_paciente

    respuesta = client.patch(
        f"/api/pacientes/{id_paciente}",
        json={"numero_farmacos": 11, "tomas_dia": 8},
        headers=cab_medico,
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["numero_farmacos"] == 11
    assert cuerpo["tomas_dia"] == 8
    assert cuerpo["edad"] == 68  # no enviado: se conserva


def test_actualizacion_valida_la_coherencia_del_estado_resultante(
    client, cab_medico, datos
):
    """La regla se evalua sobre la ficha fusionada, no solo sobre lo enviado.

    La ficha tiene 6 controles programados y 3 perdidos; bajar los programados
    a 2 sin tocar los perdidos produciria un estado incoherente.
    """
    respuesta = client.patch(
        f"/api/pacientes/{datos['ficha'].id_paciente}",
        json={"controles_programados_6m": 2},
        headers=cab_medico,
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "CONFLICTO"


def test_listado_solo_devuelve_los_pacientes_a_cargo(
    client, cab_medico, cab_otro_medico
):
    propio = client.get("/api/pacientes", headers=cab_medico).json()
    ajeno = client.get("/api/pacientes", headers=cab_otro_medico).json()

    assert propio["total"] == 1
    assert propio["items"][0]["codigo_anonimizado"] == "P-001"
    assert ajeno["total"] == 0


def test_medico_ajeno_no_accede_a_la_ficha(client, cab_otro_medico, datos):
    respuesta = client.get(
        f"/api/pacientes/{datos['ficha'].id_paciente}", headers=cab_otro_medico
    )
    assert respuesta.status_code == 403


def test_paciente_solo_accede_a_su_propia_ficha(client, cab_medico, cab_paciente, datos):
    propia = client.get(
        f"/api/pacientes/{datos['ficha'].id_paciente}", headers=cab_paciente
    )
    assert propia.status_code == 200

    otra = client.post("/api/pacientes", json=FICHA_VALIDA, headers=cab_medico).json()
    ajena = client.get(f"/api/pacientes/{otra['id_paciente']}", headers=cab_paciente)

    assert ajena.status_code == 403


def test_baja_es_logica_y_retira_del_listado(client, cab_medico, datos):
    id_paciente = datos["ficha"].id_paciente

    baja = client.delete(f"/api/pacientes/{id_paciente}", headers=cab_medico)
    assert baja.status_code == 200
    assert baja.json()["activo"] is False

    # Sale del panel, pero la ficha sigue existiendo para el analisis.
    assert client.get("/api/pacientes", headers=cab_medico).json()["total"] == 0
    assert client.get(f"/api/pacientes/{id_paciente}", headers=cab_medico).status_code == 200


def test_paciente_inexistente_responde_404(client, cab_medico):
    respuesta = client.get("/api/pacientes/no-existe", headers=cab_medico)
    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "RECURSO_NO_ENCONTRADO"


def test_sin_token_no_hay_acceso(client):
    assert client.get("/api/pacientes").status_code == 401
