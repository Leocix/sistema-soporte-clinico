"""Esquemas Pydantic del registro de adherencia (RF03).

El contrato esta pensado para una app movil que puede quedar sin conectividad:
los eventos se acumulan en el dispositivo y se envian despues, individualmente
o en lote. Por eso el identificador logico del evento no es un correlativo del
servidor sino la terna (paciente, medicamento, horario programado), que hace
la sincronizacion idempotente.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ..db.models import EstadoToma, OrigenRegistro

ESTADOS_CUMPLIDOS = (EstadoToma.TOMADA, EstadoToma.TOMADA_TARDE)

# Ventana de registro de una toma cumplida, alrededor de su hora programada.
# La aplicacion movil replica estos valores (Constantes.ventanaAntes y
# Constantes.ventanaDespues) para deshabilitar el boton fuera de la ventana; el
# API es quien la hace cumplir.
VENTANA_ANTES = timedelta(minutes=60)
VENTANA_DESPUES = timedelta(hours=3)
# Margen para relojes de telefono ligeramente desajustados.
TOLERANCIA_RELOJ = timedelta(minutes=5)


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
        if self.estado in ESTADOS_CUMPLIDOS and self.fecha_hora_registro is not None:
            # Ventana de registro: una toma solo se da por cumplida si se marca
            # cerca de su hora. Impide marcar de golpe, por la noche, todas las
            # dosis del dia. Se mide contra la hora PROGRAMADA y no contra la del
            # servidor, para que una toma marcada a tiempo sin conexion siga
            # siendo valida aunque la cola la envie horas despues.
            desfase = self.fecha_hora_registro - self.fecha_hora_programada
            if desfase < -VENTANA_ANTES or desfase > VENTANA_DESPUES:
                raise ValueError(
                    "Fuera de la ventana de registro: una toma se puede marcar como "
                    f"cumplida desde {int(VENTANA_ANTES.total_seconds() // 60)} minutos antes "
                    f"hasta {int(VENTANA_DESPUES.total_seconds() // 3600)} horas después de su hora."
                )
            # Un registro con hora futura delata un reloj del telefono adelantado.
            if self.fecha_hora_registro > datetime.now(timezone.utc) + TOLERANCIA_RELOJ:
                raise ValueError(
                    "La hora de la toma es posterior a la hora actual. Revise la hora del teléfono."
                )
        if self.estado is EstadoToma.OMITIDA and self.fecha_hora_registro is not None:
            raise ValueError(
                "Una toma omitida no puede llevar hora de toma; use 'tomada_tarde'."
            )
        return self


class TestigoOut(BaseModel):
    """Una persona que respalda el evento: quien lo registro o quien lo corroboro."""

    nombre: str
    # «registro» o «corroboro»: el papel de la persona en esta toma.
    papel: str
    # Relacion con el paciente: «paciente», «medico» o el parentesco del familiar.
    relacion: str


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
    # Todas las personas que respaldan la toma, con su nombre: el panel deja de
    # decir solo «Familiar» y muestra quien registro y quien corroboro.
    testigos: list[TestigoOut] = []

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
