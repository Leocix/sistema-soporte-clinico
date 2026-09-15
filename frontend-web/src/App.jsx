import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Layout from './components/Layout'
import RutaProtegida from './components/RutaProtegida'
import LoginMedico from './pages/LoginMedico'
import RecuperarClave from './pages/RecuperarClave'
import RestablecerClave from './pages/RestablecerClave'
import Dashboard from './pages/Dashboard'
import DetallePaciente from './pages/DetallePaciente'
import Reportes from './pages/Reportes'

/** Enrutador del panel medico. */
export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<LoginMedico />} />

          {/* Publicas: quien las abre es, por definicion, quien no puede
              iniciar sesion. El enlace del correo lleva a /restablecer. */}
          <Route path="/recuperar" element={<RecuperarClave />} />
          <Route path="/restablecer" element={<RestablecerClave />} />

          <Route
            path="/panel"
            element={
              <RutaProtegida>
                <Layout />
              </RutaProtegida>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="pacientes/:id" element={<DetallePaciente />} />
            <Route path="reportes" element={<Reportes />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
