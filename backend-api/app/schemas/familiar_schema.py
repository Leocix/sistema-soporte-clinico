"""Esquemas Pydantic del grupo familiar de acompanamiento (RF09).

El contrato distingue con cuidado dos vistas de la misma relacion:

  * la del **paciente**, que invita, ve a los suyos y puede revocarlos;
  * la del **familiar**, que solo ve a quien acompana y las tomas que puede
    corroborar.

Ningun esquema expone el ``id_paciente`` al familiar: la app del acompanante
trabaja siempre contra rutas que resuelven el vinculo desde el token, de modo
que un identificador de ficha clinica no llegue nunca a un dispositivo de un
tercero.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from ..db.models import EstadoAcompanante, Parentesco


class InvitacionCreate(BaseModel):
    """Alta de una invitacion al grupo familiar, hecha por el paciente."""

    model_config = ConfigDict(extra="forbid")

    nombre_invitado: str = Field(min_length=2, max_length=120)
    parentesco: Parentesco

    @field_validator("nombre_invitado")
    @classmethod
    def _normalizar(cls, v: str) -> str:
        return " ".join(v.split())


class AcompananteOut(BaseModel):
    """Miembro del grupo familiar tal como lo ve el paciente.

    ``codigo_invitacion`` solo viaja mientras la invitacion sigue sin canjear:
    una vez vinculado el familiar, el codigo ya no sirve para nada y seguir
    mostrandolo solo invitaria a reenviarlo.
    """

    id_acompanante: str
    nombre: str
    parentesco: Parentesco
    estado: EstadoAcompanante
    correo: str | None = None
    codigo_invitacion: str | None = None
    expira_en: datetime | None = None
    fecha_vinculacion: datetime | None = None
    # Cuantas tomas ha corroborado: es lo que hace visible el aporte real del
    # acompanante frente a una pertenencia meramente nominal.
    tomas_corroboradas: int = 0


class RegistroFamiliarRequest(BaseModel):
    """Canje del codigo: crea la cuenta del familiar y la vincula al paciente.

    Es la unica via de alta de cuentas del sistema. No existe registro
    abierto: sin un codigo vigente emitido por un paciente, esta ruta no crea
    nada.
    """

    model_config = ConfigDict(extra="forbid")

    codigo: str = Field(min_length=6, max_length=12)
    nombres: str = Field(min_length=2, max_length=120)
    apellidos: str = Field(min_length=2, max_length=120)
    correo: EmailStr
    contrasena: str = Field(min_length=8, max_length=128)

    @field_validator("codigo")
    @classmethod
    def _normalizar_codigo(cls, v: str) -> str:
        # El codigo se dicta por telefono o se copia de un mensaje: se acepta
        # en minusculas y con espacios de sobra.
        return v.strip().replace(" ", "").replace("-", "").upper()

    @field_validator("nombres", "apellidos")
    @classmethod
    def _normalizar_nombre(cls, v: str) -> str:
        return " ".join(v.split())

    @field_validator("contrasena")
    @classmethod
    def _sin_espacios(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("La contrasena no puede estar vacia.")
        return v


class VinculacionRequest(BaseModel):
    """Canje de un codigo por parte de un familiar que ya tiene cuenta.

    Existe para el caso corriente de quien acompana a dos personas de la misma
    casa: sin esta ruta necesitaria una segunda cuenta y un segundo correo.
    """

    model_config = ConfigDict(extra="forbid")

    codigo: str = Field(min_length=6, max_length=12)

    @field_validator("codigo")
    @classmethod
    def _normalizar_codigo(cls, v: str) -> str:
        return v.strip().replace(" ", "").replace("-", "").upper()


class PacienteAcompanadoOut(BaseModel):
    """A quien acompana el familiar autenticado.

    Deliberadamente escueto: el acompanante necesita saber a quien ayuda y como
    va su cumplimiento, no acceder a su ficha clinica. El diagnostico, el
    esquema farmacologico y el seudonimo del dataset quedan fuera.
    """

    id_acompanante: str
    nombre: str
    parentesco: Parentesco
    tasa_adherencia: float | None = None
    tomas_por_confirmar: int = 0


class TomaPorConfirmarOut(BaseModel):
    """Toma que el paciente reporto como cumplida y espera corroboracion."""

    model_config = ConfigDict(from_attributes=True)

    id_registro: str
    paciente: str
    medicamento: str
    dosis: str | None
    fecha_hora_programada: datetime
    fecha_hora_registro: datetime | None
    corroborada: bool
    confirmada_por: str | None = None
    fecha_confirmacion: datetime | None = None
