"""Contrato REST del microservicio de inferencia."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class FichaEntrada(BaseModel):
    """Variables del Anexo n.o 04 de un paciente, sin datos identificatorios.

    El API central envia solo el codigo anonimizado: el microservicio nunca
    recibe nombres, documentos ni contactos (RNF01).
    """

    model_config = ConfigDict(extra="forbid")

    codigo_anonimizado: str = Field(max_length=12)
    edad: int = Field(ge=18, le=120)
    sexo: Literal["M", "F"]
    diagnostico: Literal["hta", "dm2", "ambas"]
    nivel_educativo: Literal["sin_estudios", "primaria", "secundaria", "superior"] | None = None
    convivencia: Literal["solo", "acompanado"] | None = None
    apoyo_familiar: bool | None = None
    tiempo_enfermedad_anios: float | None = Field(default=None, ge=0, le=80)
    comorbilidades: int = Field(ge=0, le=15)
    numero_farmacos: int = Field(ge=5, le=30)
    tomas_dia: int = Field(ge=1, le=20)
    controles_programados_6m: int = Field(ge=0, le=30)
    controles_perdidos_6m: int = Field(ge=0, le=30)


class Contribucion(BaseModel):
    """Aporte de una variable a la prediccion de ESTE paciente (SHAP)."""

    variable: str
    valor_paciente: float | str | None
    # Positivo: empuja la probabilidad hacia el incumplimiento; negativo: la aleja.
    contribucion: float


class FactorGlobal(BaseModel):
    variable: str
    importancia: float


class FichaModelo(BaseModel):
    algoritmo: str
    entrenado_el: str
    origen_datos: str
    datos_reales: bool
    aucroc_validacion_cruzada: float | None = None


class Prediccion(BaseModel):
    codigo_anonimizado: str
    probabilidad: float = Field(ge=0, le=1)
    nivel: Literal["alto", "medio", "bajo"]
    variables_imputadas: list[str]
    # Probabilidad que el modelo asigna al paciente de referencia; la suma de
    # las contribuciones lleva de este valor a `probabilidad`.
    valor_base: float | None = None
    contribuciones: list[Contribucion] = []
    factores_globales: list[FactorGlobal]
    modelo: FichaModelo


class PeticionLote(BaseModel):
    fichas: list[FichaEntrada] = Field(max_length=500)


class RespuestaLote(BaseModel):
    predicciones: list[Prediccion]
