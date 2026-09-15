"""Reportes generales de los pacientes a cargo del medico (RF07).

Reune en una sola respuesta lo que el panel mostraba paciente por paciente:
adherencia observada, riesgo observado y predicho, y la composicion de la
poblacion en seguimiento. Tambien la exporta en CSV para abrirla en Excel.

Como se calcula cada cifra
--------------------------
* **Adherencia de un paciente**: tomas cumplidas (a tiempo o con retraso)
  entre tomas con desenlace (cumplidas + omitidas). Las pospuestas no cuentan
  porque aun no tienen desenlace.
* **Adherencia promedio**: media simple de la adherencia de los pacientes que
  tienen al menos una toma con desenlace. Cada paciente pesa lo mismo, tenga
  muchas o pocas tomas registradas.
* **Riesgo observado**: alto si la adherencia es menor al 60 % o hay 3 o mas
  omisiones seguidas; medio si es menor al 80 % o hay 2 seguidas; bajo en otro
  caso. Son los mismos umbrales que usa la ficha del paciente.
* **Riesgo predicho**: el que devuelve el modelo con la ficha del paciente.
"""
from __future__ import annotations

import csv
import io
from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..core.exceptions import ModeloNoDisponibleError
from ..core.security import requiere_rol
from ..db.database import get_db
from ..db.models import EstadoToma, Paciente, RegistroAdherencia, Rol, Usuario
from ..schemas.adherencia_schema import ESTADOS_CUMPLIDOS
from ..services import ml_inference

router = APIRouter(prefix="/api/reportes", tags=["Reportes"])

# Umbrales del riesgo observado (identicos a los de la ficha del paciente).
TASA_ALTA, TASA_MEDIA = 60, 80
RACHA_ALTA, RACHA_MEDIA = 3, 2


class FilaPaciente(BaseModel):
    id_paciente: str
    codigo_anonimizado: str
    nombre: str
    edad: int
    diagnostico: str
    numero_farmacos: int
    comorbilidades: int
    tomas_con_desenlace: int
    tasa_adherencia: float | None
    omisiones_consecutivas: int
    tomas_corroboradas: int
    riesgo_observado: str
    probabilidad_predicha: float | None
    riesgo_predicho: str | None


class Indicadores(BaseModel):
    pacientes_activos: int
    pacientes_con_tomas: int
    adherencia_promedio: float | None
    tomas_registradas: int
    tomas_cumplidas: int
    tomas_omitidas: int
    porcentaje_corroboradas: float | None
    pacientes_riesgo_alto: int


class ReporteGeneral(BaseModel):
    generado_el: datetime
    periodo_dias: int | None
    indicadores: Indicadores
    riesgo_observado: dict[str, int]
    riesgo_predicho: dict[str, int] | None
    por_diagnostico: dict[str, int]
    comorbilidades_frecuentes: list[dict]
    motivos_omision: list[dict]
    pacientes: list[FilaPaciente]


def clasificar_riesgo_observado(tasa: float | None, racha: int) -> str:
    if tasa is None:
        return "sin_datos"
    if tasa < TASA_ALTA or racha >= RACHA_ALTA:
        return "alto"
    if tasa < TASA_MEDIA or racha >= RACHA_MEDIA:
        return "medio"
    return "bajo"


def _fila(paciente: Paciente, eventos: list[RegistroAdherencia]) -> FilaPaciente:
    """Indicadores de un paciente; `eventos` en orden cronologico."""
    cumplidos = sum(e.estado in ESTADOS_CUMPLIDOS for e in eventos)
    omitidos = sum(e.estado is EstadoToma.OMITIDA for e in eventos)
    resueltos = cumplidos + omitidos
    tasa = round(100 * cumplidos / resueltos, 1) if resueltos else None

    racha = 0
    for evento in reversed(eventos):
        if evento.estado is EstadoToma.OMITIDA:
            racha += 1
        elif evento.estado in ESTADOS_CUMPLIDOS:
            break

    try:
        prediccion = ml_inference.predecir(paciente)
        probabilidad, nivel = prediccion.probabilidad, prediccion.nivel
    except ModeloNoDisponibleError:
        probabilidad = nivel = None

    return FilaPaciente(
        id_paciente=paciente.id_paciente,
        codigo_anonimizado=paciente.codigo_anonimizado,
        nombre=f"{paciente.nombres} {paciente.apellidos}",
        edad=paciente.edad,
        diagnostico=paciente.diagnostico.value,
        numero_farmacos=paciente.numero_farmacos,
        comorbilidades=paciente.comorbilidades,
        tomas_con_desenlace=resueltos,
        tasa_adherencia=tasa,
        omisiones_consecutivas=racha,
        tomas_corroboradas=sum(e.id_confirmante is not None for e in eventos),
        riesgo_observado=clasificar_riesgo_observado(tasa, racha),
        probabilidad_predicha=probabilidad,
        riesgo_predicho=nivel,
    )


def construir_reporte(db: Session, medico: Usuario, dias: int | None) -> ReporteGeneral:
    pacientes = (
        db.query(Paciente)
        .filter(Paciente.id_medico_tratante == medico.id_usuario, Paciente.activo.is_(True))
        .order_by(Paciente.codigo_anonimizado)
        .all()
    )
    ids = [p.id_paciente for p in pacientes]

    consulta = db.query(RegistroAdherencia).filter(RegistroAdherencia.id_paciente.in_(ids))
    if dias:
        desde = datetime.now(timezone.utc) - timedelta(days=dias)
        consulta = consulta.filter(RegistroAdherencia.fecha_hora_programada >= desde)
    eventos = consulta.order_by(RegistroAdherencia.fecha_hora_programada.asc()).all() if ids else []

    por_paciente: dict[str, list[RegistroAdherencia]] = {i: [] for i in ids}
    for evento in eventos:
        por_paciente[evento.id_paciente].append(evento)

    filas = [_fila(p, por_paciente[p.id_paciente]) for p in pacientes]
    # Los de mayor riesgo primero: es el orden util para decidir a quien llamar.
    orden = {"alto": 0, "medio": 1, "bajo": 2, "sin_datos": 3}
    filas.sort(key=lambda f: (orden[f.riesgo_observado], f.tasa_adherencia or 0))

    tasas = [f.tasa_adherencia for f in filas if f.tasa_adherencia is not None]
    cumplidas = sum(e.estado in ESTADOS_CUMPLIDOS for e in eventos)
    omitidas = sum(e.estado is EstadoToma.OMITIDA for e in eventos)
    corroboradas = sum(e.id_confirmante is not None for e in eventos)

    observado = Counter(f.riesgo_observado for f in filas)
    predichos = [f.riesgo_predicho for f in filas if f.riesgo_predicho]
    comorbilidades = Counter(c for p in pacientes for c in (p.lista_comorbilidades or []))
    motivos = Counter(
        (e.motivo_omision or "Sin motivo indicado").strip().capitalize()
        for e in eventos if e.estado is EstadoToma.OMITIDA
    )

    return ReporteGeneral(
        generado_el=datetime.now(timezone.utc),
        periodo_dias=dias,
        indicadores=Indicadores(
            pacientes_activos=len(pacientes),
            pacientes_con_tomas=len(tasas),
            adherencia_promedio=round(sum(tasas) / len(tasas), 1) if tasas else None,
            tomas_registradas=len(eventos),
            tomas_cumplidas=cumplidas,
            tomas_omitidas=omitidas,
            porcentaje_corroboradas=round(100 * corroboradas / cumplidas, 1) if cumplidas else None,
            pacientes_riesgo_alto=observado["alto"],
        ),
        riesgo_observado={n: observado[n] for n in ("alto", "medio", "bajo", "sin_datos")},
        riesgo_predicho=(
            {n: predichos.count(n) for n in ("alto", "medio", "bajo")} if predichos else None
        ),
        por_diagnostico={
            d: sum(p.diagnostico.value == d for p in pacientes) for d in ("hta", "dm2", "ambas")
        },
        comorbilidades_frecuentes=[
            {"comorbilidad": c, "pacientes": n} for c, n in comorbilidades.most_common(6)
        ],
        motivos_omision=[{"motivo": m, "veces": n} for m, n in motivos.most_common(5)],
        pacientes=filas,
    )


@router.get("/general", response_model=ReporteGeneral, summary="Reporte general de pacientes")
def reporte_general(
    db: Session = Depends(get_db),
    medico: Usuario = Depends(requiere_rol(Rol.MEDICO)),
    dias: int | None = Query(default=None, ge=1, le=365,
                             description="Ultimos N dias; sin valor, todo el historial"),
) -> ReporteGeneral:
    return construir_reporte(db, medico, dias)


ETIQUETAS_CSV = [
    ("codigo_anonimizado", "Codigo"),
    ("nombre", "Paciente"),
    ("edad", "Edad"),
    ("diagnostico", "Diagnostico"),
    ("numero_farmacos", "Farmacos"),
    ("comorbilidades", "Comorbilidades"),
    ("tomas_con_desenlace", "Tomas con desenlace"),
    ("tasa_adherencia", "Adherencia (%)"),
    ("omisiones_consecutivas", "Omisiones seguidas"),
    ("tomas_corroboradas", "Tomas corroboradas"),
    ("riesgo_observado", "Riesgo observado"),
    ("probabilidad_predicha", "Probabilidad predicha"),
    ("riesgo_predicho", "Riesgo predicho"),
]


@router.get("/general.csv", summary="Exportar el reporte general en CSV")
def exportar_reporte(
    db: Session = Depends(get_db),
    medico: Usuario = Depends(requiere_rol(Rol.MEDICO)),
    dias: int | None = Query(default=None, ge=1, le=365),
) -> Response:
    reporte = construir_reporte(db, medico, dias)
    salida = io.StringIO()
    escritor = csv.writer(salida)
    escritor.writerow([etiqueta for _, etiqueta in ETIQUETAS_CSV])
    for fila in reporte.pacientes:
        datos = fila.model_dump()
        escritor.writerow(["" if datos[c] is None else datos[c] for c, _ in ETIQUETAS_CSV])

    fecha = reporte.generado_el.strftime("%Y-%m-%d")
    # La marca BOM hace que Excel reconozca las tildes al abrir el archivo.
    return Response(
        content="﻿" + salida.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="reporte_pacientes_{fecha}.csv"'},
    )
