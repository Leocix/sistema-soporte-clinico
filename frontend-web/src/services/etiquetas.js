/**
 * Traduccion de los codigos del Anexo n.o 04 a texto para el medico.
 *
 * La base guarda los codigos del instrumento en minusculas (`hta`, `dm2`,
 * `bajo`) porque son los que consume el pipeline de aprendizaje automatico.
 * Capitalizarlos por CSS produce lecturas incorrectas en las siglas clinicas
 * ("Hta", "Dm2", "Sis"), asi que la conversion se hace aqui, de forma
 * explicita, sin tocar el dato de origen.
 */

const DIAGNOSTICO = {
  hta: 'HTA',
  dm2: 'DM2',
  ambas: 'HTA + DM2',
}

const NIVEL_EDUCATIVO = {
  sin_estudios: 'Sin estudios',
  primaria: 'Primaria',
  secundaria: 'Secundaria',
  superior: 'Superior',
}

const CONVIVENCIA = {
  solo: 'Vive solo',
  acompanado: 'Vive acompañado',
}

/** Catálogo de comorbilidades, en el orden en que se muestran al marcarlas. */
export const COMORBILIDADES = [
  ['dislipidemia', 'Dislipidemia'],
  ['obesidad', 'Obesidad'],
  ['enfermedad_renal_cronica', 'Enfermedad renal crónica'],
  ['cardiopatia_isquemica', 'Cardiopatía isquémica'],
  ['insuficiencia_cardiaca', 'Insuficiencia cardiaca'],
  ['enfermedad_cerebrovascular', 'Enfermedad cerebrovascular'],
  ['hipotiroidismo', 'Hipotiroidismo'],
  ['epoc_asma', 'EPOC o asma'],
  ['artrosis', 'Artrosis'],
  ['depresion', 'Depresión'],
  ['otra', 'Otra enfermedad crónica'],
]
const NOMBRE_COMORBILIDAD = Object.fromEntries(COMORBILIDADES)

const SEXO = {
  M: 'Masculino',
  F: 'Femenino',
}

const SIN_DATO = '—'

function traducir(mapa, valor) {
  if (valor === null || valor === undefined || valor === '') return SIN_DATO
  return mapa[valor] ?? valor
}

export const etiquetaDiagnostico = (v) => traducir(DIAGNOSTICO, v)
export const etiquetaNivelEducativo = (v) => traducir(NIVEL_EDUCATIVO, v)
export const etiquetaConvivencia = (v) => traducir(CONVIVENCIA, v)
export const etiquetaComorbilidad = (v) => traducir(NOMBRE_COMORBILIDAD, v)
export const etiquetaSiNo = (v) => (v === null || v === undefined ? SIN_DATO : v ? 'Sí' : 'No')

/** Lista legible de comorbilidades: «Dislipidemia, Obesidad» o «Ninguna». */
export function listaComorbilidades(lista) {
  if (!lista || lista.length === 0) return 'Ninguna registrada'
  return lista.map(etiquetaComorbilidad).join(', ')
}
export const etiquetaSexo = (v) => traducir(SEXO, v)
