"""Verificación del componente inteligente (RF04).

Cubren las tres cosas que un modelo integrado en un sistema clínico tiene que
garantizar: que la salida sea utilizable, que el sistema siga funcionando
cuando el modelo no está, y que la procedencia del resultado sea imposible de
ocultar.
"""
from __future__ import annotations

import json

import pytest

from app.services import ml_inference


@pytest.fixture(autouse=True)
def _sin_cache():
    """El servicio cachea el modelo por proceso; cada prueba parte limpia."""
    ml_inference._cargar.cache_clear()
    yield
    ml_inference._cargar.cache_clear()


@pytest.fixture()
def modelo_entrenado(tmp_path, monkeypatch):
    """Entrena un pipeline mínimo y lo deja donde el servicio lo busca.

    Se entrena aquí en lugar de depender del artefacto del repositorio: la
    prueba debe verificar la integración, no la existencia de un archivo.
    """
    import joblib
    import numpy as np
    import pandas as pd
    from sklearn.linear_model import LogisticRegression

    from app.services.ml_inference import CATEGORICAS, NUMERICAS

    sys_path_preprocess = __import__("pathlib").Path(
        ml_inference.__file__
    ).resolve().parents[3] / "ml-pipeline" / "src"
    import sys

    sys.path.insert(0, str(sys_path_preprocess))
    from preprocess import construir_preprocesador  # noqa: E402
    from imblearn.pipeline import Pipeline as PipelineImb  # noqa: E402

    rng = np.random.default_rng(7)
    n = 120
    datos = pd.DataFrame({
        "edad": rng.integers(40, 90, n),
        "tiempo_enfermedad_anios": rng.uniform(1, 30, n),
        "comorbilidades": rng.integers(0, 5, n),
        "numero_farmacos": rng.integers(5, 12, n),
        "tomas_dia": rng.integers(2, 8, n),
        "controles_programados_6m": rng.integers(2, 8, n),
        "controles_perdidos_6m": rng.integers(0, 3, n),
        "carga_terapeutica": rng.integers(10, 70, n),
        "tasa_inasistencia": rng.uniform(0, 1, n),
        "cronicidad_relativa": rng.uniform(0, 5, n),
        "nivel_socioeconomico": rng.choice(["bajo", "medio", "alto"], n),
        "sexo": rng.choice(["M", "F"], n),
        "aseguramiento": rng.choice(["sis", "essalud", "ninguno"], n),
        "zona_residencia": rng.choice(["urbana", "rural"], n),
        "diagnostico": rng.choice(["hta", "dm2", "ambas"], n),
    })
    etiqueta = (datos["tasa_inasistencia"] > 0.5).astype(int)

    pipeline = PipelineImb(steps=[
        ("prep", construir_preprocesador(NUMERICAS)),
        ("clf", LogisticRegression(max_iter=500)),
    ])
    pipeline.fit(datos[[*NUMERICAS, *CATEGORICAS]], etiqueta)

    ruta = tmp_path / "risk_model_v1.pkl"
    joblib.dump(pipeline, ruta)
    ruta.with_suffix(".json").write_text(json.dumps({
        "algoritmo": "Regresion Logistica",
        "entrenado_el": "2026-09-05",
        "origen_datos": "conjunto de demostracion simulado",
        "datos_reales": False,
        "aucroc_validacion_cruzada": 0.91,
        "factores_influyentes": [
            {"variable": "tasa_inasistencia", "importancia": 0.21},
            {"variable": "carga_terapeutica", "importancia": 0.08},
        ],
    }, ensure_ascii=False), encoding="utf-8")

    monkeypatch.setattr(ml_inference.settings, "model_path", str(ruta))
    return ruta


# --- El modelo está integrado y operativo (ítem 18) -------------------------


def test_el_medico_obtiene_la_prediccion_de_su_paciente(
    client, cab_medico, datos, modelo_entrenado
):
    """Entrada (ficha) -> procesamiento (modelo) -> salida (probabilidad)."""
    respuesta = client.get(
        f"/api/prediccion/pacientes/{datos['ficha'].id_paciente}", headers=cab_medico
    )

    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert 0.0 <= cuerpo["probabilidad"] <= 1.0
    assert cuerpo["nivel"] in ("alto", "medio", "bajo")
    assert cuerpo["codigo_anonimizado"] == "P-001"


def test_el_estado_informa_que_el_modelo_esta_cargado(
    client, cab_medico, modelo_entrenado
):
    respuesta = client.get("/api/prediccion/estado", headers=cab_medico)

    assert respuesta.status_code == 200
    assert respuesta.json()["disponible"] is True
    assert respuesta.json()["modelo"]["algoritmo"] == "Regresion Logistica"


# --- La salida es pertinente y validada (ítem 19) ---------------------------


def test_la_respuesta_incluye_los_factores_y_su_alcance(
    client, cab_medico, datos, modelo_entrenado
):
    """Una probabilidad sin explicación no es utilizable clínicamente."""
    cuerpo = client.get(
        f"/api/prediccion/pacientes/{datos['ficha'].id_paciente}", headers=cab_medico
    ).json()

    assert len(cuerpo["factores"]) >= 1
    assert cuerpo["factores"][0]["variable"] == "tasa_inasistencia"
    # El valor del propio paciente acompaña al factor.
    assert cuerpo["factores"][0]["valor_paciente"] is not None
    # Y queda explícito que la importancia es global, no individual.
    assert "global" in cuerpo["alcance_factores"].lower()


def test_el_nivel_de_riesgo_respeta_el_umbral_configurado(monkeypatch):
    monkeypatch.setattr(ml_inference.settings, "umbral_riesgo_alto", 0.70)

    assert ml_inference._nivel(0.95) == "alto"
    assert ml_inference._nivel(0.70) == "alto"
    assert ml_inference._nivel(0.55) == "medio"
    assert ml_inference._nivel(0.10) == "bajo"


def test_las_variables_derivadas_se_calculan_como_en_el_pipeline(datos):
    """Una fórmula distinta aquí produciría predicciones sobre variables que el
    modelo nunca vio durante el entrenamiento."""
    ficha = datos["ficha"]
    derivadas = ml_inference._derivar(ficha)

    assert derivadas["carga_terapeutica"] == ficha.numero_farmacos * ficha.tomas_dia
    assert derivadas["tasa_inasistencia"] == pytest.approx(
        ficha.controles_perdidos_6m / ficha.controles_programados_6m
    )


def test_sin_controles_programados_no_se_divide_entre_cero(datos, db_session):
    ficha = datos["ficha"]
    ficha.controles_programados_6m = 0
    ficha.controles_perdidos_6m = 0
    db_session.commit()

    derivadas = ml_inference._derivar(ficha)
    assert derivadas["tasa_inasistencia"] is None


def test_se_informan_las_variables_que_hubo_que_imputar(datos, modelo_entrenado):
    """El médico debe saber sobre cuánta información ausente se predijo."""
    ficha = datos["ficha"]  # sin nivel socioeconómico ni aseguramiento
    resultado = ml_inference.predecir(ficha)

    assert "nivel_socioeconomico" in resultado.variables_imputadas
    assert "aseguramiento" in resultado.variables_imputadas


# --- Riesgos del componente gestionados (ítem 20) ---------------------------


def test_la_procedencia_del_modelo_viaja_en_cada_prediccion(
    client, cab_medico, datos, modelo_entrenado
):
    """Un resultado obtenido con datos simulados no puede presentarse como real."""
    cuerpo = client.get(
        f"/api/prediccion/pacientes/{datos['ficha'].id_paciente}", headers=cab_medico
    ).json()

    assert cuerpo["modelo"]["datos_reales"] is False
    assert "simulado" in cuerpo["modelo"]["origen_datos"]
    assert "no constituye un diagnostico" in cuerpo["aviso"].lower()


def test_sin_modelo_el_resto_del_sistema_sigue_operativo(
    client, cab_medico, datos, monkeypatch
):
    """Un fallo del componente inteligente no puede tumbar la consulta clínica."""
    monkeypatch.setattr(ml_inference.settings, "model_path", "no/existe/modelo.pkl")

    prediccion = client.get(
        f"/api/prediccion/pacientes/{datos['ficha'].id_paciente}", headers=cab_medico
    )
    assert prediccion.status_code == 503
    assert prediccion.json()["codigo"] == "MODELO_NO_DISPONIBLE"

    # La auditoría de adherencia sigue respondiendo con normalidad.
    assert client.get("/api/pacientes", headers=cab_medico).status_code == 200
    assert client.get("/api/prediccion/estado", headers=cab_medico).json()["disponible"] is False


def test_un_medico_ajeno_no_predice_sobre_pacientes_de_otro(
    client, cab_otro_medico, datos, modelo_entrenado
):
    """La predicción es un dato clínico más y no puede quedar menos protegida."""
    respuesta = client.get(
        f"/api/prediccion/pacientes/{datos['ficha'].id_paciente}", headers=cab_otro_medico
    )
    assert respuesta.status_code == 403


def test_el_paciente_puede_consultar_su_propio_riesgo(
    client, cab_paciente, datos, modelo_entrenado
):
    respuesta = client.get(
        f"/api/prediccion/pacientes/{datos['ficha'].id_paciente}", headers=cab_paciente
    )
    assert respuesta.status_code == 200


def test_el_estado_del_modelo_es_privativo_del_medico(client, cab_paciente):
    assert client.get("/api/prediccion/estado", headers=cab_paciente).status_code == 403
