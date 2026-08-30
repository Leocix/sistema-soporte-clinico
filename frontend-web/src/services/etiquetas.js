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

const NIVEL_SOCIOECONOMICO = {
  bajo: 'Bajo',
  medio: 'Medio',
  alto: 'Alto',
}

const ASEGURAMIENTO = {
  sis: 'SIS',
  essalud: 'EsSalud',
  ninguno: 'Ninguno',
}

const ZONA = {
  urbana: 'Urbana',
  rural: 'Rural',
}

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
export const etiquetaNivelSocioeconomico = (v) => traducir(NIVEL_SOCIOECONOMICO, v)
export const etiquetaAseguramiento = (v) => traducir(ASEGURAMIENTO, v)
export const etiquetaZona = (v) => traducir(ZONA, v)
export const etiquetaSexo = (v) => traducir(SEXO, v)
