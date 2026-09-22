# Matriz de trazabilidad

Relación **objetivo → brecha → requisito → funcionalidad → evidencia**.

Su función es responder, para cualquier línea del proyecto, dos preguntas: por
qué existe y cómo se comprueba que está hecha. Cada fila puede recorrerse desde
el objetivo específico del proyecto de investigación hasta un archivo concreto
del repositorio.

**Corte:** semana 4 del ciclo 2026-II (Hito 2 – 50 %).

---

## 1. De los objetivos a los requisitos

| Objetivo específico | Brecha del diagnóstico (OE1) | Requisitos derivados |
| :--- | :--- | :--- |
| **OE1** Caracterizar el proceso actual y los factores de incumplimiento | — (es la fuente del diagnóstico) | Define B1–B4 |
| **OE2** Determinar requisitos funcionales y no funcionales | B1–B4 | RF01–RF08, RNF01–RNF06 |
| **OE3** Determinar el algoritmo con mayor capacidad predictiva | B3 falta de analítica predictiva | RF04, RF06 |
| **OE4** Construir el sistema integrando web, móvil y modelo | B1, B2, B4 | RF01, RF02, RF03, RF05, RF07, RF08, RF09 |
| **OE5** Evaluar la usabilidad mediante la escala SUS | — (verificación del producto) | RNF03 |

---

## 2. De los requisitos a la implementación

| Req. | Funcionalidad construida | Componente | Archivo | Verificación | Estado |
| :---: | :--- | :--- | :--- | :--- | :---: |
| RF01 | Inicio de sesión con perfil y control de acceso por rol | API | `backend-api/app/api/auth.py`, `core/security.py` | 6 pruebas | ✅ |
| RF01 | Pantalla de acceso del médico | Web | `frontend-web/src/pages/LoginMedico.jsx` | Verificado en navegador | ✅ |
| RF01 | Pantalla de acceso del paciente | Móvil | `app-movil/lib/screens/login_screen.dart` | 5 pruebas | ✅ |
| RF02 | Alta, consulta, edición y baja lógica de pacientes | API | `backend-api/app/api/pacientes.py` | 8 pruebas | ✅ |
| RF02 | Restricciones clínicas como invariantes de base de datos | Datos | `backend-api/app/db/models.py` | Migración Alembic | ✅ |
| RF02 | Formulario de alta y ficha clínica | Web | `frontend-web/src/components/FormularioPaciente.jsx`, `pages/DetallePaciente.jsx` | Verificado en navegador | ✅ |
| RF03 | Registro de toma con sincronización idempotente | API | `backend-api/app/api/adherencia.py` | 12 pruebas | ✅ |
| RF03 | Cola local y envío en lote sin conexión | Móvil | `app-movil/lib/services/sincronizacion.dart` | 9 pruebas | ✅ |
| RF03 | Confirmación de dosis y registro de omisión | Móvil | `app-movil/lib/screens/home_screen.dart`, `registro_toma.dart` | Verificado por análisis y pruebas | ✅ |
| RF04 | Predicción de riesgo en un microservicio de inferencia | ML + API | `ml-service/app/modelo.py`, `backend-api/app/services/ml_inference.py` | 13 pruebas del microservicio + 12 del API (2 de integración real) | ✅ |
| RF05 | Alertas tempranas: reglas, bandeja y cierre con nota | API + Web | `backend-api/app/services/alertas.py`, `app/api/alertas.py`, `frontend-web/src/pages/Alertas.jsx` | 17 pruebas + verificación en navegador | ✅ |
| RF06 | Explicación individual con SHAP | ML + Web | `ml-service/app/modelo.py`, `frontend-web/src/components/PrediccionRiesgo.jsx` | Propiedad aditiva probada; contraste con KernelExplainer (r = 0,993) | ✅ |
| RF07 | Panel de auditoría y reportes generales exportables | API + Web | `frontend-web/src/pages/Dashboard.jsx`, `Reportes.jsx`, `backend-api/app/api/reportes.py` | `tests/test_reportes.py` + verificación en navegador | ✅ |
| RF08 | Alertas de toma programadas en el dispositivo | Móvil | `app-movil/lib/services/notification_service.dart` | 7 pruebas · permisos verificados en el APK | ✅ |
| RF09 | Grupo familiar: invitación, alta por código y corroboración | API | `backend-api/app/api/familiares.py` | 19 pruebas | ✅ |
| RF09 | Invitación y ciclo de vida de la pertenencia como una sola fila | Datos | `backend-api/app/db/models.py` (`Acompanante`) | Migración Alembic | ✅ |
| RF09 | Grupo familiar del paciente y recorrido del acompañante | Móvil | `app-movil/lib/screens/familia_screen.dart`, `inicio_familiar.dart` | 7 pruebas | ✅ |
| RF10 | Enlace de restablecimiento de un solo uso y con caducidad | API | `backend-api/app/api/auth.py`, `services/correo.py` | 13 pruebas | ✅ |
| RF10 | Solicitud del enlace y fijación de la contraseña nueva | Web | `frontend-web/src/pages/RecuperarClave.jsx`, `RestablecerClave.jsx` | Verificado en navegador | ✅ |
| RF10 | Solicitud del enlace desde el acceso de la app | Móvil | `app-movil/lib/screens/login_screen.dart` | 3 pruebas | ✅ |

✅ terminado · ◐ parcial · ○ pendiente

---

## 3. De los requisitos no funcionales a su materialización

| Req. | Materialización concreta | Archivo | Comprobación |
| :---: | :--- | :--- | :--- |
| RNF01 | Cabeceras de seguridad, HSTS, CSP, `Cache-Control: no-store` | `app/main.py` | `curl` sobre el servicio desplegado |
| RNF01 | Secretos fuera del código; `.env` excluido del control de versiones | `core/config.py`, `.gitignore` | Auditoría previa al primer *push* |
| RNF01 | Conexión cifrada a PostgreSQL (`sslmode=require`) | `DATABASE_URL` en Render | Conexión verificada |
| RNF01 | Seudonimización: el dataset viaja con `codigo_anonimizado` | `app/db/models.py` | Revisión del esquema |
| RNF01 | Del enlace de recuperación solo se guarda su resumen SHA-256 | `app/db/models.py` (`Restablecimiento`) | Prueba dedicada |
| RNF01 | Ni el acceso ni la recuperación permiten enumerar cuentas | `app/api/auth.py` | Respuesta idéntica, verificada |
| RNF01 | Host confiable: se rechazan cabeceras `Host` falsificadas | `app/main.py` | `403` con `Host` falso |
| RNF02 | Latencia medida y expuesta por petición | `TrazaPeticionMiddleware` | Cabecera `X-Tiempo-Respuesta-ms` |
| RNF03 | Tipografía de 18 pt y áreas táctiles de 56 pt en la app | `app-movil/lib/utils/tema.dart` | Pendiente de medición SUS (semana 7) |
| RNF04 | Manejo global de excepciones; ningún fallo tumba el servicio | `core/exceptions.py` | Fallo de BD devuelve `503`, no `500` |
| RNF04 | Sonda de disponibilidad para el balanceador | `/health` | `200` en producción |
| RNF05 | Separación en capas `api / core / db / schemas / services` | Estructura del proyecto | Revisión estructural |
| RNF06 | Microservicio de ML desacoplado del backend transaccional | `render.yaml`, arquitectura | Diseño verificado |

---

## 4. De los objetivos a sus indicadores

| Objetivo | Indicador | Meta | Medición al corte |
| :---: | :--- | :--- | :--- |
| OE1 | Pacientes con adherencia deficiente (línea base) | Medida en diagnóstico | Pendiente de la aplicación del test de Morisky |
| OE1 | Factores clasificados según modelo OMS | 5 dimensiones | **5 de 5 cubiertas** |
| OE1 | Procesos de seguimiento no digitalizados | Medida | **100 %** |
| OE2 | Requisitos especificados / identificados | 100 % | **100 %** (8 RF + 6 RNF) |
| OE2 | Alineación con estándares de arquitectura | Juicio de 3 expertos (1–5) | Pendiente |
| OE3 | Algoritmos comparados | ≥ 4 | **4 configurados y ejecutables** |
| OE3 | AUCROC en validación cruzada | ≥ 0,80 | Protocolo implementado; pendiente del dataset real |
| OE3 | Sensibilidad y especificidad | Reportadas | Calculadas por el script |
| OE3 | F1-score en prueba independiente | Reportado | Calculado por el script |
| OE4 | Historias de usuario completadas | 100 % por sprint | **3 de 3** del escenario principal |
| OE4 | Módulos construidos / requeridos | Todos | **3 de 8** requisitos funcionales |
| OE4 | Densidad de errores por módulo | Decreciente | 3 defectos detectados y corregidos; 0 abiertos |
| OE4 | Cumplimiento ISO/IEC 25010 | Funcionalidad, eficiencia, usabilidad | Verificación formal en Sprint 4 |
| OE5 | Nivel de usabilidad (SUS) | ≥ 80 | Pendiente (semana 7) |
| OE5 | Tasa de éxito en tareas | Medida | Pendiente (semana 7) |
| OE5 | Tiempo de aprendizaje de uso | Medido | Pendiente (semana 7) |

---

## 5. De las variables del instrumento al modelo

Cada variable del Anexo n.° 04 llega al modelo predictivo por un camino
explícito. La columna «dimensión» es la del modelo multidimensional de
adherencia de la OMS, que es lo que da sustento teórico a la selección.

| Variable | Dimensión (OMS) | Columna en la base | Tratamiento en el pipeline |
| :--- | :--- | :--- | :--- |
| Edad | Paciente | `pacientes.edad` | Mediana + estandarización |
| Sexo | Paciente | `pacientes.sexo` | Moda + codificación binaria |
| Nivel educativo | Socioeconómica y social | `pacientes.nivel_educativo` | Moda + codificación ordinal |
| Convivencia | Socioeconómica y social | `pacientes.convivencia` | Moda + codificación binaria |
| Apoyo familiar en la medicación | Socioeconómica y social | `pacientes.apoyo_familiar` | Moda + codificación binaria |
| Diagnóstico | Enfermedad | `pacientes.diagnostico` | Moda + *one-hot* |
| Tiempo de enfermedad | Enfermedad | `pacientes.tiempo_enfermedad_anios` | Mediana + estandarización |
| Comorbilidades | Enfermedad | `pacientes.comorbilidades` (total de `lista_comorbilidades`) | Mediana + estandarización |
| N.° de fármacos | Terapia | `pacientes.numero_farmacos` | Criterio de elegibilidad + estandarización |
| Tomas por día | Terapia | `pacientes.tomas_dia` | Mediana + estandarización |
| Controles programados | Sistema de salud | `pacientes.controles_programados_6m` | Mediana + estandarización |
| Controles perdidos | Sistema de salud | `pacientes.controles_perdidos_6m` | Coherencia + mediana + estandarización |
| Puntaje de Morisky | Paciente | `pacientes.puntaje_morisky` | **Excluido como predictor** (fuente de la etiqueta) |
| Adherencia (objetivo) | Salida | `pacientes.incumplimiento_basal` | Etiqueta `incumplimiento` |

**Variables derivadas**, construidas a partir de las anteriores:

| Variable | Definición | Factor que representa |
| :--- | :--- | :--- |
| `carga_terapeutica` | N.° de fármacos × tomas por día | Complejidad del régimen |
| `tasa_inasistencia` | Controles perdidos ÷ programados | Desvinculación del seguimiento |
| `cronicidad_relativa` | Tiempo de enfermedad ÷ (edad ÷ 10) | Cronicidad ajustada por edad |
