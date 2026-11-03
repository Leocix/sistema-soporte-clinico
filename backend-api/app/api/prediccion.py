"""Endpoints de prediccion del riesgo de incumplimiento (RF04).

Cierra la brecha B3 del diagnostico: la ausencia de analitica predictiva sobre
los datos clinicos. Hasta aqui el sistema registraba la adherencia; con estas
rutas la anticipa.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.security import get_current_user, requiere_rol
from ..db.database import get_db
from ..db.models import Rol, Usuario
from ..schemas.prediccion_schema import EstadoModelo, PrediccionRiesgo
from ..services import ml_inference
from ..services.acceso import obtener_paciente_autorizado

router = APIRouter(prefix="/api/prediccion", tags=["Prediccion de riesgo"])


@router.get(
    "/estado",
    response_model=EstadoModelo,
    summary="Disponibilidad y procedencia del modelo",
)
def estado_del_modelo(
    _: Usuario = Depends(requiere_rol(Rol.MEDICO)),
) -> EstadoModelo:
    """Permite al panel saber si puede ofrecer predicciones.

    Se consulta antes de pedir ninguna: si el modelo no esta cargado, la
    interfaz oculta la seccion de riesgo en lugar de mostrar un error por cada
    paciente de la lista.
    """
    if not ml_inference.modelo_disponible():
        return EstadoModelo(
            disponible=False,
            mensaje=(
                "El modelo predictivo no está disponible. El resto del sistema "
                "sigue operativo."
            ),
        )

    ficha = ml_inference.ficha_del_modelo()
    return EstadoModelo(
        disponible=True,
        modelo={
            "algoritmo": ficha.get("algoritmo", "desconocido"),
            "entrenado_el": ficha.get("entrenado_el"),
            "origen_datos": ficha.get("origen_datos", "desconocido"),
            "datos_reales": bool(ficha.get("datos_reales", False)),
            "aucroc_validacion_cruzada": ficha.get("aucroc_validacion_cruzada"),
        },
        mensaje="Modelo cargado y operativo.",
    )


@router.get(
    "/pacientes/{id_paciente}",
    response_model=PrediccionRiesgo,
    summary="Riesgo de incumplimiento de un paciente",
)
def predecir_riesgo(
    id_paciente: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> PrediccionRiesgo:
    """Calcula el riesgo a partir de las variables del Anexo n.o 04.

    La autorizacion es la misma que para la ficha: el medico solo predice
    sobre sus pacientes, y un paciente solo sobre si mismo. La prediccion es un
    dato clinico mas y no puede quedar menos protegida que el resto.
    """
    paciente = obtener_paciente_autorizado(db, usuario, id_paciente)
    resultado = ml_inference.predecir(paciente)

    return PrediccionRiesgo(
        id_paciente=paciente.id_paciente,
        codigo_anonimizado=paciente.codigo_anonimizado,
        probabilidad=resultado.probabilidad,
        nivel=resultado.nivel,
        factores=resultado.factores,
        variables_imputadas=resultado.variables_imputadas,
        modelo=resultado.ficha_modelo,
        valor_base=resultado.valor_base,
        contribuciones=resultado.contribuciones,
    )
