"""Hasheo de contrasenas, emision de JWT y control de acceso por rol (RBAC).

Cubre RF01 (autenticar y autorizar a medicos y pacientes con perfiles
diferenciados) y RNF01 (seguridad): las contrasenas nunca se persisten en
texto plano y el token de sesion viaja firmado y con expiracion.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db.models import Rol, Usuario
from .config import settings
from .exceptions import NoAutenticadoError, PermisoDenegadoError

_bearer = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Contrasenas
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# ---------------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------------
def create_access_token(subject: str, rol: str) -> str:
    expira = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "rol": rol, "exp": expira}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise NoAutenticadoError("Token invalido o expirado.") from exc


# ---------------------------------------------------------------------------
# Dependencias de autorizacion
# ---------------------------------------------------------------------------
def get_current_user(
    credenciales: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    """Resuelve el usuario autenticado a partir del JWT del encabezado."""
    if credenciales is None:
        raise NoAutenticadoError("No se envio el token de acceso.")

    datos = decode_access_token(credenciales.credentials)
    usuario = db.query(Usuario).filter(Usuario.id_usuario == datos.get("sub")).first()

    if usuario is None or not usuario.activo:
        raise NoAutenticadoError("La sesion ya no es valida.")
    return usuario


def requiere_rol(*roles: Rol):
    """Fabrica de dependencias RBAC.

    Uso: ``Depends(requiere_rol(Rol.MEDICO))`` en los endpoints del panel
    clinico, de modo que un token de paciente no pueda auditar la adherencia
    de terceros ni consultar el listado de riesgo.
    """

    def _verificar(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.rol not in roles:
            raise PermisoDenegadoError()
        return usuario

    return _verificar
