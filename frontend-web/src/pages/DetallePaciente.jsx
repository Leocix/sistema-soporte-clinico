import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import AlertaRiesgo from '../components/AlertaRiesgo'
import { mensajeDeError, servicioAdherencia, servicioPacientes } from '../services/api'
import { etiquetaAdherenciaBasal } from '../services/riesgo'
import {
  etiquetaAseguramiento,
  etiquetaDiagnostico,
  etiquetaNivelSocioeconomico,
  etiquetaSexo,
  etiquetaZona,
} from '../services/etiquetas'

/** Ficha clinica individual: variables del Anexo n.o 04 y traza de tomas. */

const ESTADOS = {
  tomada: { texto: 'Tomada', clase: 'bajo' },
  tomada_tarde: { texto: 'Tomada con retraso', clase: 'medio' },
  omitida: { texto: 'Omitida', clase: 'alto' },
  pospuesta: { texto: 'Pospuesta', clase: 'sin_datos' },
}

const DIMENSIONES = [
  {
    titulo: 'Paciente',
    campos: [
      ['Edad', (p) => `${p.edad} años`],
      ['Sexo', (p) => etiquetaSexo(p.sexo)],
    ],
  },
  {
    titulo: 'Enfermedad',
    campos: [
      ['Diagnóstico', (p) => etiquetaDiagnostico(p.diagnostico)],
      ['Tiempo de enfermedad', (p) => (p.tiempo_enfermedad_anios ? `${p.tiempo_enfermedad_anios} años` : '—')],
      ['Comorbilidades', (p) => p.comorbilidades],
    ],
  },
  {
    titulo: 'Terapia',
    campos: [
      ['Fármacos prescritos', (p) => p.numero_farmacos],
      ['Tomas por día', (p) => p.tomas_dia],
      ['Carga terapéutica', (p) => p.numero_farmacos * p.tomas_dia],
    ],
  },
  {
    titulo: 'Socioeconómica',
    campos: [
      ['Nivel socioeconómico', (p) => etiquetaNivelSocioeconomico(p.nivel_socioeconomico)],
      ['Aseguramiento', (p) => etiquetaAseguramiento(p.aseguramiento)],
      ['Zona de residencia', (p) => etiquetaZona(p.zona_residencia)],
    ],
  },
  {
    titulo: 'Sistema de salud',
    campos: [
      ['Controles programados (6 m)', (p) => p.controles_programados_6m],
      ['Controles perdidos (6 m)', (p) => p.controles_perdidos_6m],
    ],
  },
  {
    titulo: 'Línea base de adherencia',
    campos: [
      ['Puntaje Morisky-Green', (p) => (p.puntaje_morisky ?? '—')],
      ['Clasificación', (p) => etiquetaAdherenciaBasal(p)],
    ],
  },
]

function formatearFecha(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('es-PE', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

export default function DetallePaciente() {
  const { id } = useParams()
  const [paciente, setPaciente] = useState(null)
  const [resumen, setResumen] = useState(null)
  const [registros, setRegistros] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  const cargar = useCallback(async () => {
    setCargando(true)
    setError(null)
    try {
      // El resumen y el historial pueden fallar de forma independiente sin
      // impedir que se muestre la ficha del paciente.
      const [fichaRes, resumenRes, registrosRes] = await Promise.allSettled([
        servicioPacientes.obtener(id),
        servicioAdherencia.resumen(id),
        servicioAdherencia.registros(id, { limite: 60 }),
      ])

      if (fichaRes.status === 'rejected') throw fichaRes.reason
      setPaciente(fichaRes.value.data)
      setResumen(resumenRes.status === 'fulfilled' ? resumenRes.value.data : null)
      setRegistros(registrosRes.status === 'fulfilled' ? registrosRes.value.data : [])
    } catch (fallo) {
      setError(mensajeDeError(fallo))
    } finally {
      setCargando(false)
    }
  }, [id])

  useEffect(() => {
    cargar()
  }, [cargar])

  if (cargando) {
    return (
      <div className="cargando" role="status">
        <span className="girador" aria-hidden="true" />
        <p>Cargando la ficha clínica…</p>
      </div>
    )
  }

  if (error) {
    return (
      <>
        <p className="mensaje mensaje--error" role="alert">{error}</p>
        <Link className="enlace" to="/panel">← Volver al panel</Link>
      </>
    )
  }

  return (
    <>
      <div className="seccion__cabecera">
        <div>
          <Link className="enlace enlace--volver" to="/panel">← Panel de auditoría</Link>
          <h2>Ficha del paciente {paciente.codigo_anonimizado}</h2>
          <p className="seccion__descripcion">
            {paciente.edad} años · <span>{etiquetaDiagnostico(paciente.diagnostico)}</span> ·{' '}
            {paciente.numero_farmacos} fármacos
            {!paciente.activo && <span className="distintivo distintivo--sin_datos"> Dado de baja</span>}
          </p>
        </div>
      </div>

      <div className="detalle">
        <div className="detalle__principal">
          <AlertaRiesgo resumen={resumen} />

          {resumen && resumen.total_eventos > 0 && (
            <section className="indicadores indicadores--compacto">
              <article className="indicador">
                <span className="indicador__valor">{resumen.tasa_adherencia} %</span>
                <span className="indicador__etiqueta">Cumplimiento</span>
              </article>
              <article className="indicador">
                <span className="indicador__valor">{resumen.cumplidos}/{resumen.total_eventos}</span>
                <span className="indicador__etiqueta">Tomas cumplidas</span>
              </article>
              <article className="indicador">
                <span className="indicador__valor">
                  {resumen.retraso_promedio_min === null ? '—' : `${resumen.retraso_promedio_min} min`}
                </span>
                <span className="indicador__etiqueta">Retraso promedio</span>
              </article>
              <article className="indicador">
                <span className="indicador__valor">{resumen.omisiones_consecutivas}</span>
                <span className="indicador__etiqueta">Omisiones consecutivas</span>
              </article>
            </section>
          )}

          <section className="tarjeta">
            <h3>Historial de tomas registradas</h3>
            <p className="seccion__descripcion">
              Traza digital enviada desde la aplicación móvil del paciente (RF03).
            </p>

            {registros.length === 0 ? (
              <p className="vacio">
                El paciente aún no ha registrado tomas. El seguimiento comienza
                cuando instala la aplicación móvil y confirma su primera dosis.
              </p>
            ) : (
              <div className="tabla__contenedor tabla__contenedor--alto">
                <table className="tabla">
                  <thead>
                    <tr>
                      <th scope="col">Medicamento</th>
                      <th scope="col">Horario prescrito</th>
                      <th scope="col">Hora registrada</th>
                      <th scope="col" className="num">Retraso</th>
                      <th scope="col">Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {registros.map((registro) => {
                      const estado = ESTADOS[registro.estado] ?? ESTADOS.pospuesta
                      return (
                        <tr key={registro.id_registro}>
                          <th scope="row">{registro.medicamento}</th>
                          <td>{formatearFecha(registro.fecha_hora_programada)}</td>
                          <td>{formatearFecha(registro.fecha_hora_registro)}</td>
                          <td className="num">
                            {registro.minutos_de_retraso === null
                              ? '—'
                              : `${registro.minutos_de_retraso} min`}
                          </td>
                          <td>
                            <span className={`distintivo distintivo--${estado.clase}`}>
                              {estado.texto}
                            </span>
                            {registro.motivo_omision && (
                              <span className="nota nota--inline"> {registro.motivo_omision}</span>
                            )}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </div>

        <aside className="detalle__lateral">
          <section className="tarjeta">
            <h3>Variables del Anexo n.° 04</h3>
            <p className="seccion__descripcion">
              Agrupadas por dimensión del modelo de adherencia de la OMS.
            </p>

            {DIMENSIONES.map((dimension) => (
              <div className="dimension" key={dimension.titulo}>
                <h4 className="dimension__titulo">{dimension.titulo}</h4>
                <dl className="lista-datos">
                  {dimension.campos.map(([etiqueta, valor]) => (
                    <div className="lista-datos__fila" key={etiqueta}>
                      <dt>{etiqueta}</dt>
                      <dd>{valor(paciente)}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            ))}
          </section>
        </aside>
      </div>
    </>
  )
}
