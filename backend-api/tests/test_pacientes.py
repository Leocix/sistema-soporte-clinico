"""Verificacion de HU02 - gestion de pacientes polimedicados (RF02)."""
from __future__ import annotations

FICHA_VALIDA = {
    "nombres": "Ana Maria",
    "apellidos": "Reyes Torres",
    "correo": "ana.reyes@correo.pe",
    "telefono": "987123456",
    "edad": 72,
    "sexo": "F",
    "diagnostico": "hta",
    "nivel_educativo": "secundaria",
    "convivencia": "acompanado",
    "apoyo_familiar": True,
    "tiempo_enfermedad_anios": 12.5,
    "lista_comorbilidades": ["dislipidemia", "enfermedad_renal_cronica", "depresion"],
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


# --- Identificación clínica -------------------------------------------------


def test_el_alta_exige_nombre_y_apellidos(client, cab_medico):
    """El médico debe poder saber a quién llamar ante un riesgo alto."""
    ficha = {k: v for k, v in FICHA_VALIDA.items() if k not in ("nombres", "apellidos")}
    respuesta = client.post("/api/pacientes", json=ficha, headers=cab_medico)

    assert respuesta.status_code == 422
    campos = {d["campo"] for d in respuesta.json()["detalles"]}
    assert {"nombres", "apellidos"} <= campos


def test_los_nombres_se_normalizan_al_capturarlos(client, cab_medico):
    """Se teclean a mano: dos capturas del mismo nombre no deben diferir."""
    ficha = {**FICHA_VALIDA, "nombres": "  Ana   Maria ", "apellidos": " Reyes  Torres  "}
    respuesta = client.post("/api/pacientes", json=ficha, headers=cab_medico)

    assert respuesta.status_code == 201
    assert respuesta.json()["nombres"] == "Ana Maria"
    assert respuesta.json()["apellidos"] == "Reyes Torres"


def test_el_correo_del_paciente_se_valida(client, cab_medico):
    ficha = {**FICHA_VALIDA, "correo": "no-es-un-correo"}
    respuesta = client.post("/api/pacientes", json=ficha, headers=cab_medico)

    assert respuesta.status_code == 422
    assert any(d["campo"] == "correo" for d in respuesta.json()["detalles"])


def test_la_identidad_es_visible_para_el_medico_tratante(client, cab_medico, datos):
    respuesta = client.get(
        f"/api/pacientes/{datos['ficha'].id_paciente}", headers=cab_medico
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["nombres"] == "Jose"
    assert cuerpo["telefono"] == "987654321"
    # El seudónimo sigue siendo la clave con la que el paciente viaja al dataset.
    assert cuerpo["codigo_anonimizado"] == "P-001"


def test_la_busqueda_encuentra_por_nombre_y_por_codigo(client, cab_medico):
    """El médico busca por el nombre que recuerda, no por el seudónimo."""
    client.post("/api/pacientes", json=FICHA_VALIDA, headers=cab_medico)

    def total(termino):
        return client.get("/api/pacientes", params={"busqueda": termino},
                          headers=cab_medico).json()["total"]

    assert total("Reyes") == 1        # apellidos
    assert total("ana") == 1          # nombres, sin distinguir mayúsculas
    assert total("P-002") == 1        # código
    assert total("Inexistente") == 0


def test_un_correo_heredado_no_valido_no_tumba_el_listado(client, cab_medico, datos, db_session):
    """Estricto al entrar, tolerante al salir.

    Una dirección mal formada puede llegar por una carga masiva o una
    migración. Rechazarla al mostrarla dejaría al médico sin listado entero por
    culpa de una sola ficha.
    """
    datos["ficha"].correo = "correo-heredado@dominio.local"
    db_session.commit()

    listado = client.get("/api/pacientes", headers=cab_medico)
    assert listado.status_code == 200
    assert listado.json()["total"] == 1

    # Pero el alta sí sigue exigiendo una dirección válida.
    ficha = {**FICHA_VALIDA, "correo": "otro@dominio.local"}
    assert client.post("/api/pacientes", json=ficha, headers=cab_medico).status_code == 422


# --- Comorbilidades concretas y contexto social ----------------------------


def test_el_total_de_comorbilidades_se_calcula_de_la_lista(client, cab_medico):
    """El medico marca enfermedades; el modelo recibe cuantas son."""
    ficha = {**FICHA_VALIDA, "lista_comorbilidades": ["obesidad", "artrosis", "obesidad"]}
    cuerpo = client.post("/api/pacientes", json=ficha, headers=cab_medico).json()

    assert cuerpo["lista_comorbilidades"] == ["obesidad", "artrosis"]
    assert cuerpo["comorbilidades"] == 2
    assert cuerpo["nivel_educativo"] == "secundaria"
    assert cuerpo["apoyo_familiar"] is True


def test_editar_la_lista_recalcula_el_total(client, cab_medico, datos):
    id_paciente = datos["ficha"].id_paciente
    respuesta = client.patch(
        f"/api/pacientes/{id_paciente}",
        json={"lista_comorbilidades": ["hipotiroidismo"]},
        headers=cab_medico,
    )
    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["comorbilidades"] == 1

    vacia = client.patch(
        f"/api/pacientes/{id_paciente}", json={"lista_comorbilidades": []}, headers=cab_medico
    )
    assert vacia.json()["comorbilidades"] == 0


def test_rechaza_comorbilidades_fuera_del_catalogo(client, cab_medico):
    ficha = {**FICHA_VALIDA, "lista_comorbilidades": ["gripe"]}
    assert client.post("/api/pacientes", json=ficha, headers=cab_medico).status_code == 422


def test_el_total_no_se_envia_a_mano(client, cab_medico):
    """El total lo calcula el sistema; aceptarlo permitiria contradecir la lista."""
    ficha = {**FICHA_VALIDA, "comorbilidades": 5}
    assert client.post("/api/pacientes", json=ficha, headers=cab_medico).status_code == 422


def test_ya_no_se_aceptan_las_variables_socioeconomicas_retiradas(client, cab_medico):
    ficha = {**FICHA_VALIDA, "aseguramiento": "sis"}
    assert client.post("/api/pacientes", json=ficha, headers=cab_medico).status_code == 422


# --- Defectos hallados por la caja negra (CN-18 y CN-19) ---------------------


def test_los_nombres_no_admiten_digitos_ni_simbolos(client, cab_medico, datos):
    """CN-18: la regla del formulario se aplica también en el API."""
    for campo in ("nombres", "apellidos"):
        alta = client.post("/api/pacientes", json={**FICHA_VALIDA, campo: "Ana3"}, headers=cab_medico)
        assert alta.status_code == 422, campo
    edicion = client.patch(f"/api/pacientes/{datos['ficha'].id_paciente}",
                           json={"nombres": "Jose#"}, headers=cab_medico)
    assert edicion.status_code == 422
    # Tildes, eñes, apóstrofos y guiones siguen siendo válidos.
    valido = client.post("/api/pacientes", json={**FICHA_VALIDA, "apellidos": "O'Brien Muñoz-Díaz"},
                         headers=cab_medico)
    assert valido.status_code == 201


def test_el_tiempo_de_enfermedad_no_supera_la_edad(client, cab_medico, datos):
    """CN-19: en el alta y sobre el estado resultante de una edición."""
    alta = client.post("/api/pacientes", json={**FICHA_VALIDA, "edad": 30,
                                               "tiempo_enfermedad_anios": 40}, headers=cab_medico)
    assert alta.status_code == 422
    limite = client.post("/api/pacientes", json={**FICHA_VALIDA, "edad": 30,
                                                 "tiempo_enfermedad_anios": 30}, headers=cab_medico)
    assert limite.status_code == 201
    # La ficha P-001 tiene 68 años: subir solo el tiempo de enfermedad la vuelve incoherente.
    edicion = client.patch(f"/api/pacientes/{datos['ficha'].id_paciente}",
                           json={"tiempo_enfermedad_anios": 70}, headers=cab_medico)
    assert edicion.status_code == 409
