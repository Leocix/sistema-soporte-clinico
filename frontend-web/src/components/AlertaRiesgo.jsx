import { NIVELES, clasificarRiesgo, etiquetaRiesgo, motivoRiesgo } from '../services/riesgo'

/** Distintivo compacto para las celdas de la tabla del panel. */
export function DistintivoRiesgo({ resumen }) {
  const nivel = clasificarRiesgo(resumen)
  return (
    <span className={`distintivo distintivo--${nivel}`}>{etiquetaRiesgo(nivel)}</span>
  )
}

/**
 * Aviso de riesgo en la ficha del paciente.
 *
 * Deja explicito que esta clasificacion proviene de la adherencia YA
 * OBSERVADA y no del modelo. Las dos conviven en la ficha y responden a
 * preguntas distintas: esta resume lo que el paciente hizo; la prediccion
 * (RF04) estima lo que hara antes del proximo control. Fundirlas en un solo
 * indicador ocultaria de donde sale cada cifra.
 */
export default function AlertaRiesgo({ resumen }) {
  const nivel = clasificarRiesgo(resumen)
  const sinDatos = nivel === NIVELES.SIN_DATOS

  return (
    <section className={`alerta alerta--${nivel}`} aria-live="polite">
      <div className="alerta__cabecera">
        <span className="alerta__etiqueta">Riesgo observado</span>
        <span className={`distintivo distintivo--${nivel}`}>{etiquetaRiesgo(nivel)}</span>
      </div>

      <p className="alerta__motivo">{motivoRiesgo(resumen)}</p>

      {!sinDatos && nivel !== NIVELES.BAJO && (
        <p className="alerta__accion">
          Se recomienda contacto con el paciente y refuerzo de la adherencia
          antes del próximo control.
        </p>
      )}

      <p className="alerta__pie">
        Calculado sobre las tomas ya registradas: resume el comportamiento
        pasado. La estimación de lo que ocurrirá antes del próximo control es
        la predicción del modelo, arriba.
      </p>
    </section>
  )
}
