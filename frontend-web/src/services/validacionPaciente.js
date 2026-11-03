/**
 * Validacion de la ficha del paciente polimedicado, en el navegador.
 *
 * No sustituye a la del API: la del servidor es la que manda, y ademas hay
 * reglas que solo la base de datos puede garantizar. Esta capa existe por otra
 * razon: el medico completa veintiuna variables por paciente y descubrir un
 * dato incoherente **despues** de enviar significa releer el formulario entero
 * buscando cual. Aqui el aviso aparece junto al campo, antes de enviar.
 *
 * Se distinguen dos cosas que suelen confundirse:
 *
 *   - **Errores**: impiden guardar. Son los que el API rechazaria de todos
 *     modos, replicados aqui para que el medico no gaste un viaje de ida y
 *     vuelta en descubrirlos.
 *   - **Avisos**: no impiden nada. Senalan combinaciones improbables o
 *     consecuencias que conviene conocer. Un dato raro puede ser correcto, y
 *     bloquearlo seria decidir por el medico sobre su propio paciente.
 */

// Nombres peruanos con tildes, dieresis, apostrofos y guiones compuestos.
// Se excluyen digitos a proposito: un numero en el nombre es siempre un error
// de tecleo, y colarlo ensucia la busqueda por nombre del panel.
const SOLO_LETRAS = /^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]+$/

// Dominios que el validador del API rechaza por estar reservados. Sin este
// aviso, el medico escribe «paciente@consultorio.local», recibe un error de
// formato del servidor y no entiende por que: la direccion le parece valida.
const DOMINIOS_RESERVADOS = ['.local', '.test', '.invalid', '.example', '.localhost']

const entero = (v) => Number.parseInt(v, 10)
const decimal = (v) => Number.parseFloat(v)
const vacio = (v) => v === '' || v === null || v === undefined

/** Normaliza lo que se teclea a mano: espacios de sobra y de los bordes. */
export function normalizarTexto(valor) {
  return String(valor ?? '').trim().replace(/\s+/g, ' ')
}

/** Solo los digitos, para comparar un telefono escrito con espacios o guiones. */
const soloDigitos = (valor) => String(valor ?? '').replace(/\D/g, '')

/**
 * Revisa la ficha completa.
 *
 * @returns {{errores: Object, avisos: Object}} mensajes por nombre de campo.
 */
export function validarFicha(valores, { edicion = false } = {}) {
  const errores = {}
  const avisos = {}

  // --- Identificación ------------------------------------------------------
  for (const campo of ['nombres', 'apellidos']) {
    const texto = normalizarTexto(valores[campo])
    const etiqueta = campo === 'nombres' ? 'Los nombres' : 'Los apellidos'
    if (texto.length < 2) {
      errores[campo] = `${etiqueta} son obligatorios.`
    } else if (!SOLO_LETRAS.test(texto)) {
      errores[campo] = `${etiqueta} no pueden llevar números ni símbolos.`
    }
  }

  if (!vacio(valores.documento_identidad)) {
    const doc = normalizarTexto(valores.documento_identidad).replace(/[\s-]/g, '')
    if (!/^[0-9A-Za-z]{8,12}$/.test(doc)) {
      errores.documento_identidad =
        'Escriba 8 dígitos si es DNI, o entre 9 y 12 caracteres si es carné de extranjería.'
    } else if (/^\d+$/.test(doc) && doc.length !== 8) {
      avisos.documento_identidad =
        'El DNI peruano tiene 8 dígitos. Revise que no falte o sobre alguno.'
    }
  }

  if (!vacio(valores.telefono)) {
    const digitos = soloDigitos(valores.telefono)
    if (digitos.length < 6 || digitos.length > 12) {
      errores.telefono = 'El teléfono debe tener entre 6 y 12 dígitos.'
    } else if (digitos.length === 9 && !digitos.startsWith('9')) {
      avisos.telefono = 'Un celular peruano de 9 dígitos empieza por 9. Revíselo.'
    }
  }

  if (!vacio(valores.correo)) {
    const correo = normalizarTexto(valores.correo).toLowerCase()
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(correo)) {
      errores.correo = 'La dirección no tiene un formato válido.'
    } else if (DOMINIOS_RESERVADOS.some((d) => correo.endsWith(d))) {
      errores.correo =
        'Ese dominio está reservado y no admite correo real. Use una dirección a la que el paciente pueda acceder.'
    }
  } else {
    avisos.correo =
      'Sin correo no podrá generarle el acceso a la aplicación móvil ni recuperar su contraseña.'
  }

  // El código solo se valida al dar de alta. En edición el campo está
  // bloqueado —es la clave con la que el paciente viaja al conjunto de datos—,
  // de modo que exigirle un formato ahí impediría guardar una ficha por un
  // valor que el médico no puede corregir. Es lo que ocurría con la serie D-
  // de los pacientes de demostración.
  if (!edicion && !vacio(valores.codigo_anonimizado)
      && !/^P-\d{3,6}$/.test(valores.codigo_anonimizado)) {
    // Mismo patrón que el API (^P-\d{3,6}$): aceptar otra letra aquí solo
    // trasladaba el error al momento de guardar.
    errores.codigo_anonimizado =
      'El código es P, un guion y al menos tres dígitos (P-002).'
  }

  // --- Paciente ------------------------------------------------------------
  const edad = entero(valores.edad)
  if (vacio(valores.edad) || Number.isNaN(edad)) {
    errores.edad = 'La edad es obligatoria.'
  } else if (edad < 18 || edad > 120) {
    errores.edad = 'El estudio incluye personas adultas: entre 18 y 120 años.'
  }

  // --- Enfermedad ----------------------------------------------------------
  if (!vacio(valores.tiempo_enfermedad_anios)) {
    const anios = decimal(valores.tiempo_enfermedad_anios)
    if (Number.isNaN(anios) || anios < 0 || anios > 80) {
      errores.tiempo_enfermedad_anios = 'Indique entre 0 y 80 años.'
    } else if (!Number.isNaN(edad) && anios > edad) {
      // Regla incontestable: nadie lleva enfermo más tiempo del que ha vivido.
      errores.tiempo_enfermedad_anios =
        `No puede superar la edad del paciente (${edad} años).`
    } else if (!Number.isNaN(edad) && anios > edad - 18) {
      // Posible, pero infrecuente: implicaría diagnóstico en la infancia.
      avisos.tiempo_enfermedad_anios =
        'Implicaría un diagnóstico antes de los 18 años. Confirme el dato.'
    }
  }

  // Vive solo y sin nadie que le ayude con la medicación: no es un error, pero
  // es justo el perfil en el que el olvido no tiene quien lo corrija.
  if (valores.convivencia === 'solo' && valores.apoyo_familiar === 'no') {
    avisos.apoyo_familiar =
      'Vive solo y sin apoyo en la medicación: considere invitar a un familiar a la aplicación.'
  }

  // --- Carga terapéutica ---------------------------------------------------
  const farmacos = entero(valores.numero_farmacos)
  if (vacio(valores.numero_farmacos) || Number.isNaN(farmacos)) {
    errores.numero_farmacos = 'El número de fármacos es obligatorio.'
  } else if (farmacos < 5) {
    errores.numero_farmacos =
      'El estudio solo incluye pacientes polimedicados: cinco fármacos o más.'
  } else if (farmacos > 30) {
    errores.numero_farmacos = 'Revise el dato: más de 30 fármacos es improbable.'
  }

  const tomas = entero(valores.tomas_dia)
  if (vacio(valores.tomas_dia) || Number.isNaN(tomas)) {
    errores.tomas_dia = 'Las tomas por día son obligatorias.'
  } else if (tomas < 1 || tomas > 20) {
    errores.tomas_dia = 'Indique entre 1 y 20 tomas al día.'
  } else if (!Number.isNaN(farmacos) && tomas > farmacos * 4) {
    // No es un error: hay pautas de varias tomas por fármaco. Pero cuatro
    // tomas diarias de media por medicamento es lo bastante infrecuente como
    // para merecer una segunda lectura antes de que entre al conjunto de datos.
    avisos.tomas_dia =
      `${tomas} tomas para ${farmacos} fármacos es una pauta poco habitual. Confirme el dato.`
  }

  // --- Seguimiento ---------------------------------------------------------
  const programados = entero(valores.controles_programados_6m)
  const perdidos = entero(valores.controles_perdidos_6m)

  if (!vacio(valores.controles_programados_6m) && (programados < 0 || programados > 30)) {
    errores.controles_programados_6m = 'Indique entre 0 y 30.'
  }
  if (!vacio(valores.controles_perdidos_6m) && (perdidos < 0 || perdidos > 30)) {
    errores.controles_perdidos_6m = 'Indique entre 0 y 30.'
  }
  // La regla que hasta ahora solo aparecía después de enviar, como un error del
  // servidor. Es además una restricción de la base de datos.
  if (!Number.isNaN(programados) && !Number.isNaN(perdidos) && perdidos > programados) {
    errores.controles_perdidos_6m =
      `No puede superar a los programados (${programados}).`
  }
  if (programados === 0 && !Number.isNaN(perdidos) && perdidos === 0) {
    avisos.controles_programados_6m =
      'Sin controles programados, el modelo no puede calcular la tasa de inasistencia y tendrá que estimarla.'
  }

  // --- Línea base de adherencia -------------------------------------------
  if (!vacio(valores.puntaje_morisky)) {
    const morisky = entero(valores.puntaje_morisky)
    if (Number.isNaN(morisky) || morisky < 0 || morisky > 4) {
      errores.puntaje_morisky = 'El test de Morisky-Green puntúa de 0 a 4.'
    } else if (!vacio(valores.incumplimiento_basal)) {
      // Aviso y no error: el informe declara que la clasificación sigue el
      // patrón de respuestas del test y no un umbral automático, de modo que el
      // médico puede apartarse del criterio con conocimiento de causa.
      const declaraIncumplimiento = valores.incumplimiento_basal === 'si'
      if (morisky === 4 && declaraIncumplimiento) {
        avisos.incumplimiento_basal =
          'Un puntaje de 4 corresponde al patrón adherente. Confirme la clasificación.'
      } else if (morisky < 4 && !declaraIncumplimiento) {
        avisos.incumplimiento_basal =
          `Un puntaje de ${morisky} corresponde al patrón de incumplimiento. Confirme la clasificación.`
      }
    }
  }

  return { errores, avisos }
}

// ---------------------------------------------------------------------------
// Limpieza mientras se teclea
// ---------------------------------------------------------------------------
// La validación de arriba avisa de un valor fuera de rango, pero no impide
// escribirlo. Con un campo numérico del navegador, además, lo inválido
// («--1000», «1e5») llega como cadena vacía: el campo opcional lo da por no
// respondido y el médico cree haber guardado un dato que no se guardó. Aquí se
// impide escribirlo: solo dígitos, sin ceros a la izquierda y con un tope de
// cifras acorde al rango de cada variable. Cubre también lo que se pega.
export const NUMERICOS = {
  edad: { enteros: 3 },
  tiempo_enfermedad_anios: { enteros: 2, decimales: 1 },
  numero_farmacos: { enteros: 2 },
  tomas_dia: { enteros: 2 },
  controles_programados_6m: { enteros: 2 },
  controles_perdidos_6m: { enteros: 2 },
  puntaje_morisky: { enteros: 1 },
}

function limpiarNumero(valor, { enteros, decimales = 0 }) {
  let texto = String(valor ?? '').replace(',', '.')
  texto = texto.replace(decimales ? /[^\d.]/g : /\D/g, '')
  let [parteEntera = '', ...resto] = texto.split('.')
  parteEntera = parteEntera.replace(/^0+(?=\d)/, '').slice(0, enteros)
  if (!decimales || resto.length === 0) return parteEntera
  // Un solo punto decimal, con las cifras que admite la variable.
  const parteDecimal = resto.join('').slice(0, decimales)
  return `${parteEntera || '0'}.${parteDecimal}`
}

/**
 * Devuelve el valor que puede quedar en el campo mientras se escribe.
 * Los campos que no figuran aquí se devuelven tal cual.
 */
export function limpiarAlEscribir(campo, valor) {
  if (NUMERICOS[campo]) return limpiarNumero(valor, NUMERICOS[campo])
  switch (campo) {
    case 'nombres':
    case 'apellidos':
      // Letras del castellano, apóstrofo, guion y espacio; sin dobles espacios.
      return String(valor).replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]/g, '').replace(/ {2,}/g, ' ')
    case 'documento_identidad':
      return String(valor).replace(/[^0-9A-Za-z]/g, '').slice(0, 12).toUpperCase()
    case 'telefono':
      return String(valor).replace(/[^\d +-]/g, '').slice(0, 15)
    case 'codigo_anonimizado':
      return String(valor).toUpperCase().replace(/[^A-Z0-9-]/g, '').slice(0, 8)
    default:
      return valor
  }
}

/** Aplica la normalización de texto antes de enviar la ficha. */
export function normalizarFicha(valores) {
  const limpio = { ...valores }
  for (const campo of ['nombres', 'apellidos', 'documento_identidad', 'correo']) {
    if (!vacio(limpio[campo])) limpio[campo] = normalizarTexto(limpio[campo])
  }
  if (!vacio(limpio.correo)) limpio.correo = limpio.correo.toLowerCase()
  if (!vacio(limpio.telefono)) limpio.telefono = soloDigitos(limpio.telefono)
  return limpio
}
