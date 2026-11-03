"""Esquemas de la prediccion de riesgo de incumplimiento (RF04, RF06)."""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class FactorInfluyente(BaseModel):
    """Variable que mas pesa en el modelo, con el valor de este paciente.

    La importancia es global del modelo. La contribucion de cada variable a la
    prediccion concreta de este paciente va en `contribuciones` (SHAP).
    """

    variable: str
    importancia: float
    valor_paciente: float | str | None = None


class ContribucionShap(BaseModel):
    """Aporte de una variable a la prediccion de ESTE paciente (RF06).

    Positivo: empuja la probabilidad hacia el incumplimiento; negativo: la
    aleja. El valor base mas la suma de las contribuciones da la probabilidad.
    """

    variable: str
    valor_paciente: float | str | None = None
    contribucion: float


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

    # Explicacion individual con SHAP (RF06), de mayor a menor peso.
    valor_base: float | None = Field(
        default=None, description="Probabilidad del paciente de referencia"
    )
    contribuciones: list[ContribucionShap] = []

    # Importancia global del modelo, como contexto de la explicacion individual.
    factores: list[FactorInfluyente]
    alcance_factores: str = (
        "Importancia global del modelo: cuanto depende el modelo de cada variable "
        "en general, no en este paciente."
    )

    # Variables que la ficha no tenia y que el pipeline imputo; permiten al
    # medico modular su confianza en el resultado.
    variables_imputadas: list[str]

    modelo: FichaModelo

    aviso: str = (
        "Estimación de apoyo a la decisión clínica. No constituye un diagnóstico: "
        "la decisión corresponde al médico tratante."
    )


class EstadoModelo(BaseModel):
    """Disponibilidad del componente inteligente."""

    disponible: bool
    modelo: FichaModelo | None = None
    mensaje: str
