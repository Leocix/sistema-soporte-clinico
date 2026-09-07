import { useState } from 'react'
import { mensajeDeError, servicioPacientes } from '../services/api'

/**
 * Alta y edicion de la ficha de un paciente polimedicado (HU02).
 *
 * El mismo formulario sirve para las dos operaciones: duplicarlo significaria
 * mantener dos copias de las mismas reglas y que una se quedara atras. Los
 * limites replican los del esquema Pydantic del API para que el medico reciba
 * el aviso mientras escribe; la validacion que manda sigue siendo la del
 * backend, que ademas responde con el detalle campo por campo.
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

/** Convierte un valor del formulario al tipo que espera el API. */
function convertir(campo, valor) {
  if (ENTEROS.includes(campo)) return Number.parseInt(valor, 10)
  if (campo === 'tiempo_enfermedad_anios') return Number.parseFloat(valor)
  if (campo === 'incumplimiento_basal') return valor === 'si'
  return valor
}

/** Cuerpo del alta: se omite todo opcional que se dejó sin completar. */
function payloadDeAlta(valores) {
  const payload = {}
  for (const [campo, valor] of Object.entries(valores)) {
    // El API rechaza campos con cadena vacía; un opcional sin completar
    // simplemente no se envía.
    if (valor === '' || valor === null) continue
    payload[campo] = convertir(campo, valor)
  }
  return payload
}

/**
 * Cuerpo de la edición: solo lo que cambió respecto a la ficha original.
 *
 * El API distingue «no enviado» de «enviado como nulo», así que un campo que
 * el médico vacía se manda explícitamente como `null` para borrarlo, mientras
 * que lo que no tocó ni siquiera viaja. Enviar la ficha entera sobrescribiría
 * con valores viejos cualquier cambio hecho entretanto desde otro lugar.
 */
function payloadDeEdicion(valores, iniciales) {
  const payload = {}
  for (const [campo, valor] of Object.entries(valores)) {
    // El código anonimizado no se puede reasignar: es la clave con la que el
    // paciente viaja al conjunto de datos y a los registros de adherencia.
    if (campo === 'codigo_anonimizado') continue
    if (valor === iniciales[campo]) continue
    payload[campo] = valor === '' ? null : convertir(campo, valor)
  }
  return payload
}

/** Rellena el formulario con la ficha que se va a editar. */
function valoresDesdeFicha(paciente) {
  const texto = (v) => (v === null || v === undefined ? '' : String(v))
  return {
    ...VALORES_INICIALES,
    nombres: texto(paciente.nombres),
    apellidos: texto(paciente.apellidos),
    documento_identidad: texto(paciente.documento_identidad),
    telefono: texto(paciente.telefono),
    correo: texto(paciente.correo),
    codigo_anonimizado: texto(paciente.codigo_anonimizado),
    edad: texto(paciente.edad),
    sexo: paciente.sexo,
    diagnostico: paciente.diagnostico,
    nivel_socioeconomico: texto(paciente.nivel_socioeconomico),
    aseguramiento: texto(paciente.aseguramiento),
    zona_residencia: texto(paciente.zona_residencia),
    tiempo_enfermedad_anios: texto(paciente.tiempo_enfermedad_anios),
    comorbilidades: texto(paciente.comorbilidades),
    numero_farmacos: texto(paciente.numero_farmacos),
    tomas_dia: texto(paciente.tomas_dia),
    controles_programados_6m: texto(paciente.controles_programados_6m),
    controles_perdidos_6m: texto(paciente.controles_perdidos_6m),
    puntaje_morisky: texto(paciente.puntaje_morisky),
    incumplimiento_basal:
      paciente.incumplimiento_basal === null || paciente.incumplimiento_basal === undefined
        ? ''
        : paciente.incumplimiento_basal
          ? 'si'
          : 'no',
  }
}

export default function FormularioPaciente({ paciente, alGuardar, alCancelar }) {
  const edicion = Boolean(paciente)
  const [iniciales] = useState(() =>
    edicion ? valoresDesdeFicha(paciente) : VALORES_INICIALES,
  )
  const [valores, setValores] = useState(iniciales)
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
      if (edicion) {
        const cambios = payloadDeEdicion(valores, iniciales)
        if (Object.keys(cambios).length === 0) {
          alCancelar()
          return
        }
        const { data } = await servicioPacientes.actualizar(paciente.id_paciente, cambios)
        alGuardar(data)
      } else {
        const { data } = await servicioPacientes.crear(payloadDeAlta(valores))
        alGuardar(data)
      }
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
          <h2 id="titulo-alta">
            {edicion
              ? `Editar ficha · ${paciente.codigo_anonimizado}`
              : 'Registrar paciente polimedicado'}
          </h2>
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
                  pattern="P-\d{3,6}" disabled={edicion} readOnly={edicion}
                />
                <small>
                  {edicion
                    ? 'No se puede cambiar: es la clave con la que el paciente aparece en el conjunto de datos.'
                    : 'Opcional. Si lo deja vacío, el sistema asigna el correlativo.'}
                </small>
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
              {enviando ? 'Guardando…' : edicion ? 'Guardar cambios' : 'Registrar paciente'}
            </button>
          </footer>
        </form>
      </div>
    </div>
  )
}
