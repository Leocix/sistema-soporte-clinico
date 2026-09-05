"""Esquemas de la prediccion de riesgo de incumplimiento (RF04, RF06)."""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class FactorInfluyente(BaseModel):
    """Variable que mas pesa en el modelo, con el valor de este paciente.

    La importancia es global del modelo, no la contribucion de la variable a
    esta prediccion concreta. La atribucion individual con SHAP corresponde a
    RF06 (Sprint 3), y el campo `alcance` de la respuesta lo hace explicito
    para que la interfaz no pueda presentarla como personal.
    """

    variable: str
    importancia: float
    valor_paciente: float | str | None = None


class FichaModelo(BaseModel):
    """Procedencia del modelo que produjo la prediccion."""

    algoritmo: str
    entrenado_el: date
    origen_datos: str
    # Falso cuando el modelo se entreno con el conjunto de demostracion. La
    # interfaz lo usa para avisar de que el resultado no es un hallazgo del
    # estudio.
    datos_reales: bool
    aucroc_validacion_cruzada: float | None = None


class PrediccionRiesgo(BaseModel):
    """Salida del microservicio de inferencia."""

    id_paciente: str
    codigo_anonimizado: str

    probabilidad: float = Field(ge=0, le=1, description="Probabilidad de incumplimiento")
    nivel: str = Field(description="alto, medio o bajo")

    factores: list[FactorInfluyente]
    alcance_factores: str = (
        "Importancia global del modelo, no contribucion individual de este paciente."
    )

    # Variables que la ficha no tenia y que el pipeline imputo; permiten al
    # medico modular su confianza en el resultado.
    variables_imputadas: list[str]

    modelo: FichaModelo

    aviso: str = (
        "Estimacion de apoyo a la decision clinica. No constituye un diagnostico: "
        "la decision corresponde al medico tratante."
    )


class EstadoModelo(BaseModel):
    """Disponibilidad del componente inteligente."""

    disponible: bool
    modelo: FichaModelo | None = None
    mensaje: str
