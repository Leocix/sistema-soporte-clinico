"""Endpoints del grupo familiar de acompanamiento (RF09).

Historia de usuario HU04: "Como paciente, quiero que un familiar mio pueda
confirmar que tome mi medicacion, para que el registro no dependa solo de mi
palabra".

El problema que resuelve es metodologico, no de interfaz. Toda la traza de
adherencia del sistema es autorreporte: el paciente marca su propia toma. Es
una mejora sustancial frente al recuerdo verbal en consulta que describio el
diagnostico (OE1), pero conserva su sesgo. Un conviviente que corrobore el
evento anade un segundo testigo y permite separar, en el analisis posterior,
las tomas corroboradas de las que solo tienen la palabra del paciente.

La corroboracion **no sustituye** al registro del paciente ni lo modifica: se
anade. El acompanante no puede reportar tomas, ni cambiar su estado, ni ver la
ficha clinica. Solo puede dar fe de lo que el paciente ya reporto.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.exceptions import ConflictoError, RecursoNoEncontradoError
from ..core.security import (
    create_access_token,
    hash_password,
    requiere_rol,
)
from ..db.database import get_db
from ..db.models import (
    Acompanante,
    EstadoAcompanante,
    EstadoToma,
    RegistroAdherencia,
    Rol,
    Usuario,
)
from ..schemas.adherencia_schema import ESTADOS_CUMPLIDOS
from ..schemas.auth_schema import TokenResponse, UsuarioOut
from ..schemas.familiar_schema import (
    AcompananteOut,
    InvitacionCreate,
    PacienteAcompanadoOut,
    RegistroFamiliarRequest,
    TomaPorConfirmarOut,
    VinculacionRequest,
)
from ..services.acceso import (
    acompanamiento_sobre,
    acompanamientos_activos,
    ficha_del_paciente_autenticado,
)

router = APIRouter(prefix="/api/familiares", tags=["Grupo familiar"])

# Alfabeto sin caracteres que se confundan al dictarse: no hay O frente a 0 ni
# I frente a 1. El codigo lo lee en voz alta un adulto mayor a su hija; no
# siempre se copia y pega.
_ALFABETO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
LONGITUD_CODIGO = 8

# Una invitacion es, en la practica, una credencial para crear una cuenta:
# tiene que caducar aunque nadie se acuerde de revocarla.
VIGENCIA_INVITACION = timedelta(days=7)

# Tope de miembros por paciente. Acota de paso cuantos codigos de alta puede
# tener en circulacion una misma cuenta.
MAX_ACOMPANANTES = 5

# Plazo para corroborar una toma. Quien da fe de una dosis debe haberla
# presenciado: confirmar la de hace tres semanas no seria un testimonio sino
# un tramite, y ensuciaria justo el indicador que la corroboracion refuerza.
VENTANA_CORROBORACION = timedelta(hours=48)


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


def _con_zona(valor: datetime | None) -> datetime | None:
    """SQLite devuelve las marcas sin zona; se leen como UTC, que es como se
    escribieron."""
    if valor is None:
        return None
    return valor if valor.tzinfo is not None else valor.replace(tzinfo=timezone.utc)


def _generar_codigo(db: Session) -> str:
    """Codigo de invitacion aleatorio y no repetido."""
    for _ in range(20):
        codigo = "".join(secrets.choice(_ALFABETO) for _ in range(LONGITUD_CODIGO))
        ocupado = (
            db.query(Acompanante)
            .filter(Acompanante.codigo_invitacion == codigo)
            .first()
        )
        if ocupado is None:
            return codigo
    raise ConflictoError("No se pudo generar un código de invitación; reintente.")


def _corroboraciones(db: Session, vinculo: Acompanante) -> int:
    if vinculo.id_usuario is None:
        return 0
    return (
        db.query(RegistroAdherencia)
        .filter(
            RegistroAdherencia.id_paciente == vinculo.id_paciente,
            RegistroAdherencia.id_confirmante == vinculo.id_usuario,
        )
        .count()
    )


def _salida(db: Session, vinculo: Acompanante) -> AcompananteOut:
    """Proyecta el vinculo a la vista del paciente."""
    invitado = vinculo.estado is EstadoAcompanante.INVITADO
    return AcompananteOut(
        id_acompanante=vinculo.id_acompanante,
        # Mientras no hay cuenta, el unico nombre disponible es el que escribio
        # el paciente; despues manda el que la persona declaro al registrarse.
        nombre=(
            vinculo.usuario.nombre_completo
            if vinculo.usuario is not None
            else vinculo.nombre_invitado
        ),
        parentesco=vinculo.parentesco,
        estado=vinculo.estado,
        correo=vinculo.usuario.correo if vinculo.usuario is not None else None,
        # Una vez vinculado el familiar, el codigo ya no sirve para nada y
        # seguir mostrandolo solo invitaria a reenviarlo.
        codigo_invitacion=vinculo.codigo_invitacion if invitado else None,
        expira_en=_con_zona(vinculo.expira_en) if invitado else None,
        fecha_vinculacion=_con_zona(vinculo.fecha_vinculacion),
        tomas_corroboradas=_corroboraciones(db, vinculo),
    )


# ---------------------------------------------------------------------------
# Vista del paciente: invitar, ver y retirar
# ---------------------------------------------------------------------------
@router.post(
    "/invitaciones",
    response_model=AcompananteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Invitar a un familiar al grupo de acompanamiento",
)
def invitar(
    payload: InvitacionCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_rol(Rol.PACIENTE)),
) -> AcompananteOut:
    """Emite el codigo con el que un familiar podra crear su cuenta.

    Solo el paciente invita. Que la iniciativa sea suya, y no del medico ni del
    familiar, es lo que hace de esto un consentimiento y no una vigilancia:
    nadie entra en su grupo sin que el lo pida.
    """
    ficha = ficha_del_paciente_autenticado(db, usuario)

    vigentes = [
        v for v in ficha.acompanantes if v.estado is not EstadoAcompanante.REVOCADO
    ]
    if len(vigentes) >= MAX_ACOMPANANTES:
        raise ConflictoError(
            f"Ya tiene {MAX_ACOMPANANTES} personas en su grupo familiar. "
            "Retire a alguna antes de invitar a otra."
        )

    vinculo = Acompanante(
        id_paciente=ficha.id_paciente,
        nombre_invitado=payload.nombre_invitado,
        parentesco=payload.parentesco,
        estado=EstadoAcompanante.INVITADO,
        codigo_invitacion=_generar_codigo(db),
        expira_en=_ahora() + VIGENCIA_INVITACION,
    )
    db.add(vinculo)
    db.commit()
    db.refresh(vinculo)
    return _salida(db, vinculo)


@router.get(
    "",
    response_model=list[AcompananteOut],
    summary="Grupo familiar del paciente autenticado",
)
def mi_grupo(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_rol(Rol.PACIENTE)),
) -> list[AcompananteOut]:
    ficha = ficha_del_paciente_autenticado(db, usuario)
    vinculos = [
        v for v in ficha.acompanantes if v.estado is not EstadoAcompanante.REVOCADO
    ]
    vinculos.sort(key=lambda v: v.fecha_invitacion)
    return [_salida(db, v) for v in vinculos]


@router.delete(
    "/{id_acompanante}",
    response_model=AcompananteOut,
    summary="Retirar a un familiar del grupo",
)
def revocar(
    id_acompanante: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_rol(Rol.PACIENTE)),
) -> AcompananteOut:
    """Retira al acompanante, o anula la invitacion todavia sin canjear.

    Los dos casos no son el mismo hecho y no se tratan igual. Una invitacion
    sin canjear nunca llego a ser una pertenencia: se borra, y su codigo deja
    de existir. Un acompanante ya vinculado si formo parte del grupo, y sus
    corroboraciones quedaron en la traza clinica: se marca revocado, para que
    esa historia siga siendo legible.
    """
    ficha = ficha_del_paciente_autenticado(db, usuario)
    vinculo = (
        db.query(Acompanante)
        .filter(
            Acompanante.id_acompanante == id_acompanante,
            Acompanante.id_paciente == ficha.id_paciente,
        )
        .first()
    )
    if vinculo is None:
        raise RecursoNoEncontradoError("Esa persona no figura en su grupo familiar.")

    salida = _salida(db, vinculo)

    if vinculo.estado is EstadoAcompanante.INVITADO:
        db.delete(vinculo)
    else:
        vinculo.estado = EstadoAcompanante.REVOCADO
    db.commit()

    salida.estado = EstadoAcompanante.REVOCADO
    salida.codigo_invitacion = None
    salida.expira_en = None
    return salida


# ---------------------------------------------------------------------------
# Alta del familiar: canje del codigo
# ---------------------------------------------------------------------------
def _invitacion_vigente(db: Session, codigo: str) -> Acompanante:
    vinculo = (
        db.query(Acompanante).filter(Acompanante.codigo_invitacion == codigo).first()
    )
    # Un unico mensaje para codigo inexistente, ya canjeado o caducado: el
    # codigo es una credencial y no se informa en cual de los tres estados esta.
    if vinculo is None or not vinculo.vigente:
        raise RecursoNoEncontradoError(
            "El código no es válido o ya venció. Pida uno nuevo al paciente."
        )
    return vinculo


def _vincular(vinculo: Acompanante, cuenta: Usuario) -> None:
    vinculo.id_usuario = cuenta.id_usuario
    vinculo.estado = EstadoAcompanante.ACTIVO
    vinculo.fecha_vinculacion = _ahora()


@router.post(
    "/registro",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear la cuenta de un familiar a partir de un codigo",
)
def registrar_familiar(
    payload: RegistroFamiliarRequest, db: Session = Depends(get_db)
) -> TokenResponse:
    """Unica via de alta de cuentas del sistema.

    El codigo se comprueba **antes** que el correo, y a proposito: con el orden
    inverso, cualquiera podria averiguar que direcciones estan dadas de alta
    probando correos sin tener invitacion alguna.
    """
    vinculo = _invitacion_vigente(db, payload.codigo)

    correo = payload.correo.lower()
    if db.query(Usuario).filter(Usuario.correo == correo).first() is not None:
        raise ConflictoError(
            "Ese correo ya tiene una cuenta. Inicie sesión con ella y use la "
            "opción de acompañar a otra persona."
        )

    cuenta = Usuario(
        nombres=payload.nombres,
        apellidos=payload.apellidos,
        correo=correo,
        hash_contrasena=hash_password(payload.contrasena),
        rol=Rol.FAMILIAR,
    )
    db.add(cuenta)
    db.flush()

    _vincular(vinculo, cuenta)
    db.commit()
    db.refresh(cuenta)

    return TokenResponse(
        access_token=create_access_token(cuenta.id_usuario, cuenta.rol.value),
        expira_en_minutos=settings.access_token_expire_minutes,
        usuario=UsuarioOut.model_validate(cuenta),
    )


@router.post(
    "/vinculaciones",
    response_model=PacienteAcompanadoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Acompanar a otra persona con la cuenta ya existente",
)
def unirse_con_codigo(
    payload: VinculacionRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_rol(Rol.FAMILIAR)),
) -> PacienteAcompanadoOut:
    """Anade un segundo paciente al acompanante que ya tiene cuenta."""
    vinculo = _invitacion_vigente(db, payload.codigo)

    ya_acompana = any(
        v.id_paciente == vinculo.id_paciente for v in acompanamientos_activos(db, usuario)
    )
    if ya_acompana:
        raise ConflictoError("Ya figura como acompanante de esa persona.")

    _vincular(vinculo, usuario)
    db.commit()
    db.refresh(vinculo)
    return _paciente_acompanado(db, vinculo)


# ---------------------------------------------------------------------------
# Vista del familiar: a quien acompana y que puede corroborar
# ---------------------------------------------------------------------------
def _pendientes(
    db: Session, vinculos: list[Acompanante], limite: int | None = None
) -> list[RegistroAdherencia]:
    """Tomas cumplidas, recientes y aun sin corroborar de los pacientes dados."""
    if not vinculos:
        return []

    consulta = (
        db.query(RegistroAdherencia)
        .filter(
            RegistroAdherencia.id_paciente.in_([v.id_paciente for v in vinculos]),
            RegistroAdherencia.estado.in_(ESTADOS_CUMPLIDOS),
            RegistroAdherencia.id_confirmante.is_(None),
            RegistroAdherencia.fecha_hora_programada >= _ahora() - VENTANA_CORROBORACION,
        )
        .order_by(RegistroAdherencia.fecha_hora_programada.desc())
    )
    if limite is not None:
        consulta = consulta.limit(limite)
    return consulta.all()


def _paciente_acompanado(db: Session, vinculo: Acompanante) -> PacienteAcompanadoOut:
    eventos = (
        db.query(RegistroAdherencia)
        .filter(RegistroAdherencia.id_paciente == vinculo.id_paciente)
        .all()
    )
    cumplidos = [e for e in eventos if e.estado in ESTADOS_CUMPLIDOS]
    omitidos = [e for e in eventos if e.estado is EstadoToma.OMITIDA]
    # Mismo denominador que el resumen del panel medico: una toma pospuesta
    # aun no tiene desenlace y no cuenta. Dos cifras distintas para lo mismo,
    # una en el telefono de la hija y otra en la consulta, serian un problema.
    resueltos = len(cumplidos) + len(omitidos)
    tasa = round(100 * len(cumplidos) / resueltos, 1) if resueltos else None

    return PacienteAcompanadoOut(
        id_acompanante=vinculo.id_acompanante,
        nombre=vinculo.paciente.nombre_completo,
        parentesco=vinculo.parentesco,
        tasa_adherencia=tasa,
        tomas_por_confirmar=len(_pendientes(db, [vinculo])),
    )


@router.get(
    "/mis-pacientes",
    response_model=list[PacienteAcompanadoOut],
    summary="Personas que acompana el familiar autenticado",
)
def mis_pacientes(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_rol(Rol.FAMILIAR)),
) -> list[PacienteAcompanadoOut]:
    return [_paciente_acompanado(db, v) for v in acompanamientos_activos(db, usuario)]


@router.get(
    "/tomas-por-confirmar",
    response_model=list[TomaPorConfirmarOut],
    summary="Tomas recientes que el acompanante puede corroborar",
)
def tomas_por_confirmar(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_rol(Rol.FAMILIAR)),
    limite: int = Query(default=50, ge=1, le=200),
) -> list[TomaPorConfirmarOut]:
    vinculos = acompanamientos_activos(db, usuario)
    nombres = {v.id_paciente: v.paciente.nombre_completo for v in vinculos}

    return [
        TomaPorConfirmarOut(
            id_registro=r.id_registro,
            paciente=nombres.get(r.id_paciente, ""),
            medicamento=r.medicamento,
            dosis=r.dosis,
            fecha_hora_programada=r.fecha_hora_programada,
            fecha_hora_registro=r.fecha_hora_registro,
            corroborada=False,
        )
        for r in _pendientes(db, vinculos, limite=limite)
    ]


@router.post(
    "/tomas/{id_registro}/confirmacion",
    response_model=TomaPorConfirmarOut,
    summary="Corroborar que el paciente tomo esa dosis",
)
def confirmar_toma(
    id_registro: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_rol(Rol.FAMILIAR)),
) -> TomaPorConfirmarOut:
    """Anade el testimonio del acompanante al evento ya reportado.

    Se comprueban tres cosas, y ninguna sobra: que quien confirma acompane a
    ese paciente, que el evento sea una toma cumplida —no se corrobora una
    omision, que ya es una declaracion en contra del propio interes— y que la
    dosis siga dentro de la ventana en la que el testimonio significa algo.
    """
    registro = (
        db.query(RegistroAdherencia)
        .filter(RegistroAdherencia.id_registro == id_registro)
        .first()
    )
    if registro is None:
        raise RecursoNoEncontradoError("Esa toma no existe.")

    vinculo = acompanamiento_sobre(db, usuario, registro.id_paciente)

    if registro.estado not in ESTADOS_CUMPLIDOS:
        raise ConflictoError(
            "Solo se corroboran las tomas que el paciente reporto como cumplidas."
        )
    if registro.id_confirmante is not None:
        raise ConflictoError("Esa toma ya fue corroborada.")

    programada = _con_zona(registro.fecha_hora_programada)
    if programada is not None and programada < _ahora() - VENTANA_CORROBORACION:
        raise ConflictoError(
            "El plazo para corroborar esta toma ya venció."
        )

    registro.id_confirmante = usuario.id_usuario
    registro.fecha_confirmacion = _ahora()
    db.commit()
    db.refresh(registro)

    return TomaPorConfirmarOut(
        id_registro=registro.id_registro,
        paciente=vinculo.paciente.nombre_completo,
        medicamento=registro.medicamento,
        dosis=registro.dosis,
        fecha_hora_programada=registro.fecha_hora_programada,
        fecha_hora_registro=registro.fecha_hora_registro,
        corroborada=True,
        confirmada_por=usuario.nombre_completo,
        fecha_confirmacion=_con_zona(registro.fecha_confirmacion),
    )
