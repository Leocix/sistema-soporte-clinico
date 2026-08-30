import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/useAuth'

/**
 * Cierra el paso a las vistas clinicas sin sesion valida (RF01).
 *
 * Es una defensa de usabilidad, no de seguridad: quien decide es el API, que
 * responde 401 o 403 ante cualquier peticion no autorizada. Aqui solo se
 * evita mostrar pantallas que fallarian al cargar.
 */
export default function RutaProtegida({ children }) {
  const { usuario, cargando } = useAuth()
  const ubicacion = useLocation()

  if (cargando) {
    return (
      <div className="cargando-pagina" role="status">
        <span className="girador" aria-hidden="true" />
        <p>Verificando la sesión…</p>
      </div>
    )
  }

  if (!usuario) {
    return <Navigate to="/" replace state={{ desde: ubicacion.pathname }} />
  }

  return children
}
