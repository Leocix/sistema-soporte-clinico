import { useContext } from 'react'
import { AuthContext } from './contextoAuth'

/** Acceso al estado de sesion desde cualquier vista del panel. */
export function useAuth() {
  const contexto = useContext(AuthContext)
  if (contexto === null) {
    throw new Error('useAuth debe usarse dentro de un AuthProvider.')
  }
  return contexto
}
