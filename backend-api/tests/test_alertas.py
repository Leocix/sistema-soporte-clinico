"""Alertas tempranas de riesgo (RF05).

La alerta es el unico componente que interrumpe al medico, asi que se verifica
tanto que avise cuando debe como que **no** llene la bandeja cuando no debe.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx
import pytest

from app.db.models import Alerta, EstadoAlerta, EstadoToma, OrigenRegistro, RegistroAdherencia
from app.services import ml_inference

T, O, P = EstadoToma.TOMADA, EstadoToma.OMITIDA, EstadoToma.POSPUESTA


def _tomas(db_session, ficha, estados, medicamento="Losartan 50 mg", desde_horas=None):
    """Historial en orden cronologico; el ultimo estado es el mas reciente."""
    horas = desde_horas if desde_horas is not None else len(estados)
    inicio = datetime.now(timezone.utc) - timedelta(hours=horas)
    for dia, estado in enumerate(estados):
        programada = inicio + timedelta(hours=dia)
        db_session.add(RegistroAdherencia(
            id_paciente=ficha.id_paciente, medicamento=medicamento,
            fecha_hora_programada=programada,
            fecha_hora_registro=None if estado is O else programada,
            estado=estado, origen=OrigenRegistro.APP_MOVIL,
            motivo_omision="olvido" if estado is O else None,
        ))
    db_session.commit()


def _abiertas(db_session, ficha) -> dict:
    filas = (
        db_session.query(Alerta)
        .filter(Alerta.id_paciente == ficha.id_paciente, Alerta.estado == EstadoAlerta.ABIERTA)
        .all()
    )
    return {a.tipo.value: a for a in filas}


@pytest.fixture()
def sin_modelo(monkeypatch):
    """La bandeja se consulta sin microservicio: las reglas de traza bastan."""
    def fallar(request):
        raise httpx.ConnectError("sin conexion", request=request)

    monkeypatch.setattr(ml_inference, "_cliente", lambda: httpx.Client(
        base_url="http://ml", transport=httpx.MockTransport(fallar)
    ))


@pytest.fixture()
def modelo_alto(monkeypatch):
    """Microservicio que devuelve riesgo alto para cualquier paciente."""
    def atender(request: httpx.Request) -> httpx.Response:
        import json
        fichas = json.loads(request.content)["fichas"]
        return httpx.Response(200, json={"predicciones": [{
            "codigo_anonimizado": f["codigo_anonimizado"], "probabilidad": 0.88,
            "nivel": "alto", "variables_imputadas": [], "valor_base": None,
            "contribuciones": [], "factores_globales": [],
            "modelo": {"algoritmo": "SVM (RBF)", "entrenado_el": "2026-09-22",
                       "origen_datos": "conjunto de demostracion simulado",
                       "datos_reales": False, "aucroc_validacion_cruzada": 0.8556},
        } for f in fichas]})

    monkeypatch.setattr(ml_inference, "_cliente", lambda: httpx.Client(
        base_url="http://ml", transport=httpx.MockTransport(atender)
    ))


# --- Las reglas avisan cuando deben ----------------------------------------


def test_tres_omisiones_seguidas_generan_alerta(client, cab_medico, datos, db_session, sin_modelo):
    _tomas(db_session, datos["ficha"], [T, T, O, O, O])

    cuerpo = client.get("/api/alertas", headers=cab_medico).json()

    assert cuerpo["abiertas"] >= 1
    omisiones = [a for a in cuerpo["alertas"] if a["tipo"] == "omisiones_seguidas"]
    assert len(omisiones) == 1
    assert omisiones[0]["valor"] == 3
    assert omisiones[0]["codigo_anonimizado"] == "P-001"
    assert "3 tomas omitidas seguidas" in omisiones[0]["motivo"]


def test_cumplimiento_bajo_genera_alerta(client, cab_medico, datos, db_session, sin_modelo):
    # 2 cumplidas de 6 resueltas: 33 %, por debajo del 60 %.
    _tomas(db_session, datos["ficha"], [O, O, O, O, T, T])

    tipos = {a["tipo"] for a in client.get("/api/alertas", headers=cab_medico).json()["alertas"]}
    assert "adherencia_baja" in tipos


def test_riesgo_predicho_alto_genera_alerta(client, cab_medico, datos, db_session, modelo_alto):
    _tomas(db_session, datos["ficha"], [T, T, T])

    cuerpo = client.get("/api/alertas", headers=cab_medico).json()
    predicha = [a for a in cuerpo["alertas"] if a["tipo"] == "riesgo_predicho"]

    assert cuerpo["modelo_disponible"] is True
    assert len(predicha) == 1
    assert predicha[0]["valor"] == 88
    assert "88 %" in predicha[0]["motivo"]


def test_la_alerta_nace_al_sincronizar_la_toma(client, cab_paciente, datos, db_session):
    """El medico no tiene que abrir nada para que la alerta exista."""
    programadas = [datetime.now(timezone.utc) - timedelta(days=d) for d in (3, 2, 1)]
    for programada in programadas:
        respuesta = client.post("/api/adherencia/registros", json={
            "medicamento": "Losartan 50 mg",
            "fecha_hora_programada": programada.isoformat(),
            "estado": "omitida", "motivo_omision": "olvido",
        }, headers=cab_paciente)
        assert respuesta.status_code in (200, 201), respuesta.text

    assert "omisiones_seguidas" in _abiertas(db_session, datos["ficha"])


# --- ... y callan cuando no deben -------------------------------------------


def test_un_paciente_que_cumple_no_genera_alertas(client, cab_medico, datos, db_session, sin_modelo):
    _tomas(db_session, datos["ficha"], [T, T, T, T, T, T])

    cuerpo = client.get("/api/alertas", headers=cab_medico).json()
    assert cuerpo["abiertas"] == 0 and cuerpo["alertas"] == []


def test_pocas_tomas_no_disparan_la_regla_de_adherencia(
    client, cab_medico, datos, db_session, sin_modelo
):
    """Con dos tomas, un 50 % es ruido y no evidencia de incumplimiento."""
    _tomas(db_session, datos["ficha"], [T, O])

    tipos = {a["tipo"] for a in client.get("/api/alertas", headers=cab_medico).json()["alertas"]}
    assert "adherencia_baja" not in tipos


def test_las_pospuestas_no_cuentan_como_omision(client, cab_medico, datos, db_session, sin_modelo):
    _tomas(db_session, datos["ficha"], [T, T, P, P, P])

    assert client.get("/api/alertas", headers=cab_medico).json()["abiertas"] == 0


def test_no_se_acumulan_alertas_repetidas_del_mismo_tipo(
    client, cab_medico, datos, db_session, sin_modelo
):
    """Una bandeja con el mismo aviso veinte veces se deja de leer."""
    _tomas(db_session, datos["ficha"], [T, O, O, O])
    for _ in range(3):
        client.get("/api/alertas", headers=cab_medico)

    omisiones = [
        a for a in db_session.query(Alerta).filter(Alerta.id_paciente == datos["ficha"].id_paciente)
        if a.tipo.value == "omisiones_seguidas"
    ]
    assert len(omisiones) == 1


def test_la_alerta_se_cierra_sola_cuando_el_paciente_vuelve_a_cumplir(
    client, cab_medico, datos, db_session, sin_modelo
):
    _tomas(db_session, datos["ficha"], [O, O, O])
    client.get("/api/alertas", headers=cab_medico)
    assert "omisiones_seguidas" in _abiertas(db_session, datos["ficha"])

    # Cuatro tomas cumplidas seguidas: la racha se rompe.
    _tomas(db_session, datos["ficha"], [T, T, T, T], medicamento="Metformina 850 mg",
           desde_horas=3)
    client.get("/api/alertas", headers=cab_medico)

    assert "omisiones_seguidas" not in _abiertas(db_session, datos["ficha"])
    historial = client.get("/api/alertas?estado=resuelta", headers=cab_medico).json()
    assert historial["alertas"][0]["tipo"] == "omisiones_seguidas"
    assert "dejo de cumplirse" in historial["alertas"][0]["nota_cierre"]


def test_sin_microservicio_la_bandeja_sigue_avisando(
    client, cab_medico, datos, db_session, sin_modelo
):
    _tomas(db_session, datos["ficha"], [O, O, O])

    cuerpo = client.get("/api/alertas", headers=cab_medico).json()
    assert cuerpo["modelo_disponible"] is False
    assert cuerpo["abiertas"] == 1


# --- El medico cierra la alerta ---------------------------------------------


def test_atender_guarda_lo_que_hizo_el_medico(client, cab_medico, datos, db_session, sin_modelo):
    _tomas(db_session, datos["ficha"], [O, O, O])
    alerta = client.get("/api/alertas", headers=cab_medico).json()["alertas"][0]

    respuesta = client.post(f"/api/alertas/{alerta['id_alerta']}/atender",
                            json={"nota": "Se llamo al paciente y se reforzo la pauta."},
                            headers=cab_medico)

    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "atendida"
    assert cuerpo["nota_cierre"].startswith("Se llamo")
    assert cuerpo["fecha_cierre"] is not None


def test_descartar_retira_la_alerta_de_la_bandeja(client, cab_medico, datos, db_session, sin_modelo):
    _tomas(db_session, datos["ficha"], [O, O, O])
    alerta = client.get("/api/alertas", headers=cab_medico).json()["alertas"][0]

    client.post(f"/api/alertas/{alerta['id_alerta']}/descartar",
                json={"nota": "Paciente hospitalizado; no aplica."}, headers=cab_medico)

    assert client.get("/api/alertas", headers=cab_medico).json()["abiertas"] == 0


def test_atender_no_hace_que_el_aviso_vuelva_al_instante(
    client, cab_medico, datos, db_session, sin_modelo
):
    """Si volviera en la siguiente consulta, cerrar la alerta no serviria."""
    _tomas(db_session, datos["ficha"], [O, O, O])
    alerta = client.get("/api/alertas", headers=cab_medico).json()["alertas"][0]
    client.post(f"/api/alertas/{alerta['id_alerta']}/atender", json={"nota": "Llamada"},
                headers=cab_medico)

    assert client.get("/api/alertas", headers=cab_medico).json()["abiertas"] == 0


def test_una_alerta_atendida_vuelve_si_la_evidencia_empeora(
    client, cab_medico, datos, db_session, sin_modelo
):
    """Atender cierra el caso de hoy, no el del paciente que sigue empeorando."""
    _tomas(db_session, datos["ficha"], [O, O, O])
    alerta = client.get("/api/alertas", headers=cab_medico).json()["alertas"][0]
    client.post(f"/api/alertas/{alerta['id_alerta']}/atender", json={"nota": "Llamada"},
                headers=cab_medico)

    # Una cuarta omision seguida: la racha sube de 3 a 4.
    _tomas(db_session, datos["ficha"], [O], medicamento="Metformina 850 mg", desde_horas=1)
    cuerpo = client.get("/api/alertas", headers=cab_medico).json()

    assert cuerpo["abiertas"] == 1
    assert cuerpo["alertas"][0]["valor"] == 4
    assert cuerpo["alertas"][0]["id_alerta"] != alerta["id_alerta"]


# --- Acceso -------------------------------------------------------------------


def test_un_medico_ajeno_no_ve_ni_cierra_alertas_de_otro(
    client, cab_medico, cab_otro_medico, datos, db_session, sin_modelo
):
    _tomas(db_session, datos["ficha"], [O, O, O])
    alerta = client.get("/api/alertas", headers=cab_medico).json()["alertas"][0]

    ajeno = client.get("/api/alertas", headers=cab_otro_medico).json()
    assert ajeno["alertas"] == []
    cierre = client.post(f"/api/alertas/{alerta['id_alerta']}/atender", json={"nota": "x"},
                         headers=cab_otro_medico)
    assert cierre.status_code == 404


def test_el_paciente_no_accede_a_la_bandeja(client, cab_paciente):
    assert client.get("/api/alertas", headers=cab_paciente).status_code == 403


def test_sin_token_no_hay_bandeja(client):
    assert client.get("/api/alertas").status_code == 401
