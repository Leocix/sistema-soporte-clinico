import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import FormularioPaciente from '../components/FormularioPaciente'
import { DistintivoRiesgo } from '../components/AlertaRiesgo'
import { mensajeDeError, servicioAdherencia, servicioPacientes } from '../services/api'
import { NIVELES, clasificarRiesgo, etiquetaAdherenciaBasal } from '../services/riesgo'
import { etiquetaDiagnostico } from '../services/etiquetas'

/** Panel de auditoria de adherencia (RF07, version del Sprint 2). */

const TAMANO_PAGINA = 20
const ORDEN_RIESGO = { [NIVELES.ALTO]: 0, [NIVELES.MEDIO]: 1, [NIVELES.BAJO]: 2, [NIVELES.SIN_DATOS]: 3 }

export default function Dashboard() {
  const [pagina, setPagina] = useState(1)
  const [diagnostico, setDiagnostico] = useState('')
  const [busqueda, setBusqueda] = useState('')

  const [datos, setDatos] = useState({ total: 0, items: [] })
  const [resumenes, setResumenes] = useState({})
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  // El sistema confirma lo que acaba de ocurrir: sin esta linea, el medico da
  // de alta a un paciente y la pantalla vuelve al listado sin decir nada.
  const [confirmacion, setConfirmacion] = useState(null)
  const [mostrarAlta, setMostrarAlta] = useState(false)

  const cargar = useCallback(async () => {
    setCargando(true)
    setError(null)
    try {
      const { data } = await servicioPacientes.listar({
        pagina,
        tamano: TAMANO_PAGINA,
        ...(diagnostico ? { diagnostico } : {}),
        ...(busqueda ? { busqueda } : {}),
      })
      setDatos(data)

      // El API aun no ofrece un resumen masivo, asi que se piden en paralelo
      // los de la pagina visible. Al construir el panel definitivo (RF07)
      // conviene sustituir esto por un unico endpoint agregado.
      const respuestas = await Promise.allSettled(
        data.items.map((p) => servicioAdherencia.resumen(p.id_paciente)),
      )
      const mapa = {}
      data.items.forEach((paciente, indice) => {
        const r = respuestas[indice]
        if (r.status === 'fulfilled') mapa[paciente.id_paciente] = r.value.data
      })
      setResumenes(mapa)
    } catch (fallo) {
      setError(mensajeDeError(fallo))
    } finally {
      setCargando(false)
    }
  }, [pagina, diagnostico, busqueda])

  useEffect(() => {
    cargar()
  }, [cargar])

  const filas = useMemo(() => {
    // Los pacientes de mayor riesgo encabezan la lista: es el orden util para
    // la consulta, no el alfabetico.
    return [...datos.items].sort((a, b) => {
      const ra = ORDEN_RIESGO[clasificarRiesgo(resumenes[a.id_paciente])]
      const rb = ORDEN_RIESGO[clasificarRiesgo(resumenes[b.id_paciente])]
      if (ra !== rb) return ra - rb
      return a.codigo_anonimizado.localeCompare(b.codigo_anonimizado)
    })
  }, [datos.items, resumenes])

  const indicadores = useMemo(() => {
    const conResumen = datos.items
      .map((p) => resumenes[p.id_paciente])
      .filter((r) => r && r.total_eventos > 0)

    const enRiesgo = datos.items.filter(
      (p) => clasificarRiesgo(resumenes[p.id_paciente]) === NIVELES.ALTO,
    ).length

    const promedio = conResumen.length
      ? conResumen.reduce((suma, r) => suma + r.tasa_adherencia, 0) / conResumen.length
      : null

    const deficienteBasal = datos.items.filter((p) => p.incumplimiento_basal === true).length

    return {
      total: datos.total,
      enRiesgo,
      promedio: promedio === null ? null : Math.round(promedio * 10) / 10,
      deficienteBasal,
      sinRegistros: datos.items.length - conResumen.length,
    }
  }, [datos, resumenes])

  const totalPaginas = Math.max(1, Math.ceil(datos.total / TAMANO_PAGINA))

  return (
    <>
      <div className="seccion__cabecera">
        <div>
          <h2>Panel de auditoría de adherencia</h2>
          <p className="seccion__descripcion">
            Pacientes polimedicados a su cargo, ordenados por prioridad clínica.
          </p>
        </div>
        <button type="button" className="boton boton--primario" onClick={() => setMostrarAlta(true)}>
          Registrar paciente
        </button>
      </div>

      <section className="indicadores" aria-label="Indicadores generales">
        <article className="indicador">
          <span className="indicador__valor">{indicadores.total}</span>
          <span className="indicador__etiqueta">Pacientes en seguimiento</span>
        </article>
        <article className="indicador indicador--alerta">
          <span className="indicador__valor">{indicadores.enRiesgo}</span>
          <span className="indicador__etiqueta">Con riesgo observado alto</span>
        </article>
        <article className="indicador">
          <span className="indicador__valor">
            {indicadores.promedio === null ? '—' : `${indicadores.promedio} %`}
          </span>
          <span className="indicador__etiqueta">Cumplimiento promedio registrado</span>
        </article>
        <article className="indicador">
          <span className="indicador__valor">{indicadores.deficienteBasal}</span>
          <span className="indicador__etiqueta">Adherencia basal deficiente (Morisky)</span>
        </article>
      </section>

      <section className="tarjeta">
        <div className="filtros">
          <label className="campo campo--linea">
            <span>Buscar paciente</span>
            <input
              value={busqueda}
              onChange={(e) => { setBusqueda(e.target.value); setPagina(1) }}
              placeholder="Nombre o P-001"
              maxLength={60}
            />
          </label>

          <label className="campo campo--linea">
            <span>Diagnóstico</span>
            <select
              value={diagnostico}
              onChange={(e) => { setDiagnostico(e.target.value); setPagina(1) }}
            >
              <option value="">Todos</option>
              <option value="hta">Hipertensión</option>
              <option value="dm2">Diabetes tipo 2</option>
              <option value="ambas">Ambas</option>
            </select>
          </label>
        </div>

        {confirmacion && (
        <p className="mensaje mensaje--exito" role="status">{confirmacion}</p>
      )}

      {error && <p className="mensaje mensaje--error" role="alert">{error}</p>}

        {cargando ? (
          <div className="cargando" role="status">
            <span className="girador" aria-hidden="true" />
            <p>Cargando pacientes…</p>
          </div>
        ) : filas.length === 0 ? (
          <p className="vacio">
            No hay pacientes que coincidan. Use «Registrar paciente» para dar de
            alta el primero.
          </p>
        ) : (
          <div className="tabla__contenedor">
            <table className="tabla">
              <caption className="oculto">Pacientes polimedicados en seguimiento</caption>
              <thead>
                <tr>
                  <th scope="col">Paciente</th>
                  <th scope="col">Edad</th>
                  <th scope="col">Diagnóstico</th>
                  <th scope="col" className="num">Fármacos</th>
                  <th scope="col" className="num">Tomas/día</th>
                  <th scope="col" className="num">Cumplimiento</th>
                  <th scope="col">Riesgo observado</th>
                  <th scope="col">Adherencia basal</th>
                  <th scope="col"><span className="oculto">Acciones</span></th>
                </tr>
              </thead>
              <tbody>
                {filas.map((paciente) => {
                  const resumen = resumenes[paciente.id_paciente]
                  return (
                    <tr key={paciente.id_paciente}>
                      <th scope="row">
                        <span className="paciente__nombre">
                          {paciente.nombres} {paciente.apellidos}
                        </span>
                        <span className="paciente__codigo">
                          {paciente.codigo_anonimizado}
                        </span>
                      </th>
                      <td>{paciente.edad}</td>
                      <td>{etiquetaDiagnostico(paciente.diagnostico)}</td>
                      <td className="num">{paciente.numero_farmacos}</td>
                      <td className="num">{paciente.tomas_dia}</td>
                      <td className="num">
                        {resumen && resumen.total_eventos > 0 ? `${resumen.tasa_adherencia} %` : '—'}
                      </td>
                      <td><DistintivoRiesgo resumen={resumen} /></td>
                      <td>{etiquetaAdherenciaBasal(paciente)}</td>
                      <td>
                        <Link className="enlace" to={`/panel/pacientes/${paciente.id_paciente}`}>
                          Ver ficha
                        </Link>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}

        {indicadores.sinRegistros > 0 && !cargando && (
          <p className="nota">
            {indicadores.sinRegistros} paciente(s) de esta página aún no
            registran tomas desde la aplicación móvil.
          </p>
        )}

        {totalPaginas > 1 && (
          <nav className="paginacion" aria-label="Paginación">
            <button type="button" className="boton boton--sutil"
              disabled={pagina <= 1} onClick={() => setPagina((p) => p - 1)}>
              Anterior
            </button>
            <span>Página {pagina} de {totalPaginas}</span>
            <button type="button" className="boton boton--sutil"
              disabled={pagina >= totalPaginas} onClick={() => setPagina((p) => p + 1)}>
              Siguiente
            </button>
          </nav>
        )}
      </section>

      {mostrarAlta && (
        <FormularioPaciente
          alCancelar={() => setMostrarAlta(false)}
          alGuardar={(nuevo) => {
            setMostrarAlta(false)
            setPagina(1)
            setConfirmacion(
              `Paciente ${nuevo.codigo_anonimizado} registrado. Genere su acceso móvil desde la ficha.`,
            )
            cargar()
          }}
        />
      )}
    </>
  )
}
