"""Alertas tempranas de riesgo para el medico (RF05).

Responde a la brecha B4 del diagnostico: hoy el incumplimiento se detecta
cuando el paciente ya se descompenso. Las reglas se evaluan solas —al
sincronizar una toma y al abrir la bandeja— y no dependen de que el medico
recuerde revisar a cada paciente.

Tres reglas, cada una con su umbral justificado:

* **Omisiones seguidas** (>= 3): abandono en curso, no un olvido puntual.
* **Adherencia baja** (< 60 % con al menos 5 tomas resueltas): cumplimiento
  deficiente segun la literatura. El minimo de tomas evita avisar por el ruido
  de un paciente que acaba de empezar a usar la aplicacion.
* **Riesgo predicho alto**: el microservicio de inferencia clasifica al
  paciente como de riesgo alto. Es la unica regla que mira hacia delante, y la
  razon de ser del componente inteligente. El umbral vive en el microservicio,
  que es quien conoce el modelo.

Tres decisiones sostienen que la bandeja siga siendo legible:

1. **Una alerta abierta por tipo y paciente.** La evidencia nueva actualiza la
   alerta existente en lugar de crear otra fila.
2. **Se cierran solas cuando la condicion desaparece.** Si el paciente vuelve a
   cumplir, la alerta queda `resuelta` con su historia intacta, en vez de
   seguir abierta hasta que alguien la lea.
3. **Lo cerrado por el medico no reaparece al instante.** Tras atender o
   descartar, el mismo aviso vuelve solo si la evidencia empeora o si pasa el
   plazo de silencio. De otro modo, cerrar una alerta no serviria de nada:
   volveria en la siguiente consulta de la bandeja.
"""
from __future__ import annotations

import logging
from datetime import timedelta, timezone

from sqlalchemy.orm import Session

from ..db.models import (
    Alerta,
    EstadoAlerta,
    Paciente,
    RegistroAdherencia,
    TipoAlerta,
    Usuario,
    _ahora,
)
from .riesgo import MINIMO_EVENTOS, RACHA_ALTA, TASA_ALTA, Observado

log = logging.getLogger("cdss.alertas")

# Plazo durante el cual no se repite un aviso que el medico ya cerro, salvo que
# la evidencia empeore. Descartar dice "no aplica a este paciente" y dura mas
# que atender, que dice "ya actue".
SILENCIO_ATENDIDA = timedelta(days=7)
SILENCIO_DESCARTADA = timedelta(days=30)


def abiertas_de(db: Session, id_paciente: str) -> dict[TipoAlerta, Alerta]:
    filas = (
        db.query(Alerta)
        .filter(Alerta.id_paciente == id_paciente, Alerta.estado == EstadoAlerta.ABIERTA)
        .all()
    )
    return {fila.tipo: fila for fila in filas}


def _silenciada(db: Session, paciente: Paciente, tipo: TipoAlerta, valor: float) -> bool:
    """Indica si el medico ya cerro este aviso y todavia no debe repetirse."""
    ultima = (
        db.query(Alerta)
        .filter(
            Alerta.id_paciente == paciente.id_paciente,
            Alerta.tipo == tipo,
            Alerta.estado.in_((EstadoAlerta.ATENDIDA, EstadoAlerta.DESCARTADA)),
        )
        .order_by(Alerta.fecha_cierre.desc())
        .first()
    )
    if ultima is None or ultima.fecha_cierre is None:
        return False

    plazo = (
        SILENCIO_DESCARTADA if ultima.estado is EstadoAlerta.DESCARTADA else SILENCIO_ATENDIDA
    )
    cierre = ultima.fecha_cierre
    if cierre.tzinfo is None:
        cierre = cierre.replace(tzinfo=timezone.utc)
    if _ahora() - cierre >= plazo:
        return False
    # La evidencia empeoro: el caso vuelve a la bandeja aunque este en plazo.
    return ultima.valor is None or valor <= float(ultima.valor)


def _registrar(
    db: Session,
    abiertas: dict[TipoAlerta, Alerta],
    paciente: Paciente,
    tipo: TipoAlerta,
    motivo: str,
    valor: float,
) -> Alerta | None:
    existente = abiertas.get(tipo)
    if existente is not None:
        existente.motivo = motivo
        existente.valor = valor
        existente.fecha_actualizacion = _ahora()
        return existente

    if _silenciada(db, paciente, tipo, valor):
        return None

    alerta = Alerta(
        id_paciente=paciente.id_paciente,
        tipo=tipo,
        motivo=motivo,
        valor=valor,
        estado=EstadoAlerta.ABIERTA,
    )
    db.add(alerta)
    log.info("alerta_generada tipo=%s paciente=%s", tipo.value, paciente.codigo_anonimizado)
    return alerta


def evaluar_paciente(
    db: Session,
    paciente: Paciente,
    eventos: list[RegistroAdherencia],
    prediccion: tuple[float, str] | None = None,
) -> list[Alerta]:
    """Aplica las reglas y devuelve las alertas abiertas del paciente.

    `eventos` va en orden cronologico. `prediccion` es la probabilidad y el
    nivel que devolvio el microservicio de inferencia, y solo llega cuando
    respondio; sin ella las otras dos reglas se evaluan igual, de modo que la
    bandeja no depende del componente inteligente.
    """
    observado = Observado(eventos)
    abiertas = abiertas_de(db, paciente.id_paciente)
    vigentes: set[TipoAlerta] = set()

    if observado.racha >= RACHA_ALTA:
        vigentes.add(TipoAlerta.OMISIONES_SEGUIDAS)
        _registrar(
            db, abiertas, paciente, TipoAlerta.OMISIONES_SEGUIDAS,
            f"{observado.racha} tomas omitidas seguidas.", float(observado.racha),
        )

    if (
        observado.tasa is not None
        and observado.resueltos >= MINIMO_EVENTOS
        and observado.tasa < TASA_ALTA
    ):
        vigentes.add(TipoAlerta.ADHERENCIA_BAJA)
        _registrar(
            db, abiertas, paciente, TipoAlerta.ADHERENCIA_BAJA,
            f"Cumplimiento del {observado.tasa} % en {observado.resueltos} tomas registradas.",
            float(observado.tasa),
        )

    if prediccion is not None and prediccion[1] == "alto":
        probabilidad = prediccion[0]
        vigentes.add(TipoAlerta.RIESGO_PREDICHO)
        _registrar(
            db, abiertas, paciente, TipoAlerta.RIESGO_PREDICHO,
            f"El modelo estima {round(probabilidad * 100)} % de probabilidad de "
            "incumplimiento antes del proximo control.",
            round(probabilidad * 100, 2),
        )

    for tipo, alerta in abiertas.items():
        if tipo in vigentes:
            continue
        if tipo is TipoAlerta.RIESGO_PREDICHO and prediccion is None:
            # Sin prediccion no hay evidencia de que el riesgo haya bajado.
            continue
        alerta.estado = EstadoAlerta.RESUELTA
        alerta.fecha_cierre = _ahora()
        alerta.nota_cierre = "Cerrada por el sistema: la condicion dejo de cumplirse."

    db.flush()
    return list(abiertas_de(db, paciente.id_paciente).values())


def cerrar(
    db: Session, alerta: Alerta, medico: Usuario, estado: EstadoAlerta, nota: str | None
) -> Alerta:
    """Atiende o descarta una alerta y guarda lo que hizo el medico."""
    alerta.estado = estado
    alerta.fecha_cierre = _ahora()
    alerta.nota_cierre = nota
    alerta.id_medico_cierre = medico.id_usuario
    db.commit()
    db.refresh(alerta)
    return alerta
