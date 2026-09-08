import { useState } from 'react'
import { api, mensajeDeError } from '../services/api'

/**
 * Alta y restablecimiento del acceso del paciente a la aplicacion movil.
 *
 * Cierra un hueco que no se veia en ningun diagrama: el medico daba de alta la
 * ficha con su correo y no tenia forma de decirle al paciente con que
 * contrasena entrar. La cuenta solo podia crearla un script en el servidor.
 *
 * La contrasena se muestra **una unica vez**. En la base solo queda su hash, de
 * modo que ni el medico ni el administrador pueden consultarla despues; si el
 * paciente la pierde, se genera otra. El componente lo dice en pantalla en
 * lugar de dejar que se descubra al necesitarla.
 */
export default function AccesoMovil({ paciente, alGenerar }) {
  const [credenciales, setCredenciales] = useState(null)
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)
  const [copiado, setCopiado] = useState(false)
  const [confirmando, setConfirmando] = useState(false)
  // El estado se lleva aqui y no se lee de la ficha en cada render: refrescar
  // la ficha desmonta este componente, y con el se iria la unica copia de la
  // contrasena que existe.
  const [tieneAcceso, setTieneAcceso] = useState(paciente.tiene_acceso_movil)

  const yaTiene = tieneAcceso
  const sinCorreo = !paciente.correo

  const generar = async () => {
    setError(null)
    setEnviando(true)
    try {
      const { data } = await api.post(`/api/pacientes/${paciente.id_paciente}/acceso`)
      setCredenciales(data)
      setTieneAcceso(true)
      setConfirmando(false)
      // La ficha NO se refresca aqui a proposito. Hacerlo desmontaria este
      // componente y se llevaria por delante la contrasena, que solo existe en
      // esta respuesta: el medico crearia la cuenta y no llegaria a verla. El
      // refresco se pide al cerrar, cuando ya la ha leido.
    } catch (fallo) {
      setError(mensajeDeError(fallo))
      setConfirmando(false)
    } finally {
      setEnviando(false)
    }
  }

  const copiar = () => {
    const texto =
      `Acceso a la aplicación «Mi tratamiento»\n` +
      `Correo: ${credenciales.correo}\n` +
      `Contraseña: ${credenciales.contrasena_temporal}`
    navigator.clipboard?.writeText(texto)
    setCopiado(true)
  }

  // --- Credenciales recién generadas ---------------------------------------
  if (credenciales) {
    return (
      <section className="tarjeta acceso-movil">
        <h3>{credenciales.creada ? 'Acceso creado' : 'Contraseña restablecida'}</h3>
        <p className="seccion__descripcion">
          Entrégueselas al paciente. <strong>No volverán a mostrarse.</strong>
        </p>

        <dl className="credenciales">
          <div>
            <dt>Correo</dt>
            <dd>{credenciales.correo}</dd>
          </div>
          <div>
            <dt>Contraseña</dt>
            <dd className="credenciales__clave">{credenciales.contrasena_temporal}</dd>
          </div>
        </dl>

        <div className="acceso-movil__acciones">
          <button type="button" className="boton boton--primario" onClick={copiar}>
            {copiado ? 'Copiado' : 'Copiar las dos'}
          </button>
          <button
            type="button"
            className="boton boton--sutil"
            onClick={() => { setCredenciales(null); setCopiado(false); alGenerar?.() }}
          >
            Ocultar
          </button>
        </div>

        <p className="nota">
          En el sistema solo queda el resumen cifrado de la contraseña. Si el
          paciente la pierde, genere otra desde aquí.
        </p>
      </section>
    )
  }

  // --- Estado normal --------------------------------------------------------
  return (
    <section className="tarjeta acceso-movil">
      <h3>Acceso a la aplicación móvil</h3>

      {sinCorreo ? (
        <p className="seccion__descripcion">
          Esta ficha no tiene correo electrónico. Añádalo con <em>Editar ficha</em>:
          es el usuario con el que el paciente entrará en la aplicación.
        </p>
      ) : (
        <p className="seccion__descripcion">
          {yaTiene
            ? <>El paciente ya puede entrar con <strong>{paciente.correo}</strong>.</>
            : <>Todavía no tiene cuenta. Se creará con <strong>{paciente.correo}</strong>.</>}
        </p>
      )}

      {error && <p className="mensaje mensaje--error" role="alert">{error}</p>}

      {/* Restablecer invalida la contraseña que el paciente esté usando: se
          confirma antes, porque desde la consulta no hay forma de deshacerlo. */}
      {confirmando ? (
        <>
          <p className="mensaje mensaje--aviso" role="alert">
            La contraseña actual dejará de funcionar y el paciente tendrá que
            entrar con la nueva. ¿Continuar?
          </p>
          <div className="acceso-movil__acciones">
            <button
              type="button" className="boton boton--primario"
              onClick={generar} disabled={enviando}
            >
              {enviando ? 'Generando…' : 'Sí, restablecer'}
            </button>
            <button
              type="button" className="boton boton--sutil"
              onClick={() => setConfirmando(false)} disabled={enviando}
            >
              Cancelar
            </button>
          </div>
        </>
      ) : (
        <button
          type="button"
          className={yaTiene ? 'boton boton--sutil boton--ancho' : 'boton boton--primario boton--ancho'}
          disabled={sinCorreo || enviando}
          onClick={() => (yaTiene ? setConfirmando(true) : generar())}
        >
          {enviando ? 'Generando…' : yaTiene ? 'Restablecer la contraseña' : 'Generar acceso'}
        </button>
      )}
    </section>
  )
}
