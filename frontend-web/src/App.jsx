import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Layout from './components/Layout'
import RutaProtegida from './components/RutaProtegida'
import LoginMedico from './pages/LoginMedico'
import Dashboard from './pages/Dashboard'
import DetallePaciente from './pages/DetallePaciente'

/** Enrutador del panel medico. */
export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<LoginMedico />} />

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
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
