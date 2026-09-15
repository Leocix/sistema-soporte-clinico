import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { mensajeDeError, servicioReportes } from '../services/api'
import { etiquetaComorbilidad, etiquetaDiagnostico } from '../services/etiquetas'
import { etiquetaRiesgo } from '../services/riesgo'

/**
 * Reporte general de los pacientes a cargo del médico (RF07).
 *
 * Todas las cifras las calcula el API (`/api/reportes/general`); esta página
 * solo las presenta. Así el panel y el CSV exportado nunca dicen cosas
 * distintas.
 */

const PERIODOS = [
  ['', 'Todo el historial'],
  ['30', 'Últimos 30 días'],
  ['90', 'Últimos 90 días'],
]

const NIVELES = ['alto', 'medio', 'bajo', 'sin_datos']

const porcentaje = (valor) => (valor === null || valor === undefined ? '—' : `${valor} %`)

/** Barras horizontales con su valor escrito al lado: se leen sin leyenda. */
function Barras({ filas, total, claseDe }) {
  if (filas.length === 0) return <p className="reporte__vacio">Sin datos en el periodo.</p>
  const maximo = Math.max(total ?? 0, ...filas.map((f) => f.valor), 1)
  return (
    <ul className="barras">
      {filas.map((fila) => (
        <li key={fila.clave} className="barras__fila" title={`${fila.etiqueta}: ${fila.valor}`}>
          <span className="barras__etiqueta">{fila.etiqueta}</span>
          <span className="barras__pista">
            <span
              className={`barras__relleno ${claseDe ? claseDe(fila.clave) : ''}`}
              style={{ width: `${(100 * fila.valor) / maximo}%` }}
            />
          </span>
          <span className="barras__valor">{fila.valor}</span>
        </li>
      ))}
    </ul>
  )
}

export default function Reportes() {
  const [dias, setDias] = useState('')
  const [reporte, setReporte] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [exportando, setExportando] = useState(false)
  const [error, setError] = useState(null)

  const cargar = useCallback(async () => {
    setCargando(true)
    setError(null)
    try {
      const { data } = await servicioReportes.general(dias || undefined)
      setReporte(data)
    } catch (fallo) {
      setError(mensajeDeError(fallo))
    } finally {
      setCargando(false)
    }
  }, [dias])

  useEffect(() => {
    cargar()
  }, [cargar])

  const exportar = async () => {
    setExportando(true)
    try {
      const { data } = await servicioReportes.exportar(dias || undefined)
      const url = URL.createObjectURL(new Blob([data], { type: 'text/csv;charset=utf-8' }))
      const enlace = document.createElement('a')
      enlace.href = url
      enlace.download = `reporte_pacientes_${new Date().toISOString().slice(0, 10)}.csv`
      enlace.click()
      URL.revokeObjectURL(url)
    } catch (fallo) {
      setError(mensajeDeError(fallo))
    } finally {
      setExportando(false)
    }
  }

  const ind = reporte?.indicadores

  return (
    <>
      <div className="seccion__cabecera">
        <div>
          <h2>Reportes generales</h2>
          <p className="seccion__descripcion">
            Situación de todos los pacientes activos a su cargo.
          </p>
        </div>
        <div className="filtros">
          <label className="campo campo--linea">
            <span>Periodo</span>
            <select value={dias} onChange={(e) => setDias(e.target.value)}>
              {PERIODOS.map(([valor, texto]) => (
                <option key={valor} value={valor}>{texto}</option>
              ))}
            </select>
          </label>
          <button
            type="button"
            className="boton boton--primario"
            onClick={exportar}
            disabled={exportando || !reporte}
          >
            {exportando ? 'Exportando…' : 'Exportar CSV'}
          </button>
        </div>
      </div>

      {error && <p className="mensaje mensaje--error" role="alert">{error}</p>}

      {cargando && !reporte ? (
        <div className="cargando" role="status">
          <span className="girador" aria-hidden="true" />
          <p>Preparando el reporte…</p>
        </div>
      ) : reporte && (
        <>
          <section className="indicadores" aria-label="Indicadores generales">
            <div className="indicador">
              <span className="indicador__valor">{ind.pacientes_activos}</span>
              <span className="indicador__etiqueta">
                Pacientes activos · {ind.pacientes_con_tomas} con tomas registradas
              </span>
            </div>
            <div className="indicador">
              <span className="indicador__valor">{porcentaje(ind.adherencia_promedio)}</span>
              <span className="indicador__etiqueta">Adherencia promedio</span>
            </div>
            <div className="indicador">
              <span className="indicador__valor">{ind.tomas_registradas}</span>
              <span className="indicador__etiqueta">
                Tomas registradas · {ind.tomas_cumplidas} cumplidas, {ind.tomas_omitidas} omitidas
              </span>
            </div>
            <div className="indicador">
              <span className="indicador__valor">{porcentaje(ind.porcentaje_corroboradas)}</span>
              <span className="indicador__etiqueta">Tomas cumplidas corroboradas por un familiar</span>
            </div>
            <div className={`indicador ${ind.pacientes_riesgo_alto ? 'indicador--alerta' : ''}`}>
              <span className="indicador__valor">{ind.pacientes_riesgo_alto}</span>
              <span className="indicador__etiqueta">Pacientes en riesgo alto observado</span>
            </div>
          </section>

          <section className="reporte__rejilla">
            <article className="tarjeta">
              <h3 className="tarjeta__titulo">Riesgo observado</h3>
              <Barras
                filas={NIVELES.map((n) => ({
                  clave: n, etiqueta: etiquetaRiesgo(n), valor: reporte.riesgo_observado[n],
                }))}
                total={ind.pacientes_activos}
                claseDe={(n) => `barras__relleno--${n}`}
              />
            </article>

            <article className="tarjeta">
              <h3 className="tarjeta__titulo">Riesgo predicho por el modelo</h3>
              {reporte.riesgo_predicho ? (
                <Barras
                  filas={['alto', 'medio', 'bajo'].map((n) => ({
                    clave: n, etiqueta: etiquetaRiesgo(n), valor: reporte.riesgo_predicho[n],
                  }))}
                  total={ind.pacientes_activos}
                  claseDe={(n) => `barras__relleno--${n}`}
                />
              ) : (
                <p className="reporte__vacio">El modelo no está disponible en este momento.</p>
              )}
            </article>

            <article className="tarjeta">
              <h3 className="tarjeta__titulo">Pacientes por diagnóstico</h3>
              <Barras
                filas={Object.entries(reporte.por_diagnostico).map(([d, n]) => ({
                  clave: d, etiqueta: etiquetaDiagnostico(d), valor: n,
                }))}
                total={ind.pacientes_activos}
              />
            </article>

            <article className="tarjeta">
              <h3 className="tarjeta__titulo">Comorbilidades más frecuentes</h3>
              <Barras
                filas={reporte.comorbilidades_frecuentes.map((c) => ({
                  clave: c.comorbilidad, etiqueta: etiquetaComorbilidad(c.comorbilidad), valor: c.pacientes,
                }))}
                total={ind.pacientes_activos}
              />
            </article>

            <article className="tarjeta">
              <h3 className="tarjeta__titulo">Motivos de omisión</h3>
              <Barras
                filas={reporte.motivos_omision.map((m) => ({
                  clave: m.motivo, etiqueta: m.motivo, valor: m.veces,
                }))}
              />
            </article>
          </section>

          <section className="tarjeta">
            <h3 className="tarjeta__titulo">Pacientes, de mayor a menor riesgo</h3>
            <div className="tabla__contenedor">
              <table className="tabla">
                <thead>
                  <tr>
                    <th scope="col">Código</th>
                    <th scope="col">Paciente</th>
                    <th scope="col">Diagnóstico</th>
                    <th scope="col" className="num">Fármacos</th>
                    <th scope="col" className="num">Adherencia</th>
                    <th scope="col" className="num">Omisiones seguidas</th>
                    <th scope="col">Riesgo observado</th>
                    <th scope="col">Riesgo predicho</th>
                  </tr>
                </thead>
                <tbody>
                  {reporte.pacientes.map((p) => (
                    <tr key={p.id_paciente}>
                      <th scope="row">
                        <Link className="enlace" to={`/panel/pacientes/${p.id_paciente}`}>
                          {p.codigo_anonimizado}
                        </Link>
                      </th>
                      <td>{p.nombre}</td>
                      <td>{etiquetaDiagnostico(p.diagnostico)}</td>
                      <td className="num">{p.numero_farmacos}</td>
                      <td className="num">{porcentaje(p.tasa_adherencia)}</td>
                      <td className="num">{p.omisiones_consecutivas}</td>
                      <td>
                        <span className={`distintivo distintivo--${p.riesgo_observado}`}>
                          {etiquetaRiesgo(p.riesgo_observado)}
                        </span>
                      </td>
                      <td>
                        {p.riesgo_predicho ? (
                          <span className={`distintivo distintivo--${p.riesgo_predicho}`}>
                            {etiquetaRiesgo(p.riesgo_predicho)} · {Math.round(p.probabilidad_predicha * 100)} %
                          </span>
                        ) : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <details className="tarjeta reporte__metodo">
            <summary>¿Cómo se calculan estas cifras?</summary>
            <ul>
              <li>
                <strong>Adherencia de un paciente:</strong> tomas cumplidas (a tiempo o con
                retraso) entre tomas con desenlace (cumplidas + omitidas). Las pospuestas no
                cuentan porque aún no se sabe si se tomaron.
              </li>
              <li>
                <strong>Adherencia promedio:</strong> media de la adherencia de los pacientes que
                tienen tomas registradas; cada paciente pesa lo mismo.
              </li>
              <li>
                <strong>Riesgo observado:</strong> alto si la adherencia es menor al 60 % o hay 3
                o más omisiones seguidas; medio si es menor al 80 % o hay 2 seguidas; bajo en
                los demás casos. Resume lo que el paciente ya hizo.
              </li>
              <li>
                <strong>Riesgo predicho:</strong> probabilidad que calcula el modelo a partir de la
                ficha del paciente (alto desde el 70 %, medio desde el 40 %).
                Anticipa lo que puede ocurrir antes del próximo control.
              </li>
              <li>
                <strong>Corroboradas:</strong> tomas cumplidas que un familiar confirmó desde su
                propia aplicación, sobre el total de tomas cumplidas.
              </li>
            </ul>
          </details>
        </>
      )}
    </>
  )
}
