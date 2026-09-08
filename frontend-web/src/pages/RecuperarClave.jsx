import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api, mensajeDeError } from '../services/api'

/**
 * Solicitud del enlace de restablecimiento (RF10).
 *
 * La usan los tres perfiles: el medico desde el panel y, desde el navegador
 * del telefono, el paciente y su acompanante familiar. Antes de esto, olvidar
 * la contrasena obligaba a acercarse al consultorio, que para buena parte de
 * los pacientes del estudio —adultos mayores, varios de zona rural— no es un
 * tramite menor sino un viaje.
 *
 * La pantalla responde siempre lo mismo, exista o no la cuenta. Confirmar que
 * una direccion esta registrada convertiria esta pagina en un buscador de
 * correos de pacientes del consultorio.
 */
export default function RecuperarClave() {
  const [correo, setCorreo] = useState('')
  const [respuesta, setRespuesta] = useState(null)
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)

  const enviar = async (evento) => {
    evento.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      const { data } = await api.post('/api/auth/recuperacion', {
        correo: correo.trim(),
      })
      setRespuesta(data)
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
        <h1>Recuperar el acceso</h1>
        <p>
          Escriba el correo con el que entra al sistema y le enviaremos un
          enlace para crear una contraseña nueva.
        </p>
        <p className="acceso__consultorio">Consultorio médico Milko Ugaz Zegarra · Chiclayo</p>
      </section>

      <section className="acceso__formulario">
        {respuesta ? (
          <div className="tarjeta tarjeta--acceso">
            <h2>{respuesta.correo_habilitado ? 'Revise su correo' : 'Acuda al consultorio'}</h2>
            <p
              className={
                respuesta.correo_habilitado ? 'mensaje mensaje--exito' : 'mensaje mensaje--aviso'
              }
              role="status"
            >
              {respuesta.mensaje}
            </p>
            {respuesta.correo_habilitado && (
              <p className="acceso__pie">
                Si no lo encuentra, revise la carpeta de correo no deseado. El
                enlace vence a la media hora.
              </p>
            )}
            <Link to="/" className="boton boton--sutil boton--ancho">
              Volver al inicio de sesión
            </Link>
          </div>
        ) : (
          <form onSubmit={enviar} className="tarjeta tarjeta--acceso">
            <h2>¿Olvidó su contraseña?</h2>

            <label className="campo">
              <span>Correo electrónico</span>
              <input
                type="email" name="correo" autoComplete="username" required autoFocus
                value={correo} onChange={(e) => setCorreo(e.target.value)}
                placeholder="correo@ejemplo.pe"
              />
            </label>

            {error && <p className="mensaje mensaje--error" role="alert">{error}</p>}

            <button type="submit" className="boton boton--primario boton--ancho" disabled={enviando}>
              {enviando ? 'Enviando…' : 'Enviarme el enlace'}
            </button>

            <p className="acceso__pie">
              <Link to="/">Volver al inicio de sesión</Link>
            </p>
          </form>
        )}
      </section>
    </div>
  )
}
