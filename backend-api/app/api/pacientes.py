"""Endpoints de gestion de pacientes polimedicados (RF02).

Historia de usuario HU02: "Como medico, quiero registrar y actualizar la ficha
del paciente polimedicado y su esquema farmacologico, para mantener trazable
su carga terapeutica". Criterio de aceptacion (Tabla V del proyecto):
"Alta/edicion persistida y consultable".
"""
from __future__ import annotations

import re
import secrets

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..core.exceptions import ConflictoError, RecursoNoEncontradoError
from ..core.security import get_current_user, hash_password, requiere_rol
from ..db.database import get_db
from ..db.models import Diagnostico, Paciente, Rol, Usuario
from ..schemas.paciente_schema import (
    AccesoMovilOut,
    PacienteCreate,
    PacienteOut,
    PacienteUpdate,
    PaginaPacientes,
)
from ..services.acceso import obtener_paciente_autorizado

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


# ---------------------------------------------------------------------------
# Acceso del paciente a la aplicacion movil
# ---------------------------------------------------------------------------
# La ficha clinica y la cuenta de acceso son entidades distintas: se puede
# tener ficha sin cuenta —un paciente que no usa el telefono— pero no al reves.
# Esta ruta cierra el hueco: hasta ahora la cuenta solo podia crearla un script
# en el servidor, de modo que el medico daba de alta al paciente y no tenia con
# que decirle como entrar.

# Alfabeto sin caracteres que se confundan al dictarse o al teclearse en un
# telefono: ni O frente a 0, ni I o l frente a 1.
_ALFABETO_CLAVE = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
LONGITUD_CLAVE = 10


def _clave_temporal() -> str:
    """Contrasena legible y suficientemente larga para dictarla una vez."""
    return "".join(secrets.choice(_ALFABETO_CLAVE) for _ in range(LONGITUD_CLAVE))


@router.post(
    "/{id_paciente}/acceso",
    response_model=AccesoMovilOut,
    status_code=status.HTTP_201_CREATED,
    summary="Generar o restablecer el acceso del paciente a la app movil",
)
def generar_acceso_movil(
    id_paciente: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_rol(Rol.MEDICO)),
) -> AccesoMovilOut:
    """Crea la cuenta movil del paciente, o le asigna una contrasena nueva.

    Una sola ruta para las dos cosas a proposito. Desde la consulta, «darle
    acceso» y «volver a darle acceso porque la olvido» son el mismo gesto, y
    separarlos obligaria al medico a saber de antemano si la cuenta ya existia.

    La contrasena se devuelve **una unica vez**. En la base queda su hash, de
    modo que ni el medico ni el administrador pueden consultarla despues: si se
    pierde, se genera otra.
    """
    paciente = obtener_paciente_autorizado(db, usuario, id_paciente)

    if not paciente.correo:
        raise ConflictoError(
            "La ficha no tiene correo electronico. Anadalo antes de generar el "
            "acceso: es el usuario con el que el paciente entrara."
        )
    if not paciente.activo:
        raise ConflictoError(
            "El paciente esta dado de baja del seguimiento; no admite acceso a "
            "la aplicacion."
        )

    correo = paciente.correo.strip().lower()
    clave = _clave_temporal()

    cuenta = paciente.usuario
    if cuenta is None:
        # La ficha aun no tiene cuenta. Puede existir una con ese correo si el
        # paciente ya figuraba en el sistema por otra via.
        ajena = db.query(Usuario).filter(func.lower(Usuario.correo) == correo).first()
        if ajena is not None:
            raise ConflictoError(
                "Ese correo ya pertenece a otra cuenta del sistema. Use una "
                "direccion distinta para este paciente."
            )
        cuenta = Usuario(
            nombres=paciente.nombres,
            apellidos=paciente.apellidos,
            correo=correo,
            hash_contrasena=hash_password(clave),
            rol=Rol.PACIENTE,
        )
        db.add(cuenta)
        db.flush()
        paciente.id_usuario = cuenta.id_usuario
        creada = True
    else:
        # La cuenta existe: se le asigna una contrasena nueva y se sincroniza el
        # correo, que el medico pudo corregir en la ficha despues de crearla.
        cuenta.hash_contrasena = hash_password(clave)
        cuenta.correo = correo
        cuenta.nombres = paciente.nombres
        cuenta.apellidos = paciente.apellidos
        cuenta.activo = True
        creada = False

    db.commit()

    return AccesoMovilOut(
        correo=correo,
        contrasena_temporal=clave,
        nombre_completo=paciente.nombre_completo,
        creada=creada,
    )
