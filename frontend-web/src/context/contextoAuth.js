import { createContext } from 'react'

/**
 * Objeto de contexto de la sesion, aislado en su propio modulo.
 *
 * Vive separado del proveedor y del hook porque Fast Refresh solo recarga en
 * caliente los archivos que exportan unicamente componentes. Cuando el
 * contexto, el proveedor y el hook compartian archivo, cada edicion cambiaba
 * la identidad del contexto y los componentes ya montados pasaban a leer
 * `null`, provocando el error "useAuth debe usarse dentro de un AuthProvider"
 * en pleno desarrollo.
 */
export const AuthContext = createContext(null)
