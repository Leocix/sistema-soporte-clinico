**UNIVERSIDAD CATÓLICA SANTO TORIBIO DE MOGROVEJO**

**FACULTAD DE INGENIERÍA**

**ESCUELA DE INGENIERÍA DE SISTEMAS Y COMPUTACIÓN**

---

**SISTEMA DE SOPORTE CLÍNICO CON APRENDIZAJE AUTOMÁTICO PARA PREVENIR EL INCUMPLIMIENTO TERAPÉUTICO EN PACIENTES HIPERTENSOS Y DIABÉTICOS POLIMEDICADOS DEL CONSULTORIO MÉDICO MILKO UGAZ ZEGARRA**

**PRE INFORME DE TESIS (AVANCE AL 50 %)**

**PARA EVIDENCIAR LA EJECUCIÓN DE TESIS**

**EN EL CURSO DE SEMINARIO DE TESIS I**

**AUTOR**

**LEONARDO GUZMÁN SALAZAR**

**Chiclayo, 2026**

---

# INFORMACIÓN GENERAL

**1. Facultad y Escuela**

Facultad de Ingeniería – Escuela de Ingeniería de Sistemas y Computación.

**2. Título del informe de tesis**

Sistema de soporte clínico con aprendizaje automático para prevenir el incumplimiento terapéutico en pacientes hipertensos y diabéticos polimedicados del consultorio médico Milko Ugaz Zegarra, Chiclayo.

**3. Autor y firma**

| Autor |
| :-: |
| Leonardo Jesús Guzmán Salazar |
| _______________________ |

**4. Línea y área de la investigación**

**Línea de investigación:** Desarrollo e innovación tecnológica. **Área:** Ingeniería y tecnología.

**5. Fecha de presentación**

08 de septiembre de 2026 (Hito 2 – avance al 50 %, semana 4 del cronograma del curso).

**6. Estado del avance**

| Componente | Alcance del corte (semana 4) | Estado |
| :--- | :--- | :--- |
| Sprint 1 (CRISP-DM: *Business & Data Understanding*) | Semanas 2–3 | Cerrado |
| Sprint 2 (CRISP-DM: *Data Preparation & Modeling* inicial) | Semanas 3–4 | Cerrado |
| Sprint 3 (CRISP-DM: *Modeling* y *Evaluation*) | Semanas 5–6 | En ejecución (adelantado) |
| Sprint 4 (CRISP-DM: *Deployment*) | Semanas 7–8 | Programado |

> **Convención de lectura.** Las expresiones entre comillas angulares —«*completar con…*»— señalan valores que dependen de mediciones de campo aún en curso (extracción documental del Anexo n.° 04, ejecución experimental sobre el dataset real y pruebas con usuarios). Se dejan explícitamente marcadas para no reportar como hallazgo ningún dato no medido.

---

# ÍNDICE

- **I. RESULTADOS**
  - **1.1. En base a la metodología utilizada**
    - 1.1.1. Sprint 1: Comprensión del negocio y de los datos, y primer incremento funcional
    - 1.1.2. Sprint 2: Preparación de datos, cierre del núcleo funcional y modelado inicial
    - 1.1.3. Sprint 3: Integración del modelo, aplicación móvil y acompañamiento familiar *(en ejecución)*
    - 1.1.4. Sprint 4: Cierre, rendimiento y validación de usabilidad *(programado)*
  - **1.2. En base a los objetivos del proyecto**
    - 1.2.1. OE1 – Caracterización del proceso actual de seguimiento terapéutico
    - 1.2.2. OE2 – Determinación de los requisitos funcionales y no funcionales
    - 1.2.3. OE3 – Determinación del algoritmo con mayor capacidad predictiva
    - 1.2.4. OE4 – Construcción del sistema de soporte clínico
    - 1.2.5. OE5 – Evaluación de la usabilidad mediante la escala SUS
- **II. REFERENCIAS BIBLIOGRÁFICAS**
- **ANEXOS**

---

# I. RESULTADOS

## 1.1. En base a la metodología utilizada

El desarrollo del producto acreditable se conduce con una **integración de SCRUM y CRISP-DM**. La unidad de trabajo y de rendición de cuentas es el **sprint** de SCRUM; las fases de CRISP-DM no constituyen un ciclo paralelo, sino que se ejecutan **dentro** de los sprints como trabajo especializado del mismo equipo. De ese modo cada sprint cierra a la vez un incremento de software verificable y un entregable del modelo predictivo, que es la forma en que la literatura recomienda integrar el ciclo de vida analítico con un marco ágil de entrega (enfoque MLOps) [1], [2].

La integración es deliberada y no meramente terminológica. Un sprint que solo entregara código dejaría el modelo sin datos que aprender; uno que solo entregara analítica no produciría el software que captura esos datos. Al exigir que cada sprint cierre ambos frentes, la traza digital que genera el sistema alimenta el dataset del sprint siguiente, y el conocimiento obtenido del dataset redefine lo que el software debe capturar. Cada sprint del presente informe corresponde a un sprint del cronograma oficial del curso.

**Tabla 1.** Correspondencia entre sprints, fases de CRISP-DM e hitos del cronograma.

| Sprint | Objetivo del sprint | Fase CRISP-DM ejecutada dentro | Semanas | Hito | Estado |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **1** | Planificación y primer incremento | *Business Understanding* + *Data Understanding* | 2–3 | 30 % (Hito 1) | **Cerrado** |
| **2** | Núcleo funcional y modelado inicial | *Data Preparation* + *Modeling* (inicial) | 3–4 | 40 % / 50 % (Hito 2) | **Cerrado** |
| **3** | Integración del modelo y funcionalidades complementarias | *Modeling* (selección) + *Evaluation* | 5–6 | 65 % / 80 % | **En ejecución** (adelantado) |
| **4** | Finalización, rendimiento y validación de usabilidad | *Deployment* y monitoreo | 7–8 | 90 % / 100 % (Hito 3) | Programado |

El Sprint 3 figura **en ejecución y no programado**: parte de su alcance se adelantó al corte del 50 %, según se documenta en el apartado 1.1.3. El detalle de las ceremonias de cada sprint —planificación, revisión y retrospectiva, con sus acuerdos y compromisos— consta en el Anexo n.° 11.

---

### 1.1.1. Sprint 1: Comprensión del negocio y de los datos, y primer incremento funcional

**Sprint 1 · Semanas 2–3 · CRISP-DM: *Business Understanding* y *Data Understanding*.**

**Objetivo del sprint.** Establecer el entendimiento compartido del problema clínico, construir la línea base de adherencia del consultorio, priorizar la pila de producto y entregar el primer incremento funcional verificable (autenticación con perfiles diferenciados, RF01).

#### a) Comprensión del negocio: diagnóstico del consultorio médico Milko Ugaz Zegarra

Se aplicó la **guía de entrevista semiestructurada (Anexo n.° 03)** al médico internista responsable del consultorio, Dr. Milko Ugaz Zegarra. Los hallazgos que estructuran el problema son:

1. El seguimiento de la adherencia se realiza **exclusivamente mediante autorreporte verbal** durante la consulta; no existe ficha estructurada, registro digital ni sistema de alertas que documente el consumo real entre una cita y la siguiente.
2. Las discrepancias entre lo prescrito y lo efectivamente consumido se detectan de forma **reactiva**, por lo general cuando el paciente ya presenta una descompensación clínica.
3. La población objetivo del consultorio es de aproximadamente **50 pacientes polimedicados** con hipertensión arterial y/o diabetes mellitus tipo 2.
4. Las causas percibidas del incumplimiento son, en orden de mención: **el olvido, la complejidad del régimen farmacológico y la falta de comprensión de las indicaciones**.
5. El médico manifestó que **una alerta temprana de riesgo, disponible antes de la cita**, facilitaría intervenciones oportunas y ajustes de tratamiento mejor informados.

**Brechas tecnológicas identificadas.** El diagnóstico permitió clasificar cuatro brechas que fundamentan directamente la solución propuesta:

**Tabla 2.** Brechas tecnológicas del proceso actual y su traducción en requisitos.

| N.° | Brecha identificada | Consecuencia clínica observada | Requisito derivado |
| :---: | :--- | :--- | :---: |
| B1 | Ausencia de registro estructurado de la toma de medicamentos | El cumplimiento real no es verificable ni auditable | RF03, RF07 |
| B2 | Inexistencia de trazabilidad digital entre citas | Detección reactiva, posterior a la descompensación | RF02, RF03 |
| B3 | Falta de analítica predictiva sobre los datos clínicos | Imposibilidad de anticipar el incumplimiento | RF04, RF06 |
| B4 | Ausencia de mecanismos de alerta y de recordatorio | El olvido —principal causa percibida— no se mitiga | RF05, RF08 |

**Porcentaje de procesos de seguimiento no digitalizados (indicador de OE1):** «*completar con el cómputo final sobre el inventario de subprocesos levantado en la entrevista*». El diagnóstico preliminar señala que **ninguno** de los subprocesos de seguimiento de adherencia (registro de toma, verificación entre citas, alerta de riesgo, auditoría) cuenta con soporte digital.

#### b) Comprensión de los datos: línea base de adherencia y factores de incumplimiento

Los factores de incumplimiento se clasificaron según el **modelo multidimensional de adherencia terapéutica de la OMS (2003)** [3], que organiza los determinantes en cinco dimensiones. Esta clasificación es la que gobierna, más adelante, la estructura de variables del dataset (sección 1.1.2.b).

**Tabla 3.** Factores de incumplimiento identificados, clasificados por dimensión OMS.

| Dimensión (OMS) | Factores identificados en el consultorio | Variable observable asociada |
| :--- | :--- | :--- |
| Relacionada con el paciente | Olvido de la toma; falta de comprensión de las indicaciones | Edad; puntaje de Morisky |
| Relacionada con la terapia | Complejidad del régimen; carga farmacológica (≥ 5 fármacos) | N.° de fármacos; tomas/día |
| Relacionada con la enfermedad | Cronicidad y multimorbilidad | Diagnóstico; tiempo de enfermedad; comorbilidades |
| Socioeconómica | Nivel socioeconómico; aseguramiento; distancia al establecimiento | Nivel socioeconómico; aseguramiento; zona de residencia |
| Relacionada con el sistema de salud | Seguimiento discontinuo; inasistencia a controles | Controles programados; controles perdidos |

**Referencias de contexto para la línea base.** La evidencia disponible sitúa la magnitud del problema en el entorno inmediato del estudio: el 37,1 % de los pacientes peruanos con hipertensión y diabetes presenta adherencia deficiente según el análisis de seis años de la ENDES [4]; en el Centro de Salud Pimentel (Chiclayo) solo el 31,1 % de los adultos mayores hipertensos alcanza adherencia buena [5]; y en un centro de salud de Lambayeque el 44,7 % de los pacientes crónicos no cumple con la toma de sus medicamentos, con asociación estadísticamente significativa entre polifarmacia y adherencia (p < 0,05) [6].

**Línea base propia del consultorio:** «*completar con el porcentaje de pacientes polimedicados con adherencia deficiente resultante de la aplicación del test de Morisky-Green (Anexo n.° 05) sobre la muestra del consultorio*». El instrumento se encuentra formalizado y su aplicación se ejecuta en paralelo a la extracción documental del Anexo n.° 04.

#### c) Product Backlog priorizado con MoSCoW

**Tabla 4.** Product Backlog priorizado (técnica MoSCoW) y trazabilidad al objetivo específico.

| ID | Historia / requisito funcional | Prioridad | Objetivo | Sprint | Estado al corte |
| :---: | :--- | :---: | :---: | :---: | :--- |
| RF01 | Autenticar y autorizar a médicos y pacientes con perfiles diferenciados | Must | OE2/OE4 | 1 | **Implementado** |
| RF02 | Registrar y gestionar pacientes polimedicados y su esquema farmacológico | Must | OE4 | 2 | **Implementado y verificado** |
| RF03 | Registrar la toma de medicamentos desde la app móvil del paciente | Must | OE4 | 2 | **Implementado y verificado** |
| RF04 | Calcular y mostrar la predicción de riesgo de incumplimiento por paciente | Must | OE3/OE5 | 3 | **Implementado y verificado** |
| RF05 | Generar alertas tempranas al médico ante riesgo alto de incumplimiento | Must | OE4 | 3 | Pendiente |
| RF06 | Explicar la predicción mediante factores influyentes (SHAP) | Should | OE3 | 3 | **Parcial**: importancia global del modelo; atribución individual pendiente |
| RF07 | Auditar la adherencia mediante panel clínico con reportes exportables | Should | OE2/OE4 | 3 | **Parcial**: panel operativo; exportación pendiente |
| RF08 | Enviar recordatorios de toma al paciente | Could | OE4 | 3 | **Implementado y verificado** |
| RF09 | Corroborar la toma mediante un grupo familiar de acompañamiento | Should | OE4 | 3 | **Implementado y verificado** |
| RF10 | Restablecer la contraseña mediante un enlace enviado por correo | Should | OE4 | 3 | **Implementado y verificado** |

Los requisitos **RF09 y RF10 no figuraban en la pila inicial**. Se incorporaron durante el desarrollo y su origen queda documentado aquí porque forma parte del resultado metodológico: RF09 nace al constatar que la brecha B1 quedaba a medias —el sistema sustituye el autorreporte verbal por una traza digital, pero la fuente de esa traza sigue siendo únicamente el paciente—; RF10, al constatar que remitir al consultorio a quien olvida su contraseña convierte un olvido en un desplazamiento para una población mayoritariamente rural. Ambos se clasifican como *Should*: la hipótesis puede contrastarse sin ellos, pero su ausencia degrada la calidad de la evidencia y la usabilidad, respectivamente. La incorporación de requisitos emergentes a partir de la inspección del incremento es, precisamente, el comportamiento que SCRUM prescribe para el Product Backlog [1].

#### d) Historias de usuario y criterios de aceptación

**Tabla 5.** Historias de usuario del escenario principal y sus criterios de aceptación.

| ID | Historia de usuario | Criterio de aceptación | Verificación |
| :---: | :--- | :--- | :--- |
| HU01 | Como **médico o paciente**, quiero iniciar sesión con mi perfil, para acceder solo a la información que me corresponde. | El acceso se concede únicamente con credenciales válidas **y** perfil coincidente; el mensaje de error no revela cuál dato falló; el token expira. | Prueba de integración sobre `POST /api/auth/login` |
| HU02 | Como **médico**, quiero registrar y actualizar la ficha del paciente polimedicado y su esquema farmacológico, para mantener trazable su carga terapéutica. | El alta y la edición quedan persistidas y consultables; se rechaza el alta de un paciente con menos de 5 fármacos. | Prueba unitaria + restricción `ck_paciente_polimedicado` |
| HU03 | Como **paciente**, quiero registrar desde mi celular cada toma de medicamento, para que mi médico conozca mi cumplimiento real entre citas. | Cada toma queda registrada y sincronizada; un reintento de envío tras pérdida de conectividad no duplica el evento. | Prueba de integración + restricción `uq_registro_toma_programada` |

A las tres historias del escenario principal se sumaron, en el Sprint 3, **HU04** (*«Como paciente, quiero que un familiar mío pueda confirmar que tomé mi medicación, para que el registro no dependa solo de mi palabra»*) y **HU05** (*«Como usuario del sistema, quiero recuperar mi contraseña desde mi propio teléfono, para no tener que acercarme al consultorio por un olvido»*), con sus criterios de aceptación y verificación automatizada, documentadas en el apartado 1.1.3 y en el Anexo n.° 09.

#### e) Sprint Backlog e infraestructura del entorno

Se configuró el repositorio y el entorno de trabajo con la estructura definida en `estructura_repositorio.txt`, que separa cuatro componentes desplegables de forma independiente, coherentes con la arquitectura de microservicios del proyecto:

```
sistema-soporte-clinico/
├── backend-api/     # API Gateway FastAPI (autenticación, pacientes, adherencia)
├── frontend-web/    # Panel médico React + Vite
├── app-movil/       # App del paciente en Flutter
├── ml-pipeline/     # Entorno CRISP-DM (preparación, entrenamiento, evaluación)
└── documentacion/   # Evidencias académicas y formatos exigidos por la USAT
```

#### f) Modelo de datos clínico inicial

Se diseñó el modelo relacional del núcleo funcional sobre tres entidades, implementado con SQLAlchemy 2.0 en `backend-api/app/db/models.py`:

- **`Usuario`** — credencial de acceso con perfil diferenciado (`medico` / `paciente`); la contraseña se persiste únicamente como hash bcrypt y el rol se embebe en el token para resolver el control de acceso.
- **`Paciente`** — ficha del paciente polimedicado y, simultáneamente, **fila de características del dataset**: cada columna corresponde a una variable del Anexo n.° 04 y está agrupada por la dimensión OMS a la que pertenece. El campo `codigo_anonimizado` (P-001, P-002, …) es el seudónimo con el que los datos viajan al pipeline de ML, de modo que la extracción no arrastra identificadores directos (RNF01).
- **`RegistroAdherencia`** — evento de toma reportado desde la app móvil; sustituye el autorreporte verbal por una traza digital fechada.

Las reglas clínicas del estudio quedaron escritas como **restricciones de integridad de la base de datos**, no como validaciones dispersas en el código:

| Restricción | Regla que garantiza |
| :--- | :--- |
| `ck_paciente_polimedicado` | Solo se admiten pacientes con ≥ 5 fármacos (criterio de elegibilidad del Anexo n.° 04) |
| `ck_paciente_edad_valida` | Edad entre 18 y 120 años |
| `ck_paciente_morisky_rango` | Puntaje de Morisky en el rango 0–4 |
| `ck_paciente_controles_coherentes` | No se puede faltar a más controles de los programados |
| `uq_registro_toma_programada` | Un mismo paciente, medicamento y horario no admite doble registro: la sincronización de la app es idempotente |

#### g) Primer incremento funcional: módulo de autenticación (RF01)

Se implementó y verificó el módulo de autenticación como primer incremento entregable:

| Artefacto | Ruta | Función |
| :--- | :--- | :--- |
| Endpoints de sesión | `backend-api/app/api/auth.py` | `POST /api/auth/login`, `GET /api/auth/me` |
| Seguridad y RBAC | `backend-api/app/core/security.py` | Hash bcrypt, emisión y validación de JWT (HS256), dependencia `requiere_rol()` |
| Esquemas de validación | `backend-api/app/schemas/auth_schema.py` | Validación estricta con Pydantic (`extra="forbid"`, longitud mínima de contraseña) |

**Decisión de diseño relevante.** Ante credencial inexistente, contraseña incorrecta **o perfil equivocado** se devuelve una única respuesta indistinguible (`401 NO_AUTENTICADO`), de modo que el mecanismo de inicio de sesión no permita enumerar usuarios registrados.

#### h) Evidencia de pruebas del incremento

| Caso de prueba | Resultado esperado | Resultado obtenido |
| :--- | :--- | :---: |
| Inicio de sesión con credenciales y perfil válidos | `200` + token JWT + datos del usuario | ✔ `200` |
| Inicio de sesión con perfil incorrecto (médico que selecciona «Paciente») | `401` sin distinción de causa | ✔ `401` |
| Inicio de sesión con usuario inexistente | `401` sin distinción de causa | ✔ `401` |
| Acceso a `/api/auth/me` sin token | `401 NO_AUTENTICADO` | ✔ `401` |
| Acceso a `/api/auth/me` con token válido | `200` + perfil de la sesión | ✔ `200` |
| Envío de correo malformado y contraseña corta | `422 VALIDACION_FALLIDA` con detalle por campo | ✔ `422` |

**Sprint Review (Sprint 1).** Se aceptó el incremento RF01 y se validaron con el médico el modelo de datos inicial y el Product Backlog priorizado. **Retrospectiva:** se identificó que la dispersión de las validaciones clínicas entre el código y la base de datos generaba riesgo de inconsistencia; la acción correctiva —trasladarlas a restricciones declarativas— se ejecutó en el Sprint 2.

---

### 1.1.2. Sprint 2: Preparación de datos, cierre del núcleo funcional y modelado inicial

**Sprint 2 · Semanas 3–4 · CRISP-DM: *Data Preparation* y *Modeling* inicial.**

**Objetivo del sprint.** Especificar los requisitos y la arquitectura restantes, completar el núcleo funcional RF01–RF03, dejar el dataset clínico depurado y balanceado, y montar la configuración experimental de los cuatro algoritmos candidatos.

#### a) Especificación de requisitos y arquitectura (OE2)

Se consolidaron en este sprint **ocho requisitos funcionales** y **seis requisitos no funcionales** mapeados a atributos de calidad de la norma ISO/IEC 25010 [7]. La pila creció después a diez requisitos funcionales con la incorporación de RF09 y RF10 en el Sprint 3, según se explica bajo la Tabla 4:

**Tabla 6.** Requisitos no funcionales y su materialización técnica al corte.

| Código | Requisito no funcional | Atributo ISO/IEC 25010 | Materialización al corte |
| :---: | :--- | :--- | :--- |
| RNF01 | Cifrado en tránsito (TLS) y en reposo (AES-256) | Seguridad | Cabeceras endurecidas y HSTS en `main.py`; secretos fuera del código (`config.py`, `.env.example`); seudonimización en `Paciente.codigo_anonimizado` |
| RNF02 | Respuesta de la inferencia en tiempo aceptable (≤ 2 s) | Eficiencia de desempeño | Cabecera `X-Tiempo-Respuesta-ms` emitida por petición como instrumentación base de la medición |
| RNF03 | Interfaz usable para personal médico y adultos mayores | Usabilidad | Programado para el Sprint 4 (SUS) |
| RNF04 | Disponibilidad continua para la consulta clínica | Fiabilidad | Manejo global de excepciones + sonda `/health` + `pool_pre_ping` |
| RNF05 | Código modular y mantenible | Mantenibilidad | Separación en capas `api / core / db / schemas / services` |
| RNF06 | Escalado ante mayor concurrencia | Eficiencia / Portabilidad | Microservicio de ML desacoplado del backend transaccional |

**Arquitectura implementada.** El API Gateway (`backend-api/app/main.py`) concentra las responsabilidades transversales de la capa de lógica y servicios:

1. **CORS controlado.** Se autorizan los orígenes fijos del entorno local y, mediante expresión regular, los subdominios de despliegue de Vercel del panel médico —Vercel genera un dominio distinto por cada despliegue de vista previa, por lo que enumerarlos uno a uno no es viable—. Se restringen métodos, cabeceras y se expone `X-Request-ID` al cliente.
2. **Middlewares de seguridad y observabilidad.** `CabecerasSeguridadMiddleware` fija `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Content-Security-Policy`, `Cache-Control: no-store` —los datos de salud no deben quedar en cachés intermedias— y HSTS en producción. `TrazaPeticionMiddleware` asigna un identificador único por petición y mide su latencia.
3. **Manejo global de excepciones.** Registrado en `core/exceptions.py`, traduce toda excepción a un contrato único (`codigo`, `mensaje`, `detalles`, `id_traza`). Ninguna traza interna, consulta SQL ni estructura de la base clínica se propaga al cliente: al usuario se le entrega solo el identificador de traza para el reporte de soporte. Un fallo de base de datos responde `503` en lugar de `500`, y la indisponibilidad del modelo predictivo responde `503 MODELO_NO_DISPONIBLE`, de modo que el panel clínico degrade únicamente la vista de riesgo sin bloquear la auditoría de adherencia (RNF04).

**Verificación ejecutada sobre el API:**

| Escenario | Respuesta obtenida |
| :--- | :--- |
| `GET /health` | `200 {"estado":"ok"}` con las seis cabeceras de seguridad presentes |
| Petición con origen `https://*.vercel.app` | `Access-Control-Allow-Origin` reflejado correctamente |
| Esquema de entrada inválido | `422 VALIDACION_FALLIDA` con detalle campo por campo, sin reflejar el valor recibido |
| Tabla inexistente en la base de datos | `503 BD_NO_DISPONIBLE` — la traza queda en el log del servidor, no en la respuesta |
| Acceso sin token | `401 NO_AUTENTICADO` |

#### b) Estructuración del Anexo n.° 04 (Ficha de Extracción de Datos Clínicos)

La ficha de recolección se formalizó como el **contrato de esquema del dataset**: el script de preparación valida que el CSV extraído contenga exactamente las variables del Anexo n.° 04 y aborta con un mensaje explícito si falta alguna.

**Tabla 7.** Variables del Anexo n.° 04, su dimensión OMS y su tratamiento en el pipeline.

| N.° | Variable | Tipo | Dimensión (OMS) | Tratamiento en el pipeline |
| :---: | :--- | :--- | :--- | :--- |
| 1 | Edad | Numérica (años) | Paciente | Imputación por mediana + estandarización |
| 2 | Sexo | Categórica (M/F) | Paciente | Imputación por moda + codificación binaria |
| 3 | Nivel socioeconómico | Ordinal (bajo/medio/alto) | Socioeconómica | Imputación por moda + codificación **ordinal** (preserva el orden) |
| 4 | Aseguramiento en salud | Categórica | Socioeconómica | Imputación por moda + *one-hot* |
| 5 | Zona de residencia | Categórica (urbana/rural) | Socioeconómica | Imputación por moda + codificación binaria |
| 6 | Diagnóstico | Categórica (HTA/DM2/ambas) | Enfermedad | Imputación por moda + *one-hot* |
| 7 | Tiempo de enfermedad | Numérica (años) | Enfermedad | Imputación por mediana + estandarización |
| 8 | Comorbilidades | Numérica (n.°) | Enfermedad | Imputación por mediana + estandarización |
| 9 | N.° de fármacos prescritos | Numérica (n.°) | Terapia | Criterio de elegibilidad (≥ 5) + estandarización |
| 10 | Complejidad del régimen (tomas/día) | Numérica (n.°) | Terapia | Imputación por mediana + estandarización |
| 11 | Frecuencia de controles médicos | Numérica (n.°) | Sistema de salud | Imputación por mediana + estandarización |
| 12 | Controles perdidos | Numérica (n.°) | Sistema de salud | Validación de coherencia + imputación + estandarización |
| 13 | Puntaje de adherencia (Morisky) | Ordinal (0–4) | Paciente | **Excluido como predictor** (fuente de la etiqueta) |
| 14 | Adherencia (variable objetivo) | Binaria | Variable de salida | Etiqueta `incumplimiento` (0 = adherente, 1 = incumplimiento) |

**Decisión metodológica.** El puntaje de Morisky se **excluye del conjunto de predictores**: al ser la fuente directa de la etiqueta, incorporarlo produciría fuga de información (*data leakage*) y métricas artificialmente perfectas que no reflejarían capacidad predictiva alguna.

**Captura de los datos.** La ficha se acompaña de una plantilla en formato CSV
(`documentacion/02_instrumentos/Plantilla_Extraccion_Anexo_04.csv`) cuyas columnas
y valores admitidos son exactamente los que valida el pipeline. Un nombre de
columna o un valor categórico que no coincida detiene la ejecución con un mensaje
explícito, de modo que un error de captura no llegue silenciosamente al modelo.
La documentación del anexo fija además una regla de captura relevante para la
validez del estudio: **una celda vacía es preferible a un valor supuesto**, porque
el pipeline imputa los faltantes y deja constancia del porcentaje imputado,
mientras que un dato inventado sesga el modelo sin dejar rastro.

**Conjunto de demostración.** Para poder ejercitar el sistema completo antes de
disponer de la extracción definitiva, el pipeline incorpora un generador de datos
**simulados** (`--generar-muestra`). Sirve exclusivamente para comprobar que el
flujo se ejecuta de extremo a extremo y para demostrar el funcionamiento de la
plataforma; **ningún valor obtenido con él se reporta como resultado de esta
investigación**, y los archivos que produce quedan excluidos del control de
versiones. Los resultados del OE3 se obtendrán únicamente sobre las historias
clínicas reales del consultorio.

#### c) Depuración del dataset clínico

El script `ml-pipeline/src/preprocess.py` automatiza el recorrido completo desde la ficha en bruto hasta las matrices listas para el modelado. Las reglas de limpieza implementadas son:

**Tabla 8.** Reglas de depuración aplicadas y su justificación.

| Regla | Tratamiento | Justificación |
| :--- | :--- | :--- |
| Duplicados por código de paciente | Se conserva la extracción más reciente | Un paciente, una fila |
| Normalización de texto categórico | Minúsculas, sin espacios sobrantes | Evita que «Urbana» y «urbana» sean categorías distintas |
| Categoría fuera del catálogo | Se marca como nulo | Se preserva el resto de variables del paciente |
| Valor numérico fuera de rango plausible | Se marca como nulo | Se prefiere imputar un dato a descartar al paciente completo |
| Controles perdidos > controles programados | Se anula el dato incoherente | Incoherencia clínica: solo se anula el dato, no el registro |
| Menos de 5 fármacos | Exclusión del registro | Criterio de elegibilidad del estudio (polimedicación) |
| Etiqueta ausente o no binaria | Exclusión del registro | Sin etiqueta no hay aprendizaje supervisado posible |

**Ingeniería de características.** Se derivaron tres variables que expresan los factores priorizados en el diagnóstico:

| Variable derivada | Definición | Factor que representa |
| :--- | :--- | :--- |
| `carga_terapeutica` | N.° de fármacos × tomas/día | Complejidad del régimen (2.ª causa percibida de incumplimiento) |
| `tasa_inasistencia` | Controles perdidos ÷ controles programados | Desvinculación del seguimiento clínico |
| `cronicidad_relativa` | Tiempo de enfermedad ÷ (edad ÷ 10) | Cronicidad ajustada por la edad del paciente |

#### d) Manejo de valores nulos

El tratamiento es diferenciado por naturaleza de la variable y —decisión central— **se ajusta únicamente con el subconjunto de entrenamiento**:

- **Variables numéricas:** imputación por **mediana**, robusta ante los valores extremos propios de los conteos de fármacos y de comorbilidades.
- **Variables categóricas y ordinales:** imputación por **moda**.
- **Escalado:** estandarización posterior, indispensable para SVM y Regresión Logística e inocua para Random Forest y XGBoost, que son invariantes a la escala.

El pipeline emite un **reporte de preparación en formato JSON** (`data/processed/reporte_preparacion.json`) con el porcentaje de celdas faltantes por variable antes de imputar, el conteo de valores fuera de rango y la distribución de clases. Este reporte constituye la evidencia auditable de la fase *Data Preparation*.

**Porcentaje de celdas faltantes en el dataset real:** «*completar con el reporte generado sobre la extracción definitiva del Anexo n.° 04*».

#### e) Balanceo de clases con SMOTE

La clase minoritaria del problema es, por definición, el **incumplimiento**: justamente la que el sistema debe detectar. Sin balanceo, un clasificador puede alcanzar una exactitud elevada prediciendo siempre «adherente» y una sensibilidad cercana a cero —resultado inservible como alerta temprana (RF05)—. Se aplica por ello **SMOTE** [8], que sintetiza nuevos casos de la clase minoritaria por interpolación entre vecinos cercanos.

**Salvaguarda metodológica implementada.** El orden de las operaciones es determinante y se hizo explícito en el código:

```
1. Partición estratificada train / test  (80 / 20)
2. Ajuste del imputador, codificador y escalador  →  SOLO con train
3. Transformación de test                          →  sin reajustar
4. SMOTE                                           →  SOLO sobre train
5. El conjunto de prueba permanece SIN balancear
```

Si el balanceo se aplicara antes de la partición, muestras sintéticas derivadas de registros de prueba se filtrarían al entrenamiento y las métricas (AUCROC, sensibilidad, F1-score) quedarían infladas, invalidando la comparación de algoritmos exigida por OE3. El conjunto de prueba se mantiene deliberadamente con la **prevalencia real** del consultorio, porque es sobre esa distribución que el sistema operará.

El preprocesador ajustado se serializa (`models/preprocesador_v1.pkl`) junto al modelo, de modo que la inferencia en producción (RF04) aplique exactamente la misma transformación que el entrenamiento y no se produzca desfase entre entrenamiento y servicio.

**Verificación del flujo.** El pipeline se ejecutó de extremo a extremo con un generador de muestra sintética incorporado al script (`--generar-muestra`), destinado exclusivamente a comprobar el funcionamiento del código antes de disponer de la extracción real. La ejecución recorrió correctamente las siete etapas —validación de esquema, limpieza, perfilado de nulos, derivación de variables, partición estratificada, transformación y balanceo—, confirmó la reducción del desbalance a una proporción 1:1 en entrenamiento y produjo los artefactos esperados. **Los valores obtenidos en esa corrida son artificiales y no se reportan como resultado de la investigación.**

#### f) Configuración experimental de los cuatro algoritmos candidatos (OE3)

**Tabla 9.** Configuración experimental de los algoritmos candidatos.

| Algoritmo | Fundamento de la elección | Hiperparámetros de partida |
| :--- | :--- | :--- |
| Regresión Logística | Modelo de referencia interpretable; permite contrastar la ganancia de los métodos no lineales | `penalty='l2'`, `C ∈ {0,01; 0,1; 1; 10}`, `max_iter=1000` |
| Random Forest | Robusto ante variables heterogéneas y valores extremos; desempeño reportado en clasificación de adherencia [9] | `n_estimators ∈ {200; 500}`, `max_depth ∈ {None; 8; 12}`, `min_samples_leaf ∈ {1; 3; 5}` |
| XGBoost | Potenciación de gradiente; referencia actual en datos clínicos tabulares [10] | `n_estimators ∈ {200; 400}`, `learning_rate ∈ {0,05; 0,1}`, `max_depth ∈ {3; 5; 7}` |
| SVM (RBF) | Eficaz en muestras pequeñas y fronteras no lineales; exige el escalado ya incorporado al preprocesador | `kernel='rbf'`, `C ∈ {0,1; 1; 10}`, `gamma ∈ {'scale'; 0,01}`, `probability=True` |

**Protocolo de evaluación.**

- **Validación cruzada estratificada de 5 pliegues** sobre el conjunto de entrenamiento, preservando la proporción de clases en cada pliegue.
- **Métricas reportadas:** exactitud, sensibilidad (*recall*), especificidad, F1-score y AUCROC, con media y desviación estándar entre pliegues.
- **Métrica de decisión:** AUCROC, con la meta de **≥ 0,80** fijada en la hipótesis del proyecto; en caso de empate estadístico prevalece la **sensibilidad**, por ser el error clínicamente costoso el falso negativo —un paciente en riesgo que el sistema no detecta—.
- **Semilla fija (42)** en particiones, balanceo y modelos, para garantizar la reproducibilidad del experimento.
- **Contraste estadístico:** prueba de McNemar o *t* pareada entre los dos mejores clasificadores, programada para el Sprint 3.

**Implementación del experimento.** El protocolo no quedó solo descrito: `ml-pipeline/src/train_evaluate.py` lo ejecuta de extremo a extremo —ajuste de hiperparámetros, validación cruzada, evaluación sobre el conjunto apartado, contraste estadístico y serialización del modelo ganador— y emite la tabla comparativa en formato listo para incorporar a este informe, junto con un reporte JSON auditable.

**Una precisión metodológica sobre el balanceo.** La sección 1.1.2.e establece que SMOTE se aplica solo al conjunto de entrenamiento, después de la partición. Eso es correcto para ajustar el modelo final, pero **no basta para la validación cruzada**: si se balancea el conjunto de entrenamiento completo y después se divide en pliegues, las muestras sintéticas —interpoladas entre casos reales— quedan repartidas entre los pliegues de entrenamiento y los de validación, de modo que el modelo termina evaluándose sobre casos derivados de los que ya vio. El AUCROC resultante sería optimista y la comparación entre algoritmos, inválida.

Por eso `train_evaluate.py` parte del dataset **crudo** y encadena imputación, codificación, escalado, SMOTE y clasificador en un único objeto (`imblearn.Pipeline`) que la rutina de validación cruzada reajusta por completo en cada pliegue. El conjunto de prueba se aparta antes de todo y nunca se balancea: conserva la prevalencia real del consultorio, que es la distribución sobre la que operará el sistema.

**Verificación del flujo.** El script se ejecutó de extremo a extremo sobre datos sintéticos, recorriendo las cuatro configuraciones, la búsqueda de hiperparámetros, los cinco pliegues, la evaluación en prueba, el contraste de McNemar y la escritura de los tres artefactos. **Los valores de esa corrida son artificiales y no se reportan como resultado de la investigación.**

**Resultados comparativos:** «*completar con la ejecución de `train_evaluate.py` sobre el dataset real; la tabla generada en `data/processed/tabla_comparativa.md` se incorpora directamente a este apartado*».

#### g) Cierre del núcleo funcional: gestión de pacientes (RF02) y registro de adherencia (RF03)

Se completaron los servicios REST de ambas historias, con validación estricta de esquemas Pydantic y control de acceso por rol.

**Tabla 10.** Servicios REST del núcleo funcional expuestos al corte.

| Método | Ruta | Requisito | Autorización |
| :--- | :--- | :---: | :--- |
| `POST` | `/api/auth/login` | RF01 | Pública |
| `GET` | `/api/auth/me` | RF01 | Sesión autenticada |
| `POST` | `/api/pacientes` | RF02 | Médico |
| `GET` | `/api/pacientes` | RF02 | Médico (solo sus pacientes a cargo) |
| `GET` | `/api/pacientes/{id}` | RF02 | Médico tratante o el propio paciente |
| `PATCH` | `/api/pacientes/{id}` | RF02 | Médico tratante |
| `DELETE` | `/api/pacientes/{id}` | RF02 | Médico tratante (baja lógica) |
| `POST` | `/api/adherencia/registros` | RF03 | Paciente (su propia toma) o médico tratante |
| `POST` | `/api/adherencia/registros/lote` | RF03 | Paciente o médico tratante |
| `GET` | `/api/adherencia/pacientes/{id}/registros` | RF03 | Médico tratante o el propio paciente |
| `GET` | `/api/adherencia/pacientes/{id}/resumen` | RF03/RF07 | Médico tratante o el propio paciente |
| `GET` | `/api/prediccion/pacientes/{id}` | RF04 | Médico tratante |
| `POST` | `/api/familiares/invitaciones` | RF09 | Paciente |
| `GET` | `/api/familiares` | RF09 | Paciente |
| `DELETE` | `/api/familiares/{id}` | RF09 | Paciente |
| `POST` | `/api/familiares/registro` | RF09 | Pública, solo con código de invitación vigente |
| `GET` | `/api/familiares/tomas-por-confirmar` | RF09 | Acompañante familiar |
| `POST` | `/api/familiares/tomas/{id}/confirmacion` | RF09 | Acompañante del paciente titular del evento |
| `POST` | `/api/auth/recuperacion` | RF10 | Pública |
| `POST` | `/api/auth/recuperacion/confirmar` | RF10 | Pública, solo con enlace vigente |

Las seis últimas rutas se incorporaron en el Sprint 3 y se documentan en el apartado 1.1.3. Ninguna ruta pública admite crear una cuenta ni cambiar una credencial sin un permiso de un solo uso previamente emitido por el titular.

**Tres decisiones de diseño relevantes.**

1. **El rol no basta para autorizar.** Un paciente autenticado tiene rol válido, pero solo sobre *su* ficha. Esa regla se concentró en `services/acceso.py` para que todos los servicios que reciben un `id_paciente` la apliquen de forma idéntica, en lugar de quedar dispersa —y eventualmente olvidada— en cada controlador. El médico accede únicamente a los pacientes que tiene a su cargo como tratante.

2. **La sincronización es idempotente por diseño.** La terna (paciente, medicamento, horario programado) identifica el evento de forma unívoca. Un reenvío desde la app móvil tras una pérdida de conectividad **actualiza** el registro existente y responde `200`, mientras que un evento nuevo responde `201`. Esto satisface directamente el criterio de aceptación de HU03 («cada toma queda registrada y sincronizada») y, sobre todo, protege la validez del dataset: eventos duplicados sesgarían la tasa de adherencia observada y, con ella, las características conductuales del modelo predictivo (RF04). El servicio de lote acota el envío a 200 registros y confirma la transacción de forma atómica, de modo que un fallo a mitad de camino no deje la cola del dispositivo en un estado indeterminado.

3. **La adherencia observada se distingue de la autorreportada.** El servicio de resumen calcula la tasa de cumplimiento, el retraso promedio y la racha de omisiones consecutivas —disparador de la alerta temprana (RF05)— a partir de eventos fechados. Las tomas pospuestas se excluyen del denominador por no tener desenlace todavía. Este indicador es, precisamente, la evidencia objetiva cuya ausencia identificó el diagnóstico del OE1, frente al autorreporte verbal del test de Morisky.

#### h) Evidencia de pruebas del núcleo funcional

Se construyó una batería automatizada con `pytest` sobre una base de datos en memoria (`backend-api/tests/`). **Resultado al cierre de este sprint: 25 de 25 pruebas en verde.** El recuento acumulado tras el Sprint 3 figura en la Tabla 14.

| Grupo | Caso verificado | Resultado |
| :--- | :--- | :---: |
| RF02 | Alta persistida, consultable y con código seudonimizado correlativo (P-002) | ✔ |
| RF02 | Rechazo del alta con menos de 5 fármacos (criterio de elegibilidad) | ✔ `422` |
| RF02 | Rechazo de controles perdidos > programados | ✔ `422` |
| RF02 | Rechazo de campos ajenos al Anexo n.° 04 | ✔ `422` |
| RF02 | Actualización parcial: los campos no enviados se conservan | ✔ |
| RF02 | La coherencia se valida sobre la ficha fusionada, no solo sobre lo enviado | ✔ `409` |
| RF02 | Baja lógica: sale del panel, el historial permanece para el análisis | ✔ |
| RF03 | Registro de toma con cálculo de retraso | ✔ `201` |
| RF03 | **Reintento del mismo evento: no duplica** (`201` → `200`, un solo registro) | ✔ |
| RF03 | Corrección del desenlace: pospuesta → tomada con retraso | ✔ |
| RF03 | Sincronización de cola en lote y reenvío completo sin duplicar (3 creados → 3 actualizados) | ✔ |
| RF03 | Toma cumplida sin hora real / toma omitida con hora real | ✔ `422` |
| RF03 | Resumen de adherencia: 3 cumplidas de 5 eventos resueltos = 60 % | ✔ |
| RBAC | El paciente no puede dar de alta fichas | ✔ `403` |
| RBAC | El paciente no puede registrar tomas por un tercero | ✔ `403` |
| RBAC | Un médico ajeno no accede a la ficha ni al historial | ✔ `403` |
| RBAC | El paciente accede a su propia ficha, no a otras | ✔ `200` / `403` |
| RBAC | Sin token no hay acceso | ✔ `401` |

Con ello, el **escenario de inicio a fin exigido por el hito del 50 %** queda ejecutable y verificado: alta del paciente polimedicado → registro de la toma desde la app → cálculo de las variables conductuales de adherencia. Un evento registrado con 45 minutos de retraso respecto del horario prescrito se clasifica correctamente como cumplido con retraso y su latencia se calcula como insumo directo de la ingeniería de características del modelo predictivo.

#### i) Despliegue del sistema en infraestructura real

El sistema no quedó en un entorno de desarrollo local: los tres componentes que
lo integran están desplegados y accesibles, lo que permite verificar los
requisitos no funcionales sobre la infraestructura real y no sobre una
simulación.

**Tabla 11.** Componentes desplegados y su verificación.

| Componente | Plataforma | Verificación ejecutada |
| :--- | :--- | :--- |
| Base de datos PostgreSQL | Aiven | Conexión cifrada (`sslmode=require`); esquema aplicado con Alembic |
| API Gateway | Render | `/health` responde `200`; entorno `produccion` |
| Panel médico | Vercel | Sitio servido; el paquete apunta al API de producción |

**Comprobaciones de seguridad sobre el servicio desplegado.** Las siguientes se
ejecutaron contra el dominio público, no en local:

| Comprobación | Resultado esperado | Resultado obtenido |
| :--- | :--- | :---: |
| Documentación interactiva oculta en producción | `404` en `/docs` | ✔ `404` |
| Cabecera `Host` falsificada | Rechazo | ✔ `403` |
| Origen del panel autorizado por CORS | Origen reflejado | ✔ |
| Cabeceras de seguridad (HSTS, CSP, `nosniff`, `no-store`) | Presentes | ✔ |
| Conexión efectiva a la base clínica | Error de credenciales, no de base de datos | ✔ `401`, no `503` |

La última merece explicación: un intento de acceso con credenciales inexistentes
responde `401 NO_AUTENTICADO`. Si la conexión a PostgreSQL estuviera mal
configurada, el manejador global devolvería `503 BD_NO_DISPONIBLE`. Distinguir
ambos casos es lo que permite comprobar la conectividad sin exponer ninguna
credencial válida.

**Gestión de secretos (RNF01).** Ninguna credencial está versionada. La clave de
firma del JWT y la cadena de conexión se inyectan como variables de entorno en
la plataforma de despliegue, y el repositorio excluye los archivos `.env`. Antes
de la primera publicación se auditó el índice del repositorio para confirmar que
ni las credenciales de la base de datos ni la clave de firma habían quedado
incluidas.

**Limitación conocida del entorno.** El plan gratuito de la plataforma de
alojamiento suspende el servicio tras quince minutos sin tráfico; la primera
petición posterior tarda entre 30 y 45 segundos en responder. Esta latencia es
del arranque en frío de la infraestructura, no del sistema, y debe descontarse
al medir el indicador de RNF02 (tiempo de respuesta ≤ 2 s), que se evaluará con
el servicio ya activo durante las pruebas de carga del Sprint 4.

#### j) Cierre del sprint

Las actas completas de ambas ceremonias, con los entregables aceptados, las observaciones del Product Owner y los compromisos del sprint siguiente, constan en el Anexo n.° 11.

**Sprint Review (Sprint 2).** Se aceptaron el núcleo funcional RF01–RF03, el pipeline de preparación de datos y la configuración experimental. **Retrospectiva:** se detectó que el `pd.NA` de las columnas de texto de pandas no es interpretado por los imputadores de scikit-learn, lo que interrumpía la ejecución; la corrección —normalizar las categóricas a `object` con `np.nan` antes de imputar— se incorporó al script y quedó documentada para evitar su reaparición.

---

### 1.1.3. Sprint 3: Integración del modelo, aplicación móvil y acompañamiento familiar *(en ejecución)*

**Sprint 3 · Semanas 5–6 · CRISP-DM: *Modeling* (selección) y *Evaluation*.**

**Objetivo del sprint.** Llevar el modelo predictivo del cuaderno de análisis al sistema en producción, completar la aplicación del paciente y cerrar las dos brechas de seguimiento que el diagnóstico dejó abiertas: la ausencia de avisos (B4) y la dependencia exclusiva del autorreporte como fuente de la toma (B1).

**Sobre el adelanto de alcance.** Parte del trabajo de este sprint se ejecutó antes del corte del 50 %. La razón no fue de cronograma sino técnica: el Sprint 2 dejó el modelo entrenado y serializado, pero un artefacto `.pkl` en un directorio no es un componente del sistema. Mientras no exista una ruta que lo cargue, lo alimente con los datos de una ficha real y devuelva una probabilidad, el objetivo OE4 —construir el sistema integrando el modelo— permanece sin evidencia. Se decidió por tanto adelantar la integración, que es lo que convierte el modelo en parte del producto acreditable.

#### a) Del artefacto serializado al servicio: integración del modelo (RF04)

El módulo `backend-api/app/services/ml_inference.py` carga el *pipeline* serializado una sola vez por proceso (`lru_cache`), construye la fila de características a partir de la ficha del paciente y devuelve la probabilidad de incumplimiento junto con su interpretación clínica. La ruta `GET /api/prediccion/pacientes/{id}` la expone al panel médico.

**Tabla 12.** Contrato de la predicción devuelta por el sistema.

| Campo | Contenido | Por qué forma parte del contrato |
| :--- | :--- | :--- |
| `probabilidad` | Probabilidad de incumplimiento antes del próximo control | Es el resultado del modelo, no una categoría precocinada |
| `nivel` | Bajo / medio / alto, según el umbral configurado | Traduce la probabilidad a la decisión que el médico debe tomar |
| `factores_influyentes` | Variables con mayor importancia de permutación | Sin ellos la cifra es una caja negra que el médico no puede contrastar |
| `variables_imputadas` | Campos ausentes en la ficha que el modelo tuvo que estimar | Una predicción sobre una ficha incompleta merece menos confianza, y el médico debe poder verlo |
| `modelo` y `entrenado_el` | Algoritmo y fecha de entrenamiento | Trazabilidad: identifica qué modelo produjo qué predicción |
| `origen_datos` | Procedencia del conjunto de entrenamiento | Declara si el resultado proviene de datos reales o de demostración |

**Tres salvaguardas incorporadas durante la integración.**

1. **Ausentes reales, no ausentes de Python.** Los campos opcionales de la ficha llegan desde el API como `None`, que los imputadores de *scikit-learn* no reconocen como valor faltante: solo interpretan `NaN`. La conversión explícita antes de invocar el *pipeline* evita que la inferencia falle para casi cualquier paciente con una ficha incompleta, que es el caso corriente.

2. **La ausencia del modelo no tumba el sistema.** Si el artefacto no está disponible, el manejador global responde `503 MODELO_NO_DISPONIBLE`. El panel muestra el resto de la ficha con normalidad. La predicción es un apoyo a la decisión; su indisponibilidad no debe impedir consultar la historia de adherencia.

3. **La interfaz declara lo que la cifra es y lo que no es.** La ficha muestra literalmente que se trata de una estimación de apoyo a la decisión clínica, que no constituye un diagnóstico y que la decisión corresponde al médico tratante. Cuando el modelo se ha entrenado con el conjunto de demostración, lo declara en la misma tarjeta.

**Desempeño medido (RNF02).** El tiempo de inferencia, instrumentado con la cabecera `X-Tiempo-Respuesta-ms`, se sitúa en el orden de **13 ms** con el servicio activo, frente a la meta de 2 s del RNF02. La latencia percibida en el despliegue gratuito procede del arranque en frío de la infraestructura, no del cálculo del modelo.

**Advertencia metodológica, explícita en el sistema y en este informe.** El modelo actualmente desplegado se entrenó con un **conjunto de demostración simulado** (320 filas; `datos_reales: false` en `risk_model_v1.json`). Sus métricas ilustran el funcionamiento del componente y **no constituyen un resultado de la investigación**. Los valores que responderán al indicador del OE3 son los que produzca `train_evaluate.py` sobre el dataset real, una vez concluida la extracción documental del Anexo n.° 04.

#### b) La aplicación del paciente sobre un dispositivo real

La aplicación Flutter pasó de maqueta verificada por pruebas a **APK de publicación instalable**, lo que satisface la exigencia de una versión ejecutable del núcleo funcional.

- **Navegación por barra inferior.** Las funciones estaban tras un menú de tres puntos. Para el usuario objetivo —un adulto mayor polimedicado— un icono sin etiqueta en una esquina no es un menú: es una función que no existe. Se sustituyó por cuatro destinos rotulados y permanentes (Hoy, Medicinas, Familia, Mi cuenta), decisión trazable al RNF03.
- **Alertas de toma en el dispositivo (RF08).** Los recordatorios se programan en el teléfono y no se envían desde el servidor: el paciente puede estar sin cobertura justo a la hora de su medicación, que es precisamente el escenario que más necesita el aviso. El permiso se solicita al guardar el primer medicamento con su horario, único momento en que la petición se explica por sí sola.
- **Defecto corregido con implicación de despliegue.** El manifiesto de publicación de Android no declaraba el permiso de INTERNET. Las herramientas de Flutter lo declaran por su cuenta en los manifiestos de depuración y de perfil, que no se fusionan en la compilación de publicación: la aplicación funcionaba durante el desarrollo y quedaba permanentemente «sin conexión» al instalarse desde el APK. El caso ilustra por qué la verificación debe ejecutarse sobre el artefacto que se entrega y no sobre el que se depura.

#### c) Acompañamiento familiar: la toma deja de tener una sola fuente (RF09)

Toda la traza de adherencia construida hasta el Sprint 2 es **autorreporte**: el paciente marca su propia toma. Es una mejora sustancial frente al recuerdo verbal en consulta que describió el diagnóstico (OE1), pero conserva su sesgo, que la literatura sobre medición de la adherencia reconoce como su limitación principal [3].

Se incorporó un **grupo familiar de acompañamiento**: el paciente invita hasta cinco convivientes con un código de un solo uso; el acompañante corrobora desde su propio dispositivo las dosis que el paciente ya reportó. La corroboración **se añade** al registro, no lo sustituye ni lo modifica.

**Tabla 13.** Reglas del acompañamiento familiar y su fundamento.

| Regla implementada | Fundamento |
| :--- | :--- |
| Solo el paciente invita y solo él retira | Convierte el acompañamiento en un consentimiento y no en una vigilancia |
| El código caduca a los siete días y solo sirve una vez | Una invitación pendiente es, en la práctica, una credencial de alta de cuenta |
| Solo se corroboran tomas reportadas como **cumplidas** | Una omisión ya es una declaración contra el propio interés y no requiere testigo |
| La corroboración caduca a las 48 horas | Quien da fe de una dosis debe haber podido presenciarla |
| El acompañante no accede a la ficha clínica ni registra tomas | Corroborar no es reportar por otro |

El efecto sobre el dato es lo relevante para la investigación: el historial del panel médico distingue ahora, por evento, si la toma cuenta con **dos fuentes** o solo con la palabra del paciente. Esa distinción queda disponible como variable de calidad de la evidencia en el análisis posterior.

#### d) Recuperación del acceso (RF10)

La pantalla de acceso remitía al consultorio a quien olvidara su contraseña. Para una población de adultos mayores, buena parte de ella rural, eso convierte un olvido en un desplazamiento, y para el consultorio en una intervención manual sobre la base de datos. Se implementó el restablecimiento mediante un enlace de un solo uso, válido treinta minutos, con tres cautelas: la respuesta del API es idéntica exista o no la cuenta —de otro modo la ruta permitiría enumerar los correos registrados—, del enlace se persiste únicamente su resumen SHA-256, y solicitar uno nuevo anula los anteriores.

#### e) Evidencia de pruebas del sprint

**Tabla 14.** Batería automatizada al corte, por componente.

| Componente | Casos | Alcance verificado | Resultado |
| :--- | :---: | :--- | :---: |
| API Gateway (`pytest`) | 79 | RF01–RF04, RF09, RF10, RBAC de dominio, no enumeración de cuentas | ✔ 79/79 |
| Aplicación móvil (`flutter test`) | 36 | Contrato del cliente, cola sin conexión, programación de avisos, acceso y alta con código | ✔ 36/36 |
| Panel web | — | `npm run build` y análisis estático sin errores; recorrido completo verificado en navegador | ✔ |
| **Total** | **115** | | **✔** |

Las pruebas del acompañamiento familiar y del restablecimiento no verifican únicamente que la función opere: verifican también que **no** haga lo que no debe. Un acompañante no puede corroborar tomas de un paciente ajeno (`403`), ni corroborar dos veces el mismo evento (`409`), ni corroborar fuera de plazo (`409`), ni registrar tomas en nombre del paciente. Y ni el acceso ni la recuperación permiten averiguar qué correos están registrados: la comprobación del código precede a la del correo precisamente por eso.

#### f) Alcance pendiente del sprint

Conforme al cronograma, restan dentro del Sprint 3: el módulo de **alertas tempranas al médico** (RF05), la **atribución individual con SHAP** (RF06) en sustitución de la importancia global que hoy muestra la ficha, la **exportación de reportes** del panel (RF07) y —condicionada a la extracción documental— la **ejecución de la comparación de algoritmos sobre el dataset real**, que es lo que cierra el OE3.

---

### 1.1.4. Sprint 4: Cierre, rendimiento y validación de usabilidad *(programado)*

**Sprint 4 · Semanas 7–8 · CRISP-DM: *Deployment* y monitoreo.** Alcance previsto: pruebas de rendimiento y carga sobre el API y el servicio de inferencia (RNF02, RNF06); **pruebas de usabilidad con la escala SUS y ficha de observación (OE5)**; verificación del cumplimiento de los atributos ISO/IEC 25010; consolidación del repositorio y de las evidencias de la investigación.

---

## 1.2. En base a los objetivos del proyecto

**Tabla 15.** Estado de cumplimiento de los objetivos específicos al corte de la semana 4.

| Objetivo | Resultado esperado | Estado al corte | Evidencia principal |
| :---: | :--- | :---: | :--- |
| OE1 | Informe de diagnóstico con línea base y factores de incumplimiento | **Cumplido** (línea base cuantitativa en consolidación) | Anexo n.° 03 aplicado; Tablas 2 y 3 |
| OE2 | Documento de requisitos y arquitectura | **Cumplido** | Tablas 4 y 6; `backend-api/app/main.py` |
| OE3 | Modelo predictivo seleccionado y reporte comparativo | **En ejecución** (~70 %) | `preprocess.py`, `train_evaluate.py` y modelo integrado en el sistema; Tablas 9 y 12 |
| OE4 | Sistema de soporte clínico funcional | **En ejecución** (~70 %) | RF01–RF04, RF08, RF09 y RF10 operativos y desplegados |
| OE5 | Informe de validación de usabilidad | **Pendiente** (programado semana 7) | Anexo n.° 05 (SUS) formalizado |

---

### 1.2.1. OE1 – Caracterizar el proceso actual de seguimiento terapéutico y los factores de incumplimiento

**Estado: cumplido.**

| Indicador del objetivo | Meta | Resultado al corte |
| :--- | :--- | :--- |
| Porcentaje de pacientes polimedicados con adherencia deficiente (línea base) | Medida en el diagnóstico | «*completar con el resultado del test de Morisky-Green sobre la muestra del consultorio*»; referencias de contexto: 37,1 % nacional [4], 44,7 % en Lambayeque [6] |
| N.° de factores de incumplimiento identificados y clasificados según el modelo OMS | Clasificados en las 5 dimensiones | **5 dimensiones cubiertas**, con al menos un factor observable por dimensión (Tabla 3) |
| Porcentaje de procesos de seguimiento no digitalizados | Medida en el diagnóstico | **100 %** de los subprocesos de seguimiento de adherencia carecen de soporte digital (registro de toma, verificación entre citas, alerta de riesgo, auditoría) |

**Demostración.** La entrevista semiestructurada al Dr. Milko Ugaz Zegarra (Anexo n.° 03) evidenció que el seguimiento se apoya exclusivamente en el autorreporte verbal y que la detección del incumplimiento es reactiva. De ese diagnóstico se derivaron las **cuatro brechas tecnológicas** de la Tabla 2, cada una trazada a un requisito funcional, y la **clasificación de los factores de incumplimiento en las cinco dimensiones del modelo de la OMS** (Tabla 3), que a su vez gobierna la estructura de variables del Anexo n.° 04 y, por tanto, del dataset de entrenamiento. La cadena diagnóstico → factor → variable → requisito queda así documentada de extremo a extremo.

### 1.2.2. OE2 – Determinar los requisitos funcionales y no funcionales del sistema

**Estado: cumplido.**

| Indicador del objetivo | Meta | Resultado al corte |
| :--- | :--- | :--- |
| Porcentaje de requisitos especificados respecto a los identificados | 100 % | **100 %**: 8 RF y 6 RNF especificados con criterio de aceptación y prioridad MoSCoW |
| Grado de alineación con estándares de arquitectura de software (juicio de expertos, escala 1–5) | Evaluación por 3 expertos | «*completar con el resultado del expediente de juicio de expertos*» (formato disponible en `documentacion/02_instrumentos/Expediente_Expertos.md`) |

**Demostración.** Los **diez requisitos funcionales** de la Tabla 4 —ocho especificados en el Sprint 2 y dos emergentes incorporados en el Sprint 3— se derivan uno a uno de las brechas del diagnóstico y están priorizados con MoSCoW, con criterio de aceptación y objetivo asociado. Los seis requisitos no funcionales (Tabla 6) están mapeados a atributos de la norma ISO/IEC 25010 [7] y —a diferencia de una especificación meramente declarativa— **cuatro de los seis cuentan ya con materialización técnica verificable** en el código del API Gateway: seguridad (RNF01), instrumentación de desempeño (RNF02), fiabilidad mediante manejo global de excepciones y sonda de salud (RNF04) y modularidad por capas (RNF05).

La arquitectura de microservicios desacoplados quedó definida en cuatro capas —presentación, lógica/servicios, datos e infraestructura— con el microservicio de ML separado del backend transaccional, lo que permite escalar y reentrenar el modelo sin detener la operación clínica (RNF06).

### 1.2.3. OE3 – Determinar el algoritmo de aprendizaje automático con mayor capacidad predictiva

**Estado: en ejecución (avance aproximado del 70 %).**

| Indicador del objetivo | Meta | Resultado al corte |
| :--- | :--- | :--- |
| N.° de algoritmos comparados | ≥ 4 | **4 configurados**: Regresión Logística, Random Forest, XGBoost y SVM (Tabla 9) |
| AUCROC en validación cruzada estratificada | ≥ 0,80 | Protocolo **implementado y verificado** (5 pliegues estratificados, semilla fija); «*completar con la ejecución sobre el dataset real*» |
| Sensibilidad y especificidad del modelo seleccionado | Reportadas | Calculadas por el script; pendientes de la extracción definitiva |
| F1-score en datos de prueba independientes | Reportado | Calculado sobre el conjunto apartado; pendiente de la extracción definitiva |

**Demostración del avance.** La fase *Data Preparation* está **completa y automatizada**: el script `preprocess.py` valida el esquema contra el Anexo n.° 04, depura el dataset con siete reglas documentadas, perfila y trata los valores faltantes, deriva tres características clínicamente fundamentadas, particiona de forma estratificada, ajusta el preprocesador solo con entrenamiento, aplica SMOTE solo al entrenamiento y serializa tanto los conjuntos resultantes como el preprocesador y un reporte JSON auditable de todas las transformaciones.

La fase *Modeling* está **implementada y verificada en su flujo**: `train_evaluate.py` ajusta los hiperparámetros de los cuatro algoritmos dentro de la validación cruzada, evalúa con cinco pliegues estratificados, mide sobre el conjunto apartado, contrasta los dos mejores con la prueba de McNemar —en su versión binomial exacta cuando hay pocos casos discordantes— y serializa el modelo ganador junto con su preprocesador, de modo que la inferencia en producción aplique exactamente la misma transformación que el entrenamiento.

Tres decisiones metodológicas sostienen la validez de la comparación: **(i)** la exclusión del puntaje de Morisky del conjunto de predictores, por ser la fuente de la etiqueta; **(ii)** el orden estricto partición → ajuste → balanceo, que impide la fuga hacia el conjunto de prueba; y **(iii)** la aplicación de SMOTE **dentro** de cada pliegue de la validación cruzada y no antes, que impide la fuga entre pliegues. Las tres están documentadas en el código y son verificables por revisión.

El criterio de selección es el mayor AUCROC, con desempate por sensibilidad: el error clínicamente costoso es el falso negativo, un paciente en riesgo que el sistema no detecta y que por tanto no recibe la alerta temprana (RF05).

**El modelo ya no vive fuera del sistema.** El *pipeline* ganador se serializa junto con su preprocesador y el API lo carga para responder la predicción de un paciente concreto (apartado 1.1.3.a). Esto importa para el objetivo por una razón de método: un modelo evaluado únicamente en un cuaderno de análisis no demuestra capacidad predictiva *en el sistema*, porque nada garantiza que la transformación aplicada en producción coincida con la del entrenamiento. Serializar ambos como una sola unidad es lo que hace verificable esa equivalencia.

**Lo que este avance no demuestra.** El modelo desplegado se entrenó con un conjunto de demostración simulado, declarado como tal en sus metadatos (`datos_reales: false`) y en la propia interfaz. Sus cifras evidencian que el componente funciona de extremo a extremo; **no** responden al indicador del objetivo. Lo pendiente para cerrar el OE3 es la **ejecución sobre el dataset real** una vez concluida la extracción documental del Anexo n.° 04, con el protocolo ya implementado y verificado.

### 1.2.4. OE4 – Construir el sistema de soporte clínico

**Estado: en ejecución (avance aproximado del 70 %).**

| Indicador del objetivo | Meta | Resultado al corte |
| :--- | :--- | :--- |
| Porcentaje de cumplimiento de historias de usuario | 100 % por sprint | **5 de 5** historias cerradas de extremo a extremo y verificadas (HU01–HU05): **100 %** del alcance comprometido para los Sprints 1 y 2, más el alcance adelantado del Sprint 3 |
| N.° de módulos construidos frente a módulos requeridos | Todos los módulos | **7 de 10** requisitos funcionales operativos de extremo a extremo (RF01–RF04, RF08, RF09, RF10), con los tres componentes del sistema desplegados y un APK de publicación instalable |
| Densidad de errores por módulo al cierre de cada sprint | Decreciente | **8 defectos detectados y corregidos**, todos por las pruebas automatizadas, el análisis estático o la verificación sobre el artefacto entregable (imputación de nulos de texto, persistencia de los tipos enumerados, maquetación del panel, escalado tipográfico de la app, `None` frente a `NaN` en la inferencia, validación de correo en la salida del listado, permiso de INTERNET ausente en el manifiesto de publicación, permiso de avisos no consultado al sistema). **0 defectos abiertos** al cierre; 115 de 115 pruebas en verde |
| Porcentaje de cumplimiento de atributos ISO/IEC 25010 | Funcionalidad, eficiencia y usabilidad | Verificación formal programada para el Sprint 4 |

**Demostración del avance.** El núcleo funcional está operativo y verificado:

| Componente | Estado | Artefacto |
| :--- | :--- | :--- |
| API Gateway con CORS, middlewares de seguridad y manejo global de excepciones | Implementado y verificado | `backend-api/app/main.py` |
| Modelo relacional con restricciones de integridad clínica | Implementado y verificado | `backend-api/app/db/models.py` |
| Autenticación JWT con RBAC médico/paciente (RF01) | Implementado y verificado | `backend-api/app/api/auth.py`, `core/security.py` |
| Gestión de pacientes polimedicados (RF02) | Implementado y verificado | `backend-api/app/api/pacientes.py` + `schemas/paciente_schema.py` |
| Registro de toma de medicamentos (RF03) | Implementado y verificado | `backend-api/app/api/adherencia.py` + `schemas/adherencia_schema.py` |
| Autorización de dominio (acceso a la ficha por rol y por médico tratante) | Implementado y verificado | `backend-api/app/services/acceso.py` |
| Pipeline de preparación de datos | Implementado y verificado | `ml-pipeline/src/preprocess.py` |
| Panel médico de auditoría (React + Vite) | Implementado y desplegado | `frontend-web/` |
| Aplicación del paciente (Flutter) | Implementada, verificada y empaquetada como APK | `app-movil/` |
| Comparación de algoritmos con validación cruzada | Implementada y verificada | `ml-pipeline/src/train_evaluate.py` |
| **Predicción de riesgo integrada en el sistema (RF04)** | Implementada, desplegada y verificada | `backend-api/app/services/ml_inference.py`, `api/prediccion.py`, `frontend-web/src/components/PrediccionRiesgo.jsx` |
| **Alertas de toma en el dispositivo (RF08)** | Implementada y verificada | `app-movil/lib/services/notification_service.dart` |
| **Grupo familiar de acompañamiento (RF09)** | Implementado y verificado | `backend-api/app/api/familiares.py`, `app-movil/lib/screens/familia_screen.dart` |
| **Restablecimiento de contraseña (RF10)** | Implementado y verificado | `backend-api/app/api/auth.py`, `frontend-web/src/pages/RestablecerClave.jsx` |
| Batería de pruebas automatizadas | 115 casos, todos en verde | `backend-api/tests/`, `app-movil/test/` |

**El escenario de extremo a extremo exigido por el hito está operativo sobre infraestructura desplegada:** el médico da de alta al paciente polimedicado desde el panel web; el paciente registra su toma desde la aplicación móvil, incluso sin conexión; un familiar la corrobora desde su propio dispositivo; y el médico consulta, en la misma ficha, la adherencia observada, la predicción del modelo y quién atestigua cada evento.

Quedan pendientes, conforme al cronograma, las **alertas tempranas al médico** (RF05), la **explicabilidad individual con SHAP** (RF06) —la ficha muestra hoy la importancia global del modelo, declarando expresamente esa diferencia— y la **exportación de reportes** del panel (RF07).

### 1.2.5. OE5 – Evaluar la usabilidad del sistema mediante la escala SUS

**Estado: PENDIENTE DE EJECUCIÓN.**

Este objetivo **no se ejecuta en el presente corte**. Conforme al cronograma oficial del curso, su ejecución corresponde a la **semana 7 (Sprint 4 – Finalización, hito del 90 %)**, momento en que el sistema alcanza la condición de *Release Candidate* y puede ser sometido a pruebas con usuarios reales. Evaluar la usabilidad antes de disponer de las interfaces completas —panel de auditoría, alertas y recordatorios— produciría una medición no representativa del producto final.

| Indicador del objetivo | Meta | Estado |
| :--- | :--- | :--- |
| Nivel de usabilidad medido con la escala SUS [12] | ≥ 80 puntos | Pendiente (semana 7) |
| Tasa de éxito en tareas | Medida en pruebas con usuarios | Pendiente (semana 7) |
| Tiempo promedio de aprendizaje de uso del sistema | Medido en pruebas con usuarios | Pendiente (semana 7) |

**Avance preparatorio realizado.** El instrumento se encuentra **formalizado y listo para su aplicación** (`documentacion/02_instrumentos/Escala_SUS.md`, correspondiente al Anexo n.° 05 – Parte B), junto con la ficha de observación de pruebas con usuarios (Anexo n.° 06). Los sujetos de la evaluación serán el médico del consultorio —usuario del panel web— y una muestra de pacientes polimedicados —usuarios de la aplicación móvil—.

---

# II. REFERENCIAS BIBLIOGRÁFICAS

[1] K. Schwaber y J. Sutherland, «La Guía de Scrum: La guía definitiva de Scrum: Las reglas del juego», 2020. [En línea]. Disponible en: https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf

[2] C. Schröer, F. Kruse y J. M. Gómez, «Una revisión bibliográfica sistemática sobre la aplicación del modelo de procesos CRISP-DM», *Procedia Comput. Sci.*, vol. 181, pp. 526-534, 2021, doi: 10.1016/j.procs.2021.01.199.

[3] E. Sabaté, *Cumplimiento de los tratamientos a largo plazo: datos que justifican la intervención*. Ginebra: Organización Mundial de la Salud, 2003.

[4] P. M. Calderon-Ramirez, E. Huamani-Merma, M. G. Mirano-Ortiz-de-Orue, D. Fernandez-Guzman y C. J. Toro-Huamanchumo, «Factores asociados a la falta de adherencia al tratamiento farmacológico en pacientes con diabetes e hipertensión en Perú: resultados de un análisis combinado de seis años de encuestas poblacionales», *Public Health*, vol. 231, pp. 108-115, jun. 2024, doi: 10.1016/j.puhe.2024.03.012.

[5] V. A. Soto-Cáceres, R. A. Picón-Reátegui y E. R. Sencie-Delgado, «Asociación entre nivel socioeconómico y adherencia farmacológica en adultos mayores con hipertensión arterial, Centro de Salud Pimentel - Chiclayo, Perú, 2024», *Rev. Exp. En Med. Hosp. Reg. Lambayeque*, vol. 11, n.º 3, oct. 2025, doi: 10.37065/rem.v11i3.835.

[6] C. M. Carrasco Bermeo y C. B. Cerna Chacón, «Polifarmacia y adherencia terapéutica en pacientes con enfermedades crónicas en un centro de salud de Lambayeque - 2024», Repositorio Institucional USS, 2023. [En línea]. Disponible en: https://repositorio.uss.edu.pe/handle/20.500.12802/12280

[7] «ISO/IEC 25010:2023», ISO. [En línea]. Disponible en: https://www.iso.org/standard/78176.html

[8] N. V. Chawla, K. W. Bowyer, L. O. Hall y W. P. Kegelmeyer, «SMOTE: Synthetic Minority Over-sampling Technique», *J. Artif. Intell. Res.*, vol. 16, pp. 321-357, jun. 2002, doi: 10.1613/jair.953.

[9] W. Kanyongo, A. E. Ezugwu, T. Moyo y J. V. Fonou Dombeu, «Clasificación basada en el aprendizaje automático del cumplimiento terapéutico en pacientes con enfermedades no transmisibles», *Inform. Med. Unlocked*, vol. 52, p. 101611, 2025, doi: 10.1016/j.imu.2024.101611.

[10] C. D. Marineci, A. Valeanu, C. Chiriță, S. Negreș, C. Stoicescu y V. Chioncel, «Desarrollo y validación de modelos predictivos del incumplimiento terapéutico con la medicación antihipertensiva», *Medicina (Mex.)*, vol. 61, n.º 7, p. 1313, jul. 2025, doi: 10.3390/medicina61071313.

[11] S. M. Lundberg y S.-I. Lee, «A Unified Approach to Interpreting Model Predictions», en *Advances in Neural Information Processing Systems 30*, Long Beach, CA, EE. UU., 2017, pp. 4765-4774.

[12] J. Brooke, *SUS: Una escala de usabilidad «rápida y sencilla»*. Londres: Taylor & Francis, 1996.

[13] N. E. Fenton y J. Bieman, *Métricas de software: un enfoque riguroso y práctico*, 3.ª ed. Boca Ratón, FL: CRC Press, 2015, doi: 10.1201/b17461.

---

# ANEXOS

| Anexo | Título | Ubicación | Estado |
| :---: | :--- | :--- | :--- |
| N.° 01 | Carta de aceptación institucional para ejecutar la tesis | Documento firmado por el Dr. Milko Ugaz Zegarra (22/06/2026) | Adjunto |
| N.° 02 | Matriz de consistencia del proyecto | `documentacion/00_documentacion_base/Proyecto_de_Tesis.md` | Adjunto |
| N.° 03 | Guía de entrevista semiestructurada al personal médico | `documentacion/00_documentacion_base/Proyecto_de_Tesis.md` | Aplicado |
| N.° 04 | Ficha de recolección de datos clínicos | `documentacion/02_instrumentos/Anexo_04_Ficha_Extraccion_Clinica.md` | En aplicación |
| N.° 05 | Cuestionario: test de Morisky-Green y escala SUS | `documentacion/02_instrumentos/Test_Morisky.md` · `Escala_SUS.md` | Morisky en aplicación; SUS pendiente (semana 7) |
| N.° 06 | Ficha de observación de pruebas con usuarios | `documentacion/02_instrumentos/` | Pendiente (semana 7) |
| N.° 07 | Expediente de juicio de expertos | `documentacion/02_instrumentos/Expediente_Expertos.md` | En proceso |
| N.° 08 | Repositorio de código del producto acreditable | `backend-api/`, `frontend-web/`, `app-movil/`, `ml-pipeline/` | Adjunto |
| N.° 09 | Product Backlog priorizado (MoSCoW) e historias de usuario | `documentacion/03_gestion_scrum/Product_Backlog.md` | Adjunto |
| N.° 10 | Matriz de trazabilidad objetivos → requisitos → funcionalidad → evidencia | `documentacion/03_gestion_scrum/Matriz_Trazabilidad.md` | Adjunto |
| N.° 11 | Actas de Sprint Review y Retrospectiva (Sprints 1 y 2) | `documentacion/03_gestion_scrum/Actas_Sprint.md` | Adjunto |
| N.° 12 | Plantilla de captura de la ficha de extracción | `documentacion/02_instrumentos/Plantilla_Extraccion_Anexo_04.csv` | En uso |
| N.° 13 | Guía de despliegue del sistema | `DESPLIEGUE.md` | Adjunto |
