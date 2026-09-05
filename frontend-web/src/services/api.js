import axios from 'axios'

/**
 * Cliente HTTP del panel medico.
 *
 * Concentra tres responsabilidades que, de otro modo, se repetirian en cada
 * pantalla: la URL base del API, la inyeccion del token en cada peticion y el
 * tratamiento uniforme de los errores que devuelve el manejador global del
 * backend.
 */

export const URL_API = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

const CLAVE_TOKEN = 'cdss_token'
const CLAVE_USUARIO = 'cdss_usuario'

export const almacen = {
  leerToken: () => localStorage.getItem(CLAVE_TOKEN),
  leerUsuario: () => {
    try {
      const crudo = localStorage.getItem(CLAVE_USUARIO)
      return crudo ? JSON.parse(crudo) : null
    } catch {
      return null
    }
  },
  guardarSesion: (token, usuario) => {
    localStorage.setItem(CLAVE_TOKEN, token)
    localStorage.setItem(CLAVE_USUARIO, JSON.stringify(usuario))
  },
  limpiar: () => {
    localStorage.removeItem(CLAVE_TOKEN)
    localStorage.removeItem(CLAVE_USUARIO)
  },
}

export const api = axios.create({
  baseURL: URL_API,
  timeout: 60000, // el plan gratuito de Render tarda en despertar del reposo
  headers: { 'Content-Type': 'application/json' },
})

// El token viaja en cada peticion; ninguna pantalla lo manipula directamente.
api.interceptors.request.use((config) => {
  const token = almacen.leerToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

/** Traduce cualquier fallo al mensaje que el backend ya redacto en espanol. */
export function mensajeDeError(error) {
  const cuerpo = error?.response?.data

  if (cuerpo?.codigo === 'VALIDACION_FALLIDA' && cuerpo.detalles?.length) {
    return cuerpo.detalles
      .map((d) => (d.campo && d.campo !== 'general' ? `${d.campo}: ${d.motivo}` : d.motivo))
      .join(' · ')
  }
  if (cuerpo?.mensaje) return cuerpo.mensaje
  if (error.code === 'ECONNABORTED') {
    return 'El servidor tardo demasiado en responder. Vuelva a intentarlo.'
  }
  if (!error.response) {
    return `No se pudo contactar con el servidor (${URL_API}). Verifique que el API este en ejecucion.`
  }
  return 'Ocurrio un error inesperado.'
}

/** El identificador de traza permite correlacionar el fallo con el log del API. */
export function trazaDeError(error) {
  return error?.response?.data?.id_traza ?? null
}

let alExpirarSesion = null

/** Registra que hacer cuando el API responde 401 (token vencido o invalido). */
export function registrarCierreDeSesion(callback) {
  alExpirarSesion = callback
}

api.interceptors.response.use(
  (respuesta) => respuesta,
  (error) => {
    const esLogin = error.config?.url?.includes('/api/auth/login')
    // Un 401 en el propio login es "credenciales incorrectas", no una sesion
    // caducada: no debe expulsar al usuario de la pantalla.
    if (error.response?.status === 401 && !esLogin && alExpirarSesion) {
      alExpirarSesion()
    }
    return Promise.reject(error)
  },
)

// --- Servicios del API -----------------------------------------------------

export const servicioAuth = {
  iniciarSesion: (correo, contrasena) =>
    api.post('/api/auth/login', { correo, contrasena, perfil: 'medico' }),
  perfil: () => api.get('/api/auth/me'),
}

export const servicioPacientes = {
  listar: (params) => api.get('/api/pacientes', { params }),
  obtener: (id) => api.get(`/api/pacientes/${id}`),
  crear: (datos) => api.post('/api/pacientes', datos),
  actualizar: (id, datos) => api.patch(`/api/pacientes/${id}`, datos),
  darDeBaja: (id) => api.delete(`/api/pacientes/${id}`),
}

export const servicioPrediccion = {
  estado: () => api.get('/api/prediccion/estado'),
  riesgo: (idPaciente) => api.get(`/api/prediccion/pacientes/${idPaciente}`),
}

export const servicioAdherencia = {
  resumen: (idPaciente) => api.get(`/api/adherencia/pacientes/${idPaciente}/resumen`),
  registros: (idPaciente, params) =>
    api.get(`/api/adherencia/pacientes/${idPaciente}/registros`, { params }),
}
