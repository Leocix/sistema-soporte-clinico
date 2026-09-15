import { useState } from 'react'
import { mensajeDeError, servicioPacientes } from '../services/api'
import { COMORBILIDADES } from '../services/etiquetas'
import { normalizarFicha, validarFicha } from '../services/validacionPaciente'

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
  nivel_educativo: '',
  convivencia: '',
  apoyo_familiar: '',
  tiempo_enfermedad_anios: '',
  lista_comorbilidades: [],
  numero_farmacos: '',
  tomas_dia: '',
  controles_programados_6m: '0',
  controles_perdidos_6m: '0',
  puntaje_morisky: '',
  incumplimiento_basal: '',
}

const ENTEROS = [
  'edad', 'numero_farmacos', 'tomas_dia',
  'controles_programados_6m', 'controles_perdidos_6m', 'puntaje_morisky',
]

/** Convierte un valor del formulario al tipo que espera el API. */
function convertir(campo, valor) {
  if (ENTEROS.includes(campo)) return Number.parseInt(valor, 10)
  if (campo === 'tiempo_enfermedad_anios') return Number.parseFloat(valor)
  if (campo === 'incumplimiento_basal' || campo === 'apoyo_familiar') return valor === 'si'
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
    if (Array.isArray(valor)) {
      if (JSON.stringify(valor) !== JSON.stringify(iniciales[campo])) payload[campo] = valor
      continue
    }
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
    nivel_educativo: texto(paciente.nivel_educativo),
    convivencia: texto(paciente.convivencia),
    apoyo_familiar:
      paciente.apoyo_familiar === null || paciente.apoyo_familiar === undefined
        ? ''
        : paciente.apoyo_familiar ? 'si' : 'no',
    tiempo_enfermedad_anios: texto(paciente.tiempo_enfermedad_anios),
    lista_comorbilidades: paciente.lista_comorbilidades ?? [],
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
  // Un campo se marca «tocado» al salir de él o al intentar guardar. Sin esto,
  // el formulario se pintaría de rojo mientras el médico escribe la primera
  // letra de un campo obligatorio, que es la forma más rápida de que deje de
  // leer los avisos.
  const [tocados, setTocados] = useState({})

  const { errores, avisos } = validarFicha(valores, { edicion })
  const hayErrores = Object.keys(errores).length > 0

  const cambiar = (evento) => {
    const { name, value } = evento.target
    setValores((previos) => ({ ...previos, [name]: value }))
  }

  /** Marca o desmarca una comorbilidad conservando el orden del catálogo. */
  const alternarComorbilidad = (codigo) => {
    setValores((previos) => {
      const marcadas = new Set(previos.lista_comorbilidades)
      if (marcadas.has(codigo)) marcadas.delete(codigo)
      else marcadas.add(codigo)
      return {
        ...previos,
        lista_comorbilidades: COMORBILIDADES.map(([c]) => c).filter((c) => marcadas.has(c)),
      }
    })
  }

  const marcarTocado = (evento) => {
    const { name } = evento.target
    setTocados((previos) => ({ ...previos, [name]: true }))
  }

  /** Clase del contenedor: colorea el campo solo si el médico ya pasó por él. */
  const claseCampo = (campo) =>
    tocados[campo] && errores[campo] ? 'campo campo--error' : 'campo'

  /** Mensaje bajo el campo: el error manda sobre el aviso. */
  const notaCampo = (campo) => {
    if (tocados[campo] && errores[campo]) {
      return <small className="campo__error" role="alert">{errores[campo]}</small>
    }
    if (avisos[campo]) {
      return <small className="campo__aviso">{avisos[campo]}</small>
    }
    return null
  }

  const enviar = async (evento) => {
    evento.preventDefault()

    if (hayErrores) {
      // Se marcan todos como tocados para que los mensajes aparezcan de golpe:
      // si solo se señalara el primero, el médico corregiría uno y volvería a
      // chocar con el siguiente.
      setTocados(Object.fromEntries(Object.keys(errores).map((c) => [c, true])))
      setError(
        `Revise ${Object.keys(errores).length} dato(s) señalado(s) en rojo antes de guardar.`,
      )
      // Tras el repintado: en este mismo ciclo el marcado en rojo todavía no
      // existe en el DOM, así que el foco no encontraría a dónde ir.
      requestAnimationFrame(() => {
        document.querySelector('.campo--error input, .campo--error select')?.focus()
      })
      return
    }

    setError(null)
    setEnviando(true)
    const limpios = normalizarFicha(valores)
    try {
      if (edicion) {
        const cambios = payloadDeEdicion(limpios, iniciales)
        if (Object.keys(cambios).length === 0) {
          alCancelar()
          return
        }
        const { data } = await servicioPacientes.actualizar(paciente.id_paciente, cambios)
        alGuardar(data)
      } else {
        const { data } = await servicioPacientes.crear(payloadDeAlta(limpios))
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

        {/* `noValidate` deja una sola voz validando. Sin él, el navegador
            bloquea el envío con sus propios mensajes —genéricos y en el idioma
            del navegador— antes de que corra esta validación, y el médico ve
            dos sistemas de avisos distintos para el mismo formulario. Los
            atributos `min`, `max` y `required` se conservan: siguen dando las
            flechas de los campos numéricos y el estado a los lectores de
            pantalla. */}
        <form className="formulario" onSubmit={enviar} noValidate>
          <p className="formulario__ayuda">
            Variables del Anexo n.°&nbsp;04. Solo se admiten pacientes con
            cinco o más fármacos prescritos (criterio de polimedicación).
          </p>

          <fieldset className="formulario__grupo">
            <legend>Identificación del paciente</legend>
            <div className="rejilla">
              <label className={claseCampo('nombres')}>
                <span>Nombres *</span>
                <input name="nombres" required minLength={2} maxLength={120}
                  value={valores.nombres} onChange={cambiar} onBlur={marcarTocado} placeholder="José Luis" />
                {notaCampo('nombres')}
              </label>

              <label className={claseCampo('apellidos')}>
                <span>Apellidos *</span>
                <input name="apellidos" required minLength={2} maxLength={120}
                  value={valores.apellidos} onChange={cambiar} onBlur={marcarTocado} placeholder="Vásquez Ríos" />
                {notaCampo('apellidos')}
              </label>

              <label className={claseCampo('documento_identidad')}>
                <span>Documento de identidad</span>
                <input name="documento_identidad" maxLength={20}
                  value={valores.documento_identidad} onChange={cambiar} onBlur={marcarTocado} />
                {notaCampo('documento_identidad')}
              </label>

              <label className={claseCampo('telefono')}>
                <span>Teléfono</span>
                <input name="telefono" type="tel" maxLength={25}
                  value={valores.telefono} onChange={cambiar} onBlur={marcarTocado} placeholder="987654321" />
                <small>Necesario para contactarle ante una alerta de riesgo.</small>
                {notaCampo('telefono')}
              </label>

              <label className={claseCampo('correo')}>
                <span>Correo electrónico</span>
                <input name="correo" type="email" maxLength={180}
                  value={valores.correo} onChange={cambiar} onBlur={marcarTocado} />
                <small>Con él se le crea la cuenta de la aplicación móvil.</small>
                {notaCampo('correo')}
              </label>

              <label className={claseCampo('codigo_anonimizado')}>
                <span>Código anonimizado</span>
                <input
                  name="codigo_anonimizado" value={valores.codigo_anonimizado}
                  onChange={cambiar} onBlur={marcarTocado} placeholder="Se asigna solo (P-002)"
                  pattern="[A-Z]-\d{3,6}" disabled={edicion} readOnly={edicion}
                />
                <small>
                  {edicion
                    ? 'No se puede cambiar: es la clave con la que el paciente aparece en el conjunto de datos.'
                    : 'Opcional. Si lo deja vacío, el sistema asigna el correlativo.'}
                </small>
                {notaCampo('codigo_anonimizado')}
              </label>

            </div>
          </fieldset>

          <fieldset className="formulario__grupo">
            <legend>Datos del paciente</legend>
            <div className="rejilla">
              <label className={claseCampo('edad')}>
                <span>Edad *</span>
                <input name="edad" type="number" min="18" max="120" required
                  value={valores.edad} onChange={cambiar} onBlur={marcarTocado} />
                {notaCampo('edad')}
              </label>

              <label className={claseCampo('sexo')}>
                <span>Sexo *</span>
                <select name="sexo" value={valores.sexo} onChange={cambiar} onBlur={marcarTocado}>
                  <option value="M">Masculino</option>
                  <option value="F">Femenino</option>
                </select>
                {notaCampo('sexo')}
              </label>
            </div>
          </fieldset>

          <fieldset className="formulario__grupo">
            <legend>Enfermedad</legend>
            <div className="rejilla">
              <label className={claseCampo('diagnostico')}>
                <span>Diagnóstico *</span>
                <select name="diagnostico" value={valores.diagnostico} onChange={cambiar} onBlur={marcarTocado}>
                  <option value="hta">Hipertensión arterial</option>
                  <option value="dm2">Diabetes mellitus tipo 2</option>
                  <option value="ambas">Ambas</option>
                </select>
                {notaCampo('diagnostico')}
              </label>

              <label className={claseCampo('tiempo_enfermedad_anios')}>
                <span>Tiempo de enfermedad (años)</span>
                <input name="tiempo_enfermedad_anios" type="number" step="0.5" min="0" max="80"
                  value={valores.tiempo_enfermedad_anios} onChange={cambiar} onBlur={marcarTocado} />
                {notaCampo('tiempo_enfermedad_anios')}
              </label>

            </div>

            <fieldset className="comorbilidades">
              <legend>
                Comorbilidades
                <small> · {valores.lista_comorbilidades.length} marcada(s)</small>
              </legend>
              <div className="comorbilidades__lista">
                {COMORBILIDADES.map(([codigo, nombre]) => (
                  <label key={codigo} className="campo--casilla">
                    <input
                      type="checkbox"
                      checked={valores.lista_comorbilidades.includes(codigo)}
                      onChange={() => alternarComorbilidad(codigo)}
                    />
                    {nombre}
                  </label>
                ))}
              </div>
              <small>El modelo usa el total de enfermedades marcadas.</small>
            </fieldset>
          </fieldset>

          <fieldset className="formulario__grupo">
            <legend>Carga terapéutica</legend>
            <div className="rejilla">
              <label className={claseCampo('numero_farmacos')}>
                <span>N.° de fármacos prescritos *</span>
                <input name="numero_farmacos" type="number" min="5" max="30" required
                  value={valores.numero_farmacos} onChange={cambiar} onBlur={marcarTocado} />
                <small>Mínimo 5 (criterio de elegibilidad).</small>
                {notaCampo('numero_farmacos')}
              </label>

              <label className={claseCampo('tomas_dia')}>
                <span>Tomas por día *</span>
                <input name="tomas_dia" type="number" min="1" max="20" required
                  value={valores.tomas_dia} onChange={cambiar} onBlur={marcarTocado} />
                {notaCampo('tomas_dia')}
              </label>
            </div>
          </fieldset>

          <fieldset className="formulario__grupo">
            <legend>Contexto social</legend>
            <div className="rejilla">
              <label className={claseCampo('nivel_educativo')}>
                <span>Nivel educativo</span>
                <select name="nivel_educativo" value={valores.nivel_educativo} onChange={cambiar} onBlur={marcarTocado}>
                  <option value="">Sin dato</option>
                  <option value="sin_estudios">Sin estudios</option>
                  <option value="primaria">Primaria</option>
                  <option value="secundaria">Secundaria</option>
                  <option value="superior">Superior</option>
                </select>
                <small>Influye en la comprensión de las indicaciones.</small>
                {notaCampo('nivel_educativo')}
              </label>

              <label className={claseCampo('convivencia')}>
                <span>Convivencia</span>
                <select name="convivencia" value={valores.convivencia} onChange={cambiar} onBlur={marcarTocado}>
                  <option value="">Sin dato</option>
                  <option value="solo">Vive solo</option>
                  <option value="acompanado">Vive acompañado</option>
                </select>
                {notaCampo('convivencia')}
              </label>

              <label className={claseCampo('apoyo_familiar')}>
                <span>Apoyo familiar en la medicación</span>
                <select name="apoyo_familiar" value={valores.apoyo_familiar} onChange={cambiar} onBlur={marcarTocado}>
                  <option value="">Sin dato</option>
                  <option value="si">Sí, alguien le ayuda o le recuerda</option>
                  <option value="no">No</option>
                </select>
                {notaCampo('apoyo_familiar')}
              </label>
            </div>
          </fieldset>

          <fieldset className="formulario__grupo">
            <legend>Seguimiento y línea base</legend>
            <div className="rejilla">
              <label className={claseCampo('controles_programados_6m')}>
                <span>Controles programados (6 meses)</span>
                <input name="controles_programados_6m" type="number" min="0" max="30"
                  value={valores.controles_programados_6m} onChange={cambiar} onBlur={marcarTocado} />
                {notaCampo('controles_programados_6m')}
              </label>

              <label className={claseCampo('controles_perdidos_6m')}>
                <span>Controles perdidos (6 meses)</span>
                <input name="controles_perdidos_6m" type="number" min="0" max="30"
                  value={valores.controles_perdidos_6m} onChange={cambiar} onBlur={marcarTocado} />
                <small>No puede superar a los programados.</small>
                {notaCampo('controles_perdidos_6m')}
              </label>

              <label className={claseCampo('puntaje_morisky')}>
                <span>Puntaje Morisky-Green (0–4)</span>
                <input name="puntaje_morisky" type="number" min="0" max="4"
                  value={valores.puntaje_morisky} onChange={cambiar} onBlur={marcarTocado} />
                {notaCampo('puntaje_morisky')}
              </label>

              <label className={claseCampo('incumplimiento_basal')}>
                <span>Adherencia basal</span>
                <select name="incumplimiento_basal" value={valores.incumplimiento_basal} onChange={cambiar} onBlur={marcarTocado}>
                  <option value="">No evaluada</option>
                  <option value="no">Adherente</option>
                  <option value="si">Incumplimiento</option>
                </select>
                <small>Según el patrón de respuestas del test, no un umbral automático.</small>
                {notaCampo('incumplimiento_basal')}
              </label>
            </div>
          </fieldset>

          {error && (
            <p id="resumen-errores" className="mensaje mensaje--error" role="alert">
              {error}
            </p>
          )}

          <footer className="formulario__pie">
            <button type="button" className="boton boton--sutil" onClick={alCancelar}>
              Cancelar
            </button>
            <button
              type="submit"
              className="boton boton--primario"
              disabled={enviando}
              // No se deshabilita cuando hay errores: un botón inerte no explica
              // por qué lo está. Al pulsarlo, el formulario señala qué falta.
              aria-describedby={hayErrores ? 'resumen-errores' : undefined}
            >
              {enviando ? 'Guardando…' : edicion ? 'Guardar cambios' : 'Registrar paciente'}
            </button>
          </footer>
        </form>
      </div>
    </div>
  )
}
