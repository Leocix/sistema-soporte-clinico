// Pruebas de caja blanca del panel: un caso por camino independiente.
//
//   CB-07 · limpiarAlEscribir (V(G) = 7) y limpiarNumero (V(G) = 5)
//
// limpiarNumero es interna; se recorre a través de limpiarAlEscribir con los
// campos numéricos. El análisis está en el anexo de pruebas de caja blanca.
//
//     npm test

import { describe, test } from 'node:test'
import assert from 'node:assert/strict'
import { limpiarAlEscribir } from '../src/services/validacionPaciente.js'

describe('CB-07 limpiarAlEscribir', () => {
  test('C1: campo numérico -> delega en limpiarNumero', () => {
    assert.equal(limpiarAlEscribir('numero_farmacos', '7a'), '7')
  })
  test('C2: nombres -> solo letras y un espacio entre palabras', () => {
    assert.equal(limpiarAlEscribir('nombres', 'Ana  María3'), 'Ana María')
  })
  test('C3: apellidos -> misma regla que nombres', () => {
    assert.equal(limpiarAlEscribir('apellidos', "O'Brien-Díaz#"), "O'Brien-Díaz")
  })
  test('C4: documento -> alfanumérico, mayúsculas, hasta 12', () => {
    assert.equal(limpiarAlEscribir('documento_identidad', 'ce-12.345.678.901x'), 'CE1234567890')
  })
  test('C5: teléfono -> dígitos, espacio, + y guion, hasta 15', () => {
    assert.equal(limpiarAlEscribir('telefono', '+51 987-654-321 ext'), '+51 987-654-321')
  })
  test('C6: código -> mayúsculas, letras, dígitos y guion, hasta 8', () => {
    assert.equal(limpiarAlEscribir('codigo_anonimizado', 'p-00 7?xyz'), 'P-007XYZ')
  })
  test('C7: otro campo -> se devuelve sin cambios', () => {
    assert.equal(limpiarAlEscribir('correo', ' Ana@Correo.pe '), ' Ana@Correo.pe ')
  })
})

describe('CB-07 limpiarNumero (vía campos numéricos)', () => {
  test('C1: entero -> sin letras, sin ceros a la izquierda', () => {
    assert.equal(limpiarAlEscribir('edad', '0a64'), '64')
  })
  test('C2: entero -> recorta al número de cifras de la variable', () => {
    assert.equal(limpiarAlEscribir('edad', '1234'), '123')
  })
  test('C3: decimal sin punto -> solo la parte entera', () => {
    assert.equal(limpiarAlEscribir('tiempo_enfermedad_anios', '12'), '12')
  })
  test('C4: decimal con coma -> punto y una sola cifra decimal', () => {
    assert.equal(limpiarAlEscribir('tiempo_enfermedad_anios', '8,55'), '8.5')
  })
  test('C5: decimal sin parte entera -> antepone 0', () => {
    assert.equal(limpiarAlEscribir('tiempo_enfermedad_anios', '.5'), '0.5')
  })
})
