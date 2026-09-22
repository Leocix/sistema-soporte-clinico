import { useEffect, useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../context/useAuth'
import { servicioAlertas } from '../services/api'

/** Estructura base del panel clinico: barra lateral, encabezado y contenido. */
export default function Layout() {
  const { usuario, cerrarSesion } = useAuth()
  // Cuantas alertas esperan al medico. Se consulta al entrar: sin este numero,
  // la bandeja solo se mira cuando a alguien se le ocurre abrirla.
  const [pendientes, setPendientes] = useState(0)

  useEffect(() => {
    let vigente = true
    servicioAlertas
      .listar('abierta')
      .then(({ data }) => vigente && setPendientes(data.abiertas))
      .catch(() => {})
    return () => { vigente = false }
  }, [])

  return (
    <div className="panel">
      <aside className="panel__lateral">
        <div className="marca">
          <span className="marca__sigla" aria-hidden="true">CDSS</span>
          <span className="marca__nombre">Adherencia</span>
          <span className="marca__consultorio">Consultorio Milko Ugaz Zegarra</span>
        </div>

        <nav className="navegacion" aria-label="Secciones del panel">
          <NavLink to="/panel" end className="navegacion__enlace">
            Panel de auditoría
          </NavLink>
          <NavLink to="/panel/alertas" className="navegacion__enlace">
            Alertas tempranas
            {pendientes > 0 && (
              <span className="navegacion__contador" aria-label={`${pendientes} pendientes`}>
                {pendientes}
              </span>
            )}
          </NavLink>
          <NavLink to="/panel/reportes" className="navegacion__enlace">
            Reportes generales
          </NavLink>
        </nav>

        <p className="lateral__nota">
          Las alertas avisan cuando un paciente acumula omisiones, su cumplimiento
          cae o el modelo predice riesgo alto. La ficha explica ese riesgo variable
          por variable (SHAP).
        </p>
      </aside>

      <div className="panel__cuerpo">
        <header className="encabezado">
          <div>
            <h1 className="encabezado__titulo">Sistema de soporte clínico</h1>
            <p className="encabezado__subtitulo">
              Prevención del incumplimiento terapéutico en pacientes polimedicados
            </p>
          </div>

          <div className="sesion">
            <div className="sesion__datos">
              <span className="sesion__nombre">
                Dr(a). {usuario?.nombres} {usuario?.apellidos}
              </span>
              <span className="sesion__correo">{usuario?.correo}</span>
            </div>
            <button type="button" className="boton boton--sutil" onClick={cerrarSesion}>
              Cerrar sesión
            </button>
          </div>
        </header>

        <main className="contenido">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
