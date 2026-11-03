// Vuelca la Política de privacidad y los Términos del panel en Markdown,
// para los anexos 6.2 y 6.3 del manual. Así el manual cita el mismo texto que
// publica la web y no una copia que envejece aparte.
//
//     node legales_a_md.mjs > ../legales.md

import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

const ruta = fileURLToPath(new URL('../../../frontend-web/src/services/legal.js', import.meta.url))
// `import.meta.env` solo existe dentro de Vite; aquí se toma la versión sin
// correo configurado, que remite al consultorio.
const codigo = readFileSync(ruta, 'utf8').replace(/import\.meta\.env\.\w+/g, 'undefined')
const modulo = await import('data:text/javascript;base64,' + Buffer.from(codigo).toString('base64'))

const bloque = (titulo, secciones) => {
  const lineas = [`## ${titulo}`, '', `Vigente desde el ${modulo.VIGENCIA}.`, '']
  for (const s of secciones) {
    lineas.push(`### ${s.titulo}`, '')
    for (const p of s.parrafos ?? []) lineas.push(p, '')
    for (const item of s.lista ?? []) lineas.push(`- ${item}`)
    if (s.lista) lineas.push('')
  }
  return lineas.join('\n')
}

process.stdout.write(
  bloque('6.2 Política de privacidad', modulo.PRIVACIDAD) + '\n' +
  bloque('6.3 Términos y condiciones', modulo.TERMINOS),
)
