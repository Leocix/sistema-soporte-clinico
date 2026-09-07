"""Esquemas Pydantic del registro de adherencia (RF03).

El contrato esta pensado para una app movil que puede quedar sin conectividad:
los eventos se acumulan en el dispositivo y se envian despues, individualmente
o en lote. Por eso el identificador logico del evento no es un correlativo del
servidor sino la terna (paciente, medicamento, horario programado), que hace
la sincronizacion idempotente.
"""
from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ..db.models import EstadoToma, OrigenRegistro

ESTADOS_CUMPLIDOS = (EstadoToma.TOMADA, EstadoToma.TOMADA_TARDE)


def _asegurar_utc(valor: datetime | None) -> datetime | None:
    """Normaliza a UTC: la app movil puede enviar horas sin zona horaria."""
    if valor is None:
        return None
    if valor.tzinfo is None:
        return valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc)


class RegistroTomaCreate(BaseModel):
    """Evento de toma reportado por el paciente (HU03)."""

    model_config = ConfigDict(extra="forbid")

    # Obligatorio cuando quien registra es el medico; para el paciente se
    # resuelve desde su propia ficha y no puede apuntar a un tercero.
    id_paciente: str | None = None

    medicamento: str = Field(min_length=2, max_length=150)
    dosis: str | None = Field(default=None, max_length=60)

    fecha_hora_programada: datetime
    fecha_hora_registro: datetime | None = None

    estado: EstadoToma
    motivo_omision: str | None = Field(default=None, max_length=500)
    origen: OrigenRegistro = OrigenRegistro.APP_MOVIL

    @field_validator("medicamento")
    @classmethod
    def _normalizar_medicamento(cls, v: str) -> str:
        # Evita que "Losartan 50 mg" y "losartan 50 mg " se traten como
        # medicamentos distintos y rompan la idempotencia del evento.
        return " ".join(v.split())

    @field_validator("fecha_hora_programada", "fecha_hora_registro")
    @classmethod
    def _normalizar_zona(cls, v: datetime | None) -> datetime | None:
        return _asegurar_utc(v)

    @model_validator(mode="after")
    def _coherencia_clinica(self) -> RegistroTomaCreate:
        if self.estado in ESTADOS_CUMPLIDOS and self.fecha_hora_registro is None:
            raise ValueError(
                "Una toma marcada como cumplida requiere la hora real de la toma."
            )
        if self.estado is EstadoToma.OMITIDA and self.fecha_hora_registro is not None:
            raise ValueError(
                "Una toma omitida no puede llevar hora de toma; use 'tomada_tarde'."
            )
        return self


class RegistroTomaOut(BaseModel):
    """Evento tal como queda persistido, con sus indicadores derivados."""

    model_config = ConfigDict(from_attributes=True)

    id_registro: str
    id_paciente: str
    medicamento: str
    dosis: str | None
    fecha_hora_programada: datetime
    fecha_hora_registro: datetime | None
    estado: EstadoToma
    origen: OrigenRegistro
    motivo_omision: str | None
    fecha_sincronizacion: datetime

    # Testimonio del grupo familiar sobre el evento (RF09). Permite distinguir
    # en el analisis una toma con dos fuentes de una que solo tiene la palabra
    # del paciente.
    corroborada: bool
    fecha_confirmacion: datetime | None

    # Propiedades calculadas en el modelo; insumo de las caracteristicas
    # conductuales del modelo predictivo (RF04).
    cumplida: bool
    minutos_de_retraso: float | None


class ResultadoSincronizacion(BaseModel):
    """Desenlace del envio en lote desde la app movil."""

    creados: int
    actualizados: int
    registros: list[RegistroTomaOut]


class ResumenAdherencia(BaseModel):
    """Indicadores de adherencia de un paciente para el panel clinico (RF07).

    ``tasa_adherencia`` es la proporcion de eventos cumplidos sobre los
    eventos registrados en la ventana consultada. No es el puntaje de Morisky
    —que mide adherencia autorreportada— sino la adherencia observada a partir
    de la traza digital, precisamente la brecha que el diagnostico identifico.
    """

    id_paciente: str
    codigo_anonimizado: str
    desde: datetime | None
    hasta: datetime | None
    total_eventos: int
    cumplidos: int
    omitidos: int
    tasa_adherencia: float = Field(ge=0, le=100, description="Porcentaje de cumplimiento")
    retraso_promedio_min: float | None
    omisiones_consecutivas: int = Field(
        description="Racha de omisiones mas reciente; dispara la alerta temprana (RF05)"
    )
    ultima_toma_registrada: datetime | None
