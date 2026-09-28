import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import AccesoMovil from '../components/AccesoMovil'
import AlertaRiesgo from '../components/AlertaRiesgo'
import FormularioPaciente from '../components/FormularioPaciente'
import PrediccionRiesgo from '../components/PrediccionRiesgo'
import {
  mensajeDeError,
  servicioAdherencia,
  servicioPacientes,
  servicioPrediccion,
} from '../services/api'
import { etiquetaAdherenciaBasal } from '../services/riesgo'
import {
  etiquetaConvivencia,
  etiquetaDiagnostico,
  etiquetaNivelEducativo,
  etiquetaSexo,
  etiquetaSiNo,
  listaComorbilidades,
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
    titulo: 'Contacto',
    campos: [
      ['Documento', (p) => p.documento_identidad || '—'],
      ['Teléfono', (p) => p.telefono || '—'],
      ['Correo', (p) => p.correo || '—'],
    ],
  },
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
      ['Comorbilidades', (p) => `${p.comorbilidades} · ${listaComorbilidades(p.lista_comorbilidades)}`],
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
    titulo: 'Contexto social',
    campos: [
      ['Nivel educativo', (p) => etiquetaNivelEducativo(p.nivel_educativo)],
      ['Convivencia', (p) => etiquetaConvivencia(p.convivencia)],
      ['Apoyo familiar en la medicación', (p) => etiquetaSiNo(p.apoyo_familiar)],
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
  const [prediccion, setPrediccion] = useState(null)
  const [editando, setEditando] = useState(false)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const [confirmacion, setConfirmacion] = useState(null)

  const cargar = useCallback(async () => {
    setCargando(true)
    setError(null)
    try {
      // El resumen y el historial pueden fallar de forma independiente sin
      // impedir que se muestre la ficha del paciente.
      const [fichaRes, resumenRes, registrosRes, prediccionRes] =
        await Promise.allSettled([
          servicioPacientes.obtener(id),
          servicioAdherencia.resumen(id),
          servicioAdherencia.registros(id, { limite: 60 }),
          servicioPrediccion.riesgo(id),
        ])

      if (fichaRes.status === 'rejected') throw fichaRes.reason
      setPaciente(fichaRes.value.data)
      setResumen(resumenRes.status === 'fulfilled' ? resumenRes.value.data : null)
      setRegistros(registrosRes.status === 'fulfilled' ? registrosRes.value.data : [])
      // Si el modelo no está disponible, la ficha se muestra igual: el resto
      // de la consulta clínica no depende del componente inteligente.
      setPrediccion(
        prediccionRes.status === 'fulfilled' ? prediccionRes.value.data : null,
      )
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
      {confirmacion && (
        <p className="mensaje mensaje--exito" role="status">{confirmacion}</p>
      )}

      <div className="seccion__cabecera">
        <div>
          <Link className="enlace enlace--volver" to="/panel">← Panel de auditoría</Link>
          <h2>{paciente.nombres} {paciente.apellidos}</h2>
          <p className="seccion__descripcion">
            <span className="paciente__codigo paciente__codigo--suelto">
              {paciente.codigo_anonimizado}
            </span>
            {paciente.edad} años · <span>{etiquetaDiagnostico(paciente.diagnostico)}</span> ·{' '}
            {paciente.numero_farmacos} fármacos
            {!paciente.activo && <span className="distintivo distintivo--sin_datos"> Dado de baja</span>}
          </p>
        </div>
        <button
          type="button"
          className="boton boton--primario"
          onClick={() => setEditando(true)}
        >
          Editar ficha
        </button>
      </div>

      <div className="detalle">
        <div className="detalle__principal">
          {prediccion && <PrediccionRiesgo prediccion={prediccion} />}
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
              La columna «Testigo» indica si un familiar corroboró la toma (RF09).
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
                      <th scope="col">Testigo</th>
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
                          {/* De donde procede el dato. Una toma corroborada por
                              un familiar tiene dos fuentes; el resto, solo la
                              palabra del paciente (RF09). Es una diferencia de
                              calidad de la evidencia, no un adorno. */}
                          <td>
                            {registro.corroborada ? (
                              <span className="distintivo distintivo--bajo">
                                Familiar
                              </span>
                            ) : (
                              <span className="nota nota--inline">Autorreporte</span>
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
          <AccesoMovil paciente={paciente} alGenerar={cargar} />

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

      {editando && (
        <FormularioPaciente
          paciente={paciente}
          alCancelar={() => setEditando(false)}
          alGuardar={(actualizado) => {
            setEditando(false)
            setPaciente(actualizado)
            setConfirmacion('Ficha actualizada. El riesgo se recalcula con los datos nuevos.')
            // La predicción depende de las variables que se acaban de editar,
            // así que se recalcula en lugar de mostrar la anterior.
            cargar()
          }}
        />
      )}
    </>
  )
}
