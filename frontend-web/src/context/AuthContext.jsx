import { useCallback, useEffect, useMemo, useState } from 'react'
import { almacen, registrarCierreDeSesion, servicioAuth } from '../services/api'
import { AuthContext } from './contextoAuth'

/**
 * Estado de sesion del panel medico (RF01).
 *
 * La sesion se rehidrata desde el almacenamiento local al montar la
 * aplicacion, de modo que un refresco de pagina no obligue a iniciar sesion
 * otra vez mientras el token siga vigente.
 */

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(() => almacen.leerUsuario())
  const [cargando, setCargando] = useState(true)

  const cerrarSesion = useCallback(() => {
    almacen.limpiar()
    setUsuario(null)
  }, [])

  // Cuando el API responde 401, la sesion caduco: se limpia sin intervencion
  // del usuario y el enrutador lo devuelve al inicio de sesion.
  useEffect(() => {
    registrarCierreDeSesion(cerrarSesion)
  }, [cerrarSesion])

  // Un token guardado puede haber expirado mientras la pestana estaba cerrada.
  // Se valida contra el API antes de dar la sesion por buena.
  useEffect(() => {
    let vigente = true

    async function validarSesion() {
      if (!almacen.leerToken()) {
        setCargando(false)
        return
      }
      try {
        const { data } = await servicioAuth.perfil()
        if (vigente) setUsuario(data)
      } catch {
        if (vigente) cerrarSesion()
      } finally {
        if (vigente) setCargando(false)
      }
    }

    validarSesion()
    return () => {
      vigente = false
    }
  }, [cerrarSesion])

  const iniciarSesion = useCallback(async (correo, contrasena) => {
    const { data } = await servicioAuth.iniciarSesion(correo, contrasena)
    almacen.guardarSesion(data.access_token, data.usuario)
    setUsuario(data.usuario)
    return data.usuario
  }, [])

  const valor = useMemo(
    () => ({ usuario, cargando, iniciarSesion, cerrarSesion }),
    [usuario, cargando, iniciarSesion, cerrarSesion],
  )

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>
}
