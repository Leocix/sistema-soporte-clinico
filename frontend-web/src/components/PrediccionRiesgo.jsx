import { etiquetaRiesgo } from '../services/riesgo'

/** Nombres legibles de las variables del Anexo n.° 04. */
const NOMBRE_VARIABLE = {
  tasa_inasistencia: 'Inasistencia a controles',
  carga_terapeutica: 'Carga terapéutica (fármacos × tomas)',
  numero_farmacos: 'Número de fármacos',
  tomas_dia: 'Tomas por día',
  comorbilidades: 'Comorbilidades',
  tiempo_enfermedad_anios: 'Tiempo de enfermedad',
  cronicidad_relativa: 'Cronicidad relativa a la edad',
  controles_perdidos_6m: 'Controles perdidos',
  controles_programados_6m: 'Controles programados',
  edad: 'Edad',
  nivel_educativo: 'Nivel educativo',
  convivencia: 'Convivencia',
  apoyo_familiar: 'Apoyo familiar en la medicación',
  diagnostico: 'Diagnóstico',
  sexo: 'Sexo',
}

/** Códigos del Anexo n.° 04 que llegan como valor de una variable categórica. */
const VALOR_LEGIBLE = {
  si: 'Sí', no: 'No', solo: 'Vive solo', acompanado: 'Acompañado',
  sin_estudios: 'Sin estudios', primaria: 'Primaria', secundaria: 'Secundaria', superior: 'Superior',
  hta: 'HTA', dm2: 'DM2', ambas: 'HTA + DM2', M: 'Masculino', F: 'Femenino',
}

/**
 * Predicción del modelo para un paciente (RF04).
 *
 * Se distingue de forma deliberada del bloque de riesgo observado: aquella
 * resume lo que el paciente hizo, esta anticipa lo que hará. Mezclarlas
 * confundiría al médico sobre qué está mirando.
 */
export default function PrediccionRiesgo({ prediccion }) {
  const { probabilidad, nivel, factores, modelo, variables_imputadas: imputadas } = prediccion
  const porcentaje = Math.round(probabilidad * 100)
  const mayorImportancia = Math.max(...factores.map((f) => f.importancia), 0.0001)

  return (
    <section className={`alerta alerta--${nivel}`} aria-live="polite">
      <div className="alerta__cabecera">
        <span className="alerta__etiqueta">Riesgo predicho por el modelo</span>
        <span className={`distintivo distintivo--${nivel}`}>{etiquetaRiesgo(nivel)}</span>
      </div>

      <div className="prediccion__cifra">
        <span className="prediccion__valor">{porcentaje} %</span>
        <span className="prediccion__leyenda">
          de probabilidad de incumplimiento antes del próximo control
        </span>
      </div>

      {!modelo.datos_reales && (
        <p className="prediccion__procedencia">
          Modelo entrenado con un conjunto de demostración simulado. El resultado
          ilustra el funcionamiento del componente; no es un hallazgo del estudio.
        </p>
      )}

      <div className="prediccion__factores">
        <h4>Factores que más pesan en el modelo</h4>
        <ul className="factores">
          {factores.map((factor) => (
            <li className="factor" key={factor.variable}>
              <span className="factor__nombre">
                {NOMBRE_VARIABLE[factor.variable] ?? factor.variable}
              </span>
              <span className="factor__barra" aria-hidden="true">
                <span
                  className="factor__relleno"
                  style={{ width: `${Math.round((factor.importancia / mayorImportancia) * 100)}%` }}
                />
              </span>
              <span className="factor__valor">
                {factor.valor_paciente === null ? 'sin dato' : (VALOR_LEGIBLE[factor.valor_paciente] ?? factor.valor_paciente)}
              </span>
            </li>
          ))}
        </ul>
        <p className="alerta__pie">
          {prediccion.alcance_factores} La atribución individual con SHAP (RF06)
          se incorpora en el Sprint&nbsp;3.
        </p>
      </div>

      {imputadas.length > 0 && (
        <p className="alerta__pie">
          Se estimaron {imputadas.length} variable(s) ausente(s) en la ficha:{' '}
          {imputadas.map((v) => NOMBRE_VARIABLE[v] ?? v).join(', ')}.
        </p>
      )}

      <p className="alerta__pie">
        {prediccion.aviso} Modelo: {modelo.algoritmo}, entrenado el{' '}
        {modelo.entrenado_el}.
      </p>
    </section>
  )
}
