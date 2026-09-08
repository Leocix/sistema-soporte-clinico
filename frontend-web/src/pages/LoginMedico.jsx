import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'
import { mensajeDeError } from '../services/api'

/**
 * Acceso exclusivo del personal clinico (RF01).
 *
 * El perfil se envia fijo como "medico": este panel no atiende a pacientes,
 * que usan la aplicacion movil. Un paciente que intente entrar aqui recibe el
 * mismo 401 generico que una credencial equivocada, sin pistas sobre cual de
 * los dos datos fallo.
 */
function IconoOjo() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z"
        stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  )
}

function IconoOjoTachado() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M3 3l18 18" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <path d="M10.6 6.2A9.6 9.6 0 0 1 12 5c6.4 0 10 7 10 7a17 17 0 0 1-3.2 4"
        stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <path d="M6.3 7.9A16.7 16.7 0 0 0 2 12s3.6 7 10 7a9.9 9.9 0 0 0 4-.8"
        stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <path d="M9.9 9.9a3 3 0 0 0 4.2 4.2" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  )
}

export default function LoginMedico() {
  const { usuario, cargando, iniciarSesion } = useAuth()
  const navegar = useNavigate()

  const [correo, setCorreo] = useState('')
  const [contrasena, setContrasena] = useState('')
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)
  const [mostrarContrasena, setMostrarContrasena] = useState(false)

  if (cargando) {
    return (
      <div className="cargando-pagina" role="status">
        <span className="girador" aria-hidden="true" />
        <p>Verificando la sesión…</p>
      </div>
    )
  }
  if (usuario) return <Navigate to="/panel" replace />

  const enviar = async (evento) => {
    evento.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      await iniciarSesion(correo.trim(), contrasena)
      navegar('/panel', { replace: true })
    } catch (fallo) {
      setError(mensajeDeError(fallo))
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="acceso">
      <section className="acceso__presentacion">
        <span className="marca__sigla marca__sigla--grande" aria-hidden="true">CDSS</span>
        <h1>Sistema de soporte clínico</h1>
        <p>
          Predicción del incumplimiento terapéutico en pacientes hipertensos y
          diabéticos polimedicados.
        </p>
        <p className="acceso__consultorio">Consultorio médico Milko Ugaz Zegarra · Chiclayo</p>
      </section>

      <section className="acceso__formulario">
        <form onSubmit={enviar} className="tarjeta tarjeta--acceso">
          <h2>Iniciar sesión</h2>
          <p className="acceso__perfil">Perfil: personal médico</p>

          <label className="campo">
            <span>Correo electrónico</span>
            <input
              type="email" name="correo" autoComplete="username" required autoFocus
              value={correo} onChange={(e) => setCorreo(e.target.value)}
              placeholder="medico@consultorio.pe"
            />
          </label>

          <label className="campo">
            <span>Contraseña</span>
            <div className="campo__con-boton">
              <input
                type={mostrarContrasena ? 'text' : 'password'}
                name="contrasena" autoComplete="current-password" required
                value={contrasena} onChange={(e) => setContrasena(e.target.value)}
              />
              <button
                type="button"
                className="campo__ojo"
                onClick={() => setMostrarContrasena((v) => !v)}
                // Ver lo que se escribe ayuda a quien teclea con dificultad,
                // que es una parte del personal y de los pacientes.
                aria-label={mostrarContrasena ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                title={mostrarContrasena ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              >
                {mostrarContrasena ? <IconoOjoTachado /> : <IconoOjo />}
              </button>
            </div>
          </label>

          {error && <p className="mensaje mensaje--error" role="alert">{error}</p>}

          <button type="submit" className="boton boton--primario boton--ancho" disabled={enviando}>
            {enviando ? 'Verificando…' : 'Ingresar'}
          </button>

          <p className="acceso__pie">
            <Link to="/recuperar">¿Olvidó su contraseña?</Link>
          </p>

          <p className="acceso__pie">
            Los pacientes acceden desde la aplicación móvil.
          </p>
        </form>
      </section>
    </div>
  )
}
