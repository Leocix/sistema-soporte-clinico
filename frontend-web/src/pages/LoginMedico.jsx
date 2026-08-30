import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'
import { URL_API, mensajeDeError } from '../services/api'

/**
 * Acceso exclusivo del personal clinico (RF01).
 *
 * El perfil se envia fijo como "medico": este panel no atiende a pacientes,
 * que usan la aplicacion movil. Un paciente que intente entrar aqui recibe el
 * mismo 401 generico que una credencial equivocada, sin pistas sobre cual de
 * los dos datos fallo.
 */
export default function LoginMedico() {
  const { usuario, cargando, iniciarSesion } = useAuth()
  const navegar = useNavigate()

  const [correo, setCorreo] = useState('')
  const [contrasena, setContrasena] = useState('')
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)

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
            <input
              type="password" name="contrasena" autoComplete="current-password" required
              value={contrasena} onChange={(e) => setContrasena(e.target.value)}
            />
          </label>

          {error && <p className="mensaje mensaje--error" role="alert">{error}</p>}

          <button type="submit" className="boton boton--primario boton--ancho" disabled={enviando}>
            {enviando ? 'Verificando…' : 'Ingresar'}
          </button>

          <p className="acceso__pie">
            Los pacientes acceden desde la aplicación móvil.
          </p>
        </form>

        <p className="acceso__servidor">API: {URL_API}</p>
      </section>
    </div>
  )
}
