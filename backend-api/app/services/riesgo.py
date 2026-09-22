"""Clasificacion del riesgo observado, en un solo lugar.

La adherencia observada se clasifica igual en la ficha del paciente, en los
reportes generales y en las alertas tempranas. Tenerla escrita tres veces
garantizaria que algun dia dijeran cosas distintas del mismo paciente.
"""
from __future__ import annotations

from ..db.models import EstadoToma, RegistroAdherencia
from ..schemas.adherencia_schema import ESTADOS_CUMPLIDOS

# Umbrales de cumplimiento. Por debajo del 60 % la literatura considera la
# adherencia claramente deficiente; el 80 % es el limite habitual de la
# adherencia aceptable.
TASA_ALTA, TASA_MEDIA = 60, 80
# Tres omisiones seguidas indican abandono en curso, no un olvido puntual.
RACHA_ALTA, RACHA_MEDIA = 3, 2
# Por debajo de este numero de tomas con desenlace, una tasa baja puede ser
# ruido de un paciente que acaba de empezar a usar la aplicacion.
MINIMO_EVENTOS = 5


class Observado:
    """Indicadores de adherencia observada de un paciente."""

    def __init__(self, eventos: list[RegistroAdherencia]) -> None:
        cumplidos = sum(e.estado in ESTADOS_CUMPLIDOS for e in eventos)
        omitidos = sum(e.estado is EstadoToma.OMITIDA for e in eventos)
        self.cumplidos = cumplidos
        self.omitidos = omitidos
        # Las tomas pospuestas no cuentan: aun no tienen desenlace.
        self.resueltos = cumplidos + omitidos
        self.tasa = round(100 * cumplidos / self.resueltos, 1) if self.resueltos else None

        racha = 0
        for evento in reversed(eventos):
            if evento.estado is EstadoToma.OMITIDA:
                racha += 1
            elif evento.estado in ESTADOS_CUMPLIDOS:
                break
        self.racha = racha

    @property
    def nivel(self) -> str:
        return clasificar(self.tasa, self.racha)


def clasificar(tasa: float | None, racha: int) -> str:
    """Riesgo observado: resume lo que el paciente ya hizo."""
    if tasa is None:
        return "sin_datos"
    if tasa < TASA_ALTA or racha >= RACHA_ALTA:
        return "alto"
    if tasa < TASA_MEDIA or racha >= RACHA_MEDIA:
        return "medio"
    return "bajo"
