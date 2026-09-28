**UNIVERSIDAD CATÓLICA SANTO TORIBIO DE MOGROVEJO**

**FACULTAD DE INGENIERÍA**

**ESCUELA DE INGENIERÍA DE SISTEMAS Y COMPUTACIÓN**

---

**SISTEMA DE SOPORTE CLÍNICO CON APRENDIZAJE AUTOMÁTICO PARA PREVENIR EL INCUMPLIMIENTO TERAPÉUTICO EN PACIENTES HIPERTENSOS Y DIABÉTICOS POLIMEDICADOS DEL CONSULTORIO MÉDICO MILKO UGAZ ZEGARRA**

**PRE INFORME DE TESIS (AVANCE AL 100 %)**

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

Sistema de soporte clínico con aprendizaje automático para prevenir el incumplimiento terapéutico en pacientes hipertensos y diabéticos polimedicados del consultorio médico Milko Ugaz Zegarra.

**3. Autor y firma**

| Autor |
| :-: |
| Leonardo Jesús Guzmán Salazar |
| _______________________ |

**4. Línea y área de la investigación**

**Línea de investigación:** Desarrollo e innovación tecnológica. **Área:** Ingeniería y tecnología.

**5. Fecha de presentación**

28 de septiembre de 2026 (cierre del desarrollo; Hito 3 del cronograma, semana 8).

**6. Estado del avance**

| Sprint | Semanas | Estado |
| :--- | :---: | :--- |
| Sprint 1 (CRISP-DM: *Business & Data Understanding*) | 2–3 | Cerrado |
| Sprint 2 (CRISP-DM: *Data Preparation* y *Modeling* inicial) | 3–4 | Cerrado |
| Sprint 3 (CRISP-DM: *Modeling* y *Evaluation*) | 5–6 | Cerrado |
| Sprint 4 (CRISP-DM: *Deployment*) | 7–8 | Cerrado en su alcance de desarrollo |

> **Convención de lectura.** El desarrollo está cerrado: los diez requisitos funcionales y los seis no funcionales operan y están verificados. Tres resultados dependen del trabajo de campo y no del software —la extracción de historias clínicas (Anexo n.° 04), el test de Morisky-Green y la evaluación de usabilidad con usuarios—; se reportan con su estado, su instrumento y el procedimiento que los convierte en resultado. Mientras tanto, el sistema y el modelo funcionan con un **conjunto de demostración** que permite verificar el protocolo de extremo a extremo.

---

# ÍNDICE

- **I. RESULTADOS**
  - **1.1. En base a la metodología utilizada**
    - 1.1.1. Descripción del producto
    - 1.1.2. Product Backlog general
    - 1.1.3. Sprint 1: Comprensión del negocio y de los datos
    - 1.1.4. Sprint 2: Preparación de datos y núcleo funcional
    - 1.1.5. Sprint 3: Modelo integrado y funcionalidades complementarias *(en ejecución)*
    - 1.1.6. Sprint 4: Cierre, rendimiento y validación
    - 1.1.7. Demostración del escenario principal
    - 1.1.8. Registro consolidado de incidencias
  - **1.2. En base a los objetivos del proyecto**
    - 1.2.1. OE1 – Caracterización del proceso actual de seguimiento terapéutico
    - 1.2.2. OE2 – Determinación de los requisitos funcionales y no funcionales
    - 1.2.3. OE3 – Determinación del algoritmo con mayor capacidad predictiva
    - 1.2.4. OE4 – Construcción del sistema de soporte clínico
    - 1.2.5. OE5 – Evaluación de la usabilidad mediante la escala SUS
  - **1.3. Limitaciones del estudio y trabajo futuro**
  - **1.4. Cierre del desarrollo y trabajo de campo pendiente**
- **II. REFERENCIAS BIBLIOGRÁFICAS**
- **ANEXOS**

---

# I. RESULTADOS

## 1.1. En base a la metodología utilizada

El producto se desarrolla integrando **SCRUM y CRISP-DM**. El sprint de SCRUM es la unidad de trabajo; las fases de CRISP-DM se ejecutan dentro de los sprints. Así, cada sprint entrega a la vez un incremento de software y un avance del modelo predictivo [1], [2].

**Tabla 1.** Correspondencia entre sprints, fases de CRISP-DM e hitos del cronograma.

| Sprint | Objetivo | Fase CRISP-DM | Semanas | Hito | Estado |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **1** | Planificación y primer incremento | *Business* y *Data Understanding* | 2–3 | 30 % | **Cerrado** |
| **2** | Núcleo funcional y modelado inicial | *Data Preparation* y *Modeling* inicial | 3–4 | 40 % / 50 % | **Cerrado** |
| **3** | Modelo integrado, alertas y estabilización | *Modeling* (selección) y *Evaluation* | 5–6 | 65 % / 80 % | **Cerrado** |
| **4** | Cierre, rendimiento y usabilidad | *Deployment* | 7–8 | 90 % / 100 % | **Cerrado** |

---

### 1.1.1. Descripción del producto

#### a) Función principal

El sistema **anticipa qué pacientes polimedicados tienen mayor probabilidad de dejar su tratamiento** antes del próximo control, para que el médico intervenga a tiempo. Hoy el consultorio se entera del incumplimiento cuando el paciente ya se descompensó.

Para lograrlo, el sistema hace tres cosas:

1. **Registra la toma real** de cada medicamento desde el celular del paciente, con recordatorios y confirmación de un familiar.
2. **Calcula el riesgo** de incumplimiento de cada paciente con un modelo de aprendizaje automático.
3. **Avisa al médico** cuando un paciente empieza a fallar, sin que tenga que revisarlos uno por uno.
4. **Muestra al médico** la ficha, la adherencia observada, el riesgo predicho y reportes de todos sus pacientes.

La decisión clínica sigue siendo del médico: el sistema es un apoyo, no un diagnóstico.

#### b) Estructura del producto

**Tabla 2.** Componentes del producto y sus usuarios.

| Componente | Tecnología | Usuario | Qué hace |
| :--- | :--- | :--- | :--- |
| Panel web | React + Vite (Vercel) | Médico | Registra pacientes, consulta fichas, alertas, riesgo y reportes; genera el acceso móvil del paciente |
| Aplicación móvil | Flutter (Android) | Paciente y familiar | Recordatorios, registro de tomas sin conexión, grupo familiar y corroboración |
| API central | FastAPI (Render) | — | Autenticación, reglas del negocio y cálculo de indicadores |
| Microservicio de inferencia | FastAPI + scikit-learn + SHAP (Render) | — | Carga el modelo, calcula el riesgo de cada paciente y lo explica con SHAP |
| Pipeline de entrenamiento | scikit-learn (`ml-pipeline`) | — | Prepara los datos, compara algoritmos y genera el modelo que usa el microservicio |
| Base de datos | PostgreSQL (Aiven) | — | Guarda usuarios, fichas, tomas y grupo familiar |

#### c) Arquitectura y justificación

Se eligió una **arquitectura de microservicios**: los dos clientes (web y móvil) se comunican solo con la API central mediante REST; la API es la única que accede a la base de datos y consulta, también por REST, al **microservicio de inferencia**, que es el único que carga el modelo.

**Flujo:** panel web / app móvil → API central → base de datos · API central → microservicio de inferencia → modelo.

| Decisión | Razón |
| :--- | :--- |
| Una API central para web y móvil | Las reglas clínicas y de seguridad se escriben una sola vez y valen para ambos clientes |
| Modelo en un microservicio propio | Se reentrena, reemplaza o escala sin detener el resto del sistema (RNF06); si falla, la consulta clínica sigue funcionando |
| Clave entre servicios y ficha anonimizada | El microservicio solo recibe variables clínicas con el código P-00N, nunca nombres ni contactos (RNF01) |
| Aplicación móvil con cola local | El paciente registra su toma aunque no tenga señal; se envía al recuperar conexión |
| Servicios en la nube gestionados | Despliegue real sin administrar servidores, con conexión cifrada (RNF01) |

#### d) Tecnologías elegidas y por qué

Cada herramienta se eligió por su relación con un objetivo o una restricción del proyecto, no por familiaridad.

**Tabla 3.** Justificación de las tecnologías frente a los objetivos del proyecto.

| Herramienta | Para qué | Por qué esta y no otra |
| :--- | :--- | :--- |
| **FastAPI** (API central) | Servicios REST con validación estricta de las variables del Anexo n.° 04 (OE2, OE4) | Valida y documenta el contrato a partir del propio código, de modo que una ficha con datos imposibles se rechaza en el borde del sistema. Frente a Django, evita arrastrar un marco completo para un servicio que solo expone JSON |
| **PostgreSQL** (Aiven) | Guardar la historia clínica y la traza de tomas (OE4, RNF01) | Permite escribir las reglas clínicas como restricciones de la propia base —polimedicación, coherencia de controles, una sola toma por horario—, que es lo que impide que un dato inválido llegue al conjunto de entrenamiento. Una base documental no las garantizaría |
| **SQLAlchemy y Alembic** | Modelo de datos y migraciones versionadas (OE4) | El esquema clínico cambió cinco veces durante el desarrollo; cada cambio quedó como una migración aplicable y reversible, en lugar de un script manual |
| **React + Vite** (panel) | Interfaz del médico: ficha, alertas y reportes (OE4, RNF03) | La ficha cambia continuamente mientras el médico filtra, edita o atiende alertas; un modelo declarativo evita sincronizar la pantalla a mano. Vite acorta el ciclo de cambio y produce un paquete estático desplegable sin servidor |
| **Flutter** (aplicación del paciente) | Registro de tomas, recordatorios y grupo familiar (OE4, RF03, RF08, RF09) | Una sola base de código para el teléfono, con avisos locales y base de datos propia para la cola sin conexión: el paciente registra su toma aunque no tenga señal, que es el escenario en el que más falta hace |
| **scikit-learn** | Preparación, comparación de algoritmos y modelo en servicio (OE3) | Reúne en un solo objeto la imputación, la codificación, el escalado y el clasificador, lo que garantiza que la inferencia aplique exactamente la misma transformación que el entrenamiento |
| **imbalanced-learn (SMOTE)** | Balancear la clase minoritaria dentro de la validación cruzada (OE3) | Permite encadenar el balanceo en el mismo pipeline, de modo que se reajuste en cada pliegue; hacerlo aparte habría inflado las métricas [8] |
| **SHAP** | Explicar cada predicción al médico (RF06) | Es el único método con el que las contribuciones suman exactamente la probabilidad del paciente [11], y su explicador por permutaciones funciona con el SVM seleccionado, que no tiene coeficientes interpretables |
| **Render y Vercel** | Publicar API, microservicio y panel (OE4) | Despliegue continuo desde el repositorio, con HTTPS y variables de entorno, sin administrar servidores: el proyecto es una tesis de pregrado y no dispone de infraestructura propia |
| **pytest y flutter test** | Verificación automatizada (OE4, RNF04) | Convierten cada regla clínica y cada riesgo en una prueba repetible; son las que detectaron 18 de las 22 incidencias antes de que llegaran al usuario [13] |

#### e) Variables que respaldan el sistema

Las variables siguen el **modelo multidimensional de adherencia de la OMS** [3], que agrupa las causas del incumplimiento en cinco dimensiones. Cada variable se registra en la ficha del panel y en el Anexo n.° 04.

**Tabla 4.** Variables del modelo predictivo.

| Dimensión OMS | Variables | Origen |
| :--- | :--- | :--- |
| Paciente | Edad, sexo | Historia clínica |
| Socioeconómica y social | Nivel educativo, convivencia (vive solo o acompañado), apoyo familiar en la medicación | Historia clínica o entrevista |
| Enfermedad | Diagnóstico (HTA, DM2 o ambas), tiempo de enfermedad, comorbilidades (lista marcada; el modelo usa el total) | Historia clínica |
| Terapia | Número de fármacos, tomas por día | Historia clínica |
| Sistema de salud | Controles programados y controles perdidos en 6 meses | Historia clínica |
| *Variables derivadas* | Carga terapéutica (fármacos × tomas), tasa de inasistencia (perdidos ÷ programados), cronicidad relativa (tiempo de enfermedad ÷ edad/10) | Calculadas por el sistema |
| *Variable objetivo* | Incumplimiento (sí/no) según el test de Morisky-Green | Entrevista al paciente (Anexo n.° 05) |

El puntaje de Morisky **no se usa como predictor**, porque de él sale la etiqueta: usarlo inflaría artificialmente los resultados.

#### f) Origen de los datos

| Fuente | Qué aporta | Estado |
| :--- | :--- | :--- |
| Historias clínicas del consultorio (Anexo n.° 04) | Las variables de la ficha, anonimizadas con un código P-001, P-002… | En extracción |
| Test de Morisky-Green (Anexo n.° 05) | La etiqueta de adherencia de cada paciente | En aplicación |
| Aplicación móvil | Las tomas registradas y corroboradas: la adherencia observada día a día | Operativa |

Hasta concluir la extracción, el sistema funciona con **pacientes de demostración** (códigos D-001 a D-005) y el modelo está entrenado con un **conjunto de demostración de 400 fichas**; la propia ficha del paciente lo indica en pantalla.

#### g) Modelo predictivo y entrenamiento

El entrenamiento se ejecuta con `ml-pipeline/src/train_evaluate.py` y sigue estos pasos:

1. **Limpieza:** elimina duplicados, anula valores fuera de rango y excluye a quien no cumple el criterio de polimedicación.
2. **Partición:** 80 % entrenamiento y 20 % prueba, conservando la proporción de adherentes e incumplidores.
3. **Preparación:** completa los datos faltantes (mediana o moda), codifica las categorías y estandariza los números.
4. **Balanceo con SMOTE** [8]: genera casos sintéticos de incumplimiento, solo con datos de entrenamiento.
5. **Comparación de cuatro algoritmos:** Regresión Logística, Random Forest, XGBoost y SVM, con ajuste de hiperparámetros y validación cruzada de 5 pliegues.
6. **Selección:** gana el de mayor AUCROC. Si la prueba de McNemar no encuentra diferencia significativa con el segundo, gana el de mayor sensibilidad, porque el error más costoso es no detectar a un paciente en riesgo.
7. **Evaluación final** sobre el 20 % de prueba, que el modelo nunca vio.
8. **Despliegue:** se guarda el modelo completo (preparación + algoritmo) y el microservicio de inferencia lo usa para calcular la probabilidad de cada paciente.

La probabilidad se traduce en tres niveles: **bajo** (menos de 40 %), **medio** (40 % a 69 %) y **alto** (70 % o más).

**Explicación con SHAP [11].** Para cada paciente, el microservicio calcula cuánto sube o baja el riesgo cada variable de su ficha respecto de un paciente de referencia. La suma de esas contribuciones lleva exactamente de la probabilidad de referencia a la del paciente, de modo que el médico ve **por qué** ese paciente tiene ese riesgo.

#### h) Cómo se calculan los porcentajes y promedios

**Tabla 5.** Indicadores que muestra el sistema.

| Indicador | Cálculo |
| :--- | :--- |
| Cumplimiento del paciente | Tomas cumplidas (a tiempo o con retraso) ÷ tomas con desenlace (cumplidas + omitidas) × 100. Las pospuestas no cuentan |
| Retraso promedio | Promedio de minutos entre la hora prescrita y la hora en que se registró cada toma cumplida |
| Omisiones consecutivas | Tomas omitidas seguidas, contadas desde la más reciente |
| Riesgo observado | **Alto:** cumplimiento < 60 % o 3+ omisiones seguidas. **Medio:** < 80 % o 2 seguidas. **Bajo:** en otro caso. Resume lo que el paciente ya hizo |
| Riesgo predicho | Probabilidad que devuelve el modelo con la ficha del paciente. Anticipa lo que puede ocurrir |
| Por qué tiene ese riesgo (SHAP) | Contribución de cada variable, en puntos porcentuales: positiva si aumenta el riesgo, negativa si lo reduce. Probabilidad de referencia + contribuciones = probabilidad del paciente |
| Adherencia promedio (reportes) | Promedio del cumplimiento de los pacientes con tomas registradas; cada paciente pesa lo mismo |
| Tomas corroboradas (reportes) | Tomas cumplidas confirmadas por un familiar ÷ total de tomas cumplidas × 100 |
| Alerta temprana | Se genera cuando el paciente acumula 3 omisiones seguidas, su cumplimiento baja del 60 % con al menos 5 tomas registradas, o el modelo lo clasifica en riesgo alto |

---

### 1.1.2. Product Backlog general

La pila se priorizó con **MoSCoW** según su relación con la hipótesis: *Must* si sin él no se puede contrastar la hipótesis; *Should* si aporta valor clínico importante; *Could* si mejora la experiencia. La estimación usa puntos de Fibonacci.

**Tabla 6.** Product Backlog general refinado.

| ID | Historia de usuario | Criterio de aceptación | Prioridad | Pts | Sprint | Estado |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| RF01 | Como médico o paciente, quiero iniciar sesión con mi perfil para ver solo lo que me corresponde | Acceso solo con credenciales y perfil válidos; el error no revela qué dato falló | Must | 13 | 1 | **Terminado** |
| RF02 | Como médico, quiero registrar y editar la ficha del paciente polimedicado para mantener sus datos clínicos al día | Ficha guardada y consultable; se rechaza a pacientes con menos de 5 fármacos | Must | 24 | 2–3 | **Terminado** |
| RF03 | Como paciente, quiero registrar cada toma desde mi celular para que mi médico conozca mi cumplimiento real | Cada toma queda registrada y sincronizada, sin duplicarse al reenviar | Must | 16 | 2 | **Terminado** |
| RF04 | Como médico, quiero ver el riesgo de incumplimiento de cada paciente para priorizar a quién contactar | Un microservicio calcula probabilidad y nivel; el sistema sigue operando si el microservicio falla | Must | 21 | 3 | **Terminado** |
| RF05 | Como médico, quiero recibir alertas cuando un paciente pase a riesgo alto para actuar antes del control | Bandeja con el motivo y la cifra que lo sustenta; el médico registra qué hizo y el aviso no se repite mientras tanto | Must | 15 | 3 | **Terminado** |
| RF06 | Como médico, quiero saber qué factores explican el riesgo de un paciente para decidir la intervención | Contribución individual de cada variable (SHAP) en la ficha; las contribuciones suman la probabilidad | Should | 8 | 3 | **Terminado** |
| RF07 | Como médico, quiero reportes generales de mis pacientes para auditar la adherencia | Panel con indicadores globales, distribución de riesgo y exportación CSV | Should | 10 | 2–3 | **Terminado** |
| RF08 | Como paciente, quiero recibir recordatorios de mis tomas para no olvidarlas | Aviso en el teléfono a la hora de cada toma, aun sin conexión | Could | 8 | 3 | **Terminado** |
| RF09 | Como paciente, quiero que un familiar confirme mis tomas para que el registro no dependa solo de mi palabra | El familiar se une con un código de un solo uso y solo corrobora tomas cumplidas de las últimas 48 h | Should | 18 | 3 | **Terminado** |
| RF10 | Como usuario, quiero recuperar mi contraseña por correo para no acudir al consultorio por un olvido | Enlace de un solo uso válido 30 minutos; la respuesta no revela si el correo existe | Should | 5 | 3 | **Terminado** |

**Refinamiento de la pila.** La pila se revisó al cierre de cada sprint:

- **Sprint 2:** la exportación de reportes (RF07) pasó al Sprint 3.
- **Sprint 3:** se incorporaron **RF09** y **RF10**, nacidos de la revisión del producto: el registro de tomas dependía solo del paciente, y la recuperación de contraseña obligaba a ir al consultorio.
- **Sprint 3:** RF04 se amplió con la separación del modelo en un microservicio de inferencia, para ajustarse a la arquitectura aprobada en el proyecto.
- **Sprint 3:** se refinaron las variables de la ficha (RF02). La literatura asocia el nivel socioeconómico con la adherencia en población atendida en establecimientos públicos [5]; en una clínica privada, en cambio, esa variable, el tipo de seguro y la zona de residencia casi no varían entre pacientes, de modo que no ayudan a distinguir quién incumple. Se reemplazaron por **nivel educativo, convivencia y apoyo familiar**, que sí varían y se relacionan con la comprensión de las indicaciones y el olvido, las causas señaladas por el médico. Las comorbilidades pasaron de un número a una **lista de enfermedades**, para que la ficha sea específica.

---

### 1.1.3. Sprint 1: Comprensión del negocio y de los datos

**Semanas 2–3 · CRISP-DM: *Business Understanding* y *Data Understanding*.**

**Objetivo.** Entender el problema clínico, priorizar la pila y entregar la autenticación (RF01).

**Tabla 7.** Sprint Backlog del Sprint 1.

| Elemento | Tarea | Componente | Pts | Estado |
| :---: | :--- | :--- | :---: | :--- |
| OE1 | Entrevista semiestructurada al médico y diagnóstico | Documentación | 3 | **Terminada** |
| OE1 | Clasificación de factores de incumplimiento por dimensión OMS | Documentación | 3 | **Terminada** |
| OE2 | Product Backlog priorizado e historias de usuario | Documentación | 2 | **Terminada** |
| RF01 | Modelo de datos inicial (usuario, paciente, registro de toma) | API | 5 | **Terminada** |
| RF01 | Inicio de sesión con token y control por perfil | API | 5 | **Terminada** |
| RF01 | Pantalla de acceso del panel | Web | 3 | **Terminada** |
| — | Repositorio, entorno y migraciones | Infraestructura | 3 | **Terminada** |
| | **Comprometido: 24 · Completado: 24 (100 %)** | | **24** | |

#### a) Diagnóstico del consultorio

Se aplicó la entrevista semiestructurada (Anexo n.° 03) al Dr. Milko Ugaz Zegarra. Hallazgos principales:

1. El seguimiento se basa **solo en lo que el paciente dice** en la consulta; no hay registro digital ni alertas.
2. El incumplimiento se detecta **tarde**, cuando el paciente ya se descompensó.
3. El consultorio atiende a unos **50 pacientes polimedicados** con hipertensión y/o diabetes.
4. Las causas percibidas son **el olvido, la complejidad del tratamiento y la falta de comprensión** de las indicaciones.

**Tabla 8.** Brechas identificadas y requisitos que las atienden.

| N.° | Brecha | Consecuencia | Requisito |
| :---: | :--- | :--- | :---: |
| B1 | No hay registro de la toma de medicamentos | El cumplimiento real no se puede verificar | RF03, RF07, RF09 |
| B2 | No hay seguimiento entre citas | Detección tardía | RF02, RF03 |
| B3 | No se analizan los datos clínicos | No se puede anticipar el incumplimiento | RF04, RF06 |
| B4 | No hay alertas ni recordatorios | El olvido no se mitiga | RF05, RF08 |

#### b) Factores de incumplimiento

**Tabla 9.** Factores identificados por dimensión OMS [3].

| Dimensión OMS | Factores en el consultorio | Variable asociada |
| :--- | :--- | :--- |
| Paciente | Olvido; falta de comprensión de las indicaciones | Edad, sexo |
| Socioeconómica y social | Nivel de instrucción; soledad o falta de apoyo en casa | Nivel educativo, convivencia, apoyo familiar |
| Enfermedad | Cronicidad y multimorbilidad | Diagnóstico, tiempo de enfermedad, comorbilidades |
| Terapia | Muchos fármacos y tomas | N.° de fármacos, tomas por día |
| Sistema de salud | Inasistencia a controles | Controles programados y perdidos |

**Línea base de contexto.** El 37,1 % de los pacientes peruanos con hipertensión y diabetes tiene adherencia deficiente [4]; en Lambayeque, el 44,7 % de los pacientes crónicos no cumple su tratamiento [6]. La línea base propia del consultorio se obtiene con el test de Morisky-Green (en ejecución).

#### c) Incremento: autenticación (RF01)

Se implementó el inicio de sesión con token JWT y control de acceso por perfil (`backend-api/app/api/auth.py`). Ante cualquier error de acceso se devuelve la misma respuesta, para no revelar qué correos están registrados.

**Tabla 10.** Pruebas del Sprint 1.

| Caso | Esperado | Obtenido |
| :--- | :--- | :---: |
| Credenciales y perfil válidos | Acceso con token | ✔ `200` |
| Perfil equivocado o usuario inexistente | Rechazo sin indicar la causa | ✔ `401` |
| Consulta sin token | Rechazo | ✔ `401` |
| Correo mal formado o contraseña corta | Error por campo | ✔ `422` |

**Tabla 11.** Incidencias del Sprint 1.

| ID | Componente | Incidencia | Causa | Corrección | Estado |
| :---: | :--- | :--- | :--- | :--- | :---: |
| I-01 | API / Datos | Reglas clínicas repartidas entre el código y la base de datos | No había un criterio de dónde ubicar cada regla | Llevarlas a restricciones de la base de datos (Sprint 2) | Cerrada |

**Review y retrospectiva.** Se aceptó RF01 y se validaron con el médico el modelo de datos y la pila. Mejora acordada: centralizar las reglas clínicas en la base de datos.

---

### 1.1.4. Sprint 2: Preparación de datos y núcleo funcional

**Semanas 3–4 · CRISP-DM: *Data Preparation* y *Modeling* inicial.**

**Objetivo.** Completar el núcleo funcional (RF01–RF03), preparar el pipeline de datos y configurar la comparación de algoritmos.

**Tabla 12.** Sprint Backlog del Sprint 2.

| Elemento | Tarea | Componente | Pts | Estado |
| :---: | :--- | :--- | :---: | :--- |
| OE2 | Requisitos no funcionales y arquitectura | Documentación | 3 | **Terminada** |
| RF02 | Alta, consulta, edición y baja de pacientes | API | 5 | **Terminada** |
| RF02 | Reglas clínicas como restricciones de la base de datos | Datos | 3 | **Terminada** |
| RF02 | Formulario de alta y ficha del paciente | Web | 5 | **Terminada** |
| RF03 | Registro de tomas sin duplicados y envío en lote | API | 8 | **Terminada** |
| RF03 | Cola local sin conexión | Móvil | 8 | **Terminada** |
| RF07 | Panel de auditoría con listado por prioridad | Web | 5 | **Terminada** |
| RF07 | Exportación de reportes | Web | 5 | Trasladada al Sprint 3 |
| OE3 | `preprocess.py`: limpieza, faltantes, variables derivadas y SMOTE | ML | 8 | **Terminada** |
| OE3 | `train_evaluate.py`: cuatro algoritmos, validación cruzada y McNemar | ML | 8 | **Terminada** |
| RNF01/04 | Despliegue en Aiven, Render y Vercel | Infraestructura | 5 | **Terminada** |
| | **Comprometido: 63 · Completado: 58 (92 %)** | | **63** | |

#### a) Requisitos no funcionales

**Tabla 13.** Requisitos no funcionales (ISO/IEC 25010 [7]).

| Código | Requisito | Atributo | Cómo se cumple |
| :---: | :--- | :--- | :--- |
| RNF01 | Datos protegidos en tránsito y en reposo | Seguridad | HTTPS, cabeceras de seguridad, contraseñas cifradas, código anonimizado; 20 pruebas de verificación (Tabla 22) |
| RNF02 | Respuesta de la predicción en ≤ 2 s | Eficiencia | Tiempo medido en cada respuesta (≈ 13 ms por predicción) |
| RNF03 | Interfaz usable por médicos y adultos mayores | Usabilidad | Barra de navegación rotulada; evaluación SUS en el Sprint 4 |
| RNF04 | Disponibilidad para la consulta clínica | Fiabilidad | Manejo global de errores, sonda `/health`, reintento en la app y reintento de la conexión al arrancar el servicio |
| RNF05 | Código modular | Mantenibilidad | Capas `api`, `core`, `db`, `schemas`, `services` |
| RNF06 | Escalable y reentrenable | Portabilidad | Modelo desacoplado de la API |

#### b) Preparación de los datos

El Anexo n.° 04 se formalizó como el esquema del conjunto de datos, con una plantilla CSV que el pipeline valida columna por columna.

**Tabla 14.** Reglas de limpieza del pipeline.

| Regla | Tratamiento |
| :--- | :--- |
| Paciente duplicado | Se conserva el registro más reciente |
| Categoría o número fuera de rango | Se marca como faltante y se completa después |
| Controles perdidos mayores que programados | Se anula ese dato |
| Menos de 5 fármacos o sin etiqueta | Se excluye al paciente |

El balanceo con SMOTE se aplica **después** de separar entrenamiento y prueba, y dentro de cada pliegue de la validación cruzada, para que las métricas no salgan infladas.

#### c) Configuración de la comparación de algoritmos (OE3)

**Tabla 15.** Algoritmos candidatos.

| Algoritmo | Por qué se incluye | Hiperparámetros evaluados |
| :--- | :--- | :--- |
| Regresión Logística | Referencia simple e interpretable | `C` ∈ {0,01; 0,1; 1; 10} |
| Random Forest | Robusto con variables mixtas [9] | `n_estimators` ∈ {200; 500}, `max_depth` ∈ {None; 8; 12} |
| XGBoost | Referente en datos clínicos tabulares [10] | `learning_rate` ∈ {0,05; 0,1}, `max_depth` ∈ {3; 5; 7} |
| SVM (RBF) | Eficaz con muestras pequeñas | `C` ∈ {0,1; 1; 10}, `gamma` ∈ {scale; 0,01} |

Métricas: exactitud, sensibilidad, especificidad, F1-score y AUCROC (meta ≥ 0,80), con semilla fija 42.

#### d) Núcleo funcional (RF02 y RF03)

- **Pacientes:** el médico registra, edita y da de baja fichas; solo ve a sus propios pacientes.
- **Tomas:** la app envía cada toma; si la reenvía por falta de señal, se actualiza en lugar de duplicarse.
- **Despliegue:** base de datos en Aiven, API en Render y panel en Vercel, con conexión cifrada.

**Tabla 16.** Pruebas del Sprint 2 (selección).

| Grupo | Caso | Resultado |
| :--- | :--- | :---: |
| RF02 | Alta guardada con código correlativo | ✔ `201` |
| RF02 | Rechazo con menos de 5 fármacos o controles incoherentes | ✔ `422` |
| RF02 | Baja lógica: el historial se conserva | ✔ |
| RF03 | Reenvío de la misma toma no duplica | ✔ `201` → `200` |
| RF03 | Cumplimiento: 3 cumplidas de 5 = 60 % | ✔ |
| Seguridad | Médico ajeno o paciente sin permiso | ✔ `403` |
| Despliegue | Documentación oculta y `Host` falsificado rechazado en producción | ✔ `404` / `403` |

**Tabla 17.** Incidencias del Sprint 2.

| ID | Componente | Incidencia | Causa | Corrección | Estado |
| :---: | :--- | :--- | :--- | :--- | :---: |
| I-02 | ML | La preparación fallaba al completar categorías vacías | Los imputadores no reconocen `pd.NA` | Convertir a `NaN` antes de imputar | Cerrada |
| I-03 | Datos | La base guardaba `MASCULINO` en vez de `M` | Comportamiento por defecto de SQLAlchemy | Guardar el valor del catálogo | Cerrada |
| I-04 | Web | El contenido desbordaba la página | Alto fijo sin contenedor definido | Usar alto mínimo | Cerrada |
| I-05 | Móvil | La app no arrancaba | Tamaño de letra nulo en el tema | Fijar tamaños explícitos | Cerrada |
| I-06 | Móvil | Un fallo de red se mostraba como demora del servidor | Tipo de excepción mal capturado | Distinguir ambos errores | Cerrada |
| I-07 | API | Mensajes de validación con prefijo técnico | Texto de la librería sin depurar | Limpiar el mensaje | Cerrada |

**Review y retrospectiva.** Se aceptaron el núcleo RF01–RF03, el pipeline y la configuración experimental. Mejora acordada: verificar el comportamiento de cada librería en su documentación antes de usarla.

---

### 1.1.5. Sprint 3: Modelo integrado y funcionalidades complementarias *(cerrado)*

**Semanas 5–6 · CRISP-DM: *Modeling* (selección) y *Evaluation*.**

**Objetivo.** Integrar el modelo al sistema mediante un microservicio de inferencia con explicación SHAP, completar la app del paciente y el grupo familiar, y seleccionar el algoritmo.

**Tabla 18.** Sprint Backlog del Sprint 3.

| Elemento | Tarea | Componente | Pts | Estado |
| :---: | :--- | :--- | :---: | :--- |
| RF04 | Servicio de predicción | API | 8 | **Terminada** |
| RF04 | Tarjeta de riesgo predicho en la ficha | Web | 5 | **Terminada** |
| RF04 | Microservicio de inferencia independiente y cliente REST en el API | ML + API | 8 | **Terminada** |
| RF08 | Recordatorios en el dispositivo | Móvil | 5 | **Terminada** |
| RF08 | APK de publicación | Móvil | 3 | **Terminada** |
| RF09 | Grupo familiar y corroboración | API | 8 | **Terminada** |
| RF09 | Pantallas del paciente y del familiar | Móvil | 8 | **Terminada** |
| RF09 | Columna «Testigo» en el historial | Web | 2 | **Terminada** |
| RF10 | Recuperación de contraseña por correo | API + Web | 5 | **Terminada** |
| RF02 | Acceso móvil generado desde el panel | API + Web | 3 | **Terminada** |
| RF02 | Validación de la ficha en el formulario | Web | 3 | **Terminada** |
| RF02 | Refinamiento de variables: contexto social y lista de comorbilidades | API + Web + ML | 5 | **Terminada** |
| RF07 | Reportes generales y exportación CSV *(del Sprint 2)* | API + Web | 5 | **Terminada** |
| RNF03 | Barra inferior de navegación | Móvil | 3 | **Terminada** |
| RNF04 | Reintento ante el arranque lento del servidor | Móvil | 2 | **Terminada** |
| OE3 | Corrida de verificación del protocolo de selección | ML | 3 | **Terminada** |
| RF05 | Reglas de alerta y bandeja del médico | API | 5 | **Terminada** |
| RF05 | Pantalla de alertas con cierre y nota | Web | 5 | **Terminada** |
| RNF01 | Batería de verificación de seguridad del API | API | 5 | **Terminada** |
| RF06 | Explicación individual con SHAP | ML + Web | 8 | **Terminada** |
| OE3 | Comparación sobre las historias clínicas reales | ML | 5 | Bloqueada: depende de la extracción |
| | **Comprometido: 104 · Completado: 99 (95 %)** | | **104** | |

#### a) Microservicio de inferencia (RF04)

El modelo se separó del API central en el servicio `ml-service`, desplegado de forma independiente. El API le envía por REST la ficha anonimizada con una clave de servicio y recibe la probabilidad, el nivel, las variables que faltaban y la explicación SHAP.

| Ruta del microservicio | Qué devuelve |
| :--- | :--- |
| `GET /modelo` | Algoritmo, fecha de entrenamiento y procedencia de los datos |
| `POST /predicciones` | Probabilidad, nivel y explicación SHAP de un paciente |
| `POST /predicciones/lote` | Probabilidad y nivel de varios pacientes (para reportes) |
| `GET /health` | Disponibilidad del servicio |

Si el microservicio no responde, la ficha y los reportes se muestran sin el riesgo predicho y el resto del sistema sigue operando.

#### b) Explicación individual con SHAP (RF06)

El microservicio aplica el explicador por permutaciones de SHAP [11], que funciona con cualquier algoritmo, incluido el SVM seleccionado. La referencia son 12 perfiles promedio del entrenamiento (centroides), no fichas de pacientes reales. La ficha muestra las seis variables con más peso, con barras que suben o bajan el riesgo.

**Tabla 19.** Verificación de la explicación SHAP.

| Verificación | Resultado |
| :--- | :--- |
| Probabilidad de referencia + contribuciones = probabilidad del paciente | ✔ Cumple en todas las pruebas (tolerancia 0,005) |
| Coincidencia con el explicador *Kernel* de SHAP | ✔ Correlación 0,993; diferencia máxima 0,029 |
| Misma ficha, misma explicación | ✔ Reproducible |
| Más controles perdidos, mayor contribución de la inasistencia | ✔ |
| Tiempo de respuesta con el servicio activo | ✔ ≈ 90 ms (meta RNF02: ≤ 2 s) |

**Ejemplo con el paciente de demostración D-001.** Riesgo predicho 54 % frente a 34 % del paciente de referencia. Suben el riesgo: controles perdidos (+21,5 pp), inasistencia a controles (+15,4 pp) y tiempo de enfermedad (+6,9 pp). Lo bajan: controles programados (−11,0 pp), apoyo familiar en la medicación (−8,5 pp) y número de fármacos (−6,9 pp).

#### c) Selección del algoritmo: corrida de verificación

El protocolo completo se ejecutó sobre el conjunto de demostración (400 fichas: 320 de entrenamiento y 80 de prueba). En la preparación, el 2,25 % de las celdas estaba vacío (tiempo de enfermedad 12 %, nivel educativo 8 %, convivencia 5 %, edad 2 %) y la proporción fue de 334 adherentes y 66 incumplidores; SMOTE equilibró el entrenamiento a 267 y 267.

**Tabla 20.** Comparación de algoritmos en la corrida de verificación (validación cruzada de 5 pliegues; media ± desviación).

| Algoritmo | Hiperparámetros | Exactitud | Sensibilidad | Especificidad | F1-score | AUCROC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Regresión Logística | `C=1` | 0,781 ± 0,049 | 0,625 ± 0,094 | 0,813 ± 0,056 | 0,490 ± 0,074 | **0,864 ± 0,047** |
| **SVM (RBF)** *(seleccionado)* | `C=1`, `gamma=0,01` | 0,762 ± 0,047 | **0,794 ± 0,064** | 0,757 ± 0,060 | 0,530 ± 0,056 | 0,856 ± 0,044 |
| Random Forest | `n_estimators=500`, `max_depth=8` | 0,822 ± 0,051 | 0,494 ± 0,167 | 0,888 ± 0,036 | 0,477 ± 0,140 | 0,825 ± 0,057 |
| XGBoost | `learning_rate=0,05`, `max_depth=3` | 0,816 ± 0,030 | 0,455 ± 0,081 | 0,888 ± 0,026 | 0,450 ± 0,074 | 0,815 ± 0,063 |

**Lectura.** Los cuatro algoritmos superan la meta de AUCROC ≥ 0,80. Regresión Logística obtuvo el mayor AUCROC, pero la prueba de McNemar frente a SVM no mostró diferencia significativa (10 casos discordantes, *p* = 0,754). Por el criterio de desempate se seleccionó **SVM**, que detecta más incumplidores (sensibilidad 0,794 frente a 0,625). En el conjunto de prueba, SVM obtuvo exactitud 0,775, sensibilidad 0,615, especificidad 0,806, F1-score 0,471 y AUCROC 0,809. Estas cifras verifican que el protocolo y el sistema funcionan; el resultado del OE3 se obtendrá con el mismo script sobre las historias clínicas reales.

#### d) Aplicación del paciente y grupo familiar (RF08, RF09, RF10)

- **App instalable** con barra inferior (Hoy, Medicinas, Familia, Mi cuenta) y recordatorios que funcionan sin conexión.
- **Grupo familiar:** el paciente invita a un familiar con un código; el familiar confirma las tomas cumplidas desde su teléfono. El historial del médico indica qué tomas tienen testigo.
- **Recuperación de contraseña** por enlace de un solo uso enviado al correo.
- **Acceso móvil:** el médico genera desde el panel la contraseña temporal del paciente.

#### e) Ficha refinada y reportes generales (RF02, RF07)

- **Ficha:** el formulario valida los datos antes de guardar, pide nivel educativo, convivencia y apoyo familiar, y permite marcar comorbilidades concretas; el sistema calcula el total.
- **Reportes generales:** nueva sección del panel con pacientes activos, adherencia promedio, tomas registradas y corroboradas, distribución del riesgo observado y predicho, pacientes por diagnóstico, comorbilidades y motivos de omisión más frecuentes, y una tabla de pacientes ordenada por riesgo exportable a CSV.

#### f) Alertas tempranas (RF05)

El sistema avisa al médico sin que tenga que revisar paciente por paciente, que es la brecha B4 del diagnóstico. Las reglas se evalúan al sincronizar una toma desde la aplicación y al abrir la bandeja.

**Tabla 21.** Reglas de alerta y su fundamento.

| Alerta | Cuándo se genera | Por qué ese umbral |
| :--- | :--- | :--- |
| Omisiones seguidas | 3 o más tomas omitidas consecutivas | Indica abandono en curso, no un olvido puntual |
| Adherencia baja | Cumplimiento menor al 60 % con al menos 5 tomas resueltas | Por debajo del 60 % la adherencia es deficiente; el mínimo de tomas evita avisar por el ruido de un paciente recién incorporado |
| Riesgo predicho alto | El modelo clasifica al paciente en riesgo alto | Es la única regla que mira hacia delante, y la razón de ser del componente inteligente |

**Tres decisiones para que la bandeja se siga leyendo.** Una bandeja con veinte avisos repetidos se deja de mirar, y entonces la alerta no sirve de nada:

1. **Un aviso abierto por tipo y paciente.** La evidencia nueva actualiza el aviso existente en lugar de crear otro.
2. **Los avisos se cierran solos** cuando la condición desaparece: si el paciente vuelve a cumplir, el aviso queda como resuelto con su historia intacta.
3. **Lo que el médico cierra no reaparece al instante.** Tras atender un aviso no vuelve en siete días, y tras descartarlo, en treinta, salvo que la evidencia empeore.

El médico cierra cada alerta con una nota de lo que hizo —una llamada, un control adelantado— y esa nota queda registrada: es la evidencia de que el sistema sirvió para intervenir a tiempo.

#### g) Verificación de seguridad (RNF01)

Se construyó una batería de 20 pruebas que comprueban lo que el sistema **no** debe hacer.

**Tabla 22.** Verificación de seguridad del API.

| Qué se comprueba | Resultado |
| :--- | :---: |
| Las contraseñas se guardan solo cifradas, y dos iguales producen cifrados distintos | ✔ |
| Un token firmado con otra clave, vencido o mal formado no da acceso | ✔ |
| Un paciente que se declara médico en su token sigue sin serlo | ✔ |
| El acceso y la recuperación responden igual exista o no la cuenta | ✔ |
| Un médico no alcanza fichas, historiales ni predicciones de pacientes ajenos | ✔ |
| El paciente no accede a las vistas del médico | ✔ |
| Una búsqueda con instrucciones SQL no altera la base | ✔ |
| Los errores no revelan trazas, consultas ni rutas internas | ✔ |
| Las respuestas llevan las cabeceras de seguridad y prohíben la caché | ✔ |
| Al microservicio no viajan nombres, documentos ni contactos | ✔ |

El cifrado del tráfico (TLS) y el cifrado en reposo son garantías de la plataforma y se verifican sobre el servicio desplegado: conexión HTTPS con HSTS en Render y `sslmode=require` contra Aiven.

**Tabla 23.** Pruebas automatizadas al corte.

| Componente | Casos | Alcance | Resultado |
| :--- | :---: | :--- | :---: |
| API central (`pytest`) | 142 | RF01–RF05, RF07, RF09, RF10, permisos, seguridad (RNF01), resistencia del arranque e integración real con el modelo | ✔ 142/142 |
| Microservicio de inferencia (`pytest`) | 13 | Predicción, lote, clave de servicio, propiedad aditiva de SHAP y versiones del modelo | ✔ 13/13 |
| App móvil (`flutter test`) | 40 | Sincronización sin conexión, reintento, recordatorios, acceso y grupo familiar | ✔ 40/40 |
| Panel web | — | Compilación y análisis estático; recorrido verificado en navegador | ✔ |
| **Total** | **195** | | **✔** |

**Tabla 24.** Incidencias del Sprint 3.

| ID | Componente | Incidencia | Causa | Corrección | Estado |
| :---: | :--- | :--- | :--- | :--- | :---: |
| I-08 | Móvil | La app instalada quedaba siempre «sin conexión» | Faltaba el permiso de internet en la versión de publicación | Declarar el permiso y verificar el APK | Cerrada |
| I-09 | API / ML | La predicción fallaba con fichas incompletas | Los campos vacíos llegaban como `None` | Convertirlos a `NaN` | Cerrada |
| I-10 | Móvil | Al cambiar la hora quedaba el aviso anterior | Se asumía el permiso denegado | Consultar el permiso real | Cerrada |
| I-11 | API | Un correo mal escrito rompía el listado | Validación estricta también en la salida | Validar solo al registrar | Cerrada |
| I-12 | Datos | Las fichas de demostración quedaban sin cuenta | La carga no completaba fichas existentes | Carga que completa lo que falta | Cerrada |
| I-13 | Web | El panel decía que la predicción aún no existía | Texto desactualizado | Actualizar el aviso | Cerrada |
| I-14 | API / Despliegue | En producción no aparecía la predicción | Faltaba una librería y la versión no coincidía con la del entrenamiento | Fijar versiones y probar con el modelo real | Cerrada |
| I-15 | Móvil | «Sin conexión» con internet disponible | El servidor gratuito tarda en despertar | Reintentar las consultas | Cerrada |
| I-16 | Web | No se guardaban cambios en fichas D- | Se validaba el código también al editar | Validarlo solo en el alta | Cerrada |
| I-17 | Web | La contraseña temporal desaparecía | Se recargaba la ficha al generarla | Recargar solo al ocultarla | Cerrada |
| I-18 | ML | El desempate por sensibilidad no se aplicaba | El código solo desempataba con AUCROC idéntico | Aplicar McNemar antes de elegir | Cerrada |
| I-19 | Microservicio | La primera explicación SHAP tardaba 5 s | SHAP se prepara internamente en su primer uso | Ejecutar una explicación de prueba al arrancar | Cerrada |
| I-20 | API | La alerta de riesgo predicho hacía fallar la bandeja | El umbral se trasladó al microservicio y el API seguía consultándolo | Usar el nivel de riesgo que devuelve el microservicio | Cerrada |
| I-21 | API | Una alerta cerrada por el médico reaparecía en la consulta siguiente | Las reglas no distinguían un caso ya atendido | Plazo de silencio tras atender o descartar, salvo que la evidencia empeore | Cerrada |
| I-22 | Despliegue | El servicio publicado dejó de arrancar y no se podía entrar al sistema | Las migraciones se aplican al arrancar y la base gestionada no resolvió su nombre en ese instante: un fallo de segundos tumbaba el despliegue entero | Reintentar la conexión (5 s, 15 s y 30 s) antes de rendirse, con un mensaje que indica qué revisar | Cerrada |

**Cierre del sprint.** Se entregaron todos los elementos comprometidos salvo la comparación de algoritmos sobre las historias clínicas reales, que no depende del desarrollo sino de la extracción documental y se arrastra al Sprint 4.

**Sprint Review (Sprint 3).** Se aceptaron el microservicio de inferencia con explicación SHAP, las alertas tempranas, el acceso móvil, los reportes y la verificación de seguridad. **Retrospectiva:** los tres defectos que solo aparecieron sobre el servicio publicado (I-14, I-15 e I-22) llevaron a incorporar al procedimiento la verificación sobre el entorno desplegado y no solo en local, y a que el arranque del servicio reintente la conexión en lugar de rendirse al primer fallo.

---

### 1.1.6. Sprint 4: Cierre, rendimiento y validación

**Semanas 7–8 · CRISP-DM: *Deployment*.**

**Objetivo.** Medir el rendimiento del sistema con usuarios simultáneos, verificar los atributos de calidad, evaluar la usabilidad con usuarios reales y consolidar las evidencias.

**Tabla 25.** Sprint Backlog del Sprint 4 (semanas 7–8).

| Elemento | Tarea | Componente | Pts | Estado |
| :---: | :--- | :--- | :---: | :--- |
| RNF02 / RNF06 | Prueba de rendimiento y carga con usuarios simultáneos | API | 8 | **Terminada** |
| RNF01–RNF06 | Verificación de los atributos ISO/IEC 25010 | Todos | 5 | **Terminada** |
| — | Guion de demostración y despertador de servicios | Documentación | 3 | **Terminada** |
| — | Consolidación del repositorio y de las evidencias | Documentación | 3 | **Terminada** |
| OE5 | Pruebas de usabilidad con la escala SUS | Web + Móvil | 8 | Pendiente: requiere usuarios reales |
| OE3 | Comparación sobre las historias clínicas reales *(del Sprint 3)* | ML | 5 | Bloqueada: depende de la extracción |
| | **Comprometido: 32 · Completado: 19 (59 %); 13 puntos dependen del trabajo de campo** | | **32** | |

#### a) Rendimiento y carga (RNF02, RNF06)

Se midió con `backend-api/scripts/prueba_carga.py`, que reproduce lo que hace el médico en una consulta —abrir el listado, la ficha, el resumen, la predicción, los reportes y la bandeja— con varios usuarios a la vez. Cada usuario abre su propia sesión; el establecimiento de la conexión y el arranque en frío del plan gratuito se descuentan con una petición previa, porque son latencia de la infraestructura y no del sistema.

**Tabla 26.** Tiempo de respuesta según el número de usuarios simultáneos (mediana y percentil 95).

| Operación | 1 usuario | 10 usuarios | 20 usuarios |
| :--- | :---: | :---: | :---: |
| Listado de pacientes | 10 ms · 14 ms | 94 ms · 142 ms | 295 ms · 388 ms |
| Ficha del paciente | 9 ms · 10 ms | 74 ms · 133 ms | 218 ms · 367 ms |
| Resumen de adherencia | 10 ms · 13 ms | 81 ms · 133 ms | 213 ms · 295 ms |
| Predicción con SHAP | 240 ms · 254 ms | 957 ms · 1300 ms | 1506 ms · **2225 ms** |
| Reporte general | 14 ms · 31 ms | 86 ms · 183 ms | 290 ms · 474 ms |
| Bandeja de alertas | 36 ms · 48 ms | 196 ms · 314 ms | 428 ms · 672 ms |

**Resultado.** Con hasta **10 usuarios simultáneos todas las operaciones responden por debajo de 1,4 segundos**, frente a la meta de 2 segundos del RNF02. Con 20 usuarios el sistema sigue respondiendo, pero la predicción con SHAP supera la meta: es la operación más costosa, porque calcula la contribución de cada variable para ese paciente. El consultorio tiene un único médico, de modo que el margen es amplio; el límite medido sirve para dimensionar un despliegue mayor (RNF06).

**Tres hallazgos de la medición, ya corregidos.** El cliente hacia el microservicio abría una conexión nueva en cada consulta, con su saludo de red incluido; ahora se reutiliza. Los reportes y la bandeja pedían al modelo la predicción de **todos** los pacientes en cada apertura; ahora se guardan sesenta segundos, y editar una ficha invalida la suya al instante. Y la primera petición de cada usuario cargaba con el establecimiento de su conexión, que no es tiempo del sistema: la medición lo descuenta con una petición previa. Con los tres cambios, el reporte general responde en **86 ms** de mediana con 10 usuarios, frente a los **794 ms** de la primera medición.

#### b) Verificación de los atributos de calidad (ISO/IEC 25010)

**Tabla 27.** Atributos verificados y su evidencia.

| Atributo [7] | Qué se verificó | Evidencia | Estado |
| :--- | :--- | :--- | :---: |
| Adecuación funcional | Los 10 requisitos funcionales operan de extremo a extremo | 195 pruebas automatizadas; apartado 1.1.7 | ✔ |
| Eficiencia de desempeño | Respuesta ≤ 2 s con 10 usuarios simultáneos | Tabla 26 | ✔ |
| Compatibilidad | Panel en navegador, aplicación en Android 8 o superior, servicios comunicados por REST | APK instalado en dispositivo real | ✔ |
| Usabilidad | Interfaz rotulada, validación con mensajes y confirmación de cada acción | Pendiente de medir con la escala SUS (OE5) | ◐ |
| Fiabilidad | El sistema degrada sin detenerse: cola sin conexión, reintentos y arranque tolerante a cortes | Incidencias I-08, I-15 e I-22 y sus pruebas | ✔ |
| Seguridad | Acceso por perfil, aislamiento por médico tratante, cifrado en tránsito y datos anonimizados hacia el modelo | 20 pruebas de seguridad (Tabla 22) | ✔ |
| Mantenibilidad | Separación en capas y servicios, migraciones versionadas, pruebas por componente | Estructura del repositorio; 195 pruebas | ✔ |
| Portabilidad | Despliegue reproducible desde el repositorio en tres plataformas | `render.yaml`, `DESPLIEGUE.md` | ✔ |

La usabilidad queda como el único atributo sin medir: su evaluación con la escala SUS necesita al médico y a una muestra de pacientes, y se ejecuta sobre el recorrido del apartado 1.1.7.

#### c) Cierre del sprint

**Sprint Review (Sprint 4).** Se aceptaron la prueba de rendimiento, la verificación ISO/IEC 25010, el guion de demostración, el arranque tolerante a cortes de la base y la consolidación del repositorio. Quedaron sin entregar los dos elementos que dependen de personas: la evaluación SUS y la comparación sobre historias clínicas reales.

**Retrospectiva.** Medir antes de optimizar resultó decisivo: la prueba de carga señaló dos costes —una conexión nueva por consulta y la predicción de todos los pacientes en cada apertura— que ninguna lectura del código habría revelado. Descontar de la medición lo que no es tiempo del sistema evitó además una conclusión falsa: el primer intento atribuía al listado de pacientes una demora que era el establecimiento de la conexión del cliente.

Las actas completas de las cuatro ceremonias constan en el Anexo n.° 11.

---

### 1.1.7. Demostración del escenario principal

El escenario principal recorre, de principio a fin, la función para la que existe el producto: **anticipar el incumplimiento de un paciente polimedicado y avisar al médico antes del próximo control**. Se ejecuta sobre el sistema desplegado, sin depender de funciones no implementadas, y cada paso corresponde a un requisito y a un objetivo.

**Tabla 28.** Escenario principal: pasos, requisitos y evidencia.

| # | Paso | Requisito · Objetivo | Resultado observable |
| :---: | :--- | :--- | :--- |
| 1 | El médico registra al paciente polimedicado con las variables del Anexo n.° 04 | RF02 · OE4 | Ficha guardada con código P-00N y confirmación en pantalla |
| 2 | El sistema rechaza una ficha con menos de 5 fármacos o con controles incoherentes | RF02 · OE2 | Mensaje junto al campo; el dato no entra al conjunto de datos |
| 3 | El médico genera el acceso móvil del paciente | RF01 · OE4 | Contraseña temporal mostrada una sola vez |
| 4 | El paciente registra su toma desde el teléfono, incluso sin conexión | RF03 · OE4 | La toma queda en cola y se sincroniza sin duplicarse |
| 5 | El paciente recibe el recordatorio de su siguiente toma | RF08 · OE4 | Aviso en el dispositivo a la hora prescrita |
| 6 | Un familiar corrobora la toma desde su propio teléfono | RF09 · OE4 | La columna «Testigo» del historial pasa a «Familiar» |
| 7 | El sistema calcula el riesgo de incumplimiento del paciente | RF04 · OE3 | Probabilidad y nivel en la ficha, con la procedencia del modelo |
| 8 | El sistema explica qué variables producen ese riesgo | RF06 · OE3 | Contribuciones que suman la probabilidad del paciente |
| 9 | El sistema avisa al médico cuando el paciente empieza a fallar | RF05 · OE4 | Alerta con su motivo y la cifra que la sustenta |
| 10 | El médico registra la intervención y la alerta se cierra | RF05 · OE4 | Nota guardada; el aviso no se repite mientras tanto |
| 11 | El médico audita a todos sus pacientes y exporta el reporte | RF07 · OE4 | Indicadores, distribución de riesgo y archivo CSV |
| 12 | El sistema impide que otro médico acceda a la ficha | RNF01 · OE2 | Respuesta de acceso denegado |

El guion detallado de la demostración, con los tiempos de cada paso y qué hacer si un servicio está suspendido, está en `documentacion/04_demostracion/Guion_demostracion.md`.

**Antes de demostrar.** El plan gratuito suspende los servicios tras quince minutos sin tráfico; `backend-api/scripts/despertar.py` los despierta y confirma que el modelo está cargado, de modo que la espera no ocurra durante la sustentación.

---

### 1.1.8. Registro consolidado de incidencias

**Tabla 29.** Incidencias por sprint.

| Sprint | Incidencias | Componentes tocados | Por componente | Detectadas por prueba o revisión | Abiertas |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 1 | 4 | 0,25 | 0 de 1 (retrospectiva) | 0 |
| 2 | 6 | 5 | 1,20 | 5 de 6 | 0 |
| 3 *(al corte)* | 15 | 6 | 2,50 | 13 de 15 | 0 |
| **Total** | **22** | — | — | **18 de 22** | **0** |

**Lectura.** Las incidencias aumentan en el Sprint 3 porque es el primero que se ejecuta sobre el servidor publicado y un teléfono real, y el que más componentes nuevos incorpora. Todas están cerradas.

Según su origen: seis por el comportamiento de librerías de terceros (I-02, I-03, I-05, I-06, I-09, I-10), seis por diferencias entre el entorno de desarrollo y el publicado (I-08, I-11, I-12, I-14, I-15, I-22), cuatro de interfaz (I-04, I-07, I-16, I-17), dos por diferencias entre lo documentado y lo implementado (I-18, I-20), una de texto desactualizado (I-13), una de rendimiento en el primer uso (I-19), una de diseño de la propia alerta (I-21) y una de diseño detectada en retrospectiva (I-01).

El grupo que más pesa sigue siendo el de las diferencias entre desarrollo y publicación, y de ahí la práctica que se mantiene: verificar cada cambio sobre el artefacto que se entrega —el APK de publicación, el servicio desplegado— y no solo sobre la ejecución local.

---

## 1.2. En base a los objetivos del proyecto

**Tabla 30.** Estado de los objetivos específicos.

| Objetivo | Resultado esperado | Estado | Evidencia |
| :---: | :--- | :---: | :--- |
| OE1 | Diagnóstico con línea base y factores de incumplimiento | **Cumplido** (línea base propia en ejecución) | Tablas 8 y 9 |
| OE2 | Requisitos y arquitectura | **Cumplido** (juicio de expertos en curso) | Tablas 2, 6 y 13 |
| OE3 | Algoritmo seleccionado y reporte comparativo | **En ejecución** (~80 %) | Tablas 15, 19 y 20 |
| OE4 | Sistema de soporte clínico funcional | **Cumplido** | Tablas 6, 18, 23, 26, 27 y 28 |
| OE5 | Validación de usabilidad | **Pendiente**: requiere usuarios reales | Anexo n.° 05; recorrido preparado (Tabla 28) |

### 1.2.1. OE1 – Caracterizar el proceso actual de seguimiento terapéutico y los factores de incumplimiento

**Estado: cumplido.**

| Indicador | Meta | Resultado |
| :--- | :--- | :--- |
| Pacientes con adherencia deficiente (línea base) | Medida en el diagnóstico | En ejecución (test de Morisky-Green); referencia: 37,1 % nacional [4], 44,7 % en Lambayeque [6] |
| Factores clasificados según la OMS | 5 dimensiones | **5 dimensiones** cubiertas (Tabla 9) |
| Procesos de seguimiento no digitalizados | Medido en el diagnóstico | **100 %**: ninguno de los 4 subprocesos (registro de toma, seguimiento entre citas, alerta de riesgo y auditoría) tiene soporte digital |

### 1.2.2. OE2 – Determinar los requisitos funcionales y no funcionales del sistema

**Estado: cumplido.**

| Indicador | Meta | Resultado |
| :--- | :--- | :--- |
| Requisitos especificados respecto a los identificados | 100 % | **100 %**: 10 RF y 6 RNF con criterio de aceptación y prioridad |
| Alineación con estándares de arquitectura (juicio de expertos, 1–5) | 3 expertos | Expediente formalizado (Anexo n.° 07); evaluación en curso |

### 1.2.3. OE3 – Determinar el algoritmo de aprendizaje automático con mayor capacidad predictiva

**Estado: en ejecución.**

| Indicador | Meta | Resultado |
| :--- | :--- | :--- |
| Algoritmos comparados | ≥ 4 | **4**: Regresión Logística, Random Forest, XGBoost y SVM |
| AUCROC en validación cruzada | ≥ 0,80 | Corrida de verificación: **0,856** (SVM seleccionado; Tabla 20) |
| Sensibilidad y especificidad | Reportadas | Corrida de verificación: 0,794 y 0,757 |
| F1-score en prueba independiente | Reportado | Corrida de verificación: 0,471 |

El protocolo está implementado, verificado y en servicio a través del microservicio de inferencia, que además explica cada predicción con SHAP. Falta ejecutarlo sobre las historias clínicas reales cuando concluya la extracción del Anexo n.° 04.

### 1.2.4. OE4 – Construir el sistema de soporte clínico

**Estado: cumplido.**

| Indicador | Meta | Resultado |
| :--- | :--- | :--- |
| Historias de usuario cumplidas | 100 % por sprint | Sprint 1: 100 %; Sprint 2: 92 %; Sprint 3: 95 %; Sprint 4: 100 % de lo que no depende del trabajo de campo |
| Módulos construidos frente a requeridos | Todos | **10 de 10** RF operativos (RF01–RF10) |
| Densidad de errores por sprint | Decreciente | 22 incidencias registradas y cerradas (Tabla 29); 195 pruebas en verde |
| Atributos ISO/IEC 25010 | Funcionalidad, eficiencia y usabilidad | **7 de 8 atributos verificados** (Tabla 27); la usabilidad queda pendiente de la escala SUS |

**Escenario de extremo a extremo operativo:** el médico registra al paciente y le genera su acceso; el paciente recibe recordatorios y registra sus tomas desde el celular, incluso sin conexión; un familiar las corrobora; y el médico recibe una alerta cuando ese paciente empieza a fallar, consulta en la ficha la adherencia y el riesgo predicho con su explicación SHAP, y ve en reportes la situación de todos sus pacientes.

### 1.2.5. OE5 – Evaluar la usabilidad del sistema mediante la escala SUS

**Estado: pendiente de aplicación con usuarios.** El sistema ya está completo y el recorrido que se evaluará es el de la Tabla 28.

| Indicador | Meta | Estado |
| :--- | :--- | :--- |
| Usabilidad con la escala SUS [12] | ≥ 80 puntos | Pendiente |
| Tasa de éxito en tareas | Medida con usuarios | Pendiente |
| Tiempo promedio de aprendizaje | Medido con usuarios | Pendiente |

El instrumento SUS (Anexo n.° 05) y la ficha de observación (Anexo n.° 06) están preparados, y el guion de la sesión —qué hace el usuario, en qué orden y qué se observa— es el del apartado 1.1.7. Participarán el médico, sobre el panel web, y una muestra de pacientes polimedicados, sobre la aplicación móvil. **Es el único resultado del proyecto que no depende del desarrollo, sino de la disponibilidad de los participantes.**

---

## 1.3. Limitaciones del estudio y trabajo futuro

Declarar los límites del trabajo forma parte del resultado: sin ellos, cualquier lectura del sistema sería más optimista de lo que la evidencia permite.

**Tabla 31.** Limitaciones reconocidas y su alcance.

| Limitación | Por qué existe | Qué implica para la interpretación |
| :--- | :--- | :--- |
| El modelo desplegado se entrenó con un conjunto de demostración | La extracción documental del Anexo n.° 04 no ha concluido | Las métricas publicadas verifican el protocolo y el sistema, **no** la capacidad predictiva sobre pacientes reales. El sistema lo declara en pantalla y en la ficha del modelo |
| Un solo consultorio y una muestra prevista de unos 50 pacientes | Es el universo del estudio y el alcance de una tesis de pregrado | Los resultados no son extrapolables a otras poblaciones; describen a los pacientes polimedicados de este consultorio |
| La adherencia observada procede del autorreporte del paciente | Solo un método directo —recuento de comprimidos, medición en sangre— eliminaría el sesgo, y está fuera del alcance [3] | La corroboración familiar (RF09) añade un segundo testigo, pero no convierte el dato en una medida objetiva |
| Variables limitadas a las del instrumento | El Anexo n.° 04 se fijó a partir de lo disponible en la historia clínica | Factores como la creencia sobre la enfermedad o el costo del tratamiento no están representados |
| La explicación SHAP se calcula frente a un paciente de referencia | El modelo seleccionado no tiene coeficientes interpretables | Las contribuciones indican asociación dentro del modelo, no causalidad clínica |
| Infraestructura en planes gratuitos | El proyecto no dispone de servidores propios | Los servicios se suspenden sin tráfico; la latencia de arranque no es del sistema y debe descontarse al medir |
| Usabilidad sin medir al cierre del desarrollo | La escala SUS requiere usuarios reales | El RNF03 queda verificado por diseño, no por evidencia empírica, hasta aplicar el instrumento |

**Trabajo futuro.** Más allá del alcance de esta tesis quedan: la atribución de causalidad mediante un diseño experimental —el sistema predice, no demuestra que la intervención mejore la adherencia—; el reentrenamiento periódico del modelo con los datos que el propio sistema genera; la integración con la historia clínica institucional; y la extensión del acompañamiento a mensajería con el paciente.

---

## 1.4. Cierre del desarrollo y trabajo de campo pendiente

El desarrollo está cerrado. Lo que resta son tres mediciones con personas, cada una con su instrumento formalizado y su cálculo automatizado, de modo que obtener el resultado no requiere programar nada más.

**Tabla 32.** Qué falta, qué lo produce y qué resultado cierra.

| Pendiente | Instrumento | Cómo se obtiene el resultado | Objetivo que cierra |
| :--- | :--- | :--- | :---: |
| Extracción de historias clínicas | Anexo n.° 04 y su plantilla CSV | `python src/preprocess.py --entrada <csv>` valida el esquema y reporta faltantes | OE1, OE3 |
| Test de Morisky-Green | Anexo n.° 05 (parte A) | Aporta la etiqueta de cada paciente y la línea base del consultorio | OE1 |
| Comparación de algoritmos sobre datos reales | `train_evaluate.py` | Un comando produce la tabla comparativa, el contraste de McNemar y el modelo listo para desplegar | OE3 |
| Evaluación de usabilidad | Anexo n.° 05 (parte B) y ficha de observación | `python documentacion/herramientas/calcular_sus.py <respuestas.csv>` devuelve el puntaje por participante y el promedio frente a la meta de 80 | OE5 |
| Juicio de expertos | Anexo n.° 07 | Tres evaluadores completan el expediente | OE2 |

El recorrido que se somete a la evaluación de usabilidad es el del apartado 1.1.7, y la sesión se conduce con el guion del Anexo n.° 14.

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
| N.° 01 | Carta de aceptación institucional | Documento firmado por el Dr. Milko Ugaz Zegarra (22/06/2026) | Adjunto |
| N.° 02 | Matriz de consistencia del proyecto | `documentacion/00_documentacion_base/Proyecto_de_Tesis.md` | Adjunto |
| N.° 03 | Guía de entrevista semiestructurada al personal médico | `documentacion/00_documentacion_base/Proyecto_de_Tesis.md` | Aplicado |
| N.° 04 | Ficha de recolección de datos clínicos | `documentacion/02_instrumentos/Anexo_04_Ficha_Extraccion_Clinica.docx` | En aplicación |
| N.° 05 | Test de Morisky-Green y escala SUS | `documentacion/02_instrumentos/` | Morisky en aplicación; SUS en la semana 7 |
| N.° 06 | Ficha de observación de pruebas con usuarios | `documentacion/02_instrumentos/` | Semana 7 |
| N.° 07 | Expediente de juicio de expertos | `documentacion/02_instrumentos/Anexo_07_Expediente_Expertos.docx` | En proceso |
| N.° 08 | Repositorio de código del producto | `backend-api/`, `frontend-web/`, `app-movil/`, `ml-pipeline/` | Adjunto |
| N.° 09 | Product Backlog e historias de usuario | `documentacion/03_gestion_scrum/Anexo_09_Product_Backlog.docx` | Adjunto |
| N.° 10 | Matriz de trazabilidad | `documentacion/03_gestion_scrum/Anexo_10_Matriz_Trazabilidad.docx` | Adjunto |
| N.° 11 | Actas de Sprint Review y retrospectiva (Sprints 1 a 4) | `documentacion/03_gestion_scrum/Anexo_11_Actas_Sprint.docx` | Adjunto |
| N.° 12 | Plantilla de captura de la ficha de extracción | `documentacion/02_instrumentos/Plantilla_Extraccion_Anexo_04.csv` | En uso |
| N.° 13 | Guía de despliegue del sistema | `DESPLIEGUE.md` | Adjunto |
| N.° 14 | Guion de demostración del producto | `documentacion/04_demostracion/Guion_demostracion.md` | Adjunto |
| N.° 15 | Plantilla de captura y cálculo de la escala SUS | `documentacion/02_instrumentos/Plantilla_Respuestas_SUS.csv` · `herramientas/calcular_sus.py` | En uso |
