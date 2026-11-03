"""Microservicio de inferencia: prediccion, explicacion SHAP y contrato REST.

Se prueba contra el modelo realmente desplegado
(`ml-pipeline/models/risk_model_v1.pkl`), no contra uno sintetico: fue un
modelo de prueba el que dejo pasar la incidencia I-14.
"""
from __future__ import annotations

import re
from importlib.metadata import version
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import modelo
from app.config import settings
from app.esquemas import FichaEntrada
from app.main import app

RAIZ = Path(__file__).resolve().parents[1]
CLAVE = "clave-de-prueba"

FICHA = {
    "codigo_anonimizado": "P-900", "edad": 68, "sexo": "M", "diagnostico": "ambas",
    "nivel_educativo": "secundaria", "convivencia": "solo", "apoyo_familiar": False,
    "tiempo_enfermedad_anios": 12.0, "comorbilidades": 2, "numero_farmacos": 7,
    "tomas_dia": 5, "controles_programados_6m": 6, "controles_perdidos_6m": 3,
}


@pytest.fixture(autouse=True)
def _entorno(monkeypatch):
    monkeypatch.setattr(settings, "clave_servicio", CLAVE)
    modelo.cargar.cache_clear()
    yield
    modelo.cargar.cache_clear()


@pytest.fixture()
def cliente():
    return TestClient(app, headers={"X-Clave-Servicio": CLAVE})


# --- Contrato y seguridad --------------------------------------------------


def test_sin_clave_no_hay_prediccion():
    anonimo = TestClient(app)
    assert anonimo.post("/predicciones", json=FICHA).status_code == 401
    assert anonimo.get("/modelo").status_code == 401
    # La sonda de salud si es publica: la necesita la plataforma.
    assert anonimo.get("/health").status_code == 200


def test_no_acepta_datos_identificatorios(cliente):
    """El microservicio no debe recibir nombres ni documentos (RNF01)."""
    respuesta = cliente.post("/predicciones", json={**FICHA, "nombres": "Jose"})
    assert respuesta.status_code == 422


def test_sin_modelo_responde_503(cliente, monkeypatch):
    monkeypatch.setattr(settings, "model_path", "no/existe.pkl")
    respuesta = cliente.post("/predicciones", json=FICHA)
    assert respuesta.status_code == 503
    assert respuesta.json()["codigo"] == "MODELO_NO_DISPONIBLE"


# --- Prediccion (RF04) -----------------------------------------------------


def test_predice_con_la_ficha_completa(cliente):
    cuerpo = cliente.post("/predicciones", json=FICHA).json()

    assert 0 <= cuerpo["probabilidad"] <= 1
    assert cuerpo["nivel"] in {"alto", "medio", "bajo"}
    assert cuerpo["variables_imputadas"] == []
    assert cuerpo["modelo"]["datos_reales"] is False


def test_predice_con_el_contexto_social_vacio(cliente):
    ficha = {**FICHA, "nivel_educativo": None, "convivencia": None, "apoyo_familiar": None,
             "tiempo_enfermedad_anios": None}
    cuerpo = cliente.post("/predicciones", json=ficha).json()

    assert 0 <= cuerpo["probabilidad"] <= 1
    assert {"nivel_educativo", "convivencia", "apoyo_familiar"} <= set(cuerpo["variables_imputadas"])


def test_el_lote_coincide_con_la_prediccion_individual(cliente):
    individual = cliente.post("/predicciones", json=FICHA).json()
    lote = cliente.post("/predicciones/lote", json={"fichas": [FICHA, {**FICHA, "codigo_anonimizado": "P-901", "controles_perdidos_6m": 0}]}).json()

    assert len(lote["predicciones"]) == 2
    assert lote["predicciones"][0]["probabilidad"] == individual["probabilidad"]
    # El lote no calcula SHAP: es para reportes, donde importa la rapidez.
    assert lote["predicciones"][0]["contribuciones"] == []


def test_bandas_de_riesgo():
    assert modelo.nivel(0.70) == "alto"
    assert modelo.nivel(0.69) == "medio"
    assert modelo.nivel(0.40) == "medio"
    assert modelo.nivel(0.39) == "bajo"


def test_sin_controles_programados_no_se_divide_entre_cero():
    ficha = FichaEntrada(**{**FICHA, "controles_programados_6m": 0, "controles_perdidos_6m": 0})
    assert modelo.derivar(ficha)["tasa_inasistencia"] is None


# --- Explicacion individual con SHAP (RF06) --------------------------------


def test_las_contribuciones_suman_la_diferencia_con_la_referencia(cliente):
    """Propiedad que define a SHAP: base + suma de contribuciones = prediccion."""
    cuerpo = cliente.post("/predicciones", json=FICHA).json()

    suma = cuerpo["valor_base"] + sum(c["contribucion"] for c in cuerpo["contribuciones"])
    assert suma == pytest.approx(cuerpo["probabilidad"], abs=0.005)


def test_hay_una_contribucion_por_variable_del_anexo(cliente):
    cuerpo = cliente.post("/predicciones", json=FICHA).json()
    variables = {c["variable"] for c in cuerpo["contribuciones"]}

    # Las columnas one-hot se agrupan en su variable original.
    assert "convivencia" in variables and "convivencia_solo" not in variables
    assert "diagnostico" in variables
    assert len(variables) == len(modelo.cargar().columnas_entrada)
    # Ordenadas de mayor a menor peso.
    pesos = [abs(c["contribucion"]) for c in cuerpo["contribuciones"]]
    assert pesos == sorted(pesos, reverse=True)


def test_la_explicacion_es_reproducible(cliente):
    a = cliente.post("/predicciones", json=FICHA).json()["contribuciones"]
    b = cliente.post("/predicciones", json=FICHA).json()["contribuciones"]
    assert a == b


def test_la_contribucion_sigue_al_dato(cliente):
    """Faltar a mas controles debe empujar el riesgo hacia arriba en este modelo,
    cuya variable mas influyente es la inasistencia."""
    faltador = cliente.post("/predicciones", json={**FICHA, "controles_perdidos_6m": 5}).json()
    cumplidor = cliente.post("/predicciones", json={**FICHA, "controles_perdidos_6m": 0}).json()

    def aporte(cuerpo):
        return next(c["contribucion"] for c in cuerpo["contribuciones"] if c["variable"] == "tasa_inasistencia")

    assert aporte(faltador) > aporte(cumplidor)


# --- Versiones del artefacto ------------------------------------------------


def test_las_versiones_instaladas_son_las_declaradas():
    texto = (RAIZ / "requirements.txt").read_text(encoding="utf-8")
    for paquete in ("scikit-learn", "imbalanced-learn", "numpy", "pandas", "joblib"):
        declarada = re.search(rf"^{re.escape(paquete)}==([\w.]+)", texto, re.M)
        assert declarada, f"{paquete} no esta fijado"
        assert version(paquete) == declarada.group(1), f"{paquete}: {version(paquete)}"
