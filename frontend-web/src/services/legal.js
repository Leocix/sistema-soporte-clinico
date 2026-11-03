/**
 * Textos de la Política de privacidad y de los Términos y condiciones.
 *
 * Viven en un solo módulo para que las dos páginas públicas y el resto del
 * panel citen la misma versión. Cada sección es { titulo, parrafos, lista? }.
 * La aplicación móvil muestra un resumen y remite a estas páginas.
 *
 * El correo de contacto se configura con VITE_CORREO_CONTACTO; mientras no
 * exista, el texto remite al consultorio en lugar de inventar una dirección.
 */

export const VIGENCIA = '3 de noviembre de 2026'

const CORREO = import.meta.env.VITE_CORREO_CONTACTO

/** A dónde dirigirse, ya con su preposición: «al correo …» o «al consultorio». */
export const CONTACTO = CORREO
  ? `al correo ${CORREO}`
  : 'al consultorio, en persona o en su próxima consulta'

const RESPONSABLE = 'Consultorio médico Milko Ugaz Zegarra, Chiclayo'

export const PRIVACIDAD = [
  {
    titulo: '1. Quién es responsable de sus datos',
    parrafos: [
      `El responsable del tratamiento de sus datos personales es el ${RESPONSABLE}. ` +
      'El sistema fue desarrollado como parte de una investigación de tesis de la ' +
      'Universidad Católica Santo Toribio de Mogrovejo.',
      `Para cualquier consulta sobre sus datos puede dirigirse ${CONTACTO}.`,
    ],
  },
  {
    titulo: '2. Qué datos tratamos',
    parrafos: ['Solo los necesarios para acompañar su tratamiento:'],
    lista: [
      'Identificación y contacto: nombres, apellidos, documento de identidad (opcional), teléfono y correo electrónico.',
      'Datos de salud: diagnóstico, enfermedades asociadas, número de medicamentos y de tomas al día, controles programados y perdidos, y el resultado del test de Morisky-Green.',
      'Registro de tomas: hora programada, hora en que usted registró la toma, si la tomó o no y el motivo, si lo indica.',
      'Datos del familiar acompañante: nombre, correo, parentesco y las tomas que confirmó.',
      'Datos técnicos mínimos: fecha y hora de los accesos y un código de seguimiento de errores.',
    ],
  },
  {
    titulo: '3. Lo que no recogemos',
    parrafos: [
      'La aplicación no accede a su ubicación, sus contactos, sus fotos, su micrófono ni su cámara, y no ' +
      'recoge datos biométricos. Tampoco usamos sus datos para publicidad ni los vendemos.',
    ],
  },
  {
    titulo: '4. Para qué los usamos',
    lista: [
      'Que su médico tratante conozca cómo va su tratamiento y le acompañe a tiempo.',
      'Estimar el riesgo de incumplimiento y explicar sus causas, como apoyo a la decisión del médico. El sistema no toma decisiones clínicas por sí solo: siempre decide el médico.',
      'Enviarle recordatorios en su propio teléfono a la hora de cada toma.',
      'Permitir que el familiar que usted invite confirme las tomas que presenció.',
      'Investigación académica, solo si usted firmó el consentimiento informado del estudio. En ese caso sus datos se identifican con un código (por ejemplo, P-001) y no con su nombre.',
    ],
  },
  {
    titulo: '5. Base legal',
    parrafos: [
      'Sus datos de salud son datos sensibles. Los tratamos con su consentimiento expreso, conforme a ' +
      'la Ley N.° 29733, Ley de Protección de Datos Personales, y su Reglamento, y con el deber de ' +
      'confidencialidad que establece la Ley N.° 26842, Ley General de Salud.',
    ],
  },
  {
    titulo: '6. Quién puede verlos',
    lista: [
      'Su médico tratante: toda su ficha y su historial.',
      'El familiar que usted invite: solo su porcentaje de cumplimiento y las tomas pendientes de confirmar. Usted puede retirarlo cuando quiera desde la opción «Familia».',
      'El encargado técnico del sistema: únicamente para mantenerlo y resolver fallas.',
      'Los proveedores de alojamiento del sistema cuando funciona en internet (base de datos y servidores en la nube), que procesan la información por encargo y bajo condiciones de seguridad. Pueden estar ubicados fuera del Perú. Cuando el sistema funciona en modo local, los datos no salen de la computadora del consultorio.',
    ],
  },
  {
    titulo: '7. Cómo los protegemos',
    lista: [
      'Las contraseñas se guardan cifradas: nadie, ni siquiera el médico, puede leerlas.',
      'Las conexiones del sistema publicado viajan cifradas (HTTPS y SSL).',
      'Cada perfil ve solo lo que le corresponde, y las sesiones vencen solas.',
      'Los datos que se usan en la investigación van seudonimizados.',
    ],
  },
  {
    titulo: '8. Cuánto tiempo los conservamos',
    parrafos: [
      'Mientras dure su seguimiento y el estudio. Si el médico le da de baja, su historial se conserva ' +
      'como parte de su atención y del estudio durante el plazo que exijan las normas sobre historias ' +
      'clínicas y el protocolo de investigación; después se elimina o se anonimiza.',
    ],
  },
  {
    titulo: '9. Sus derechos',
    parrafos: [
      'Usted puede pedir en cualquier momento acceder a sus datos, corregirlos, que se cancelen o ' +
      'oponerse a su uso, y retirar su consentimiento para la investigación sin que eso afecte su ' +
      `atención médica. Solicítelo ${CONTACTO}. Responderemos dentro de los plazos que establece la ley.`,
      'Si considera que no se atendió su solicitud, puede presentar un reclamo ante la Autoridad ' +
      'Nacional de Protección de Datos Personales del Ministerio de Justicia y Derechos Humanos.',
    ],
  },
  {
    titulo: '10. Menores de edad',
    parrafos: ['El sistema está dirigido a personas adultas. No registramos a menores de 18 años.'],
  },
  {
    titulo: '11. Cambios en esta política',
    parrafos: [
      'Si cambiamos esta política, publicaremos la nueva versión en esta página con su fecha de ' +
      'vigencia y se lo informaremos en la consulta.',
    ],
  },
]

export const TERMINOS = [
  {
    titulo: '1. Aceptación',
    parrafos: [
      'Al crear su cuenta o ingresar al panel o a la aplicación «Mi tratamiento», usted acepta estos ' +
      'Términos y condiciones y la Política de privacidad. Si no está de acuerdo, no use el sistema e ' +
      'infórmelo en el consultorio: su atención médica no depende de usarlo.',
    ],
  },
  {
    titulo: '2. Qué es el sistema',
    parrafos: [
      `Es una herramienta de apoyo para el seguimiento de la toma de medicamentos de los pacientes del ${RESPONSABLE}. ` +
      'Registra sus tomas, le recuerda sus horarios y ayuda al médico a identificar a quién acompañar primero.',
    ],
  },
  {
    titulo: '3. Lo que el sistema no es',
    lista: [
      'No es un servicio de emergencias. Ante una emergencia, acuda al establecimiento de salud más cercano o llame al SAMU (106).',
      'No diagnostica ni indica tratamientos. No cambie, suspenda ni duplique un medicamento por lo que vea en la aplicación: consulte siempre a su médico.',
      'El riesgo que estima el modelo es una probabilidad de apoyo, no una certeza. La decisión clínica corresponde al médico tratante.',
    ],
  },
  {
    titulo: '4. Su cuenta',
    lista: [
      'Su cuenta es personal. Guarde su contraseña y no la comparta; el consultorio nunca se la pedirá.',
      'Si cree que alguien conoce su contraseña, cámbiela o pida al médico una nueva.',
      'Mantenga sus datos correctos y avise en el consultorio si cambian.',
    ],
  },
  {
    titulo: '5. Uso correcto',
    lista: [
      'Paciente: registre sus tomas con la verdad, cuando realmente ocurran. Un registro honesto, incluso de las tomas que no pudo hacer, es lo que permite ayudarle.',
      'Familiar: confirme solo las tomas que usted presenció.',
      'Médico: use la información solo para la atención de sus pacientes y la investigación autorizada, y no descargue reportes en equipos ajenos al consultorio.',
      'Está prohibido acceder a cuentas ajenas, intentar vulnerar la seguridad del sistema o usarlo con fines distintos a los descritos.',
    ],
  },
  {
    titulo: '6. Recordatorios y funcionamiento',
    parrafos: [
      'Los recordatorios dependen de su teléfono: de que tenga batería, de que la aplicación tenga ' +
      'permiso para enviar notificaciones y de la hora configurada. Son una ayuda, no una garantía. ' +
      'El sistema puede interrumpirse por mantenimiento o por fallas de conexión; sin internet, la ' +
      'aplicación guarda sus registros y los envía cuando vuelve la señal.',
    ],
  },
  {
    titulo: '7. Responsabilidad',
    parrafos: [
      'El sistema se ofrece como apoyo al seguimiento clínico, en el marco de un proyecto académico. ' +
      'No reemplaza la consulta médica ni las indicaciones de su médico, que prevalecen siempre sobre ' +
      'lo que muestre la aplicación.',
    ],
  },
  {
    titulo: '8. Fin del uso',
    parrafos: [
      'Puede dejar de usar el sistema cuando quiera. El médico puede dar de baja su cuenta al terminar ' +
      'el seguimiento o si se incumplen estos términos. Su historial se conserva según la Política de privacidad.',
    ],
  },
  {
    titulo: '9. Propiedad intelectual',
    parrafos: [
      'El software, su diseño y sus textos pertenecen a sus autores. Se autoriza su uso únicamente para ' +
      'los fines descritos en estos términos.',
    ],
  },
  {
    titulo: '10. Ley aplicable y contacto',
    parrafos: [
      'Estos términos se rigen por las leyes de la República del Perú. Para cualquier consulta, ' +
      `diríjase ${CONTACTO}.`,
    ],
  },
]
