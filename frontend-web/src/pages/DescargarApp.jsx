import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import QRCode from 'qrcode'
import PaginaPublica from '../components/PaginaPublica'

/**
 * Dónde se descarga la aplicación del paciente y del familiar.
 *
 * El APK no se versiona en el repositorio: en local lo deja aquí
 * `python iniciar_local.py apk`, y en el despliegue se publica aparte (por
 * ejemplo, como archivo de una *release* de GitHub) y su dirección se indica
 * en VITE_APK_URL.
 */
const URL_APK = import.meta.env.VITE_APK_URL || '/descargas/mi-tratamiento.apk'

export default function DescargarApp() {
  const [qr, setQr] = useState(null)

  // El código QR lleva a esta misma página: el médico la abre en la
  // computadora del consultorio y el paciente la escanea con su celular.
  useEffect(() => {
    QRCode.toDataURL(window.location.href, { width: 220, margin: 1 })
      .then(setQr)
      .catch(() => setQr(null))
  }, [])

  return (
    <PaginaPublica titulo="Descargue «Mi tratamiento»">
      <section className="descarga">
        <div className="descarga__principal">
          <img src="/icono-app.png" alt="Ícono de la aplicación Mi tratamiento"
               width="96" height="96" className="descarga__icono" />
          <div>
            <p className="publica__entrada">
              La aplicación para pacientes y familiares del Consultorio médico
              Milko Ugaz Zegarra. Le recuerda sus medicamentos, registra sus
              tomas y permite que un familiar le acompañe.
            </p>
            <a className="boton boton--primario descarga__boton" href={URL_APK} download>
              Descargar para Android (APK)
            </a>
            <p className="nota">Requiere Android 7.0 o superior y unos 150 MB libres.</p>
          </div>
        </div>
        {qr && (
          <figure className="descarga__qr">
            <img src={qr} alt="Código QR de esta página" width="220" height="220" />
            <figcaption>¿Está en una computadora? Escanee este código con la cámara de su celular.</figcaption>
          </figure>
        )}
      </section>

      <section className="publica__seccion">
        <h2>Cómo instalarla</h2>
        <ol>
          <li>Toque <strong>Descargar para Android (APK)</strong> desde su celular y espere a que termine.</li>
          <li>Abra el archivo descargado (aparece en las notificaciones o en la carpeta <em>Descargas</em>).</li>
          <li>Si Android le avisa que la aplicación proviene de una fuente desconocida, toque <strong>Configuración</strong>, active <strong>Permitir de esta fuente</strong> y vuelva atrás.</li>
          <li>Toque <strong>Instalar</strong>. Al terminar, busque el ícono azul <strong>Mi tratamiento</strong>.</li>
        </ol>
      </section>

      <section className="publica__seccion">
        <h2>Cómo entrar</h2>
        <ul>
          <li><strong>Si es paciente:</strong> su médico le entrega en la consulta su correo y una contraseña temporal.</li>
          <li><strong>Si es familiar:</strong> pida al paciente su código de invitación y toque <strong>Crear mi cuenta con el código</strong>.</li>
        </ul>
        <p>
          Al usar la aplicación acepta los <Link to="/terminos">Términos y condiciones</Link> y
          la <Link to="/privacidad">Política de privacidad</Link>.
        </p>
      </section>
    </PaginaPublica>
  )
}
