"""Endpoints de autenticacion y sesion (RF01).

Historia de usuario HU01 del Sprint 1. Criterio de aceptacion: "Acceso por rol
con credenciales validas" (Tabla V del proyecto de investigacion).
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.exceptions import NoAutenticadoError, RecursoNoEncontradoError
from ..core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from ..db.database import get_db
from ..db.models import Restablecimiento, Usuario
from ..schemas.auth_schema import (
    ConfirmarRecuperacionRequest,
    LoginRequest,
    RecuperacionRequest,
    RecuperacionResponse,
    TokenResponse,
    UsuarioOut,
)
from ..services.correo import enviar_restablecimiento

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


# ---------------------------------------------------------------------------
# RF10 - Restablecimiento de la contrasena
# ---------------------------------------------------------------------------
# Hasta ahora, un paciente que olvidaba su clave tenia que acercarse al
# consultorio. Para la poblacion del estudio —adultos mayores, buena parte de
# zona rural— eso no es un tramite menor: es un viaje. Y para el consultorio
# significaba ejecutar un script a mano por cada olvido.

# Mensaje unico de la solicitud. Es el mismo exista o no la cuenta: contestar
# distinto convertiria esta ruta en un buscador de correos registrados.
_AVISO_ENVIADO = (
    "Si esa direccion corresponde a una cuenta, le hemos enviado un enlace "
    "para crear una contrasena nueva. Revise su correo."
)
_AVISO_SIN_CORREO = (
    "El envio de correos no esta disponible. Solicite el restablecimiento en "
    "el consultorio."
)


def _huella(testigo: str) -> str:
    """Resumen que se persiste en lugar del testigo."""
    return hashlib.sha256(testigo.encode("utf-8")).hexdigest()


def _anular_pendientes(db: Session, id_usuario: str, momento: datetime) -> None:
    """Invalida los permisos anteriores que aun no se hubieran usado.

    Quien no recuerda si ya pidio el enlace lo pide dos o tres veces. Sin esto
    quedarian varios vivos a la vez y bastaria con que uno solo se filtrase.
    """
    pendientes = (
        db.query(Restablecimiento)
        .filter(
            Restablecimiento.id_usuario == id_usuario,
            Restablecimiento.usado_en.is_(None),
        )
        .all()
    )
    for anterior in pendientes:
        anterior.usado_en = momento


@router.post(
    "/recuperacion",
    response_model=RecuperacionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Pedir un enlace para restablecer la contrasena",
)
def solicitar_recuperacion(
    payload: RecuperacionRequest,
    tareas: BackgroundTasks,
    db: Session = Depends(get_db),
) -> RecuperacionResponse:
    """Emite el enlace y lo envia por correo, si la cuenta existe.

    La respuesta es siempre la misma. El envio se delega a una tarea de fondo,
    no solo por rapidez: si el API esperase al servidor de correo, el tiempo de
    respuesta delataria por si solo que direcciones estan registradas.
    """
    if not settings.correo_configurado:
        return RecuperacionResponse(mensaje=_AVISO_SIN_CORREO, correo_habilitado=False)

    correo = payload.correo.strip().lower()
    usuario = (
        db.query(Usuario).filter(func.lower(Usuario.correo) == correo).first()
    )

    if usuario is not None and usuario.activo:
        ahora = datetime.now(timezone.utc)
        _anular_pendientes(db, usuario.id_usuario, ahora)

        # El testigo se genera aqui y no vuelve a existir en el servidor: de el
        # solo se guarda el resumen.
        testigo = secrets.token_urlsafe(32)
        db.add(
            Restablecimiento(
                id_usuario=usuario.id_usuario,
                hash_testigo=_huella(testigo),
                expira_en=ahora
                + timedelta(minutes=settings.minutos_vigencia_restablecimiento),
            )
        )
        db.commit()

        enlace = f"{settings.frontend_url.rstrip('/')}/restablecer?t={testigo}"
        tareas.add_task(
            enviar_restablecimiento, usuario.correo, usuario.nombres, enlace
        )

    return RecuperacionResponse(mensaje=_AVISO_ENVIADO, correo_habilitado=True)


@router.post(
    "/recuperacion/confirmar",
    response_model=RecuperacionResponse,
    summary="Fijar la contrasena nueva con el enlace recibido",
)
def confirmar_recuperacion(
    payload: ConfirmarRecuperacionRequest, db: Session = Depends(get_db)
) -> RecuperacionResponse:
    """Cambia la contrasena y consume el permiso.

    Un unico mensaje para el enlace inexistente, el ya usado y el caducado: los
    tres significan lo mismo para quien lo tiene delante, y distinguirlos solo
    ayudaria a quien esta probando enlaces ajenos.
    """
    permiso = (
        db.query(Restablecimiento)
        .filter(Restablecimiento.hash_testigo == _huella(payload.testigo))
        .first()
    )
    if permiso is None or not permiso.vigente:
        raise RecursoNoEncontradoError(
            "El enlace no es valido o ya vencio. Pida uno nuevo."
        )

    usuario = permiso.usuario
    if usuario is None or not usuario.activo:
        raise RecursoNoEncontradoError(
            "El enlace no es valido o ya vencio. Pida uno nuevo."
        )

    usuario.hash_contrasena = hash_password(payload.contrasena)
    permiso.usado_en = datetime.now(timezone.utc)
    # Los demas permisos pendientes de esa cuenta caen con este: si el olvido
    # ya se resolvio, ninguno de los enlaces anteriores deberia seguir sirviendo.
    _anular_pendientes(db, usuario.id_usuario, permiso.usado_en)
    db.commit()

    return RecuperacionResponse(
        mensaje="Su contrasena quedo cambiada. Ya puede iniciar sesion.",
        correo_habilitado=True,
    )
