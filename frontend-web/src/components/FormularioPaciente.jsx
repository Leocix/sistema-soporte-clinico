import { useState } from 'react'
import { mensajeDeError, servicioPacientes } from '../services/api'

/**
 * Alta de un paciente polimedicado (HU02).
 *
 * Los limites replican los del esquema Pydantic del API para que el medico
 * reciba el aviso mientras escribe; la validacion que manda sigue siendo la
 * del backend, que ademas responde con el detalle campo por campo.
 */

const VALORES_INICIALES = {
  nombres: '',
  apellidos: '',
  documento_identidad: '',
  telefono: '',
  correo: '',
  codigo_anonimizado: '',
  edad: '',
  sexo: 'M',
  diagnostico: 'hta',
  nivel_socioeconomico: '',
  aseguramiento: '',
  zona_residencia: '',
  tiempo_enfermedad_anios: '',
  comorbilidades: '0',
  numero_farmacos: '',
  tomas_dia: '',
  controles_programados_6m: '0',
  controles_perdidos_6m: '0',
  puntaje_morisky: '',
  incumplimiento_basal: '',
}

const ENTEROS = [
  'edad', 'comorbilidades', 'numero_farmacos', 'tomas_dia',
  'controles_programados_6m', 'controles_perdidos_6m', 'puntaje_morisky',
]

/** Convierte el formulario al cuerpo que espera el API, omitiendo lo vacio. */
function construirPayload(valores) {
  const payload = {}

  for (const [campo, valor] of Object.entries(valores)) {
    // El API rechaza campos con cadena vacia; un opcional sin completar
    // simplemente no se envia.
    if (valor === '' || valor === null) continue

    if (ENTEROS.includes(campo)) payload[campo] = Number.parseInt(valor, 10)
    else if (campo === 'tiempo_enfermedad_anios') payload[campo] = Number.parseFloat(valor)
    else if (campo === 'incumplimiento_basal') payload[campo] = valor === 'si'
    else payload[campo] = valor
  }

  return payload
}

export default function FormularioPaciente({ alGuardar, alCancelar }) {
  const [valores, setValores] = useState(VALORES_INICIALES)
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)

  const cambiar = (evento) => {
    const { name, value } = evento.target
    setValores((previos) => ({ ...previos, [name]: value }))
  }

  const enviar = async (evento) => {
    evento.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      const { data } = await servicioPacientes.crear(construirPayload(valores))
      alGuardar(data)
    } catch (fallo) {
      setError(mensajeDeError(fallo))
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="modal" role="dialog" aria-modal="true" aria-labelledby="titulo-alta">
      <div className="modal__panel">
        <header className="modal__cabecera">
          <h2 id="titulo-alta">Registrar paciente polimedicado</h2>
          <button type="button" className="modal__cerrar" onClick={alCancelar} aria-label="Cerrar">
            ×
          </button>
        </header>

        <form className="formulario" onSubmit={enviar}>
          <p className="formulario__ayuda">
            Variables del Anexo n.°&nbsp;04. Solo se admiten pacientes con
            cinco o más fármacos prescritos (criterio de polimedicación).
          </p>

          <fieldset className="formulario__grupo">
            <legend>Identificación del paciente</legend>
            <div className="rejilla">
              <label className="campo">
                <span>Nombres *</span>
                <input name="nombres" required minLength={2} maxLength={120}
                  value={valores.nombres} onChange={cambiar} placeholder="José Luis" />
              </label>

              <label className="campo">
                <span>Apellidos *</span>
                <input name="apellidos" required minLength={2} maxLength={120}
                  value={valores.apellidos} onChange={cambiar} placeholder="Vásquez Ríos" />
              </label>

              <label className="campo">
                <span>Documento de identidad</span>
                <input name="documento_identidad" maxLength={20}
                  value={valores.documento_identidad} onChange={cambiar} />
              </label>

              <label className="campo">
                <span>Teléfono</span>
                <input name="telefono" type="tel" maxLength={25}
                  value={valores.telefono} onChange={cambiar} placeholder="987654321" />
                <small>Necesario para contactarle ante una alerta de riesgo.</small>
              </label>

              <label className="campo">
                <span>Correo electrónico</span>
                <input name="correo" type="email" maxLength={180}
                  value={valores.correo} onChange={cambiar} />
                <small>Con él se le crea la cuenta de la aplicación móvil.</small>
              </label>

              <label className="campo">
                <span>Código anonimizado</span>
                <input
                  name="codigo_anonimizado" value={valores.codigo_anonimizado}
                  onChange={cambiar} placeholder="Se asigna solo (P-002)"
                  pattern="P-\d{3,6}"
                />
                <small>Opcional. Si lo deja vacío, el sistema asigna el correlativo.</small>
              </label>

            </div>
          </fieldset>

          <fieldset className="formulario__grupo">
            <legend>Datos del paciente</legend>
            <div className="rejilla">
              <label className="campo">
                <span>Edad *</span>
                <input name="edad" type="number" min="18" max="120" required
                  value={valores.edad} onChange={cambiar} />
              </label>

              <label className="campo">
                <span>Sexo *</span>
                <select name="sexo" value={valores.sexo} onChange={cambiar}>
                  <option value="M">Masculino</option>
                  <option value="F">Femenino</option>
                </select>
              </label>
            </div>
          </fieldset>

          <fieldset className="formulario__grupo">
            <legend>Enfermedad</legend>
            <div className="rejilla">
              <label className="campo">
                <span>Diagnóstico *</span>
                <select name="diagnostico" value={valores.diagnostico} onChange={cambiar}>
                  <option value="hta">Hipertensión arterial</option>
                  <option value="dm2">Diabetes mellitus tipo 2</option>
                  <option value="ambas">Ambas</option>
                </select>
              </label>

              <label className="campo">
                <span>Tiempo de enfermedad (años)</span>
                <input name="tiempo_enfermedad_anios" type="number" step="0.5" min="0" max="80"
                  value={valores.tiempo_enfermedad_anios} onChange={cambiar} />
              </label>

              <label className="campo">
                <span>Comorbilidades</span>
                <input name="comorbilidades" type="number" min="0" max="15"
                  value={valores.comorbilidades} onChange={cambiar} />
              </label>
            </div>
          </fieldset>

          <fieldset className="formulario__grupo">
            <legend>Carga terapéutica</legend>
            <div className="rejilla">
              <label className="campo">
                <span>N.° de fármacos prescritos *</span>
                <input name="numero_farmacos" type="number" min="5" max="30" required
                  value={valores.numero_farmacos} onChange={cambiar} />
                <small>Mínimo 5 (criterio de elegibilidad).</small>
              </label>

              <label className="campo">
                <span>Tomas por día *</span>
                <input name="tomas_dia" type="number" min="1" max="20" required
                  value={valores.tomas_dia} onChange={cambiar} />
              </label>
            </div>
          </fieldset>

          <fieldset className="formulario__grupo">
            <legend>Contexto socioeconómico</legend>
            <div className="rejilla">
              <label className="campo">
                <span>Nivel socioeconómico</span>
                <select name="nivel_socioeconomico" value={valores.nivel_socioeconomico} onChange={cambiar}>
                  <option value="">Sin dato</option>
                  <option value="bajo">Bajo</option>
                  <option value="medio">Medio</option>
                  <option value="alto">Alto</option>
                </select>
              </label>

              <label className="campo">
                <span>Aseguramiento</span>
                <select name="aseguramiento" value={valores.aseguramiento} onChange={cambiar}>
                  <option value="">Sin dato</option>
                  <option value="sis">SIS</option>
                  <option value="essalud">EsSalud</option>
                  <option value="ninguno">Ninguno</option>
                </select>
              </label>

              <label className="campo">
                <span>Zona de residencia</span>
                <select name="zona_residencia" value={valores.zona_residencia} onChange={cambiar}>
                  <option value="">Sin dato</option>
                  <option value="urbana">Urbana</option>
                  <option value="rural">Rural</option>
                </select>
              </label>
            </div>
          </fieldset>

          <fieldset className="formulario__grupo">
            <legend>Seguimiento y línea base</legend>
            <div className="rejilla">
              <label className="campo">
                <span>Controles programados (6 meses)</span>
                <input name="controles_programados_6m" type="number" min="0" max="30"
                  value={valores.controles_programados_6m} onChange={cambiar} />
              </label>

              <label className="campo">
                <span>Controles perdidos (6 meses)</span>
                <input name="controles_perdidos_6m" type="number" min="0" max="30"
                  value={valores.controles_perdidos_6m} onChange={cambiar} />
                <small>No puede superar a los programados.</small>
              </label>

              <label className="campo">
                <span>Puntaje Morisky-Green (0–4)</span>
                <input name="puntaje_morisky" type="number" min="0" max="4"
                  value={valores.puntaje_morisky} onChange={cambiar} />
              </label>

              <label className="campo">
                <span>Adherencia basal</span>
                <select name="incumplimiento_basal" value={valores.incumplimiento_basal} onChange={cambiar}>
                  <option value="">No evaluada</option>
                  <option value="no">Adherente</option>
                  <option value="si">Incumplimiento</option>
                </select>
                <small>Según el patrón de respuestas del test, no un umbral automático.</small>
              </label>
            </div>
          </fieldset>

          {error && <p className="mensaje mensaje--error" role="alert">{error}</p>}

          <footer className="formulario__pie">
            <button type="button" className="boton boton--sutil" onClick={alCancelar}>
              Cancelar
            </button>
            <button type="submit" className="boton boton--primario" disabled={enviando}>
              {enviando ? 'Guardando…' : 'Registrar paciente'}
            </button>
          </footer>
        </form>
      </div>
    </div>
  )
}
