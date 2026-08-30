"""Esquemas Pydantic de autenticacion (RF01).

La validacion estricta en el borde del API impide que datos malformados
alcancen la capa de datos y garantiza un contrato explicito para el panel
medico (React) y la app del paciente (Flutter).
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from ..db.models import Rol


class LoginRequest(BaseModel):
    """Credenciales enviadas desde la pantalla de inicio de sesion."""

    correo: EmailStr
    contrasena: str = Field(min_length=8, max_length=128)
    # El usuario declara el perfil con el que intenta ingresar (Fig. 2).
    perfil: Rol

    model_config = ConfigDict(extra="forbid")

    @field_validator("contrasena")
    @classmethod
    def _sin_espacios(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("La contrasena no puede estar vacia.")
        return v


class UsuarioOut(BaseModel):
    id_usuario: str
    nombres: str
    apellidos: str
    correo: EmailStr
    rol: Rol

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expira_en_minutos: int
    usuario: UsuarioOut
