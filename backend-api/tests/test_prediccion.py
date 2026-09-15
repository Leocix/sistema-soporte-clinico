"""El API central y su microservicio de inferencia (RF04, RF06).

Estas pruebas sustituyen el microservicio por uno simulado a nivel HTTP: lo que
se verifica aqui es el lado del API —que envia la ficha anonimizada con la
clave, que traduce la respuesta, que protege el acceso y que sobrevive a un
microservicio caido—. El modelo y SHAP se prueban en `ml-service/tests`, y la
integracion real de ambos en `test_integracion_ml.py`.
"""
from __future__ import annotations

import json

import httpx
import pytest

from app.services import ml_inference

MODELO = {
    "algoritmo": "SVM (RBF)", "entrenado_el": "2026-09-15",
    "origen_datos": "conjunto de demostracion simulado", "datos_reales": False,
    "aucroc_validacion_cruzada": 0.8556,
}


def _respuesta_prediccion(ficha: dict) -> dict:
    return {
        "codigo_anonimizado": ficha["codigo_anonimizado"],
        "probabilidad": 0.72, "nivel": "alto",
        "variables_imputadas": ["convivencia", "nivel_educativo"],
        "valor_base": 0.34,
        "contribuciones": [
            {"variable": "tasa_inasistencia", "valor_paciente": 0.5, "contribucion": 0.25},
            {"variable": "numero_farmacos", "valor_paciente": 7, "contribucion": 0.18},
            {"variable": "edad", "valor_paciente": 68, "contribucion": -0.05},
        ],
        "factores_globales": [{"variable": "tasa_inasistencia", "importancia": 0.09}],
        "modelo": MODELO,
    }


@pytest.fixture()
def microservicio(monkeypatch):
    """Microservicio simulado. Registra lo que recibe para inspeccionarlo."""
    recibido: list[httpx.Request] = []

    def atender(request: httpx.Request) -> httpx.Response:
        recibido.append(request)
        if request.headers.get("X-Clave-Servicio") != "clave-api":
            return httpx.Response(401)
        if request.url.path == "/modelo":
            return httpx.Response(200, json=MODELO)
        cuerpo = json.loads(request.content)
        if request.url.path == "/predicciones":
            return httpx.Response(200, json=_respuesta_prediccion(cuerpo))
        if request.url.path == "/predicciones/lote":
            return httpx.Response(200, json={"predicciones": [
                {**_respuesta_prediccion(f), "contribuciones": [], "valor_base": None}
                for f in cuerpo["fichas"]
            ]})
        return httpx.Response(404)

    monkeypatch.setattr(ml_inference.settings, "ml_service_clave", "clave-api")
    monkeypatch.setattr(ml_inference, "_cliente", lambda: httpx.Client(
        base_url="http://ml", headers={"X-Clave-Servicio": ml_inference.settings.ml_service_clave},
        transport=httpx.MockTransport(atender),
    ))
    return recibido


@pytest.fixture()
def microservicio_caido(monkeypatch):
    def fallar(request):
        raise httpx.ConnectError("sin conexion", request=request)

    monkeypatch.setattr(ml_inference, "_cliente", lambda: httpx.Client(
        base_url="http://ml", transport=httpx.MockTransport(fallar)
    ))


def _url(datos) -> str:
    return f"/api/prediccion/pacientes/{datos['ficha'].id_paciente}"


# --- Integracion por REST (RF04) --------------------------------------------


def test_el_medico_obtiene_la_prediccion_y_su_explicacion(client, cab_medico, datos, microservicio):
    respuesta = client.get(_url(datos), headers=cab_medico)

    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["probabilidad"] == 0.72 and cuerpo["nivel"] == "alto"
    assert cuerpo["valor_base"] == 0.34
    assert cuerpo["contribuciones"][0]["variable"] == "tasa_inasistencia"
    # El factor global lleva el valor del propio paciente.
    assert cuerpo["factores"][0]["valor_paciente"] == 0.5


def test_al_microservicio_solo_viaja_la_ficha_anonimizada(client, cab_medico, datos, microservicio):
    """Nombres, documento, correo y telefono se quedan en el API (RNF01)."""
    client.get(_url(datos), headers=cab_medico)

    enviado = json.loads(microservicio[-1].content)
    assert enviado["codigo_anonimizado"] == "P-001"
    for dato_personal in ("nombres", "apellidos", "correo", "telefono", "documento_identidad"):
        assert dato_personal not in enviado
    assert enviado["comorbilidades"] == 2
    assert microservicio[-1].headers["X-Clave-Servicio"] == "clave-api"


def test_el_estado_informa_el_modelo_del_microservicio(client, cab_medico, microservicio):
    cuerpo = client.get("/api/prediccion/estado", headers=cab_medico).json()
    assert cuerpo["disponible"] is True
    assert cuerpo["modelo"]["algoritmo"] == "SVM (RBF)"


def test_la_procedencia_del_modelo_viaja_en_cada_prediccion(client, cab_medico, datos, microservicio):
    cuerpo = client.get(_url(datos), headers=cab_medico).json()
    assert cuerpo["modelo"]["datos_reales"] is False
    assert "no constituye un diagnostico" in cuerpo["aviso"].lower()


def test_el_reporte_pide_todas_las_predicciones_en_una_sola_llamada(
    client, cab_medico, datos, microservicio
):
    reporte = client.get("/api/reportes/general", headers=cab_medico).json()

    llamadas = [r for r in microservicio if r.url.path.startswith("/predicciones")]
    assert [r.url.path for r in llamadas] == ["/predicciones/lote"]
    assert reporte["pacientes"][0]["riesgo_predicho"] == "alto"


# --- El sistema sobrevive al microservicio (RNF04) --------------------------


def test_sin_microservicio_la_prediccion_responde_503(client, cab_medico, datos, microservicio_caido):
    respuesta = client.get(_url(datos), headers=cab_medico)
    assert respuesta.status_code == 503
    assert respuesta.json()["codigo"] == "MODELO_NO_DISPONIBLE"

    # La consulta clinica sigue funcionando.
    assert client.get("/api/pacientes", headers=cab_medico).status_code == 200
    assert client.get("/api/prediccion/estado", headers=cab_medico).json()["disponible"] is False
    reporte = client.get("/api/reportes/general", headers=cab_medico).json()
    assert reporte["riesgo_predicho"] is None


def test_una_clave_equivocada_se_trata_como_microservicio_no_disponible(
    client, cab_medico, datos, microservicio, monkeypatch
):
    monkeypatch.setattr(ml_inference.settings, "ml_service_clave", "otra")
    assert client.get(_url(datos), headers=cab_medico).status_code == 503


# --- Acceso -------------------------------------------------------------------


def test_un_medico_ajeno_no_predice_sobre_pacientes_de_otro(client, cab_otro_medico, datos, microservicio):
    assert client.get(_url(datos), headers=cab_otro_medico).status_code == 403
    # Y el microservicio ni siquiera llega a consultarse.
    assert not microservicio


def test_el_paciente_puede_consultar_su_propio_riesgo(client, cab_paciente, datos, microservicio):
    assert client.get(_url(datos), headers=cab_paciente).status_code == 200


def test_el_estado_del_modelo_es_privativo_del_medico(client, cab_paciente):
    assert client.get("/api/prediccion/estado", headers=cab_paciente).status_code == 403
