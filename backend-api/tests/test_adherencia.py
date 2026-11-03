"""Verificacion de HU03 - registro y sincronizacion de tomas (RF03)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

BASE = datetime(2026, 9, 1, 8, 0, tzinfo=timezone.utc)


def toma(horas: int, estado: str = "tomada", retraso_min: int | None = 0) -> dict:
    """Construye un evento de toma programado a BASE + `horas`."""
    programada = BASE + timedelta(hours=horas)
    evento = {
        "medicamento": "Losartan 50 mg",
        "dosis": "1 tableta",
        "fecha_hora_programada": programada.isoformat(),
        "estado": estado,
    }
    if retraso_min is not None and estado in ("tomada", "tomada_tarde"):
        evento["fecha_hora_registro"] = (
            programada + timedelta(minutes=retraso_min)
        ).isoformat()
    return evento


def test_paciente_registra_su_toma(client, cab_paciente):
    """Criterio de aceptacion: cada toma queda registrada y sincronizada."""
    respuesta = client.post("/api/adherencia/registros", json=toma(0), headers=cab_paciente)

    assert respuesta.status_code == 201, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["cumplida"] is True
    assert cuerpo["minutos_de_retraso"] == 0.0


def test_el_reintento_no_duplica_el_evento(client, cab_paciente, cab_medico, datos):
    """Idempotencia: reenviar la misma toma actualiza, no crea otra fila."""
    evento = toma(0)

    primera = client.post("/api/adherencia/registros", json=evento, headers=cab_paciente)
    segunda = client.post("/api/adherencia/registros", json=evento, headers=cab_paciente)

    assert primera.status_code == 201
    assert segunda.status_code == 200  # reintento reconocido, no un alta nueva
    assert primera.json()["id_registro"] == segunda.json()["id_registro"]

    historial = client.get(
        f"/api/adherencia/pacientes/{datos['ficha'].id_paciente}/registros",
        headers=cab_medico,
    )
    assert len(historial.json()) == 1


def test_el_desenlace_de_una_dosis_puede_corregirse(client, cab_paciente):
    """Una toma pospuesta que finalmente se cumple conserva el ultimo estado."""
    client.post("/api/adherencia/registros", json=toma(0, "pospuesta", None),
                headers=cab_paciente)
    correccion = client.post(
        "/api/adherencia/registros", json=toma(0, "tomada_tarde", 45), headers=cab_paciente
    )

    assert correccion.status_code == 200
    assert correccion.json()["estado"] == "tomada_tarde"
    assert correccion.json()["minutos_de_retraso"] == 45.0


def test_sincronizacion_en_lote_tras_perdida_de_conectividad(
    client, cab_paciente, cab_medico, datos
):
    lote = [toma(0), toma(8, "omitida", None), toma(16, "tomada_tarde", 30)]

    respuesta = client.post("/api/adherencia/registros/lote", json=lote, headers=cab_paciente)

    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["creados"] == 3
    assert respuesta.json()["actualizados"] == 0

    # Reenvio completo de la cola: la app no sabe que ya se sincronizo.
    reenvio = client.post("/api/adherencia/registros/lote", json=lote, headers=cab_paciente)
    assert reenvio.json()["creados"] == 0
    assert reenvio.json()["actualizados"] == 3

    historial = client.get(
        f"/api/adherencia/pacientes/{datos['ficha'].id_paciente}/registros",
        headers=cab_medico,
    )
    assert len(historial.json()) == 3


def test_lote_vacio_y_lote_excedido_se_rechazan(client, cab_paciente):
    assert client.post("/api/adherencia/registros/lote", json=[],
                       headers=cab_paciente).status_code == 400

    excedido = [toma(h) for h in range(201)]
    assert client.post("/api/adherencia/registros/lote", json=excedido,
                       headers=cab_paciente).status_code == 413


def test_toma_cumplida_exige_hora_real(client, cab_paciente):
    evento = toma(0)
    evento.pop("fecha_hora_registro")

    respuesta = client.post("/api/adherencia/registros", json=evento, headers=cab_paciente)

    assert respuesta.status_code == 422
    assert respuesta.json()["codigo"] == "VALIDACION_FALLIDA"


def test_toma_omitida_no_admite_hora_de_toma(client, cab_paciente):
    evento = toma(0, "omitida", None)
    evento["fecha_hora_registro"] = BASE.isoformat()

    respuesta = client.post("/api/adherencia/registros", json=evento, headers=cab_paciente)
    assert respuesta.status_code == 422


def test_paciente_no_puede_registrar_por_un_tercero(client, cab_paciente):
    evento = {**toma(0), "id_paciente": "otro-paciente"}

    respuesta = client.post("/api/adherencia/registros", json=evento, headers=cab_paciente)

    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "PERMISO_DENEGADO"


def test_medico_debe_indicar_el_paciente(client, cab_medico):
    respuesta = client.post("/api/adherencia/registros", json=toma(0), headers=cab_medico)

    assert respuesta.status_code == 400
    assert respuesta.json()["codigo"] == "PACIENTE_REQUERIDO"


def test_paciente_dado_de_baja_no_admite_registros(client, cab_medico, cab_paciente, datos):
    client.delete(f"/api/pacientes/{datos['ficha'].id_paciente}", headers=cab_medico)

    respuesta = client.post("/api/adherencia/registros", json=toma(0), headers=cab_paciente)

    assert respuesta.status_code == 409


def test_resumen_calcula_la_adherencia_observada(client, cab_paciente, cab_medico, datos):
    """Tres cumplidas, dos omitidas y una pospuesta (excluida del calculo)."""
    lote = [
        toma(0, "tomada", 0),
        toma(8, "tomada_tarde", 60),
        toma(16, "omitida", None),
        toma(24, "tomada", 20),
        toma(32, "omitida", None),
        toma(40, "pospuesta", None),
    ]
    client.post("/api/adherencia/registros/lote", json=lote, headers=cab_paciente)

    resumen = client.get(
        f"/api/adherencia/pacientes/{datos['ficha'].id_paciente}/resumen",
        headers=cab_medico,
    ).json()

    assert resumen["total_eventos"] == 6
    assert resumen["cumplidos"] == 3
    assert resumen["omitidos"] == 2
    # 3 cumplidas sobre 5 eventos resueltos; la pospuesta no cuenta.
    assert resumen["tasa_adherencia"] == 60.0
    assert resumen["retraso_promedio_min"] == round((0 + 60 + 20) / 3, 1)
    # La racha se cuenta desde el evento mas reciente con desenlace.
    assert resumen["omisiones_consecutivas"] == 1


def test_medico_ajeno_no_ve_el_historial(client, cab_paciente, cab_otro_medico, datos):
    client.post("/api/adherencia/registros", json=toma(0), headers=cab_paciente)

    respuesta = client.get(
        f"/api/adherencia/pacientes/{datos['ficha'].id_paciente}/registros",
        headers=cab_otro_medico,
    )
    assert respuesta.status_code == 403


# --- Rutas del propio paciente (app móvil) ---------------------------------


def test_paciente_consulta_su_resumen_y_su_historial(client, cab_paciente):
    client.post("/api/adherencia/registros/lote",
                json=[toma(0), toma(8, "omitida", None), toma(16)],
                headers=cab_paciente)

    resumen = client.get("/api/adherencia/mi-resumen", headers=cab_paciente)
    assert resumen.status_code == 200
    assert resumen.json()["total_eventos"] == 3
    assert resumen.json()["cumplidos"] == 2

    historial = client.get("/api/adherencia/mis-registros", headers=cab_paciente)
    assert historial.status_code == 200
    assert len(historial.json()) == 3


def test_las_rutas_propias_exigen_perfil_paciente(client, cab_medico):
    """El médico no tiene ficha propia: sus rutas son las de por identificador."""
    assert client.get("/api/adherencia/mi-resumen", headers=cab_medico).status_code == 404
    assert client.get("/api/adherencia/mis-registros", headers=cab_medico).status_code == 404


# --- Ventana de registro -------------------------------------------------------


def test_una_toma_marcada_dentro_de_la_ventana_se_acepta(client, cab_paciente):
    """Dos horas despues de su hora sigue dentro de la ventana (hasta 3 h)."""
    respuesta = client.post(
        "/api/adherencia/registros", json=toma(0, "tomada_tarde", retraso_min=120), headers=cab_paciente
    )
    assert respuesta.status_code == 201, respuesta.text


def test_no_se_marca_como_tomada_horas_despues_de_su_hora(client, cab_paciente):
    """Marcar por la noche las dosis de la manana es lo que la ventana impide."""
    respuesta = client.post(
        "/api/adherencia/registros", json=toma(0, "tomada_tarde", retraso_min=240), headers=cab_paciente
    )
    assert respuesta.status_code == 422
    assert "ventana de registro" in respuesta.text


def test_no_se_marca_como_tomada_mucho_antes_de_su_hora(client, cab_paciente):
    respuesta = client.post(
        "/api/adherencia/registros", json=toma(0, "tomada", retraso_min=-90), headers=cab_paciente
    )
    assert respuesta.status_code == 422


def test_una_hora_de_toma_futura_delata_un_reloj_adelantado(client, cab_paciente):
    futura = datetime.now(timezone.utc) + timedelta(hours=1)
    respuesta = client.post(
        "/api/adherencia/registros",
        json={"medicamento": "Losartan 50 mg", "fecha_hora_programada": futura.isoformat(),
              "fecha_hora_registro": futura.isoformat(), "estado": "tomada"},
        headers=cab_paciente,
    )
    assert respuesta.status_code == 422
    assert "hora del teléfono" in respuesta.json()["detalles"][0]["motivo"]


def test_la_omision_no_depende_de_la_ventana(client, cab_paciente):
    """Declarar que no se tomo una dosis puede hacerse en cualquier momento."""
    respuesta = client.post("/api/adherencia/registros", json=toma(0, "omitida"), headers=cab_paciente)
    assert respuesta.status_code == 201, respuesta.text
