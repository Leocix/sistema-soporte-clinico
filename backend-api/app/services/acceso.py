"""Reglas de acceso a la ficha de un paciente (RBAC de dominio).

El rol por si solo no basta para autorizar: un paciente autenticado tiene rol
valido, pero solo sobre *su* ficha. Esta regla se concentra aqui para que
todos los endpoints que reciben un ``id_paciente`` la apliquen de forma
identica y no quede dispersa —ni olvidada— en cada router.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from ..core.exceptions import PermisoDenegadoError, RecursoNoEncontradoError
from ..db.models import Paciente, Rol, Usuario


def obtener_paciente_autorizado(
    db: Session, usuario: Usuario, id_paciente: str
) -> Paciente:
    """Devuelve la ficha solicitada si el usuario tiene derecho a verla.

    - Medico: accede a las fichas de los pacientes que tiene a cargo.
    - Paciente: accede unicamente a su propia ficha.
    """
    paciente = db.query(Paciente).filter(Paciente.id_paciente == id_paciente).first()
    if paciente is None:
        raise RecursoNoEncontradoError("El paciente indicado no existe.")

    if usuario.rol is Rol.MEDICO:
        if paciente.id_medico_tratante != usuario.id_usuario:
            # Se responde 403 y no 404: el recurso existe, pero corresponde a
            # otro medico tratante.
            raise PermisoDenegadoError(
                "El paciente no figura a su cargo como medico tratante."
            )
        return paciente

    if paciente.id_usuario != usuario.id_usuario:
        raise PermisoDenegadoError("Solo puede consultar su propia ficha clinica.")
    return paciente


def ficha_del_paciente_autenticado(db: Session, usuario: Usuario) -> Paciente:
    """Resuelve la ficha clinica del usuario con rol PACIENTE."""
    paciente = db.query(Paciente).filter(Paciente.id_usuario == usuario.id_usuario).first()
    if paciente is None:
        raise RecursoNoEncontradoError(
            "Su cuenta aun no tiene una ficha clinica asociada. "
            "Solicite al consultorio que complete su registro."
        )
    return paciente
