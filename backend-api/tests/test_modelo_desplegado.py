"""El artefacto real del modelo se carga y predice con las dependencias del API.

Las pruebas de `test_prediccion.py` entrenan un modelo sintetico al vuelo: son
rapidas y aislan la logica del servicio, pero nunca abren el `.pkl` que se
despliega. Por ese hueco paso inadvertido un fallo que dejaba la prediccion
inservible en produccion. El artefacto real es un `imblearn.pipeline.Pipeline`,
y `imbalanced-learn` no figuraba en `requirements.txt`: el API arrancaba, el
resto del sistema funcionaba y la ficha del paciente mostraba todo menos el
riesgo predicho, porque el cargador convertia el `ModuleNotFoundError` en un
503 generico.

Estas pruebas abren el archivo que de verdad se sirve.
"""
from __future__ import annotations

import re
from importlib.metadata import version
from pathlib import Path

import pytest

from app.db.models import Diagnostico, Paciente, Sexo
from app.services import ml_inference

RAIZ_REPO = Path(__file__).resolve().parents[2]
ARTEFACTO = RAIZ_REPO / "ml-pipeline" / "models" / "risk_model_v1.pkl"
REQUISITOS = RAIZ_REPO / "backend-api" / "requirements.txt"

pytestmark = pytest.mark.skipif(
    not ARTEFACTO.exists(), reason="el artefacto del modelo no esta en el repositorio"
)


@pytest.fixture(autouse=True)
def _modelo_real(monkeypatch):
    monkeypatch.setattr(ml_inference.settings, "model_path", str(ARTEFACTO))
    ml_inference._cargar.cache_clear()
    yield
    ml_inference._cargar.cache_clear()


def _paciente(**campos) -> Paciente:
    base = dict(
        codigo_anonimizado="P-900", nombres="Prueba", apellidos="Artefacto",
        edad=68, sexo=Sexo.MASCULINO, diagnostico=Diagnostico.AMBAS,
        lista_comorbilidades=["dislipidemia", "obesidad"], comorbilidades=2,
        numero_farmacos=7, tomas_dia=5,
        controles_programados_6m=6, controles_perdidos_6m=3,
        tiempo_enfermedad_anios=12.0,
    )
    base.update(campos)
    return Paciente(**base)


def test_el_artefacto_desplegado_se_deserializa():
    """Sin la dependencia correcta esto falla con ModuleNotFoundError."""
    import joblib

    # Se llama a joblib directamente, sin pasar por el cargador del servicio:
    # el cargador convierte cualquier excepcion en un 503 generico, y aqui lo
    # que interesa es ver la causa real si algo falta.
    pipeline = joblib.load(ARTEFACTO)
    assert hasattr(pipeline, "predict_proba")


def test_el_servicio_informa_el_modelo_disponible():
    assert ml_inference.modelo_disponible() is True


def test_predice_sobre_una_ficha_completa():
    prediccion = ml_inference.predecir(_paciente())

    assert 0.0 <= prediccion.probabilidad <= 1.0
    assert prediccion.nivel in {"bajo", "medio", "alto"}


def test_predice_con_los_opcionales_vacios():
    """El caso corriente: fichas con el contexto social sin completar.

    Es el que fallaba antes de convertir `None` en `NaN` (incidencia I-09), y
    solo el artefacto real, con sus imputadores, lo ejercita de verdad.
    """
    prediccion = ml_inference.predecir(_paciente(
        nivel_educativo=None, convivencia=None, apoyo_familiar=None,
        tiempo_enfermedad_anios=None,
    ))

    assert 0.0 <= prediccion.probabilidad <= 1.0
    assert "convivencia" in prediccion.variables_imputadas


def test_las_versiones_instaladas_son_las_declaradas():
    """Un artefacto serializado solo es fiable con las versiones que lo crearon.

    Si alguien actualiza scikit-learn en el entorno sin reentrenar, o reentrena
    sin actualizar `requirements.txt`, esta prueba lo detecta antes del
    despliegue.
    """
    texto = REQUISITOS.read_text(encoding="utf-8")
    for paquete in ("scikit-learn", "imbalanced-learn", "numpy", "pandas", "joblib"):
        declarada = re.search(rf"^{re.escape(paquete)}==([\w.]+)", texto, re.M)
        assert declarada, f"{paquete} no esta fijado en requirements.txt"
        assert version(paquete) == declarada.group(1), (
            f"{paquete}: instalado {version(paquete)}, declarado {declarada.group(1)}"
        )
