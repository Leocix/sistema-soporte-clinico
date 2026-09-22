"""Bandeja de alertas tempranas del medico (RF05).

    GET  /api/alertas                     alertas del medico, recalculadas
    POST /api/alertas/{id}/atender        el medico actuo, con su nota
    POST /api/alertas/{id}/descartar      no pertinente para ese paciente

Al abrir la bandeja se reevaluan las reglas sobre todos los pacientes activos
del medico, incluida la prediccion del modelo: asi el aviso no depende de que
el paciente haya sincronizado algo desde la ultima vez que se miro.
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..core.exceptions import ModeloNoDisponibleError, RecursoNoEncontradoError
from ..core.security import requiere_rol
from ..db.database import get_db
from ..db.models import Alerta, EstadoAlerta, Paciente, RegistroAdherencia, Rol, Usuario
from ..services import alertas as servicio
from ..services import ml_inference

router = APIRouter(prefix="/api/alertas", tags=["Alertas tempranas"])

ETIQUETAS_TIPO = {
    "omisiones_seguidas": "Omisiones seguidas",
    "adherencia_baja": "Adherencia baja",
    "riesgo_predicho": "Riesgo predicho alto",
}


class AlertaOut(BaseModel):
    id_alerta: str
    id_paciente: str
    codigo_anonimizado: str
    paciente: str
    tipo: str
    tipo_legible: str
    estado: str
    motivo: str
    valor: float | None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    fecha_cierre: datetime | None
    nota_cierre: str | None


class BandejaAlertas(BaseModel):
    abiertas: int
    modelo_disponible: bool
    alertas: list[AlertaOut]


class CierreAlerta(BaseModel):
    nota: str | None = Field(default=None, max_length=500)


def _salida(alerta: Alerta) -> AlertaOut:
    return AlertaOut(
        id_alerta=alerta.id_alerta,
        id_paciente=alerta.id_paciente,
        codigo_anonimizado=alerta.paciente.codigo_anonimizado,
        paciente=f"{alerta.paciente.nombres} {alerta.paciente.apellidos}",
        tipo=alerta.tipo.value,
        tipo_legible=ETIQUETAS_TIPO.get(alerta.tipo.value, alerta.tipo.value),
        estado=alerta.estado.value,
        motivo=alerta.motivo,
        valor=float(alerta.valor) if alerta.valor is not None else None,
        fecha_creacion=alerta.fecha_creacion,
        fecha_actualizacion=alerta.fecha_actualizacion,
        fecha_cierre=alerta.fecha_cierre,
        nota_cierre=alerta.nota_cierre,
    )


def _alerta_del_medico(db: Session, medico: Usuario, id_alerta: str) -> Alerta:
    """Una alerta es un dato clinico: solo la ve el medico tratante."""
    alerta = (
        db.query(Alerta)
        .join(Paciente, Alerta.id_paciente == Paciente.id_paciente)
        .filter(
            Alerta.id_alerta == id_alerta,
            Paciente.id_medico_tratante == medico.id_usuario,
        )
        .first()
    )
    if alerta is None:
        raise RecursoNoEncontradoError("La alerta indicada no existe.")
    return alerta


def refrescar(db: Session, medico: Usuario) -> bool:
    """Reevalua las reglas de todos los pacientes activos del medico.

    Devuelve si el microservicio de inferencia respondio. Cuando no lo hace,
    las reglas sobre la traza de tomas se evaluan igual: la bandeja degrada,
    no se apaga.
    """
    pacientes = (
        db.query(Paciente)
        .filter(Paciente.id_medico_tratante == medico.id_usuario, Paciente.activo.is_(True))
        .all()
    )
    if not pacientes:
        return False

    try:
        predicciones = ml_inference.predecir_lote(pacientes)
        modelo_disponible = True
    except ModeloNoDisponibleError:
        predicciones, modelo_disponible = {}, False

    eventos = (
        db.query(RegistroAdherencia)
        .filter(RegistroAdherencia.id_paciente.in_([p.id_paciente for p in pacientes]))
        .order_by(RegistroAdherencia.fecha_hora_programada.asc())
        .all()
    )
    por_paciente: dict[str, list[RegistroAdherencia]] = {p.id_paciente: [] for p in pacientes}
    for evento in eventos:
        por_paciente[evento.id_paciente].append(evento)

    for paciente in pacientes:
        prediccion = predicciones.get(paciente.codigo_anonimizado)
        servicio.evaluar_paciente(
            db, paciente, por_paciente[paciente.id_paciente], prediccion
        )
    db.commit()
    return modelo_disponible


@router.get("", response_model=BandejaAlertas, summary="Alertas tempranas del medico")
def listar_alertas(
    db: Session = Depends(get_db),
    medico: Usuario = Depends(requiere_rol(Rol.MEDICO)),
    estado: EstadoAlerta | None = Query(default=EstadoAlerta.ABIERTA,
                                        description="null para ver todo el historial"),
    limite: int = Query(default=50, ge=1, le=200),
) -> BandejaAlertas:
    modelo_disponible = refrescar(db, medico)

    consulta = (
        db.query(Alerta)
        .join(Paciente, Alerta.id_paciente == Paciente.id_paciente)
        .filter(Paciente.id_medico_tratante == medico.id_usuario)
    )
    abiertas = consulta.filter(Alerta.estado == EstadoAlerta.ABIERTA).count()
    if estado is not None:
        consulta = consulta.filter(Alerta.estado == estado)

    filas = consulta.order_by(Alerta.fecha_actualizacion.desc()).limit(limite).all()
    return BandejaAlertas(
        abiertas=abiertas,
        modelo_disponible=modelo_disponible,
        alertas=[_salida(a) for a in filas],
    )


@router.post("/{id_alerta}/atender", response_model=AlertaOut,
             summary="Registrar que el medico actuo sobre la alerta")
def atender(
    id_alerta: str,
    payload: CierreAlerta,
    db: Session = Depends(get_db),
    medico: Usuario = Depends(requiere_rol(Rol.MEDICO)),
) -> AlertaOut:
    alerta = _alerta_del_medico(db, medico, id_alerta)
    return _salida(servicio.cerrar(db, alerta, medico, EstadoAlerta.ATENDIDA, payload.nota))


@router.post("/{id_alerta}/descartar", response_model=AlertaOut,
             status_code=status.HTTP_200_OK,
             summary="Descartar una alerta no pertinente")
def descartar(
    id_alerta: str,
    payload: CierreAlerta,
    db: Session = Depends(get_db),
    medico: Usuario = Depends(requiere_rol(Rol.MEDICO)),
) -> AlertaOut:
    alerta = _alerta_del_medico(db, medico, id_alerta)
    return _salida(servicio.cerrar(db, alerta, medico, EstadoAlerta.DESCARTADA, payload.nota))
