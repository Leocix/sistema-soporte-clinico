import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { mensajeDeError, servicioAlertas } from '../services/api'

/**
 * Bandeja de alertas tempranas del medico (RF05).
 *
 * Es la unica pantalla del sistema que interrumpe: pide atencion sobre un
 * paciente concreto. Por eso cada aviso llega con su motivo y su cifra, y con
 * las dos unicas respuestas posibles —actuar o descartar—, ambas con una nota
 * que queda registrada.
 */

const ESTADOS = [
  ['abierta', 'Pendientes'],
  ['atendida', 'Atendidas'],
  ['descartada', 'Descartadas'],
  ['resuelta', 'Resueltas solas'],
]

const CLASE_TIPO = {
  riesgo_predicho: 'alto',
  omisiones_seguidas: 'alto',
  adherencia_baja: 'medio',
}

function fecha(iso) {
  return new Date(iso).toLocaleString('es-PE', {
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

export default function Alertas() {
  const [estado, setEstado] = useState('abierta')
  const [bandeja, setBandeja] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const [confirmacion, setConfirmacion] = useState(null)
  const [abierta, setAbierta] = useState(null)
  const [nota, setNota] = useState('')
  const [enviando, setEnviando] = useState(false)

  const cargar = useCallback(async () => {
    setCargando(true)
    setError(null)
    try {
      const { data } = await servicioAlertas.listar(estado)
      setBandeja(data)
    } catch (fallo) {
      setError(mensajeDeError(fallo))
    } finally {
      setCargando(false)
    }
  }, [estado])

  useEffect(() => {
    cargar()
  }, [cargar])

  const cerrar = async (alerta, accion) => {
    setEnviando(true)
    try {
      await servicioAlertas[accion](alerta.id_alerta, nota.trim() || null)
      setAbierta(null)
      setNota('')
      setConfirmacion(
        accion === 'atender'
          ? `Alerta de ${alerta.codigo_anonimizado} registrada como atendida.`
          : `Alerta de ${alerta.codigo_anonimizado} descartada.`,
      )
      await cargar()
    } catch (fallo) {
      setError(mensajeDeError(fallo))
    } finally {
      setEnviando(false)
    }
  }

  const pendientes = estado === 'abierta'

  return (
    <>
      <div className="seccion__cabecera">
        <div>
          <h2>Alertas tempranas</h2>
          <p className="seccion__descripcion">
            Pacientes que necesitan contacto antes de su próximo control.
            {bandeja && ` ${bandeja.abiertas} pendiente(s).`}
          </p>
        </div>
        <label className="campo campo--linea">
          <span>Ver</span>
          <select value={estado} onChange={(e) => setEstado(e.target.value)}>
            {ESTADOS.map(([valor, texto]) => (
              <option key={valor} value={valor}>{texto}</option>
            ))}
          </select>
        </label>
      </div>

      {confirmacion && (
        <p className="mensaje mensaje--exito" role="status">{confirmacion}</p>
      )}

      {error && <p className="mensaje mensaje--error" role="alert">{error}</p>}

      {bandeja && !bandeja.modelo_disponible && (
        <p className="mensaje mensaje--aviso">
          El modelo predictivo no está disponible: se muestran las alertas basadas en las
          tomas registradas, sin las del riesgo predicho.
        </p>
      )}

      {cargando && !bandeja ? (
        <div className="cargando" role="status">
          <span className="girador" aria-hidden="true" />
          <p>Revisando a sus pacientes…</p>
        </div>
      ) : bandeja?.alertas.length === 0 ? (
        <p className="tarjeta vacio">
          {pendientes
            ? 'Ningún paciente supera hoy los umbrales de riesgo.'
            : 'No hay alertas en este estado.'}
        </p>
      ) : (
        <ul className="alertas">
          {bandeja?.alertas.map((alerta) => (
            <li className={`tarjeta alerta-tarjeta alerta-tarjeta--${CLASE_TIPO[alerta.tipo] ?? 'medio'}`}
                key={alerta.id_alerta}>
              <div className="alerta-tarjeta__cabecera">
                <span className={`distintivo distintivo--${CLASE_TIPO[alerta.tipo] ?? 'medio'}`}>
                  {alerta.tipo_legible}
                </span>
                <Link className="enlace" to={`/panel/pacientes/${alerta.id_paciente}`}>
                  {alerta.codigo_anonimizado} · {alerta.paciente}
                </Link>
                <span className="alerta-tarjeta__fecha">{fecha(alerta.fecha_actualizacion)}</span>
              </div>

              <p className="alerta-tarjeta__motivo">{alerta.motivo}</p>

              {alerta.nota_cierre && (
                <p className="alerta-tarjeta__nota">
                  {alerta.estado === 'resuelta' ? 'Cierre automático: ' : 'Nota: '}
                  {alerta.nota_cierre}
                </p>
              )}

              {pendientes && abierta !== alerta.id_alerta && (
                <div className="alerta-tarjeta__acciones">
                  <button type="button" className="boton boton--primario"
                          onClick={() => { setAbierta(alerta.id_alerta); setNota('') }}>
                    Registrar lo que hice
                  </button>
                </div>
              )}

              {pendientes && abierta === alerta.id_alerta && (
                <div className="alerta-tarjeta__cierre">
                  <label className="campo">
                    <span>¿Qué hizo con este paciente?</span>
                    <textarea
                      id={`nota-${alerta.id_alerta}`} rows={2} maxLength={500} value={nota}
                      onChange={(e) => setNota(e.target.value)}
                      placeholder="Se le llamó y se reforzó la pauta; control adelantado al viernes."
                    />
                  </label>
                  <div className="alerta-tarjeta__acciones">
                    <button type="button" className="boton boton--sutil"
                            onClick={() => setAbierta(null)} disabled={enviando}>
                      Cancelar
                    </button>
                    <button type="button" className="boton boton--sutil"
                            onClick={() => cerrar(alerta, 'descartar')} disabled={enviando}>
                      No aplica
                    </button>
                    <button type="button" className="boton boton--primario"
                            onClick={() => cerrar(alerta, 'atender')} disabled={enviando}>
                      {enviando ? 'Guardando…' : 'Atendida'}
                    </button>
                  </div>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </>
  )
}
