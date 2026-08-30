/**
 * Clasificacion PROVISIONAL del riesgo de incumplimiento.
 *
 * Estas reglas NO son el modelo predictivo del proyecto. Son una heuristica
 * sobre la adherencia ya observada —lo que el paciente hizo— que permite al
 * panel ordenar la lista por prioridad clinica mientras el modelo (RF04) se
 * entrena y se despliega como microservicio en el Sprint 3.
 *
 * La diferencia es importante y debe sostenerse en la sustentacion: el modelo
 * ANTICIPA el incumplimiento a partir de las variables del Anexo n.o 04; esta
 * heuristica solo RESUME el comportamiento pasado. Cuando RF04 este
 * disponible, la probabilidad devuelta por el modelo sustituye este calculo y
 * los factores influyentes vienen de SHAP (RF06).
 */

export const NIVELES = {
  ALTO: 'alto',
  MEDIO: 'medio',
  BAJO: 'bajo',
  SIN_DATOS: 'sin_datos',
}

const ETIQUETAS = {
  [NIVELES.ALTO]: 'Alto',
  [NIVELES.MEDIO]: 'Medio',
  [NIVELES.BAJO]: 'Bajo',
  [NIVELES.SIN_DATOS]: 'Sin datos',
}

/** Umbrales de la heuristica, en un solo lugar para poder justificarlos. */
export const UMBRALES = {
  // Por debajo del 60 % de cumplimiento la literatura considera la adherencia
  // claramente deficiente.
  tasaAlta: 60,
  tasaMedia: 80,
  // Tres omisiones seguidas indican abandono en curso, no un olvido puntual.
  rachaAlta: 3,
  rachaMedia: 2,
}

export function clasificarRiesgo(resumen) {
  if (!resumen || resumen.total_eventos === 0) return NIVELES.SIN_DATOS

  const { tasa_adherencia: tasa, omisiones_consecutivas: racha } = resumen

  if (tasa < UMBRALES.tasaAlta || racha >= UMBRALES.rachaAlta) return NIVELES.ALTO
  if (tasa < UMBRALES.tasaMedia || racha >= UMBRALES.rachaMedia) return NIVELES.MEDIO
  return NIVELES.BAJO
}

export function etiquetaRiesgo(nivel) {
  return ETIQUETAS[nivel] ?? ETIQUETAS[NIVELES.SIN_DATOS]
}

/** Motivo legible de la clasificacion, para que el medico sepa por que. */
export function motivoRiesgo(resumen) {
  if (!resumen || resumen.total_eventos === 0) {
    return 'El paciente aun no ha registrado tomas desde la aplicacion movil.'
  }

  const motivos = []
  if (resumen.tasa_adherencia < UMBRALES.tasaAlta) {
    motivos.push(`cumplimiento del ${resumen.tasa_adherencia} %`)
  } else if (resumen.tasa_adherencia < UMBRALES.tasaMedia) {
    motivos.push(`cumplimiento parcial del ${resumen.tasa_adherencia} %`)
  }
  if (resumen.omisiones_consecutivas >= UMBRALES.rachaMedia) {
    motivos.push(`${resumen.omisiones_consecutivas} omisiones consecutivas`)
  }
  if (motivos.length === 0) {
    return `Cumplimiento del ${resumen.tasa_adherencia} % sin omisiones recientes.`
  }
  return `Motivo: ${motivos.join(' y ')}.`
}

/** Clasificacion de la adherencia basal autorreportada (test de Morisky). */
export function etiquetaAdherenciaBasal(paciente) {
  if (paciente?.incumplimiento_basal === null || paciente?.incumplimiento_basal === undefined) {
    return 'No evaluada'
  }
  return paciente.incumplimiento_basal ? 'Deficiente' : 'Buena'
}
