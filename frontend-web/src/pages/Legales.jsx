import PaginaPublica, { DocumentoLegal } from '../components/PaginaPublica'
import { PRIVACIDAD, TERMINOS } from '../services/legal'

export function Privacidad() {
  return (
    <PaginaPublica titulo="Política de privacidad">
      <p className="publica__entrada">
        Cómo cuidamos los datos personales y de salud que usted registra en el
        panel médico y en la aplicación «Mi tratamiento».
      </p>
      <DocumentoLegal secciones={PRIVACIDAD} />
    </PaginaPublica>
  )
}

export function Terminos() {
  return (
    <PaginaPublica titulo="Términos y condiciones">
      <p className="publica__entrada">
        Las reglas de uso del panel médico y de la aplicación «Mi tratamiento».
      </p>
      <DocumentoLegal secciones={TERMINOS} />
    </PaginaPublica>
  )
}
