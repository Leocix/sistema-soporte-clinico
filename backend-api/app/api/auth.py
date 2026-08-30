"""Endpoints de autenticacion y sesion (RF01).

Historia de usuario HU01 del Sprint 1. Criterio de aceptacion: "Acceso por rol
con credenciales validas" (Tabla V del proyecto de investigacion).
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.exceptions import NoAutenticadoError
from ..core.security import create_access_token, get_current_user, verify_password
from ..db.database import get_db
from ..db.models import Usuario
from ..schemas.auth_schema import LoginRequest, TokenResponse, UsuarioOut

router = APIRouter(prefix="/api/auth", tags=["Autenticacion"])


@router.post("/login", response_model=TokenResponse, summary="Iniciar sesion")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    usuario = db.query(Usuario).filter(Usuario.correo == payload.correo).first()

    # Un unico mensaje para credencial inexistente, contrasena incorrecta o
    # perfil equivocado: no se revela cual de los tres datos fallo.
    if (
        usuario is None
        or not usuario.activo
        or not verify_password(payload.contrasena, usuario.hash_contrasena)
        or usuario.rol != payload.perfil
    ):
        raise NoAutenticadoError("Usuario o contrasena incorrectos.")

    usuario.ultimo_acceso = datetime.now(timezone.utc)
    db.commit()
    db.refresh(usuario)

    return TokenResponse(
        access_token=create_access_token(usuario.id_usuario, usuario.rol.value),
        expira_en_minutos=settings.access_token_expire_minutes,
        usuario=UsuarioOut.model_validate(usuario),
    )


@router.get("/me", response_model=UsuarioOut, summary="Perfil de la sesion actual")
def perfil_actual(usuario: Usuario = Depends(get_current_user)) -> UsuarioOut:
    return UsuarioOut.model_validate(usuario)
