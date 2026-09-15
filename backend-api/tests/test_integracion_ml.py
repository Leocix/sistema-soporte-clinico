"""Integracion real: API central -> microservicio de inferencia -> modelo desplegado.

A diferencia de `test_prediccion.py`, aqui no hay simulacion: el API llama al
microservicio de `ml-service` (montado en memoria) y este carga el modelo real
de `ml-pipeline/models` y calcula SHAP. Requiere las dependencias del
microservicio; si no estan instaladas, se omite.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("shap")

RAIZ_REPO = Path(__file__).resolve().parents[2]


@pytest.fixture()
def microservicio_real(monkeypatch):
    from fastapi.testclient import TestClient

    from app.services import ml_inference

    # Los dos servicios tienen un paquete llamado `app`: se carga el del
    # microservicio con otro nombre para no pisar el del API.
    import importlib.util

    raiz = RAIZ_REPO / "ml-service"
    nombre = "ml_service_app"
    if nombre not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            nombre, raiz / "app" / "__init__.py", submodule_search_locations=[str(raiz / "app")]
        )
        paquete = importlib.util.module_from_spec(spec)
        sys.modules[nombre] = paquete
        spec.loader.exec_module(paquete)
    main = importlib.import_module(f"{nombre}.main")
    config = importlib.import_module(f"{nombre}.config")

    monkeypatch.setattr(config.settings, "clave_servicio", "clave-integracion")
    monkeypatch.setattr(config.settings, "model_path",
                        str(RAIZ_REPO / "ml-pipeline" / "models" / "risk_model_v1.pkl"))
    monkeypatch.setattr(ml_inference.settings, "ml_service_clave", "clave-integracion")
    monkeypatch.setattr(ml_inference, "_cliente", lambda: TestClient(
        main.app, headers={"X-Clave-Servicio": "clave-integracion"}
    ))


def test_prediccion_con_shap_de_extremo_a_extremo(client, cab_medico, datos, microservicio_real):
    cuerpo = client.get(
        f"/api/prediccion/pacientes/{datos['ficha'].id_paciente}", headers=cab_medico
    ).json()

    assert 0 <= cuerpo["probabilidad"] <= 1
    assert cuerpo["modelo"]["algoritmo"]
    suma = cuerpo["valor_base"] + sum(c["contribucion"] for c in cuerpo["contribuciones"])
    assert suma == pytest.approx(cuerpo["probabilidad"], abs=0.005)
    # Ficha de prueba sin contexto social: el microservicio lo informa.
    assert "convivencia" in cuerpo["variables_imputadas"]


def test_reporte_general_con_el_modelo_real(client, cab_medico, datos, microservicio_real):
    reporte = client.get("/api/reportes/general", headers=cab_medico).json()
    assert reporte["pacientes"][0]["riesgo_predicho"] in {"alto", "medio", "bajo"}
