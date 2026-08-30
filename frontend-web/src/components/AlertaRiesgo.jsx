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
 * Deja explicito que la clasificacion proviene de la adherencia YA OBSERVADA
 * y no del modelo predictivo: mientras RF04 no este desplegado, el panel no
 * debe insinuar una capacidad de anticipacion que todavia no tiene.
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
        Clasificación provisional calculada sobre las tomas registradas. La
        predicción del modelo de aprendizaje automático (RF04) y sus factores
        influyentes (SHAP, RF06) sustituirán este cálculo en el Sprint&nbsp;3.
      </p>
    </section>
  )
}
