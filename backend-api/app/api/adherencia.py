"""Endpoints de registro y auditoria de la adherencia (RF03).

Historia de usuario HU03: "Como paciente, quiero registrar desde mi celular
cada toma de medicamento, para que mi medico conozca mi cumplimiento real
entre citas". Criterio de aceptacion (Tabla V del proyecto): "Cada toma queda
registrada y sincronizada".

La sincronizacion es **idempotente**: la terna (paciente, medicamento, horario
programado) identifica de forma univoca el evento, de modo que un reintento
tras una perdida de conectividad actualiza el registro existente en lugar de
duplicarlo. Es la condicion que exige el criterio de aceptacion y la que
protege la validez del dataset: eventos duplicados sesgarian la tasa de
adherencia observada y, con ella, las caracteristicas del modelo (RF04).
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from ..core.exceptions import AppError, ConflictoError, PermisoDenegadoError
from ..core.security import get_current_user
from ..db.database import get_db
from ..db.models import (
    Acompanante,
    EstadoToma,
    OrigenRegistro,
    Paciente,
    RegistroAdherencia,
    Rol,
    Usuario,
)
from ..schemas.adherencia_schema import (
    ESTADOS_CUMPLIDOS,
    RegistroTomaCreate,
    RegistroTomaOut,
    ResultadoSincronizacion,
    ResumenAdherencia,
)
from ..services import alertas as servicio_alertas
from ..services.acceso import ficha_del_paciente_autenticado, obtener_paciente_autorizado

router = APIRouter(prefix="/api/adherencia", tags=["Adherencia"])

# Tope del envio en lote: acota el tamano de la transaccion cuando la app
# vacia una cola acumulada tras varios dias sin conexion.
MAX_LOTE = 200


def _paciente_destino(
    db: Session, usuario: Usuario, id_paciente: str | None
) -> Paciente:
    """Determina sobre que ficha se registra, segun el rol de quien envia."""
    if usuario.rol is Rol.PACIENTE:
        ficha = ficha_del_paciente_autenticado(db, usuario)
        if id_paciente is not None and id_paciente != ficha.id_paciente:
            raise PermisoDenegadoError("Solo puede registrar sus propias tomas.")
        paciente = ficha
    else:
        if id_paciente is None:
            raise AppError(
                "Indique el paciente sobre el que se registra la toma.",
                codigo="PACIENTE_REQUERIDO",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        paciente = obtener_paciente_autorizado(db, usuario, id_paciente)

    if not paciente.activo:
        raise ConflictoError(
            "El paciente está dado de baja del seguimiento; no admite nuevos registros."
        )
    return paciente


def _registrar_evento(
    db: Session, paciente: Paciente, datos: RegistroTomaCreate
) -> tuple[RegistroAdherencia, bool]:
    """Crea el evento o actualiza el existente. Devuelve (registro, fue_creado)."""
    existente = (
        db.query(RegistroAdherencia)
        .filter(
            RegistroAdherencia.id_paciente == paciente.id_paciente,
            RegistroAdherencia.medicamento == datos.medicamento,
            RegistroAdherencia.fecha_hora_programada == datos.fecha_hora_programada,
        )
        .first()
    )

    if existente is not None:
        # El desenlace de una dosis puede cambiar legitimamente: una toma
        # pospuesta que finalmente se cumple. Se conserva el ultimo estado
        # reportado en lugar de rechazar el envio.
        existente.estado = datos.estado
        existente.fecha_hora_registro = datos.fecha_hora_registro
        existente.dosis = datos.dosis
        existente.motivo_omision = datos.motivo_omision
        existente.origen = datos.origen
        existente.sincronizado = True
        existente.fecha_sincronizacion = datetime.now(timezone.utc)
        return existente, False

    nuevo = RegistroAdherencia(
        id_paciente=paciente.id_paciente,
        medicamento=datos.medicamento,
        dosis=datos.dosis,
        fecha_hora_programada=datos.fecha_hora_programada,
        fecha_hora_registro=datos.fecha_hora_registro,
        estado=datos.estado,
        origen=datos.origen,
        motivo_omision=datos.motivo_omision,
        sincronizado=True,
    )
    db.add(nuevo)
    return nuevo, True


@router.post(
    "/registros",
    response_model=RegistroTomaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar la toma de un medicamento",
)
def registrar_toma(
    payload: RegistroTomaCreate,
    respuesta: Response,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> RegistroAdherencia:
    paciente = _paciente_destino(db, usuario, payload.id_paciente)
    registro, fue_creado = _registrar_evento(db, paciente, payload)
    db.commit()
    db.refresh(registro)
    _revisar_alertas(db, paciente)

    # 201 cuando el evento es nuevo; 200 cuando el envio es un reintento que
    # actualizo el evento ya sincronizado.
    respuesta.status_code = (
        status.HTTP_201_CREATED if fue_creado else status.HTTP_200_OK
    )
    return registro


@router.post(
    "/registros/lote",
    response_model=ResultadoSincronizacion,
    summary="Sincronizar la cola de tomas acumulada sin conexion",
)
def sincronizar_lote(
    payload: list[RegistroTomaCreate],
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> ResultadoSincronizacion:
    if not payload:
        raise AppError(
            "El lote no contiene registros.",
            codigo="LOTE_VACIO",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if len(payload) > MAX_LOTE:
        raise AppError(
            f"El lote supera el maximo de {MAX_LOTE} registros por envio.",
            codigo="LOTE_EXCEDIDO",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        )

    creados = actualizados = 0
    registros: list[RegistroAdherencia] = []

    for datos in payload:
        paciente = _paciente_destino(db, usuario, datos.id_paciente)
        registro, fue_creado = _registrar_evento(db, paciente, datos)
        # Se vuelca lo pendiente en cada iteracion para que dos eventos
        # identicos dentro del mismo lote se resuelvan como uno solo.
        db.flush()
        registros.append(registro)
        creados += fue_creado
        actualizados += not fue_creado

    # Todo el lote se confirma en una sola transaccion: o entra completo o no
    # entra, de modo que un fallo a mitad de camino no deje la cola del
    # dispositivo en un estado indeterminado.
    db.commit()
    for registro in registros:
        db.refresh(registro)
    for paciente in {r.id_paciente: r for r in registros}.values():
        _revisar_alertas(db, paciente.paciente)

    return ResultadoSincronizacion(
        creados=creados,
        actualizados=actualizados,
        registros=[RegistroTomaOut.model_validate(r) for r in registros],
    )


# ---------------------------------------------------------------------------
# Consulta de la traza de adherencia
# ---------------------------------------------------------------------------
def _consultar_registros(
    db: Session,
    paciente: Paciente,
    desde: datetime | None,
    hasta: datetime | None,
    limite: int | None = None,
    ascendente: bool = False,
) -> list[RegistroAdherencia]:
    """Eventos del paciente en la ventana indicada."""
    consulta = db.query(RegistroAdherencia).filter(
        RegistroAdherencia.id_paciente == paciente.id_paciente
    )
    if desde is not None:
        consulta = consulta.filter(RegistroAdherencia.fecha_hora_programada >= desde)
    if hasta is not None:
        consulta = consulta.filter(RegistroAdherencia.fecha_hora_programada <= hasta)

    orden = (
        RegistroAdherencia.fecha_hora_programada.asc()
        if ascendente
        else RegistroAdherencia.fecha_hora_programada.desc()
    )
    consulta = consulta.order_by(orden)
    if limite is not None:
        consulta = consulta.limit(limite)
    return consulta.all()


def _revisar_alertas(db: Session, paciente: Paciente) -> None:
    """Reevalua las reglas de alerta del paciente tras registrar una toma.

    Es el momento en que la evidencia cambia: una omision mas puede completar
    la racha que el medico necesita conocer hoy, no en su proxima consulta. No
    se pide la prediccion al microservicio —encarecerian cada sincronizacion de
    la app— porque esa regla se evalua al abrir la bandeja.
    """
    eventos = _consultar_registros(db, paciente, None, None, ascendente=True)
    servicio_alertas.evaluar_paciente(db, paciente, eventos)
    db.commit()


def _construir_resumen(
    paciente: Paciente,
    eventos: list[RegistroAdherencia],
    desde: datetime | None,
    hasta: datetime | None,
) -> ResumenAdherencia:
    """Calcula los indicadores de adherencia observada sobre `eventos`.

    Se espera la lista en orden cronologico ascendente: la racha de omisiones
    se recorre desde el evento mas reciente hacia atras.
    """
    cumplidos = [e for e in eventos if e.estado in ESTADOS_CUMPLIDOS]
    omitidos = [e for e in eventos if e.estado is EstadoToma.OMITIDA]
    # Una toma pospuesta aun no tiene desenlace: se excluye del denominador
    # para no penalizar ni premiar al paciente por un evento en curso.
    resueltos = len(cumplidos) + len(omitidos)
    tasa = round(100 * len(cumplidos) / resueltos, 2) if resueltos else 0.0

    retrasos = [
        e.minutos_de_retraso for e in cumplidos if e.minutos_de_retraso is not None
    ]
    retraso_promedio = round(sum(retrasos) / len(retrasos), 1) if retrasos else None

    # Racha de omisiones mas reciente: el disparador de la alerta temprana.
    racha = 0
    for evento in reversed(eventos):
        if evento.estado is EstadoToma.OMITIDA:
            racha += 1
        elif evento.estado in ESTADOS_CUMPLIDOS:
            break

    horas_registro = [e.fecha_hora_registro for e in cumplidos if e.fecha_hora_registro]

    return ResumenAdherencia(
        id_paciente=paciente.id_paciente,
        codigo_anonimizado=paciente.codigo_anonimizado,
        desde=desde,
        hasta=hasta,
        total_eventos=len(eventos),
        cumplidos=len(cumplidos),
        omitidos=len(omitidos),
        tasa_adherencia=tasa,
        retraso_promedio_min=retraso_promedio,
        omisiones_consecutivas=racha,
        ultima_toma_registrada=max(horas_registro) if horas_registro else None,
    )


# --- Rutas del propio paciente (app movil) ---------------------------------
# La app del paciente no conoce su `id_paciente`: la cuenta de usuario y la
# ficha clinica son entidades distintas y el identificador de la ficha solo lo
# maneja el panel medico. Estas dos rutas resuelven la ficha desde el token,
# de modo que el paciente pueda ver su propio seguimiento sin que el API le
# revele identificadores de terceros.


@router.get(
    "/mis-registros",
    response_model=list[RegistroTomaOut],
    summary="Historial de tomas del paciente autenticado",
)
def mis_registros(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    limite: int = Query(default=100, ge=1, le=500),
) -> list[RegistroAdherencia]:
    paciente = ficha_del_paciente_autenticado(db, usuario)
    return _consultar_registros(db, paciente, desde, hasta, limite=limite)


@router.get(
    "/mi-resumen",
    response_model=ResumenAdherencia,
    summary="Indicadores de adherencia del paciente autenticado",
)
def mi_resumen(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
) -> ResumenAdherencia:
    paciente = ficha_del_paciente_autenticado(db, usuario)
    eventos = _consultar_registros(db, paciente, desde, hasta, ascendente=True)
    return _construir_resumen(paciente, eventos, desde, hasta)


# --- Rutas por identificador (panel medico) --------------------------------


@router.get(
    "/pacientes/{id_paciente}/registros",
    response_model=list[RegistroTomaOut],
    summary="Historial de tomas de un paciente",
)
def listar_registros(
    id_paciente: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    limite: int = Query(default=100, ge=1, le=500),
) -> list[RegistroAdherencia]:
    paciente = obtener_paciente_autorizado(db, usuario, id_paciente)
    registros = _consultar_registros(db, paciente, desde, hasta, limite=limite)
    _anotar_testigos(db, paciente, registros)
    return registros


# Quien registra la toma, segun el canal por el que entro el dato.
_REGISTRA = {
    OrigenRegistro.APP_MOVIL: "paciente",
    OrigenRegistro.PANEL_WEB: "medico",
    OrigenRegistro.IMPORTACION: "importacion",
}


def _anotar_testigos(db: Session, paciente: Paciente, registros: list[RegistroAdherencia]) -> None:
    """Agrega a cada toma la lista de personas que la respaldan.

    Una sola consulta trae a los familiares del paciente; el resto se resuelve
    en memoria, de modo que el historial no hace una consulta por fila.
    """
    familiares = {
        a.id_usuario: a
        for a in db.query(Acompanante).filter(
            Acompanante.id_paciente == paciente.id_paciente,
            Acompanante.id_usuario.isnot(None),
        )
    }
    nombre_paciente = (paciente.nombres or "").split(" ")[0] or paciente.codigo_anonimizado
    for registro in registros:
        testigos = []
        relacion = _REGISTRA.get(registro.origen, "paciente")
        if relacion == "paciente":
            testigos.append({"nombre": nombre_paciente, "papel": "registro", "relacion": "paciente"})
        elif relacion == "medico":
            testigos.append({"nombre": "Médico tratante", "papel": "registro", "relacion": "medico"})
        else:
            testigos.append({"nombre": "Carga de datos", "papel": "registro", "relacion": "importacion"})
        if registro.id_confirmante:
            familiar = familiares.get(registro.id_confirmante)
            testigos.append({
                "nombre": familiar.nombre_invitado if familiar else "Familiar",
                "papel": "corroboro",
                "relacion": familiar.parentesco.value if familiar else "familiar",
            })
        # Atributo transitorio: no es columna, solo viaja en la respuesta.
        registro.testigos = testigos


@router.get(
    "/pacientes/{id_paciente}/resumen",
    response_model=ResumenAdherencia,
    summary="Indicadores de adherencia observada",
)
def resumen_adherencia(
    id_paciente: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
) -> ResumenAdherencia:
    """Adherencia observada a partir de la traza digital.

    A diferencia del puntaje de Morisky —autorreportado en consulta—, estos
    indicadores se calculan sobre eventos fechados, que es exactamente la
    evidencia objetiva cuya ausencia identifico el diagnostico (OE1).
    """
    paciente = obtener_paciente_autorizado(db, usuario, id_paciente)
    eventos = _consultar_registros(db, paciente, desde, hasta, ascendente=True)
    return _construir_resumen(paciente, eventos, desde, hasta)
