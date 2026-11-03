import { Link, NavLink } from 'react-router-dom'
import { VIGENCIA } from '../services/legal'

/**
 * Marco de las páginas que se abren sin iniciar sesión: descarga de la
 * aplicación y textos legales. Las leen sobre todo pacientes y familiares,
 * casi siempre desde el celular, así que van en una columna estrecha.
 */
export default function PaginaPublica({ titulo, children }) {
  return (
    <div className="publica">
      <header className="publica__cabecera">
        <Link to="/descargar" className="publica__marca">
          <img src="/icono-app.png" alt="" width="40" height="40" />
          <span>Mi tratamiento</span>
        </Link>
        <nav className="publica__nav" aria-label="Páginas públicas">
          <NavLink to="/descargar">Descargar la app</NavLink>
          <NavLink to="/privacidad">Privacidad</NavLink>
          <NavLink to="/terminos">Términos</NavLink>
          <NavLink to="/" end>Acceso médico</NavLink>
        </nav>
      </header>

      <main className="publica__contenido">
        <h1>{titulo}</h1>
        {children}
      </main>

      <footer className="publica__pie">
        Consultorio médico Milko Ugaz Zegarra · Chiclayo · Textos vigentes desde el {VIGENCIA}
      </footer>
    </div>
  )
}

/** Cuerpo de un documento legal a partir de su lista de secciones. */
export function DocumentoLegal({ secciones }) {
  return secciones.map((s) => (
    <section key={s.titulo} className="publica__seccion">
      <h2>{s.titulo}</h2>
      {s.parrafos?.map((p) => <p key={p.slice(0, 40)}>{p}</p>)}
      {s.lista && (
        <ul>
          {s.lista.map((item) => <li key={item.slice(0, 40)}>{item}</li>)}
        </ul>
      )}
    </section>
  ))
}
