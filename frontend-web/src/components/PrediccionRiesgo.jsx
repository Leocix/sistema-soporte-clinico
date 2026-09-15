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

const textoValor = (valor) =>
  valor === null || valor === undefined ? 'sin dato' : (VALOR_LEGIBLE[valor] ?? valor)

/**
 * Predicción del modelo para un paciente (RF04) y su explicación con SHAP (RF06).
 *
 * Se distingue de forma deliberada del bloque de riesgo observado: aquella
 * resume lo que el paciente hizo, esta anticipa lo que hará. Mezclarlas
 * confundiría al médico sobre qué está mirando.
 */
export default function PrediccionRiesgo({ prediccion }) {
  const { probabilidad, nivel, modelo, variables_imputadas: imputadas } = prediccion
  const porcentaje = Math.round(probabilidad * 100)
  const contribuciones = prediccion.contribuciones ?? []
  const valorBase = prediccion.valor_base ?? 0
  const principales = contribuciones.slice(0, 6)
  const mayorAporte = Math.max(...principales.map((c) => Math.abs(c.contribucion)), 0.0001)

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

      {contribuciones.length > 0 && (
        <div className="prediccion__factores">
          <h4>Por qué este paciente tiene este riesgo</h4>
          <p className="shap__lectura">
            Un paciente de referencia tendría {Math.round(valorBase * 100)} %. Cada variable
            de la ficha sube o baja esa cifra hasta llegar a {porcentaje} %.
          </p>
          <ul className="shap" aria-label="Contribución de cada variable al riesgo">
            {principales.map((c) => {
              const ancho = Math.round((Math.abs(c.contribucion) / mayorAporte) * 100)
              const sube = c.contribucion > 0
              return (
                <li className="shap__fila" key={c.variable}>
                  <span className="shap__nombre">
                    {NOMBRE_VARIABLE[c.variable] ?? c.variable}
                    <small>{textoValor(c.valor_paciente)}</small>
                  </span>
                  <span className="shap__eje" aria-hidden="true">
                    <span className="shap__mitad shap__mitad--baja">
                      {!sube && <span className="shap__barra shap__barra--baja" style={{ width: `${ancho}%` }} />}
                    </span>
                    <span className="shap__mitad">
                      {sube && <span className="shap__barra shap__barra--sube" style={{ width: `${ancho}%` }} />}
                    </span>
                  </span>
                  <span className={`shap__valor ${sube ? 'shap__valor--sube' : 'shap__valor--baja'}`}>
                    {sube ? '+' : '−'}{Math.abs(c.contribucion * 100).toFixed(1)} pp
                  </span>
                </li>
              )
            })}
          </ul>
          <p className="alerta__pie">
            Explicación individual con SHAP: <strong>+</strong> aumenta el riesgo, <strong>−</strong> lo
            reduce, en puntos porcentuales (pp). Se muestran las {principales.length} variables con
            más peso de {contribuciones.length}.
          </p>
        </div>
      )}

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
