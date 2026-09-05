"""Endpoints de gestion de pacientes polimedicados (RF02).

Historia de usuario HU02: "Como medico, quiero registrar y actualizar la ficha
del paciente polimedicado y su esquema farmacologico, para mantener trazable
su carga terapeutica". Criterio de aceptacion (Tabla V del proyecto):
"Alta/edicion persistida y consultable".
"""
from __future__ import annotations

import re

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..core.exceptions import ConflictoError, RecursoNoEncontradoError
from ..core.security import get_current_user, requiere_rol
from ..db.database import get_db
from ..db.models import Diagnostico, Paciente, Rol, Usuario
from ..schemas.paciente_schema import (
    PacienteCreate,
    PacienteOut,
    PacienteUpdate,
    PaginaPacientes,
)
from ..services.acceso import ficha_del_paciente_autenticado, obtener_paciente_autorizado

router = APIRouter(prefix="/api/pacientes", tags=["Pacientes"])

_PATRON_CODIGO = re.compile(r"^P-(\d+)$")


def _siguiente_codigo(db: Session) -> str:
    """Correlativo seudonimizado P-001, P-002, ...

    La unicidad real la garantiza la restriccion de la columna; esta funcion
    solo propone el siguiente valor libre. Si dos altas concurrentes proponen
    el mismo codigo, la segunda recibe un 409 y basta con reintentar.
    """
    codigos = db.query(Paciente.codigo_anonimizado).all()
    maximo = 0
    for (codigo,) in codigos:
        coincidencia = _PATRON_CODIGO.match(codigo or "")
        if coincidencia:
            maximo = max(maximo, int(coincidencia.group(1)))
    return f"P-{maximo + 1:03d}"


@router.post(
    "",
    response_model=PacienteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un paciente polimedicado",
)
def crear_paciente(
    payload: PacienteCreate,
    db: Session = Depends(get_db),
    medico: Usuario = Depends(requiere_rol(Rol.MEDICO)),
) -> Paciente:
    datos = payload.model_dump()
    codigo = datos.pop("codigo_anonimizado", None) or _siguiente_codigo(db)

    if db.query(Paciente).filter(Paciente.codigo_anonimizado == codigo).first():
        raise ConflictoError(f"Ya existe un paciente con el codigo {codigo}.")

    id_usuario = datos.pop("id_usuario", None)
    if id_usuario is not None:
        cuenta = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
        if cuenta is None:
            raise RecursoNoEncontradoError("La cuenta de usuario indicada no existe.")
        if cuenta.rol is not Rol.PACIENTE:
            raise ConflictoError(
                "La ficha clinica solo puede vincularse a una cuenta con perfil paciente."
            )
        if db.query(Paciente).filter(Paciente.id_usuario == id_usuario).first():
            raise ConflictoError("Esa cuenta ya tiene una ficha clinica asociada.")

    paciente = Paciente(
        **datos,
        codigo_anonimizado=codigo,
        id_usuario=id_usuario,
        # El medico que da de alta queda como tratante y define el alcance de
        # su listado en el panel clinico.
        id_medico_tratante=medico.id_usuario,
    )
    db.add(paciente)
    db.commit()
    db.refresh(paciente)
    return paciente


@router.get(
    "",
    response_model=PaginaPacientes,
    summary="Listar los pacientes a cargo del medico",
)
def listar_pacientes(
    db: Session = Depends(get_db),
    medico: Usuario = Depends(requiere_rol(Rol.MEDICO)),
    pagina: int = Query(default=1, ge=1),
    tamano: int = Query(default=20, ge=1, le=100),
    activo: bool | None = Query(default=True, description="null para incluir las bajas"),
    diagnostico: Diagnostico | None = Query(default=None),
    busqueda: str | None = Query(default=None, max_length=60,
                                 description="Coincidencia parcial por nombre, apellidos o codigo"),
) -> PaginaPacientes:
    consulta = db.query(Paciente).filter(Paciente.id_medico_tratante == medico.id_usuario)

    if activo is not None:
        consulta = consulta.filter(Paciente.activo.is_(activo))
    if diagnostico is not None:
        consulta = consulta.filter(Paciente.diagnostico == diagnostico)
    if busqueda:
        # El medico busca por el nombre que recuerda; el codigo seudonimizado
        # es util cuando ya tiene la ficha delante. Se admiten ambos.
        patron = f"%{busqueda.strip()}%"
        consulta = consulta.filter(
            or_(
                Paciente.nombres.ilike(patron),
                Paciente.apellidos.ilike(patron),
                Paciente.codigo_anonimizado.ilike(patron),
            )
        )

    total = consulta.with_entities(func.count(Paciente.id_paciente)).scalar() or 0
    items = (
        consulta.order_by(Paciente.codigo_anonimizado)
        .offset((pagina - 1) * tamano)
        .limit(tamano)
        .all()
    )
    return PaginaPacientes(
        total=total,
        pagina=pagina,
        tamano=tamano,
        items=[PacienteOut.model_validate(p) for p in items],
    )


@router.get(
    "/mi-ficha",
    response_model=PacienteOut,
    summary="Ficha clinica del paciente autenticado",
)
def mi_ficha(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> Paciente:
    """Resuelve la ficha desde el token, para la aplicacion movil.

    El paciente no conoce su `id_paciente`: la cuenta de usuario y la ficha
    clinica son entidades distintas, y ese identificador solo lo maneja el
    panel medico. Esta ruta debe declararse ANTES que `/{id_paciente}`; en caso
    contrario "mi-ficha" se interpretaria como un identificador y la peticion
    terminaria en un 404.
    """
    return ficha_del_paciente_autenticado(db, usuario)


@router.get(
    "/{id_paciente}",
    response_model=PacienteOut,
    summary="Consultar la ficha de un paciente",
)
def obtener_paciente(
    id_paciente: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> Paciente:
    # Un paciente autenticado puede leer su propia ficha; el medico, la de los
    # pacientes que tiene a cargo.
    return obtener_paciente_autorizado(db, usuario, id_paciente)


@router.patch(
    "/{id_paciente}",
    response_model=PacienteOut,
    summary="Actualizar la ficha o el esquema farmacologico",
)
def actualizar_paciente(
    id_paciente: str,
    payload: PacienteUpdate,
    db: Session = Depends(get_db),
    medico: Usuario = Depends(requiere_rol(Rol.MEDICO)),
) -> Paciente:
    paciente = obtener_paciente_autorizado(db, medico, id_paciente)

    cambios = payload.campos_enviados()
    if not cambios:
        raise ConflictoError("No se envio ningun campo para actualizar.")

    for campo, valor in cambios.items():
        setattr(paciente, campo, valor)

    # La coherencia entre controles debe verificarse sobre el estado resultante
    # de la fusion, no solo sobre los campos enviados.
    if paciente.controles_perdidos_6m > paciente.controles_programados_6m:
        db.rollback()
        raise ConflictoError(
            "Los controles perdidos no pueden superar a los programados."
        )

    db.commit()
    db.refresh(paciente)
    return paciente


@router.delete(
    "/{id_paciente}",
    response_model=PacienteOut,
    summary="Dar de baja a un paciente del seguimiento",
)
def dar_de_baja(
    id_paciente: str,
    db: Session = Depends(get_db),
    medico: Usuario = Depends(requiere_rol(Rol.MEDICO)),
) -> Paciente:
    """Baja logica.

    Los registros de adherencia son la evidencia del estudio y no se eliminan:
    el paciente se marca como inactivo y deja de aparecer en el panel, pero su
    historial permanece disponible para el analisis.
    """
    paciente = obtener_paciente_autorizado(db, medico, id_paciente)
    paciente.activo = False
    db.commit()
    db.refresh(paciente)
    return paciente
