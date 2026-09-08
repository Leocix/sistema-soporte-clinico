import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { api, mensajeDeError } from '../services/api'

/**
 * Fijacion de la contrasena nueva con el enlace recibido (RF10).
 *
 * El testigo llega en la consulta de la URL (`/restablecer?t=…`) y no se
 * guarda en ninguna parte del navegador: viaja del enlace al cuerpo de la
 * peticion y ahi termina su vida. El servidor lo consume en ese mismo momento.
 *
 * La pagina la abre cualquiera de los tres perfiles, casi siempre desde el
 * navegador del telefono, de modo que se diseña para leerse en una columna
 * estrecha.
 */
export default function RestablecerClave() {
  const [parametros] = useSearchParams()
  const navegar = useNavigate()
  const testigo = parametros.get('t') ?? ''

  const [contrasena, setContrasena] = useState('')
  const [repetida, setRepetida] = useState('')
  const [mostrar, setMostrar] = useState(false)
  const [error, setError] = useState(null)
  const [listo, setListo] = useState(false)
  const [enviando, setEnviando] = useState(false)

  const enviar = async (evento) => {
    evento.preventDefault()
    // La repeticion se comprueba aqui y no en el servidor: es un error de
    // tecleo del usuario, no una regla del dominio, y gastar un enlace de un
    // solo uso en descubrirlo obligaria a pedir otro.
    if (contrasena !== repetida) {
      setError('Las dos contraseñas no coinciden.')
      return
    }

    setError(null)
    setEnviando(true)
    try {
      await api.post('/api/auth/recuperacion/confirmar', { testigo, contrasena })
      setListo(true)
    } catch (fallo) {
      setError(mensajeDeError(fallo))
    } finally {
      setEnviando(false)
    }
  }

  if (!testigo) {
    return (
      <div className="acceso">
        <section className="acceso__formulario acceso__formulario--solo">
          <div className="tarjeta tarjeta--acceso">
            <h2>Enlace incompleto</h2>
            <p className="mensaje mensaje--error" role="alert">
              Abra el enlace tal como llegó en el correo, sin recortarlo.
            </p>
            <Link to="/recuperar" className="boton boton--sutil boton--ancho">
              Pedir un enlace nuevo
            </Link>
          </div>
        </section>
      </div>
    )
  }

  return (
    <div className="acceso">
      <section className="acceso__presentacion">
        <span className="marca__sigla marca__sigla--grande" aria-hidden="true">CDSS</span>
        <h1>Una contraseña nueva</h1>
        <p>
          Elija una que recuerde con facilidad y que no use en otro sitio. Debe
          tener al menos ocho caracteres.
        </p>
        <p className="acceso__consultorio">Consultorio médico Milko Ugaz Zegarra · Chiclayo</p>
      </section>

      <section className="acceso__formulario">
        {listo ? (
          <div className="tarjeta tarjeta--acceso">
            <h2>Listo</h2>
            <p className="mensaje mensaje--exito" role="status">
              Su contraseña quedó cambiada. Ya puede entrar con ella, aquí o en
              la aplicación del teléfono.
            </p>
            <button
              type="button"
              className="boton boton--primario boton--ancho"
              onClick={() => navegar('/', { replace: true })}
            >
              Ir al inicio de sesión
            </button>
          </div>
        ) : (
          <form onSubmit={enviar} className="tarjeta tarjeta--acceso">
            <h2>Escriba su nueva contraseña</h2>

            <label className="campo">
              <span>Contraseña nueva</span>
              <input
                type={mostrar ? 'text' : 'password'}
                name="contrasena" autoComplete="new-password" required autoFocus
                minLength={8}
                value={contrasena} onChange={(e) => setContrasena(e.target.value)}
              />
            </label>

            <label className="campo">
              <span>Repítala</span>
              <input
                type={mostrar ? 'text' : 'password'}
                name="repetida" autoComplete="new-password" required
                minLength={8}
                value={repetida} onChange={(e) => setRepetida(e.target.value)}
              />
            </label>

            <label className="campo campo--casilla">
              <input
                type="checkbox"
                checked={mostrar}
                onChange={(e) => setMostrar(e.target.checked)}
              />
              <span>Ver lo que escribo</span>
            </label>

            {error && <p className="mensaje mensaje--error" role="alert">{error}</p>}

            <button type="submit" className="boton boton--primario boton--ancho" disabled={enviando}>
              {enviando ? 'Guardando…' : 'Guardar la contraseña'}
            </button>

            <p className="acceso__pie">
              El enlace vence a la media hora y solo sirve una vez.
            </p>
          </form>
        )}
      </section>
    </div>
  )
}
