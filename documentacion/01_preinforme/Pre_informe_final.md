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

3 de noviembre de 2026.

---

# ÍNDICE

- **I. RESULTADOS**
  - **1.1. En base a la metodología utilizada**
    - 1.1.1. Marco de trabajo: SCRUM como marco anfitrión
    - 1.1.2. Descripción del producto, usuarios y criterios de éxito
    - 1.1.3. Product Backlog general
    - 1.1.4. Sprint 1: Comprensión del negocio y de los datos
    - 1.1.5. Sprint 2: Preparación de datos y registro clínico
    - 1.1.6. Sprint 3: Modelo integrado y cierre del núcleo funcional
    - 1.1.7. Sprint 4: Cierre, rendimiento y validación
    - 1.1.8. Comparación de algoritmos sobre datos reales: conjunto externo ENDES
    - 1.1.9. Demostración del escenario principal
    - 1.1.10. Registro consolidado de incidencias
    - 1.1.11. Verificación formal del producto: pruebas de caja negra y caja blanca (PBI-12)
  - **1.2. En base a los objetivos del proyecto**
    - 1.2.1. OE1 – Caracterización del proceso actual de seguimiento terapéutico
    - 1.2.2. OE2 – Determinación de los requisitos funcionales y no funcionales
    - 1.2.3. OE3 – Determinación del algoritmo con mayor capacidad predictiva
    - 1.2.4. OE4 – Construcción del sistema de soporte clínico
    - 1.2.5. OE5 – Evaluación de la usabilidad mediante la escala SUS
  - **1.3. Limitaciones del estudio y trabajo futuro**
  - **1.4. Cierre del desarrollo y trabajo de campo pendiente**
- **REFERENCIAS BIBLIOGRÁFICAS**
- **ANEXOS**

---

# I. RESULTADOS

## 1.1. En base a la metodología utilizada

El producto se desarrolla integrando **SCRUM y CRISP-DM**. El sprint de SCRUM es la unidad de trabajo; las fases de CRISP-DM se ejecutan dentro de los sprints. Así, cada sprint entrega a la vez un incremento de software y un avance del modelo predictivo [1], [2].

**Tabla 1.** Correspondencia entre sprints, fases de CRISP-DM e hitos del cronograma.

| Sprint | Objetivo | Fase CRISP-DM | Semanas | Hito | Estado |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **1** | Planificación y primer incremento | *Business* y *Data Understanding* | 2–3 | 30 % | **Cerrado** |
| **2** | Registro clínico y modelado inicial | *Data Preparation* y *Modeling* inicial | 3–4 | 40 % / 50 % | **Cerrado** |
| **3** | Modelo integrado, alertas y cierre del núcleo funcional | *Modeling* (selección) y *Evaluation* | 5–6 | 65 % / 80 % | **Cerrado** |
| **4** | Cierre, rendimiento y verificación de calidad | *Deployment* | 7–8 | 90 % / 100 % | **Cerrado** |
| PBI-11 | Comparación de algoritmos sobre datos reales (elemento posterior al Sprint 4) | *Evaluation* | 9 | — | **Cerrado** |
| PBI-12 | Verificación formal del producto: pruebas de caja negra y caja blanca, y ajustes de cierre | *Evaluation* y *Deployment* | 10 | — | **Cerrado** |

El Anexo n.° 20 relaciona cada actividad, técnica y herramienta de desarrollo con el apartado que la describe, y el Anexo n.° 21 presenta los productos, artefactos y entregables obtenidos en cada fase.

### 1.1.1. Marco de trabajo: SCRUM como marco anfitrión

#### a) Reparto de responsabilidades entre los dos marcos

El proyecto aprobado declara **SCRUM como marco de trabajo del desarrollo** y CRISP-DM como proceso de referencia del modelo predictivo, con sus fases ejecutándose **como sprints especializados dentro del flujo SCRUM** [1], [2]. El sprint es, por tanto, la unidad de planificación, de entrega y de rendición de cuentas; CRISP-DM no organiza el documento, sino que ordena el trabajo del modelo **dentro** de cada sprint. Esta tabla fija qué marco gobierna cada decisión, de modo que no haya ambigüedad sobre cuál manda cuando ambos tienen algo que decir.

**Tabla 2.** Responsabilidad de cada marco en el proyecto.

| Decisión | Marco que la gobierna | Cómo se concreta |
| :--- | :--- | :--- |
| Qué se construye y en qué orden | **SCRUM** | Product Backlog priorizado con MoSCoW y refinado al inicio de cada sprint |
| Cuándo algo está terminado | **SCRUM** | Definición de Terminado (Tabla 5), aplicada a todo elemento sin excepción |
| Cuánto trabajo entra en un sprint | **SCRUM** | Velocidad medida del sprint anterior (Tabla 7) |
| Qué se acepta y qué se corrige | **SCRUM** | Sprint Review con el médico y retrospectiva del equipo |
| Cómo se entiende el problema y se fijan los criterios de éxito del modelo | CRISP-DM (*Business Understanding*) | Criterios CEN y CEA (Tablas 15 y 16), establecidos en el Sprint 1 |
| Cómo se exploran, depuran y transforman los datos | CRISP-DM (*Data Preparation*) | Pipeline del apartado 1.1.5.b, ejecutado dentro del Sprint 2 |
| Cómo se entrena, compara y selecciona el algoritmo | CRISP-DM (*Modeling* y *Evaluation*) | Protocolo del apartado 1.1.6.c y comparación del 1.1.8 |
| Cómo llega el modelo al usuario | Ambos | CRISP-DM aporta el *Deployment*; SCRUM lo entrega como incremento del Sprint 3 y lo estabiliza en el 4 |

#### b) Roles, artefactos y eventos de SCRUM

SCRUM supone un equipo de varias personas. Esta tesis la desarrolla una sola, de modo que los roles se acumulan. Declararlo es parte del rigor: un informe que describiera ceremonias imposibles para un equipo de uno no demostraría dominio del marco, sino desconocimiento.

**Tabla 3.** Roles de SCRUM y su realización en el proyecto.

| Rol | Quién lo asume | Adaptación declarada |
| :--- | :--- | :--- |
| **Product Owner** | Dr. Milko Ugaz Zegarra, médico del consultorio | Es el dueño del problema: aporta las necesidades, prioriza el Product Backlog y acepta o rechaza cada incremento en la Sprint Review. No participa en la estimación |
| **Scrum Master** | El tesista | Facilita los eventos, mantiene los artefactos y retira impedimentos. Con un equipo de una persona el rol no es de coordinación sino de disciplina de proceso: que la Definición de Terminado se respete y que la retrospectiva produzca una acción concreta |
| **Equipo de Desarrollo** | El tesista | Equipo de un solo integrante. Las decisiones técnicas no se consensúan; se documentan con su justificación y su alternativa descartada (Tabla 11) para que sean auditables en lugar de consensuadas |
| Asesor de tesis | Docente asesor | No es un rol de SCRUM. Interviene como revisor externo de la coherencia entre el producto y el proyecto aprobado |

**Tabla 4.** Artefactos de SCRUM y dónde está cada uno.

| Artefacto | Realización en el proyecto | Ubicación |
| :--- | :--- | :--- |
| **Product Backlog** | 10 requisitos funcionales y 6 no funcionales, priorizados con MoSCoW y vinculados a la brecha del diagnóstico y al objetivo específico que atienden | Tabla 17 · Anexo n.° 07 |
| **Sprint Backlog** | Un backlog por sprint, con tarea, componente, estimación en puntos y estado | Tablas 18, 23, 29 y 36 |
| **Incremento** | Software desplegado y utilizable al cierre de cada sprint, no una rama sin integrar | Apartado 1.1.9 · Anexo n.° 06 |
| **Definición de Terminado** | Condición única y explícita para dar por terminado cualquier elemento | Tabla 5 |
| Registro de impedimentos | 22 incidencias con causa, corrección y sprint de origen | Tabla 44 |

**Tabla 5.** Definición de Terminado (*Definition of Done*).

Un elemento del Sprint Backlog se considera terminado cuando cumple **todas** estas condiciones. No hay excepciones ni grados de cumplimiento: si falta una, el elemento vuelve al Product Backlog.

| # | Condición |
| :---: | :--- |
| 1 | El criterio de aceptación de la historia de usuario se verifica de extremo a extremo sobre el sistema en ejecución |
| 2 | Existe al menos una prueba automatizada que cubre el comportamiento y pasa en verde |
| 3 | La regla clínica que corresponda está impuesta en el borde del sistema (esquema de entrada o restricción de la base), no solo en la interfaz |
| 4 | El código está integrado en la rama principal y desplegado en el entorno publicado, no solo en local |
| 5 | La interfaz devuelve al usuario un mensaje comprensible tanto en el caso correcto como en el error previsible |
| 6 | El cambio queda registrado en la matriz de trazabilidad con su requisito y su objetivo específico |
| 7 | Si el elemento toca datos clínicos, existe una prueba que verifica que un perfil no autorizado no accede a ellos |

La condición 4 se incorporó tras la retrospectiva del Sprint 3: tres defectos (I-14, I-15 e I-22) solo se manifestaron sobre el servicio publicado, de modo que «funciona en local» dejó de ser suficiente para dar algo por terminado.

**Tabla 6.** Eventos de SCRUM y cómo se ejecutaron.

| Evento | Ejecución en el proyecto | Adaptación declarada |
| :--- | :--- | :--- |
| **Sprint Planning** | Al inicio de cada sprint: refinamiento del Product Backlog, selección de elementos según la velocidad medida y formulación del objetivo del sprint | El Product Owner prioriza por mensajería o en consulta, no en reunión formal, por su disponibilidad clínica |
| **Daily Scrum** | Registro diario de avance, impedimentos y siguiente tarea | Con un equipo de uno no hay sincronización entre personas; se conserva como control diario de impedimentos, que es lo que el evento busca |
| **Sprint Review** | Demostración del incremento al médico sobre el sistema desplegado, con su aceptación o sus observaciones | Se conduce sobre el entorno publicado y no sobre capturas de pantalla |
| **Retrospectiva** | Análisis de los defectos del sprint y **una** acción correctiva concreta por sprint, aplicada en el siguiente | Actas en el Anexo n.° 09 |
| Refinamiento del Backlog | Continuo; dos requisitos (RF09 y RF10) se incorporaron a partir de observaciones del Product Owner | — |

**Tabla 7.** Velocidad por sprint y su efecto en la planificación siguiente.

| Sprint | Elementos | Puntos comprometidos | Puntos terminados | Cumplimiento | Qué informó a la planificación siguiente |
| :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | 7 | 24 | 24 | 100 % | Velocidad inicial conocida; el Sprint 2 pudo comprometer más del doble |
| 2 | 11 | 63 | 58 | 92 % | Los 5 puntos no terminados eran de modelado y dependían del dato: se replanificaron como dependencia explícita del Sprint 3 |
| 3 | 21 | 104 | 99 | 95 % | Velocidad sostenida con el núcleo funcional cerrado; el Sprint 4 se dedicó a estabilización y no a nueva funcionalidad |
| 4 | 6 | 32 | 19 | 59 % | Los 13 puntos restantes corresponden a trabajo de campo con personas (extracción, Morisky y SUS) y no a desarrollo; se declaran en 1.4 |
| PBI-11 | 1 | 13 | 13 | 100 % | Elemento incorporado tras la retrospectiva del Sprint 4 y atendido con la velocidad ya conocida (apartado 1.1.8) |
| PBI-12 | 6 | 13 | 13 | 100 % | Verificación formal exigida para el cierre; sus defectos se corrigieron dentro del mismo elemento (apartado 1.1.11) |

El cumplimiento del Sprint 4 es el más bajo del proyecto y conviene leerlo con precisión: **ningún elemento de desarrollo quedó sin terminar**. Los 13 puntos pendientes son los que dependen de aplicar instrumentos a personas, que no es trabajo que el equipo pueda completar por sí mismo. Mantenerlos en el Sprint Backlog en lugar de retirarlos es deliberado: un backlog que oculta lo que no se entregó deja de ser un instrumento de control.

#### c) Definición del núcleo funcional y secuenciación de los sprints

SCRUM exige que cada sprint termine en un incremento potencialmente entregable y que el núcleo funcional quede completo y ejecutable antes del cierre del desarrollo. Para que esa exigencia sea verificable y no una declaración, el núcleo funcional de esta tesis se define de forma explícita:

> **Núcleo funcional.** El recorrido extremo a extremo que va del registro de la toma por el paciente (RF03) al riesgo predicho y explicado en la ficha del médico (RF04, RF06) y de ahí a la alerta temprana (RF05). Es el recorrido que da sentido al producto: sin la predicción no hay soporte a la decisión, y sin el registro no hay dato con el que predecir.

**Cierre del núcleo funcional: Sprint 3.** Al cierre del Sprint 3 el recorrido completo es ejecutable y así se demuestra en 1.1.9. Al cierre del Sprint 4 lo están los **diez** requisitos funcionales y los **seis** no funcionales; la verificación formal del PBI-12 (apartado 1.1.11) los respalda con 282 pruebas automatizadas, 59 casos de caja negra y doce funciones analizadas por caja blanca.

**Por qué la predicción no pudo cerrar en el Sprint 2.** RF04 depende de que exista el dato que alimenta al modelo: la predicción se calcula sobre las variables de la ficha (RF02) y sobre la traza de tomas que produce la aplicación del paciente (RF03). Entregar el servicio de inferencia antes del registro que lo alimenta habría producido un incremento no demostrable —un modelo sin entrada— y habría contradicho el principio de incremento potencialmente entregable. La secuenciación responde, por tanto, a una **dependencia técnica real y documentada** —la correspondencia entre brechas y requisitos está en la Tabla 19, y la asignación a sprints en la Tabla 17—, no a una postergación del alcance.

**Decisiones de secuenciación y simplificaciones conscientes.** Se declaran como decisiones deliberadas, y no como omisiones:

**Tabla 8.** Decisiones de secuenciación y su justificación.

| Decisión | Sprint | Por qué se tomó |
| :--- | :---: | :--- |
| RF04 y RF06 después de RF02 y RF03 | 3 | La inferencia necesita la ficha y la traza de tomas como entrada; antes no hay nada que predecir |
| RF05 (alertas) después de RF04 | 3 | La regla de alerta por riesgo predicho consume la salida del modelo |
| Inferencia en un microservicio separado, no en el API | 3 | El API arranca en segundos; cargar las bibliotecas del modelo en el mismo proceso lo haría arrancar en minutos y acoplaría dos ciclos de versiones distintos |
| RF08, RF09 y RF10 en el Sprint 3, no en el 1 | 3 | Son *Could* y *Should* en MoSCoW; se ordenaron después del núcleo para no desplazarlo |
| Sin cifrado de campo en la base de datos | — | El proveedor cifra en reposo y en tránsito; el cifrado de campo impediría las restricciones de integridad que protegen el conjunto de entrenamiento |
| Sin aplicación nativa separada para iOS | — | El consultorio opera con pacientes de teléfono Android; una segunda compilación no atendería ninguna necesidad declarada (Tabla 10) |

---

### 1.1.2. Descripción del producto, usuarios y criterios de éxito

#### a) Función principal

El sistema **anticipa qué pacientes polimedicados tienen mayor probabilidad de dejar su tratamiento** antes del próximo control, para que el médico intervenga a tiempo. Hoy el consultorio se entera del incumplimiento cuando el paciente ya se descompensó.

Para lograrlo, el sistema hace cuatro cosas:

1. **Registra la toma real** de cada medicamento desde el celular del paciente, con recordatorios y confirmación de un familiar.
2. **Calcula el riesgo** de incumplimiento de cada paciente con un modelo de aprendizaje automático.
3. **Avisa al médico** cuando un paciente empieza a fallar, sin que tenga que revisarlos uno por uno.
4. **Muestra al médico** la ficha, la adherencia observada, el riesgo predicho y reportes de todos sus pacientes.

La decisión clínica sigue siendo del médico: el sistema es un apoyo, no un diagnóstico.

#### b) Estructura del producto

**Tabla 9.** Componentes del producto y sus usuarios.

| Componente | Tecnología | Usuario | Qué hace |
| :--- | :--- | :--- | :--- |
| Panel web | React + Vite (Vercel) | Médico | Registra pacientes, consulta fichas, alertas, riesgo y reportes; genera el acceso móvil del paciente |
| Aplicación móvil | Flutter (Android) | Paciente y familiar | Recordatorios, registro de tomas sin conexión, grupo familiar y corroboración |
| API central | FastAPI (Render) | — | Autenticación, reglas del negocio y cálculo de indicadores |
| Microservicio de inferencia | FastAPI + scikit-learn + SHAP (Render) | — | Carga el modelo, calcula el riesgo de cada paciente y lo explica con SHAP |
| Pipeline de entrenamiento | scikit-learn (`ml-pipeline`) | — | Prepara los datos, compara algoritmos y genera el modelo que usa el microservicio |
| Base de datos | PostgreSQL (Aiven) | — | Guarda usuarios, fichas, tomas y grupo familiar |

Los componentes atienden necesidades declaradas por usuarios concretos del consultorio. Cada necesidad derivó en requisitos, y cada requisito en una brecha del diagnóstico (Tabla 19):

**Tabla 10.** Usuarios del sistema, necesidades declaradas y requisitos derivados.

| # | Usuario / rol | Necesidad declarada en el diagnóstico | Requisito asociado |
| :---: | :--- | :--- | :--- |
| U1 | Médico del consultorio | Saber, antes de la cita, qué pacientes están dejando el tratamiento | RF04, RF05, RF07 |
| U2 | Médico del consultorio | Registrar y mantener la ficha del paciente polimedicado con datos verificables | RF01, RF02 |
| U3 | Médico del consultorio | Entender en qué se basa el riesgo que informa el sistema, para poder discutirlo con el paciente | RF06 |
| U4 | Paciente polimedicado | Recordar sus tomas y poder registrarlas aunque no tenga señal | RF03, RF08 |
| U5 | Familiar acompañante | Acompañar la toma sin acceder a la información clínica del paciente | RF09 |
| U6 | Médico del consultorio | Recuperar el acceso al sistema sin depender de un administrador | RF10 |

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

Ninguna herramienta se eligió por familiaridad. Cada una atiende un objetivo específico o una restricción del proyecto, y se contrastó con una alternativa viable que se descartó por una razón verificable. La columna de alternativa descartada es la que permite auditar la decisión: una elección sin alternativa considerada no es una justificación.

**Tabla 11.** Justificación de las tecnologías frente a los objetivos y restricciones del proyecto.

| Herramienta | Objetivo o restricción que atiende | Alternativa descartada | Razón de la elección |
| :--- | :--- | :--- | :--- |
| **FastAPI** (API central) | OE2, OE4: servicios REST con validación estricta de las variables del Anexo n.° 03 | Django REST Framework | Valida y documenta el contrato a partir del propio código, de modo que una ficha con datos imposibles se rechaza en el borde del sistema. Django arrastraría un marco completo —plantillas, administrador, ORM propio— para un servicio que solo expone JSON |
| **PostgreSQL** (Aiven) | OE4, RNF01: guardar la historia clínica y la traza de tomas | MongoDB | Permite escribir las reglas clínicas como restricciones de la propia base —polimedicación, coherencia de controles, una sola toma por horario—, que es lo que impide que un dato inválido llegue al conjunto de entrenamiento. Una base documental dejaría esa garantía en manos del código de aplicación |
| **SQLAlchemy y Alembic** | OE4: modelo de datos y migraciones versionadas | Scripts SQL manuales | El esquema clínico cambió cinco veces durante el desarrollo; cada cambio quedó como una migración aplicable y reversible, verificada contra PostgreSQL real. Un script manual no es reversible ni reproducible en producción |
| **React + Vite** (panel) | OE4, RNF03: interfaz del médico con ficha, alertas y reportes | Plantillas renderizadas en el servidor | La ficha cambia continuamente mientras el médico filtra, edita o atiende alertas; un modelo declarativo evita sincronizar la pantalla a mano. Vite produce un paquete estático desplegable sin servidor, lo que elimina un componente de infraestructura |
| **Flutter** (aplicación del paciente) | OE4, RF03, RF08, RF09: registro de tomas, recordatorios y grupo familiar | Aplicación web progresiva (PWA) | Una sola base de código con avisos locales programados y base de datos propia para la cola sin conexión. Una PWA no garantiza la notificación programada ni la persistencia local en Android, y el registro sin señal es el escenario en el que más falta hace |
| **scikit-learn** | OE3: preparación, comparación de algoritmos y modelo en servicio | Implementación propia de cada algoritmo | Reúne en un solo objeto serializable la imputación, la codificación, el escalado y el clasificador, lo que garantiza que la inferencia aplique exactamente la misma transformación que el entrenamiento. Una implementación propia no sería contrastable con la literatura |
| **XGBoost** | OE3: cuarto algoritmo candidato de la comparación | Solo los tres de scikit-learn | El potenciado por gradiente es el referente en datos tabulares clínicos [3]; excluirlo dejaría la comparación del OE3 sin la familia de algoritmos que la literatura reporta como más competitiva |
| **imbalanced-learn (SMOTE)** | OE3: balancear la clase minoritaria dentro de la validación cruzada | Submuestreo de la clase mayoritaria | Permite encadenar el balanceo en el mismo pipeline, de modo que se reajuste en cada pliegue; hacerlo aparte habría filtrado información de validación al entrenamiento e inflado las métricas [4]. El submuestreo descartaría datos clínicos escasos |
| **SHAP** | RF06: explicar cada predicción al médico | Importancia global por permutación | Garantiza que las contribuciones sumen exactamente la probabilidad del paciente —su propiedad aditiva— [5], de modo que la explicación es del paciente y no del modelo. La importancia por permutación solo describe el modelo en conjunto |
| **Microservicio separado + `httpx`** | OE4, RNF02: aislar la inferencia del API | Cargar el modelo en el proceso del API | Las bibliotecas del modelo tardan segundos en cargarse; en el mismo proceso, cada arranque del API los pagaría y un cambio de modelo exigiría redesplegar el API completo |
| **Render y Vercel** | OE4: publicar API, microservicio y panel | Servidor propio o máquina virtual | Despliegue continuo desde el repositorio, con HTTPS y variables de entorno, sin administrar servidores: una tesis de pregrado no dispone de infraestructura ni de personal de operación |
| **pytest y flutter test** | OE4, RNF04: verificación automatizada | Pruebas manuales por lista de comprobación | Convierten cada regla clínica y cada riesgo en una prueba repetible; son las que detectaron 18 de las 22 incidencias antes de que llegaran al usuario. Una lista manual no se ejecuta en cada cambio |

#### e) Variables que respaldan el sistema

Las variables siguen el **modelo multidimensional de adherencia de la OMS** [6], que agrupa las causas del incumplimiento en cinco dimensiones. Cada variable se registra en la ficha del panel y en el Anexo n.° 03.

**Tabla 12.** Variables del modelo predictivo.

| Dimensión OMS | Variables | Origen |
| :--- | :--- | :--- |
| Paciente | Edad, sexo | Historia clínica |
| Socioeconómica y social | Nivel educativo, convivencia (vive solo o acompañado), apoyo familiar en la medicación | Historia clínica o entrevista |
| Enfermedad | Diagnóstico (HTA, DM2 o ambas), tiempo de enfermedad, comorbilidades (lista marcada; el modelo usa el total) | Historia clínica |
| Terapia | Número de fármacos, tomas por día | Historia clínica |
| Sistema de salud | Controles programados y controles perdidos en 6 meses | Historia clínica |
| *Variables derivadas* | Carga terapéutica (fármacos × tomas), tasa de inasistencia (perdidos ÷ programados), cronicidad relativa (tiempo de enfermedad ÷ edad/10) | Calculadas por el sistema |
| *Variable objetivo* | Incumplimiento (sí/no) según el test de Morisky-Green | Entrevista al paciente (Anexo n.° 04) |

El puntaje de Morisky **no se usa como predictor**, porque de él sale la etiqueta: usarlo inflaría artificialmente los resultados.

**Variables médicas del proyecto.** De las variables anteriores, las que proceden de la historia clínica, de la receta o de la medición clínica de la adherencia son las siguientes; las demás describen al paciente o a su entorno.

**Tabla 13.** Variables médicas del proyecto, su fuente y su uso.

| Variable médica | Valores | Fuente | Uso en el proyecto |
| :--- | :--- | :--- | :--- |
| Diagnóstico | Hipertensión arterial, diabetes mellitus tipo 2 o ambas | Historia clínica | Predictor y criterio de inclusión |
| Tiempo de enfermedad | Años desde el diagnóstico (0 a 80, no mayor que la edad) | Historia clínica | Predictor; origina la cronicidad relativa |
| Comorbilidades | Once condiciones: dislipidemia, obesidad, enfermedad renal crónica, cardiopatía isquémica, insuficiencia cardiaca, enfermedad cerebrovascular, hipotiroidismo, EPOC o asma, artrosis, depresión y otra enfermedad crónica | Historia clínica | El modelo usa el total marcado; los reportes, la frecuencia de cada una |
| Número de fármacos prescritos | 5 a 30 | Receta | Predictor y criterio de inclusión (polimedicación) |
| Tomas por día | 1 a 20 | Receta | Predictor; origina la carga terapéutica |
| Controles programados y perdidos en 6 meses | 0 a 30; los perdidos no superan a los programados | Agenda e historia clínica | Predictores; originan la tasa de inasistencia |
| Test de Morisky-Green | Cuatro preguntas; adherente o incumplimiento | Entrevista al paciente (Anexo n.° 04) | Variable objetivo y línea base del OE1; nunca predictor |
| Registro de cada toma | Medicamento, dosis, hora programada, hora de registro, estado y motivo de omisión | Aplicación del paciente | Adherencia observada, retraso, alertas tempranas (RF05) |

El proyecto **no registra mediciones fisiológicas** —presión arterial, glucemia o hemoglobina glicosilada—. La decisión es deliberada: el sistema predice una conducta, la toma de la medicación, y no el control de la enfermedad; esos valores no constan de forma sistemática en todas las historias del consultorio, y un valor escrito por el propio paciente en la aplicación no sería verificable. Su incorporación, con dispositivos de medición conectados, es trabajo futuro (apartado 1.3).

#### f) Origen de los datos

| Fuente | Qué aporta | Estado |
| :--- | :--- | :--- |
| Historias clínicas del consultorio (Anexo n.° 03) | Las variables de la ficha, anonimizadas con un código P-001, P-002… | En extracción |
| Test de Morisky-Green (Anexo n.° 04) | La etiqueta de adherencia de cada paciente | En aplicación |
| Aplicación móvil | Las tomas registradas y corroboradas: la adherencia observada día a día | Operativa |

Hasta concluir la extracción, el sistema funciona con **pacientes de demostración** ficticios (códigos P-001 a P-005, solo en la base local de demostración) y el modelo está entrenado con un **conjunto de demostración de 400 fichas**; la propia ficha del paciente lo indica en pantalla.

#### g) Modelo predictivo y entrenamiento

El entrenamiento se ejecuta con `ml-pipeline/src/train_evaluate.py` y sigue estos pasos:

1. **Limpieza:** elimina duplicados, anula valores fuera de rango y excluye a quien no cumple el criterio de polimedicación.
2. **Partición:** 80 % entrenamiento y 20 % prueba, conservando la proporción de adherentes e incumplidores.
3. **Preparación:** completa los datos faltantes (mediana o moda), codifica las categorías y estandariza los números.
4. **Balanceo con SMOTE** [7]: genera casos sintéticos de incumplimiento, solo con datos de entrenamiento.
5. **Comparación de cuatro algoritmos:** Regresión Logística, Random Forest, XGBoost y SVM, con ajuste de hiperparámetros y validación cruzada de 5 pliegues.
6. **Selección:** gana el de mayor AUCROC en validación cruzada. La diferencia con el segundo se contrasta con la **prueba de DeLong**, que es la que corresponde a dos AUCROC medidas sobre los mismos pacientes [8]. Si no es significativa, el AUCROC no basta para preferir a uno y gana el de mayor sensibilidad, porque el error más costoso es no detectar a un paciente en riesgo. El contraste se hace sobre las predicciones fuera de pliegue del entrenamiento, de modo que el conjunto de prueba no interviene en la elección.
7. **Contraste complementario de decisiones:** la prueba de McNemar compara si los dos mejores, con el umbral de 0,5, alertarían sobre los mismos pacientes. No decide la selección: responde a una pregunta distinta de la del AUCROC, que mide cómo se ordena a los pacientes por riesgo sin depender de ningún umbral.
8. **Evaluación final** sobre el 20 % de prueba, que el modelo nunca vio, con el intervalo de confianza al 95 % de su AUCROC y su contraste frente al azar.
9. **Despliegue:** se guarda el modelo completo (preparación + algoritmo) y el microservicio de inferencia lo usa para calcular la probabilidad de cada paciente.

La probabilidad se traduce en tres niveles: **bajo** (menos de 40 %), **medio** (40 % a 69 %) y **alto** (70 % o más).

**Explicación con SHAP [5].** Para cada paciente, el microservicio calcula cuánto sube o baja el riesgo cada variable de su ficha respecto de un paciente de referencia. La suma de esas contribuciones lleva exactamente de la probabilidad de referencia a la del paciente, de modo que el médico ve **por qué** ese paciente tiene ese riesgo.

#### h) Cómo se calculan los porcentajes y promedios

**Tabla 14.** Indicadores que muestra el sistema.

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

#### i) Criterios de éxito del proyecto

Los criterios de éxito se fijaron al inicio del desarrollo con su métrica, su línea base y su meta, de modo que el cumplimiento pueda afirmarse o negarse con un número y no con una apreciación. Se distinguen los criterios de negocio, que miden el efecto sobre el consultorio, y los criterios analíticos, que miden el modelo predictivo.

**Tabla 15.** Criterios de éxito de negocio (CEN).

| Código | Criterio | Métrica | Línea base del consultorio | Meta |
| :---: | :--- | :--- | :--- | :--- |
| CEN-01 | Digitalizar el registro de la toma de medicamentos | % de tomas con registro digital trazable | 0 % (solo autorreporte verbal en consulta) | 100 % de las tomas prescritas |
| CEN-02 | Anticipar el incumplimiento antes de la cita | Días de anticipación del aviso respecto de la consulta | 0 (se detecta en la consulta, o después) | ≥ 1 aviso antes del próximo control |
| CEN-03 | Reducir el tiempo de revisión de la cartera de pacientes | Minutos para identificar a los pacientes en riesgo | ~50 fichas revisadas una a una | Lista priorizada en < 1 min |
| CEN-04 | Adopción del sistema por sus usuarios | Puntaje de la escala SUS [9] | No medido | ≥ 80 puntos |
| CEN-05 | Trazabilidad de la actuación del médico sobre el aviso | % de alertas cerradas con nota de lo actuado | 0 % (no existe registro) | 100 % de las alertas atendidas |

**Tabla 16.** Criterios de éxito analíticos del modelo predictivo (CEA).

| Código | Criterio | Métrica | Meta |
| :---: | :--- | :--- | :--- |
| CEA-01 | Capacidad discriminativa del modelo seleccionado | AUCROC en validación cruzada de 5 pliegues | ≥ 0,80 |
| CEA-02 | Detección de los pacientes que incumplen | Sensibilidad (exhaustividad de la clase incumplimiento) | ≥ 0,70 |
| CEA-03 | Comparación entre algoritmos con respaldo estadístico | Prueba de DeLong entre las AUCROC de los dos mejores, sobre predicciones fuera de pliegue | *p* e intervalo reportados, y criterio de desempate declarado |
| CEA-04 | Ausencia de fuga de información en la preparación | Imputación, codificación y balanceo ajustados solo con entrenamiento | 0 transformaciones ajustadas con el conjunto de prueba |
| CEA-05 | Explicación individual verificable | Probabilidad de referencia + contribuciones SHAP = probabilidad del paciente | Error ≤ 0,001 |
| CEA-06 | Tamaño mínimo del conjunto de entrenamiento | Fichas con etiqueta de adherencia | ≥ 50 pacientes del consultorio |
| CEA-07 | Latencia de la predicción en servicio | Tiempo de respuesta del microservicio | ≤ 2 s |
| CEA-08 | Procedencia declarada del modelo | Ficha del modelo con origen de los datos y marca de datos reales o simulados | 100 % de las predicciones con procedencia |

El estado frente a estos criterios se reporta en 1.1.8 para los analíticos y en 1.2 para los de negocio, y se resume en 1.4. Cuatro de ellos **no se cumplen a la fecha** y se declaran como tales, con su diagnóstico y su acción correctiva: CEA-01, CEA-02, CEA-06 y CEN-04.

---

### 1.1.3. Product Backlog general

La pila se priorizó con **MoSCoW** según su relación con la hipótesis: *Must* si sin él no se puede contrastar la hipótesis; *Should* si aporta valor clínico importante; *Could* si mejora la experiencia. La estimación usa puntos de Fibonacci.

**Tabla 17.** Product Backlog general refinado.

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
| PBI-11 | Como tesista, quiero comparar los algoritmos sobre una fuente de datos real y de acceso público para que el OE3 no dependa de la extracción documental | Protocolo completo ejecutado sobre pacientes reales con diagnóstico médico, con contraste estadístico y análisis de errores; el resultado se reporta aunque no alcance la meta | Must | 13 | Posterior al 4 | **Terminado** |
| PBI-12 | Como tesista, quiero verificar el producto con pruebas de caja negra y caja blanca para demostrar que cumple sus requisitos y que su lógica interna es correcta | Casos diseñados con técnicas formales y ejecutados sobre el sistema en marcha; cada defecto corregido con una prueba de regresión; informe de resultados reales | Must | 13 | Posterior al 4 | **Terminado** |

**Refinamiento de la pila.** La pila se revisó al cierre de cada sprint:

- **Sprint 2:** la exportación de reportes (RF07) pasó al Sprint 3.
- **Sprint 3:** se incorporaron **RF09** y **RF10**, nacidos de la revisión del producto: el registro de tomas dependía solo del paciente, y la recuperación de contraseña obligaba a ir al consultorio.
- **Sprint 3:** RF04 se amplió con la separación del modelo en un microservicio de inferencia, para ajustarse a la arquitectura aprobada en el proyecto.
- **Sprint 3:** se refinaron las variables de la ficha (RF02). La literatura asocia el nivel socioeconómico con la adherencia en población atendida en establecimientos públicos [10]; en una clínica privada, en cambio, esa variable, el tipo de seguro y la zona de residencia casi no varían entre pacientes, de modo que no ayudan a distinguir quién incumple. Se reemplazaron por **nivel educativo, convivencia y apoyo familiar**, que sí varían y se relacionan con la comprensión de las indicaciones y el olvido, las causas señaladas por el médico. Las comorbilidades pasaron de un número a una **lista de enfermedades**, para que la ficha sea específica.
- **Sprint 4:** se incorporó **PBI-11** como acción correctiva de la retrospectiva, al constatar que el OE3 quedaría indefinidamente en ejecución si su único resultado provenía del conjunto de demostración (apartado 1.1.8).
- **Tras el Sprint 4:** se incorporó **PBI-12**, la verificación formal del producto con pruebas de caja negra y caja blanca, exigida para el cierre; incluyó los ajustes que el Product Owner aceptó durante la verificación (apartado 1.1.11).

---

### 1.1.4. Sprint 1: Comprensión del negocio y de los datos

**Semanas 2–3 · CRISP-DM: *Business Understanding* y *Data Understanding*.**

**Objetivo.** Entender el problema clínico, priorizar la pila y entregar la autenticación (RF01).

**Tabla 18.** Sprint Backlog del Sprint 1.

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

Se aplicó la entrevista semiestructurada (Anexo n.° 02) al Dr. Milko Ugaz Zegarra. Hallazgos principales:

1. El seguimiento se basa **solo en lo que el paciente dice** en la consulta; no hay registro digital ni alertas.
2. El incumplimiento se detecta **tarde**, cuando el paciente ya se descompensó.
3. El consultorio atiende a unos **50 pacientes polimedicados** con hipertensión y/o diabetes.
4. Las causas percibidas son **el olvido, la complejidad del tratamiento y la falta de comprensión** de las indicaciones.

**Tabla 19.** Brechas identificadas y requisitos que las atienden.

| N.° | Brecha | Consecuencia | Requisito |
| :---: | :--- | :--- | :---: |
| B1 | No hay registro de la toma de medicamentos | El cumplimiento real no se puede verificar | RF03, RF07, RF09 |
| B2 | No hay seguimiento entre citas | Detección tardía | RF02, RF03 |
| B3 | No se analizan los datos clínicos | No se puede anticipar el incumplimiento | RF04, RF06 |
| B4 | No hay alertas ni recordatorios | El olvido no se mitiga | RF05, RF08 |

#### b) Factores de incumplimiento

**Tabla 20.** Factores identificados por dimensión OMS [6].

| Dimensión OMS | Factores en el consultorio | Variable asociada |
| :--- | :--- | :--- |
| Paciente | Olvido; falta de comprensión de las indicaciones | Edad, sexo |
| Socioeconómica y social | Nivel de instrucción; soledad o falta de apoyo en casa | Nivel educativo, convivencia, apoyo familiar |
| Enfermedad | Cronicidad y multimorbilidad | Diagnóstico, tiempo de enfermedad, comorbilidades |
| Terapia | Muchos fármacos y tomas | N.° de fármacos, tomas por día |
| Sistema de salud | Inasistencia a controles | Controles programados y perdidos |

**Línea base de contexto.** El 37,1 % de los pacientes peruanos con hipertensión y diabetes tiene adherencia deficiente [11]; en Lambayeque, el 44,7 % de los pacientes crónicos no cumple su tratamiento [12]. La línea base propia del consultorio se obtiene con el test de Morisky-Green (en ejecución).

#### c) Incremento: autenticación (RF01)

Se implementó el inicio de sesión con token JWT y control de acceso por perfil (`backend-api/app/api/auth.py`). Ante cualquier error de acceso se devuelve la misma respuesta, para no revelar qué correos están registrados.

**Tabla 21.** Pruebas del Sprint 1.

| Caso | Esperado | Obtenido |
| :--- | :--- | :---: |
| Credenciales y perfil válidos | Acceso con token | ✔ `200` |
| Perfil equivocado o usuario inexistente | Rechazo sin indicar la causa | ✔ `401` |
| Consulta sin token | Rechazo | ✔ `401` |
| Correo mal formado o contraseña corta | Error por campo | ✔ `422` |

**Tabla 22.** Incidencias del Sprint 1.

| ID | Componente | Incidencia | Causa | Corrección | Estado |
| :---: | :--- | :--- | :--- | :--- | :---: |
| I-01 | API / Datos | Reglas clínicas repartidas entre el código y la base de datos | No había un criterio de dónde ubicar cada regla | Llevarlas a restricciones de la base de datos (Sprint 2) | Cerrada |

**Review y retrospectiva.** Se aceptó RF01 y se validaron con el médico el modelo de datos y la pila. Mejora acordada: centralizar las reglas clínicas en la base de datos.

---

### 1.1.5. Sprint 2: Preparación de datos y registro clínico

**Semanas 3–4 · CRISP-DM: *Data Preparation* y *Modeling* inicial.**

**Objetivo.** Entregar el registro clínico que alimenta al modelo (RF02 y RF03), preparar el pipeline de datos y configurar la comparación de algoritmos. Es la entrada del núcleo funcional, cuyo cierre completo corresponde al Sprint 3 por la dependencia técnica declarada en 1.1.

**Tabla 23.** Sprint Backlog del Sprint 2.

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
| OE3 | `train_evaluate.py`: cuatro algoritmos, validación cruzada y contraste estadístico | ML | 8 | **Terminada** |
| RNF01/04 | Despliegue en Aiven, Render y Vercel | Infraestructura | 5 | **Terminada** |
| | **Comprometido: 63 · Completado: 58 (92 %)** | | **63** | |

#### a) Requisitos no funcionales

**Tabla 24.** Requisitos no funcionales (ISO/IEC 25010 [13]).

| Código | Requisito | Atributo | Cómo se cumple |
| :---: | :--- | :--- | :--- |
| RNF01 | Datos protegidos en tránsito y en reposo | Seguridad | HTTPS, cabeceras de seguridad, contraseñas cifradas, código anonimizado; 20 pruebas de verificación (Tabla 33) |
| RNF02 | Respuesta de la predicción en ≤ 2 s | Eficiencia | Tiempo medido en cada respuesta: entre 90 y 250 ms por predicción con su explicación, con un usuario (Tablas 30 y 37) |
| RNF03 | Interfaz usable por médicos y adultos mayores | Capacidad de interacción | Barra de navegación rotulada; evaluación SUS en el Sprint 4 |
| RNF04 | Disponibilidad para la consulta clínica | Fiabilidad | Manejo global de errores, sonda `/health`, reintento en la app y reintento de la conexión al arrancar el servicio |
| RNF05 | Código modular | Mantenibilidad | Capas `api`, `core`, `db`, `schemas`, `services` |
| RNF06 | Escalable y reentrenable | Flexibilidad | Modelo desacoplado de la API |

#### b) Preparación de los datos

El Anexo n.° 03 se formalizó como el esquema del conjunto de datos, con una plantilla CSV que el pipeline valida columna por columna.

**Tabla 25.** Reglas de limpieza del pipeline.

| Regla | Tratamiento |
| :--- | :--- |
| Paciente duplicado | Se conserva el registro más reciente |
| Categoría o número fuera de rango | Se marca como faltante y se completa después |
| Controles perdidos mayores que programados | Se anula ese dato |
| Menos de 5 fármacos o sin etiqueta | Se excluye al paciente |

El balanceo con SMOTE se aplica **después** de separar entrenamiento y prueba, y dentro de cada pliegue de la validación cruzada, para que las métricas no salgan infladas.

#### c) Configuración de la comparación de algoritmos (OE3)

**Tabla 26.** Algoritmos candidatos.

| Algoritmo | Por qué se incluye | Hiperparámetros evaluados |
| :--- | :--- | :--- |
| Regresión Logística | Referencia simple e interpretable | `C` ∈ {0,01; 0,1; 1; 10} |
| Random Forest | Robusto con variables mixtas [14] | `n_estimators` ∈ {200; 500}, `max_depth` ∈ {None; 8; 12} |
| XGBoost | Referente en datos clínicos tabulares [3] | `learning_rate` ∈ {0,05; 0,1}, `max_depth` ∈ {3; 5; 7} |
| SVM (RBF) | Eficaz con muestras pequeñas | `C` ∈ {0,1; 1; 10}, `gamma` ∈ {scale; 0,01} |

Métricas: exactitud, sensibilidad, especificidad, F1-score y AUCROC (meta ≥ 0,80), con semilla fija 42.

#### d) Núcleo funcional (RF02 y RF03)

- **Pacientes:** el médico registra, edita y da de baja fichas; solo ve a sus propios pacientes.
- **Tomas:** la app envía cada toma; si la reenvía por falta de señal, se actualiza en lugar de duplicarse.
- **Despliegue:** base de datos en Aiven, API en Render y panel en Vercel, con conexión cifrada.

**Tabla 27.** Pruebas del Sprint 2 (selección).

| Grupo | Caso | Resultado |
| :--- | :--- | :---: |
| RF02 | Alta guardada con código correlativo | ✔ `201` |
| RF02 | Rechazo con menos de 5 fármacos o controles incoherentes | ✔ `422` |
| RF02 | Baja lógica: el historial se conserva | ✔ |
| RF03 | Reenvío de la misma toma no duplica | ✔ `201` → `200` |
| RF03 | Cumplimiento: 3 cumplidas de 5 = 60 % | ✔ |
| Seguridad | Médico ajeno o paciente sin permiso | ✔ `403` |
| Despliegue | Documentación oculta y `Host` falsificado rechazado en producción | ✔ `404` / `403` |

**Tabla 28.** Incidencias del Sprint 2.

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

### 1.1.6. Sprint 3: Modelo integrado y cierre del núcleo funcional

**Semanas 5–6 · CRISP-DM: *Modeling* (selección) y *Evaluation*.**

**Objetivo.** Integrar el modelo al sistema mediante un microservicio de inferencia con explicación SHAP, completar la app del paciente y el grupo familiar, y seleccionar el algoritmo.

**Tabla 29.** Sprint Backlog del Sprint 3.

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

El microservicio aplica el explicador por permutaciones de SHAP [5], que funciona con cualquier algoritmo, incluido el SVM seleccionado. La referencia son 12 perfiles promedio del entrenamiento (centroides), no fichas de pacientes reales. La ficha muestra las seis variables con más peso, con barras que suben o bajan el riesgo.

**Tabla 30.** Verificación de la explicación SHAP.

| Verificación | Resultado |
| :--- | :--- |
| Probabilidad de referencia + contribuciones = probabilidad del paciente | ✔ Cumple en todas las pruebas (tolerancia 0,005) |
| Coincidencia con el explicador *Kernel* de SHAP | ✔ Correlación 0,993; diferencia máxima 0,029 |
| Misma ficha, misma explicación | ✔ Reproducible |
| Más controles perdidos, mayor contribución de la inasistencia | ✔ |
| Tiempo de respuesta con el servicio activo | ✔ ≈ 90 ms (meta RNF02: ≤ 2 s) |

**Ejemplo con el paciente de demostración P-001.** Riesgo predicho 54 % frente a 34 % del paciente de referencia. Suben el riesgo: controles perdidos (+21,5 pp), inasistencia a controles (+15,4 pp) y tiempo de enfermedad (+6,9 pp). Lo bajan: controles programados (−11,0 pp), apoyo familiar en la medicación (−8,5 pp) y número de fármacos (−6,9 pp).

#### c) Selección del algoritmo: corrida de verificación

El protocolo completo se ejecutó sobre el conjunto de demostración (400 fichas: 320 de entrenamiento y 80 de prueba). En la preparación, el 2,25 % de las celdas estaba vacío (tiempo de enfermedad 12 %, nivel educativo 8 %, convivencia 5 %, edad 2 %) y la proporción fue de 334 adherentes y 66 incumplidores; SMOTE equilibró el entrenamiento a 267 y 267.

**Tabla 31.** Comparación de algoritmos en la corrida de verificación (validación cruzada de 5 pliegues; media ± desviación).

| Algoritmo | Hiperparámetros | Exactitud | Sensibilidad | Especificidad | F1-score | AUCROC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Regresión Logística | `C=1` | 0,781 ± 0,049 | 0,625 ± 0,094 | 0,813 ± 0,056 | 0,490 ± 0,074 | **0,864 ± 0,047** |
| **SVM (RBF)** *(seleccionado)* | `C=1`, `gamma=0,01` | 0,762 ± 0,047 | **0,794 ± 0,064** | 0,757 ± 0,060 | 0,530 ± 0,056 | 0,856 ± 0,044 |
| Random Forest | `n_estimators=500`, `max_depth=8` | 0,822 ± 0,051 | 0,494 ± 0,167 | 0,888 ± 0,036 | 0,477 ± 0,140 | 0,825 ± 0,057 |
| XGBoost | `learning_rate=0,05`, `max_depth=3` | 0,816 ± 0,030 | 0,455 ± 0,081 | 0,888 ± 0,026 | 0,450 ± 0,074 | 0,815 ± 0,063 |

**Lectura.** Los cuatro algoritmos superan la meta de AUCROC ≥ 0,80. Regresión Logística obtuvo el mayor AUCROC, pero la prueba de DeLong frente a SVM no encontró diferencia entre ambas AUCROC (diferencia +0,009; IC95 −0,010 a 0,027; *p* = 0,349). Con las dos AUCROC estadísticamente equivalentes, el criterio de desempate seleccionó **SVM**, que detecta más incumplidores (sensibilidad 0,794 frente a 0,625). En el conjunto de prueba, SVM obtuvo exactitud 0,775, sensibilidad 0,615, especificidad 0,806, F1-score 0,471 y AUCROC 0,809 (IC95 0,698 a 0,921). Estas cifras **verifican que el protocolo y el sistema funcionan**, y nada más: se obtuvieron sobre un conjunto generado con una relación latente conocida, de modo que no constituyen un hallazgo de la investigación y así se declaran en la ficha del modelo (CEA-08). El resultado del OE3 sobre datos reales se presenta en 1.1.8, y el definitivo se obtendrá con el mismo script sobre las historias clínicas del consultorio.

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

**Tabla 32.** Reglas de alerta y su fundamento.

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

**Tabla 33.** Verificación de seguridad del API.

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

**Tabla 34.** Pruebas automatizadas al corte.

| Componente | Casos | Alcance | Resultado |
| :--- | :---: | :--- | :---: |
| API central (`pytest`) | 183 | RF01–RF05, RF07, RF09, RF10, permisos, seguridad (RNF01), resistencia del arranque, integración real con el modelo y caminos básicos de caja blanca | ✔ 182/182; 1 omitida, la de integración real, que requiere el entorno del microservicio |
| Microservicio de inferencia (`pytest`) | 25 | Predicción, lote, clave de servicio, propiedad aditiva de SHAP, versiones del modelo y caminos básicos de caja blanca | ✔ 25/25 |
| App móvil (`flutter test`) | 62 | Sincronización sin conexión, reintento, recordatorios, acceso, grupo familiar, tarjeta de toma y términos | ✔ 62/62 |
| Panel web (`node --test`) | 12 | Limpieza de los campos del formulario; además, compilación y análisis estático | ✔ 12/12 |
| **Total** | **282** | 281 ejecutadas y aprobadas | **✔** |

Sobre estas pruebas se aplicaron las dos técnicas clásicas de verificación. Las **pruebas de caja negra** (Anexo n.° 24) diseñan 59 casos automatizados y 10 manuales desde los requisitos, con partición de equivalencia, valores límite, tablas de decisión y transición de estados. La ejecución final fue conforme en los 59 casos, y los ciclos previos detectaron y corrigieron cinco defectos. Las **pruebas de caja blanca** (Anexo n.° 25) analizan doce funciones del núcleo funcional: miden su complejidad ciclomática, recorren cada camino independiente con una prueba y alcanzan el 100 % de líneas y ramas de esas funciones. La cobertura de cada componente completo es del 92 % en el API y del 94 % en el microservicio.

**Tabla 35.** Incidencias del Sprint 3.

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
| I-16 | Web | No se guardaban cambios en las fichas de demostración | Se validaba el código también al editar | Validarlo solo en el alta | Cerrada |
| I-17 | Web | La contraseña temporal desaparecía | Se recargaba la ficha al generarla | Recargar solo al ocultarla | Cerrada |
| I-18 | ML | El desempate por sensibilidad no se aplicaba | El código solo desempataba con AUCROC idéntico | Contrastar estadísticamente la diferencia de AUCROC antes de elegir (hoy, prueba de DeLong; apartado 1.1.8.c) | Cerrada |
| I-19 | Microservicio | La primera explicación SHAP tardaba 5 s | SHAP se prepara internamente en su primer uso | Ejecutar una explicación de prueba al arrancar | Cerrada |
| I-20 | API | La alerta de riesgo predicho hacía fallar la bandeja | El umbral se trasladó al microservicio y el API seguía consultándolo | Usar el nivel de riesgo que devuelve el microservicio | Cerrada |
| I-21 | API | Una alerta cerrada por el médico reaparecía en la consulta siguiente | Las reglas no distinguían un caso ya atendido | Plazo de silencio tras atender o descartar, salvo que la evidencia empeore | Cerrada |
| I-22 | Despliegue | El servicio publicado dejó de arrancar y no se podía entrar al sistema | Las migraciones se aplican al arrancar y la base gestionada no resolvió su nombre en ese instante: un fallo de segundos tumbaba el despliegue entero | Reintentar la conexión (5 s, 15 s y 30 s) antes de rendirse, con un mensaje que indica qué revisar | Cerrada |

**Cierre del sprint: el núcleo funcional queda completo.** Con RF04, RF05 y RF06 terminados sobre el registro que entregó el Sprint 2, el recorrido definido en 1.1 —registro de la toma → riesgo predicho y explicado → alerta temprana— es ejecutable de extremo a extremo y así se demuestra en 1.1.9. Es el punto en el que el producto deja de ser un registro de tomas y se convierte en un sistema de soporte a la decisión. Se entregaron todos los elementos comprometidos salvo la comparación de algoritmos sobre las historias clínicas reales, que no depende del desarrollo sino de la extracción documental.

**Sprint Review (Sprint 3).** Se aceptaron el microservicio de inferencia con explicación SHAP, las alertas tempranas, el acceso móvil, los reportes y la verificación de seguridad. **Retrospectiva:** los tres defectos que solo aparecieron sobre el servicio publicado (I-14, I-15 e I-22) llevaron a incorporar al procedimiento la verificación sobre el entorno desplegado y no solo en local, y a que el arranque del servicio reintente la conexión en lugar de rendirse al primer fallo.

---

### 1.1.7. Sprint 4: Cierre, rendimiento y validación

**Semanas 7–8 · CRISP-DM: *Deployment*.**

**Objetivo.** Medir el rendimiento del sistema con usuarios simultáneos, verificar los atributos de calidad, evaluar la usabilidad con usuarios reales y consolidar las evidencias.

**Tabla 36.** Sprint Backlog del Sprint 4 (semanas 7–8).

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

**Tabla 37.** Tiempo de respuesta según el número de usuarios simultáneos (mediana y percentil 95).

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

**Tabla 38.** Atributos verificados y su evidencia.

| Atributo [13] | Qué se verificó | Evidencia | Estado |
| :--- | :--- | :--- | :---: |
| Adecuación funcional | Los 10 requisitos funcionales operan de extremo a extremo | 282 pruebas automatizadas, 59 casos de caja negra (Anexo n.° 24) y apartado 1.1.9 | ✔ |
| Eficiencia de desempeño | Respuesta ≤ 2 s con 10 usuarios simultáneos | Tabla 37 | ✔ |
| Compatibilidad | Panel en navegador, aplicación en Android 7.0 o superior, servicios comunicados por REST | APK instalado en dispositivo real | ✔ |
| Capacidad de interacción *(usabilidad en la edición de 2011)* | Interfaz rotulada, validación con mensajes y confirmación de cada acción | Pendiente de medir con la escala SUS (OE5) | ◐ |
| Fiabilidad | El sistema degrada sin detenerse: cola sin conexión, reintentos y arranque tolerante a cortes | Incidencias I-08, I-15 e I-22 y sus pruebas | ✔ |
| Seguridad | Acceso por perfil, aislamiento por médico tratante, cifrado en tránsito y datos anonimizados hacia el modelo | 20 pruebas de seguridad (Tabla 33) | ✔ |
| Mantenibilidad | Separación en capas y servicios, migraciones versionadas, pruebas por componente | Estructura del repositorio; complejidad ciclomática promedio 2,5 y cobertura del 92 % en el API (Anexo n.° 25) | ✔ |
| Flexibilidad *(portabilidad en la edición de 2011)* | Despliegue reproducible desde el repositorio en tres plataformas | `render.yaml`, `DESPLIEGUE.md` | ✔ |
| Protección *(safety; nueva en la edición de 2023)* | El sistema no presenta como riesgo un valor que no calculó: sin el microservicio responde «no disponible» y las alertas por reglas siguen operando; cada predicción declara con qué datos se entrenó el modelo; los datos clínicamente imposibles se rechazan antes de entrar | Pruebas de microservicio caído, de procedencia en cada predicción y de alertas sin modelo; validaciones de la ficha (Tabla 43, paso 2) | ✔ |

La edición de 2023 de la norma organiza la calidad del producto en nueve características: renombra la usabilidad como *capacidad de interacción* y la portabilidad como *flexibilidad*, y añade la *protección* —que el producto no ponga en riesgo la salud—, especialmente pertinente en un sistema de soporte clínico. La capacidad de interacción queda como la única característica sin medir: su evaluación con la escala SUS necesita al médico y a una muestra de pacientes, y se ejecuta sobre el recorrido del apartado 1.1.9.

#### c) Cierre del sprint

**Sprint Review (Sprint 4).** Se aceptaron la prueba de rendimiento, la verificación ISO/IEC 25010, el guion de demostración, el arranque tolerante a cortes de la base y la consolidación del repositorio. Quedaron sin entregar los dos elementos que dependen de personas: la evaluación SUS y la comparación sobre historias clínicas reales.

**Retrospectiva.** Medir antes de optimizar resultó decisivo: la prueba de carga señaló dos costes —una conexión nueva por consulta y la predicción de todos los pacientes en cada apertura— que ninguna lectura del código habría revelado. Descontar de la medición lo que no es tiempo del sistema evitó además una conclusión falsa: el primer intento atribuía al listado de pacientes una demora que era el establecimiento de la conexión del cliente.

**Acción correctiva acordada: PBI-11.** La retrospectiva identificó un impedimento que el desarrollo no podía retirar: con el único resultado proveniente del conjunto de demostración, el OE3 quedaría «en ejecución» mientras durase la extracción documental, y el informe no podría reportar ninguna comparación de algoritmos defendible. En lugar de arrastrar el elemento otro sprint, el Product Owner incorporó a la pila **PBI-11 — comparar los algoritmos sobre una fuente de datos real y de acceso público**, con prioridad *Must* y por encima de cualquier funcionalidad nueva. Su incremento es el apartado 1.1.8.

Las actas completas de las cuatro ceremonias constan en el Anexo n.° 09.

---

### 1.1.8. Comparación de algoritmos sobre datos reales: conjunto externo ENDES

Este apartado es el incremento de **PBI-11**, el elemento que la retrospectiva del Sprint 4 incorporó a la pila como acción correctiva (apartado 1.1.7.c). En el reparto de los dos marcos corresponde a la fase de *Evaluation* de CRISP-DM, atendida como elemento de SCRUM posterior al Sprint 4 y sujeta a la misma Definición de Terminado que el resto (Tabla 5).

El criterio de aceptación acordado fue: *ejecutar el protocolo completo de comparación —cuatro algoritmos, validación cruzada estratificada, contraste estadístico y análisis de errores— sobre pacientes reales con diagnóstico médico de hipertensión o diabetes, y reportar el resultado aunque no alcance la meta.*

#### a) Fuente y construcción del conjunto

Se emplearon los microdatos de la Encuesta Demográfica y de Salud Familiar (ENDES) del Instituto Nacional de Estadística e Informática [15], en los módulos de salud (CSALUD01) y de hogar (RECH0) de los años 2014 a 2017. La etiqueta proviene de las preguntas QS106 y QS113 de la propia encuesta —«¿tomó los medicamentos tal cual le indicó el médico?»—, que miden el mismo constructo que el test de Morisky-Green: un paciente que dispone del medicamento y no lo toma como se le indicó.

**Tabla 39.** Conjunto externo construido a partir de la ENDES 2014-2017.

| Característica | Valor |
| :--- | :--- |
| Pacientes con diagnóstico médico de hipertensión o diabetes y respuesta de adherencia | 8 422 |
| Distribución del diagnóstico | Hipertensión 5 843 · Diabetes 1 397 · Ambas 1 182 |
| Incumplimiento (clase positiva) | 1 155 (13,7 %); razón de desbalance 6,29 : 1 |
| Celdas faltantes tras la depuración | 1,89 % |
| Partición estratificada | 6 737 entrenamiento / 1 685 prueba |
| Entrenamiento tras SMOTE | 11 626 filas (5 813 por clase) |

El rango se cerró en 2017 porque **desde 2018 el INEI dejó de publicar el tiempo transcurrido desde el diagnóstico**: las columnas existen en el archivo pero vienen vacías. Incluir esos años habría duplicado la muestra a costa de imputar la mitad de una variable clínica, lo que no es defendible.

**Por qué esta prevalencia no es la de la línea base.** El apartado 1.1.4 cita el 37,1 % de adherencia deficiente que reporta el análisis nacional sobre esta misma encuesta [11], y aquí se obtiene 13,7 %. La diferencia no es un error de construcción, sino de **operacionalización de la etiqueta**, y conviene dejarla explícita:

**Tabla 40.** Prevalencia del incumplimiento según la definición de la etiqueta.

| Definición de incumplimiento | Pacientes | Incumplimiento |
| :--- | :---: | :---: |
| **Estricta** — compró el medicamento y declara no haberlo tomado como se le indicó | 8 422 | 13,7 % |
| **Amplia** — suma a quien no llegó a comprar el medicamento | 13 033 | 46,0 % |
| Referencia publicada para el Perú, 2014-2019 [11] | 15 184 | 37,1 % |

El modelo se entrena con la **definición estricta** porque es la que corresponde al constructo del estudio: el sistema predice que un paciente *con tratamiento disponible* dejará de cumplirlo, que es lo que mide el test de Morisky-Green y lo que el médico puede intervenir. No adquirir el medicamento es un problema de acceso, clínicamente relevante pero distinto, y mezclarlo haría que el modelo aprendiera dos fenómenos a la vez. La cifra amplia se reporta para que la comparación con la literatura sea verificable y no quede una contradicción aparente entre dos apartados del propio informe.

#### b) Variables disponibles y variables ausentes

La encuesta cubre siete de los doce predictores del Anexo n.° 03 y **ninguno** de los que dependen de la receta o de la agenda de controles. Quedan fuera del modelo `numero_farmacos`, `tomas_dia`, `controles_programados_6m`, `controles_perdidos_6m` y `apoyo_familiar`; tampoco puede aplicarse el criterio de elegibilidad por polimedicación, de modo que la población es más amplia que la del estudio. El pipeline se ejecutó con un **perfil reducido** declarado explícitamente, que recorta el esquema a lo que la fuente registra en lugar de rellenar con ceros columnas que nadie midió.

#### c) Resultados de la comparación

**Tabla 41.** Comparación de algoritmos sobre la ENDES 2014-2017 (validación cruzada de 5 pliegues; media ± desviación).

| Algoritmo | Hiperparámetros | Exactitud | Sensibilidad | Especificidad | F1-score | AUCROC | Decisión |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Random Forest** *(seleccionado)* | `n_estimators=200`, `max_depth=8`, `min_samples_leaf=5` | 0,635 ± 0,011 | 0,450 ± 0,054 | 0,664 ± 0,021 | 0,252 ± 0,018 | **0,591 ± 0,018** | Mayor AUCROC; empata con XGBoost según DeLong y lo supera en sensibilidad |
| XGBoost | `learning_rate=0,05`, `max_depth=3`, `n_estimators=400` | 0,825 ± 0,009 | 0,097 ± 0,017 | 0,941 ± 0,012 | 0,132 ± 0,018 | 0,589 ± 0,024 | Empata en AUCROC; descartado por sensibilidad |
| Regresión Logística | `C=0,1` | 0,545 ± 0,007 | 0,590 ± 0,030 | 0,538 ± 0,012 | 0,262 ± 0,008 | 0,588 ± 0,017 | Menor AUCROC en validación cruzada |
| SVM (RBF) | `C=0,1`, `gamma=escala` | 0,519 ± 0,025 | 0,622 ± 0,049 | 0,503 ± 0,036 | 0,262 ± 0,009 | 0,586 ± 0,021 | Menor AUCROC en validación cruzada |

**Contraste entre los dos mejores.** La diferencia de AUCROC entre Random Forest y XGBoost se contrastó con la prueba de DeLong [8], sobre las predicciones fuera de pliegue del entrenamiento: diferencia +0,002, IC95 −0,009 a 0,013, *p* = 0,742. Ambos ordenan a los pacientes por riesgo con la misma capacidad, de modo que el AUCROC no permite preferir a uno, y el criterio de desempate seleccionó Random Forest por su sensibilidad (0,450 frente a 0,097).

**Contraste complementario de decisiones.** La prueba de McNemar, con el umbral de 0,5, encontró 2 034 pacientes en los que ambos modelos discrepan (χ² = 809,29; *p* < 0,001). No contradice al contraste anterior, porque responde a otra pregunta: dos modelos pueden ordenar igual de bien a los pacientes y, con un mismo umbral, alertar sobre pacientes distintos. Es lo que ocurre aquí: XGBoost reúne 1 659 aciertos que Random Forest no tiene, casi todos en pacientes adherentes, porque casi nunca predice incumplimiento.

**Desempeño en la prueba reservada.** Random Forest obtuvo AUCROC 0,571 (IC95 0,532 a 0,610), mayor que el azar de forma estadísticamente significativa (*p* = 0,0002). En la prueba reservada el orden de los cuatro algoritmos cambia —sus AUCROC van de 0,571 a 0,626—, lo que es coherente con diferencias entre ellos que no son estables.

> **Corrección tras la evaluación del pre informe.** En la versión anterior, la selección se justificaba con la prueba de McNemar calculada sobre el conjunto de prueba. La observación del evaluador era correcta: McNemar compara aciertos con un umbral, no AUCROC. El protocolo se corrigió en el código —DeLong para el AUCROC, sobre predicciones fuera de pliegue, y McNemar solo como contraste de decisiones— y la comparación se ejecutó de nuevo. El modelo seleccionado no cambia, pero su fundamento sí: la versión anterior afirmaba que ambos modelos diferían de forma significativa, y lo que difiere son sus decisiones, no su AUCROC.

#### d) Análisis de resultados y de errores

**CEA-01 no se cumple.** El mejor AUCROC es 0,591, muy por debajo de la meta de 0,80. En validación cruzada los cuatro algoritmos quedan en una banda de 0,586 a 0,591: por encima del azar, lejos de la meta y sin diferencias apreciables entre familias de algoritmos de naturaleza tan distinta —lineal, de ensamble por promediado, de ensamble secuencial y de margen máximo—.

El caso de XGBoost conviene leerlo con cuidado: alcanza una **exactitud de 0,825 con una sensibilidad de 0,097**. Detecta a uno de cada diez pacientes que incumplen. Con clases desbalanceadas, la exactitud premia al clasificador que predice casi siempre la clase mayoritaria, y por eso la literatura la desaconseja como criterio de selección [16]: XGBoost predice «adherente» casi siempre y acierta el 82,5 % de las veces porque el 86,3 % de la muestra es adherente. Reportarlo por su exactitud lo haría parecer el mejor modelo, cuando es el más inservible como alerta temprana (RF05). Esta es la razón de que el protocolo seleccione por AUCROC y desempate por sensibilidad.

El análisis de importancia por permutación del modelo seleccionado sitúa en cabeza a la edad (0,035), al tiempo de enfermedad (0,026) y al nivel educativo (0,009), con un aporte prácticamente nulo de las comorbilidades (−0,0001). Son contribuciones pequeñas en términos absolutos, coherentes con el bajo AUCROC.

**Qué permite afirmar el resultado y qué no.** Que cuatro familias de algoritmos converjan en el mismo desempeño indica que, con estas variables y esta etiqueta, la elección del algoritmo no es el factor limitante. No permite, en cambio, atribuir el bajo desempeño a una sola causa. Al menos tres explicaciones son compatibles con él, y este análisis no las separa:

1. **Información insuficiente en las variables.** La encuesta no registra el número de fármacos, las tomas al día, los controles perdidos ni el apoyo familiar en la toma.
2. **Ruido en la etiqueta.** El incumplimiento procede de una sola pregunta de autorreporte, un método indirecto con limitaciones conocidas frente a otras formas de medir la adherencia [17].
3. **Diferencia de población.** La ENDES incluye a pacientes no polimedicados y de todo el país; la relación entre las variables y la adherencia puede no ser la misma que en el consultorio.

**Tabla 42.** Qué demuestra y qué no demuestra cada análisis del conjunto externo.

| Análisis | Qué demuestra | Qué no demuestra |
| :--- | :--- | :--- |
| Comparación en validación cruzada | Ninguno de los cuatro algoritmos alcanza AUCROC 0,80 con estas variables y esta etiqueta | Que ningún algoritmo pueda alcanzarlo con otras variables o con otra etiqueta |
| DeLong entre los dos mejores | Random Forest y XGBoost ordenan a los pacientes con capacidad equivalente | Que Random Forest supere a los otros tres: solo se contrastaron los dos primeros |
| McNemar con umbral de 0,5 | Con el mismo umbral, ambos alertarían sobre pacientes distintos | Que uno ordene mejor que el otro |
| AUCROC en prueba con su intervalo | Las variables contienen señal: el desempeño supera al azar | Que esa señal sea clínicamente útil: 0,571 está lejos de la meta |
| Importancia por permutación | Qué variables usa más el modelo elegido | Que esas variables causen el incumplimiento, ni qué aportarían las variables ausentes |
| Prevalencia según la definición (Tabla 40) | El conjunto es comparable con la literatura nacional cuando se usa una definición equivalente | Que la etiqueta equivalga al test de Morisky-Green |

#### e) Qué aporta este resultado al OE3

El objetivo específico queda **ejecutado sobre datos reales**: cuatro algoritmos comparados con validación cruzada estratificada, contraste estadístico, análisis de errores y modelo seleccionado, sobre 8 422 pacientes peruanos con diagnóstico médico de hipertensión o diabetes. Su hallazgo es acotado y conviene enunciarlo con esa precisión: **con las variables sociodemográficas que registra la encuesta, el incumplimiento se predice solo débilmente —por encima del azar y lejos de la meta—, y la elección del algoritmo no cambia ese resultado.**

La extracción del Anexo n.° 03 permite contrastar la primera de las tres explicaciones, y el diseño de ese contraste queda fijado desde ahora. La ficha registra las variables de terapia y de seguimiento que la encuesta no tiene —las que el modelo de adherencia de la OMS sitúa en sus dimensiones de terapia y de sistema de salud [6]—, y su etiqueta procede del test de Morisky-Green completo. Sobre los **mismos pacientes del consultorio** se compararán dos modelos: uno restringido a las variables que tiene la encuesta y otro con la ficha completa. Si el segundo mejora de forma significativa, el resultado apoyará que la limitación estaba en las variables; si no mejora, esa explicación deberá descartarse. Hasta entonces es una **hipótesis de trabajo**, no una conclusión del estudio.

**Trazabilidad de la ejecución.** El conjunto se reconstruye con `python src/endes.py` y la comparación se repite con `python src/train_evaluate.py --perfil endes`. Los artefactos del perfil reducido se escriben con sufijo propio (`risk_model_endes_v1`), de modo que no sustituyen al modelo en servicio: son dos esquemas de variables distintos y confundirlos rompería la inferencia.

---

### 1.1.9. Demostración del escenario principal

El escenario principal recorre, de principio a fin, la función para la que existe el producto: **anticipar el incumplimiento de un paciente polimedicado y avisar al médico antes del próximo control**. Se ejecuta sobre el sistema desplegado, sin depender de funciones no implementadas, y cada paso corresponde a un requisito y a un objetivo.

**Tabla 43.** Escenario principal: pasos, requisitos y evidencia.

| # | Paso | Requisito · Objetivo | Resultado observable |
| :---: | :--- | :--- | :--- |
| 1 | El médico registra al paciente polimedicado con las variables del Anexo n.° 03 | RF02 · OE4 | Ficha guardada con código P-00N y confirmación en pantalla |
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

El paso a paso de cada pantalla, con capturas, está en el manual de usuario (Anexo n.° 23), y la verificación de cada paso con datos de prueba, en las pruebas de caja negra (Anexo n.° 24).

**Antes de demostrar.** El plan gratuito suspende los servicios tras quince minutos sin tráfico; `backend-api/scripts/despertar.py` los despierta y confirma que el modelo está cargado, de modo que la espera no ocurra durante la sustentación.

---

### 1.1.10. Registro consolidado de incidencias

**Tabla 44.** Incidencias por sprint.

| Sprint | Incidencias | Componentes tocados | Por componente | Detectadas por prueba o revisión | Abiertas |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 1 | 4 | 0,25 | 0 de 1 (retrospectiva) | 0 |
| 2 | 6 | 5 | 1,20 | 5 de 6 | 0 |
| 3 | 15 | 6 | 2,50 | 13 de 15 | 0 |
| 4 | 0 | — | — | — | 0 |
| **Total** | **22** | — | — | **18 de 22** | **0** |

**Lectura.** Las incidencias aumentan en el Sprint 3 porque es el primero que se ejecuta sobre el servidor publicado y un teléfono real, y el que más componentes nuevos incorpora. El Sprint 4 no registró ninguna nueva: se dedicó a medir y verificar lo ya construido, y la condición 4 de la Definición de Terminado —desplegado, no solo en local— había absorbido en el sprint anterior la clase de defecto que más pesaba. Todas están cerradas.

Según su origen: seis por el comportamiento de librerías de terceros (I-02, I-03, I-05, I-06, I-09, I-10), seis por diferencias entre el entorno de desarrollo y el publicado (I-08, I-11, I-12, I-14, I-15, I-22), cuatro de interfaz (I-04, I-07, I-16, I-17), dos por diferencias entre lo documentado y lo implementado (I-18, I-20), una de texto desactualizado (I-13), una de rendimiento en el primer uso (I-19), una de diseño de la propia alerta (I-21) y una de diseño detectada en retrospectiva (I-01).

El grupo que más pesa sigue siendo el de las diferencias entre desarrollo y publicación, y de ahí la práctica que se mantiene: verificar cada cambio sobre el artefacto que se entrega —el APK de publicación, el servicio desplegado— y no solo sobre la ejecución local.

---

### 1.1.11. Verificación formal del producto: pruebas de caja negra y caja blanca (PBI-12)

Las pruebas automatizadas de cada sprint verifican lo que el equipo decidió probar. El cierre exige además una verificación formal, con técnicas de diseño de casos reconocidas y resultados reales. Se atendió como **PBI-12**, elemento posterior al Sprint 4 sujeto a la misma Definición de Terminado (Tabla 5), y se aplicaron las dos familias de técnicas, que se complementan: la caja negra prueba el sistema desde fuera, por sus entradas y salidas, y la caja blanca, desde su código.

**Tabla 45.** Técnicas de verificación aplicadas y sus resultados.

| Técnica | Cómo se diseñaron los casos | Qué se ejecutó | Resultado | Anexo |
| :--- | :--- | :--- | :--- | :---: |
| Caja negra | Partición de equivalencia, valores límite, tablas de decisión, transición de estados, casos de uso y medición de tiempos | 59 casos automatizados contra el API y el panel en marcha, y 10 casos manuales en la aplicación móvil | 59 de 59 conformes en la ejecución final; las dos anteriores dieron 55 y 59. Todas las operaciones principales responden con un percentil 95 por debajo de 300 ms | N.° 24 |
| Caja blanca: camino básico | Grafo de flujo, complejidad ciclomática V(G), un caso por camino independiente y prueba de bucles | 12 funciones del núcleo funcional en el API, el modelo, el panel y la aplicación; 77 casos | 100 % de líneas y ramas de las doce funciones | N.° 25 |
| Caja blanca: cobertura | Cobertura de sentencias y de ramas de cada componente | 282 pruebas automatizadas | API 92 %, microservicio 94 %; en la aplicación móvil 32,7 %, porque sus pantallas se verifican por caja negra | N.° 25 |

**Tabla 46.** Defectos hallados por la verificación formal.

| ID | Defecto | Técnica que lo halló | Corrección |
| :---: | :--- | :--- | :--- |
| D-01 | Tras iniciar sesión, la aplicación mostraba «sin conexión» en cada consulta hasta reabrirse | Caja negra, prueba manual | El cliente de red vive lo que vive la aplicación y no la pantalla de arranque |
| D-02 | La dosis aparecía repetida en la tarjeta de la toma y en la vista del familiar | Caja negra, prueba manual | La dosis se muestra una sola vez |
| D-03 | El API aceptaba nombres con dígitos; solo el panel lo impedía | Caja negra, partición de equivalencia | Validación también en el servidor |
| D-04 | El API aceptaba un tiempo de enfermedad mayor que la edad | Caja negra, tabla de decisión | Validación en el alta y en la edición |
| D-05 | Los rechazos del API llegaban en inglés | Caja negra, observación de usabilidad | Traducción central de los mensajes de validación |
| D-06 | La predicción fallaba con un lote vacío si el llamador no lo filtraba | Caja blanca, camino básico | La función se protege a sí misma |

Los seis defectos están corregidos y cada uno tiene su prueba de regresión. Ninguno afectaba al cálculo del riesgo ni a la seguridad de los datos.

**Ajustes de cierre aceptados por el Product Owner.** Durante la verificación, el médico pidió reforzar la veracidad del registro y completar la entrega a pacientes y familiares:

- **Ventana de registro de la toma (RF03).** «Ya la tomé» solo se acepta desde 60 minutos antes hasta 3 horas después de la hora programada, y el servidor rechaza una hora futura. Impide marcar de golpe, por la noche, todas las dosis del día (casos CN-22 a CN-27; CB-01).
- **Baja del paciente desde la ficha (RF02).** Con confirmación previa; el paciente deja el seguimiento y su historial se conserva como evidencia del estudio (CN-49).
- **Descarga de la aplicación y textos legales.** Página pública con el instalador y un código QR, política de privacidad conforme a la Ley N.° 29733 de Protección de Datos Personales y términos de uso; el familiar debe aceptarlos para crear su cuenta (CN-59, CN-M10).
- **Manual de usuario** dividido por perfil —médico, paciente y familiar, encargado del sistema— (Anexo n.° 23).

---

## 1.2. En base a los objetivos del proyecto

**Tabla 47.** Estado de los objetivos específicos.

| Objetivo | Resultado esperado | Estado | Evidencia |
| :---: | :--- | :---: | :--- |
| OE1 | Diagnóstico con línea base y factores de incumplimiento | **Parcial**: 2 de 3 indicadores; falta la línea base propia (Morisky-Green) | Tablas 19 y 20 |
| OE2 | Requisitos y arquitectura | **Parcial**: 1 de 2 indicadores; falta el juicio de expertos | Tablas 9, 17 y 24 |
| OE3 | Algoritmo seleccionado y reporte comparativo | **Ejecutado sobre datos reales**; meta de AUCROC no alcanzada con las variables disponibles | Tablas 26, 30, 31, 39 y 41 |
| OE4 | Sistema de soporte clínico funcional | **Cumplido** | Tablas 17, 29, 34, 37, 38 y 43 |
| OE5 | Validación de usabilidad | **Pendiente**: requiere usuarios reales | Anexo n.° 04; recorrido preparado (Tabla 43) |

### 1.2.1. OE1 – Caracterizar el proceso actual de seguimiento terapéutico y los factores de incumplimiento

**Estado: parcialmente cumplido (2 de 3 indicadores).** El diagnóstico del proceso y la clasificación de factores están completos; la línea base propia del consultorio depende de aplicar el test de Morisky-Green, y mientras tanto solo se dispone de las referencias externas.

| Indicador | Meta | Resultado |
| :--- | :--- | :--- |
| Pacientes con adherencia deficiente (línea base) | Medida en el diagnóstico | **Sin dato propio**: pendiente del test de Morisky-Green; referencia externa: 37,1 % nacional [11], 44,7 % en Lambayeque [12] |
| Factores clasificados según la OMS | 5 dimensiones | **5 dimensiones** cubiertas (Tabla 20) |
| Procesos de seguimiento no digitalizados | Medido en el diagnóstico | **100 %**: ninguno de los 4 subprocesos (registro de toma, seguimiento entre citas, alerta de riesgo y auditoría) tiene soporte digital |

### 1.2.2. OE2 – Determinar los requisitos funcionales y no funcionales del sistema

**Estado: parcialmente cumplido (1 de 2 indicadores).** Los requisitos están especificados al 100 %; la alineación de la arquitectura con estándares requiere la calificación de tres expertos, que aún no se ha obtenido.

| Indicador | Meta | Resultado |
| :--- | :--- | :--- |
| Requisitos especificados respecto a los identificados | 100 % | **100 %**: 10 RF y 6 RNF con criterio de aceptación y prioridad |
| Alineación con estándares de arquitectura (juicio de expertos, escala 1–5) | ≥ 4/5, con 3 expertos | **Sin dato**: expediente formalizado (Anexo n.° 19), calificación pendiente |

### 1.2.3. OE3 – Determinar el algoritmo de aprendizaje automático con mayor capacidad predictiva

**Estado: ejecutado sobre datos reales; meta de AUCROC no alcanzada con las variables disponibles.**

| Indicador (OVI) | Meta | Resultado a la fecha | Fuente |
| :--- | :--- | :--- | :--- |
| Algoritmos comparados | ≥ 4 | **4**: Regresión Logística, Random Forest, XGBoost y SVM | Tabla 41 |
| Pacientes reales en la comparación | ≥ 50 | **8 422** con diagnóstico médico de hipertensión o diabetes | Tabla 39 |
| AUCROC en validación cruzada (CEA-01) | ≥ 0,80 | **0,591** (Random Forest seleccionado) — **no cumple** | Tabla 41 |
| Sensibilidad de la clase incumplimiento (CEA-02) | ≥ 0,70 | 0,450 — **no cumple** | Tabla 41 |
| Contraste estadístico entre los dos mejores (CEA-03) | *p* e intervalo reportados | **Cumple**: DeLong, diferencia +0,002 (IC95 −0,009 a 0,013), *p* = 0,742 | 1.1.8.c |
| AUCROC del elegido en la prueba reservada | Reportada con su intervalo | 0,571 (IC95 0,532 a 0,610), mayor que el azar (*p* = 0,0002) | 1.1.8.c |
| Ausencia de fuga de información (CEA-04) | 0 transformaciones con prueba | **Cumple**: imputador, codificador, escalador y SMOTE ajustados dentro de cada pliegue | 1.1.5.b |
| Explicación individual verificable (CEA-05) | Error ≤ 0,001 | **Cumple**: 0,0000 en las cinco fichas verificadas | Tabla 30 |
| Latencia de la predicción (CEA-07) | ≤ 2 s | **Cumple**: ~90 ms tras el calentamiento | Tabla 37 |

**Modelos probados.** El protocolo de comparación se ejecutó dos veces con los mismos cuatro algoritmos, la misma validación cruzada y el mismo criterio de selección: sobre el conjunto de demostración, para verificar el protocolo y el sistema, y sobre la ENDES, con datos reales.

**Tabla 48.** Modelos probados y resultado de la selección.

| Conjunto de datos | Algoritmo e hiperparámetros elegidos | AUCROC (VC) | Sensibilidad (VC) | Decisión |
| :--- | :--- | :---: | :---: | :--- |
| Verificación: 400 fichas de demostración | Regresión Logística · `C=1` | 0,864 | 0,625 | Empata en AUCROC con SVM según DeLong (*p* = 0,349) |
| Verificación: 400 fichas de demostración | **SVM (RBF)** · `C=1`, `gamma=0,01` | 0,856 | **0,794** | **Seleccionado** por sensibilidad; AUCROC en prueba 0,809 |
| Verificación: 400 fichas de demostración | Random Forest · `n_estimators=500`, `max_depth=8` | 0,825 | 0,494 | Menor AUCROC |
| Verificación: 400 fichas de demostración | XGBoost · `learning_rate=0,05`, `max_depth=3` | 0,815 | 0,455 | Menor AUCROC |
| ENDES: 8 422 pacientes reales | **Random Forest** · `n_estimators=200`, `max_depth=8`, `min_samples_leaf=5` | **0,591** | 0,450 | **Seleccionado**: empata con XGBoost según DeLong (*p* = 0,742) y lo supera en sensibilidad; AUCROC en prueba 0,571 |
| ENDES: 8 422 pacientes reales | XGBoost · `learning_rate=0,05`, `max_depth=3`, `n_estimators=400` | 0,589 | 0,097 | Descartado por sensibilidad |
| ENDES: 8 422 pacientes reales | Regresión Logística · `C=0,1` | 0,588 | 0,590 | Menor AUCROC |
| ENDES: 8 422 pacientes reales | SVM (RBF) · `C=0,1`, `gamma=escala` | 0,586 | 0,622 | Menor AUCROC |

**Tabla 49.** Variables con que se entrena cada modelo.

| Dimensión OMS [6] | Ficha del consultorio y corrida de verificación (15 predictores) | Conjunto ENDES (8 predictores) |
| :--- | :--- | :--- |
| Paciente | Edad, sexo | Edad, sexo |
| Socioeconómica y social | Nivel educativo, convivencia, apoyo familiar | Nivel educativo, convivencia |
| Enfermedad | Diagnóstico, tiempo de enfermedad, comorbilidades | Diagnóstico, tiempo de enfermedad, comorbilidades |
| Terapia | Número de fármacos, tomas por día | No registrada por la encuesta |
| Sistema de salud | Controles programados y perdidos | No registrada por la encuesta |
| Derivadas | Carga terapéutica, tasa de inasistencia, cronicidad relativa | Cronicidad relativa |
| **Etiqueta** | Test de Morisky-Green | Preguntas QS106 y QS113 de la encuesta |

**Tabla 50.** Variables que miden el modelo y su papel en la selección.

| Métrica | Qué mide | Papel en la selección | Por qué se usa así |
| :--- | :--- | :--- | :--- |
| AUCROC en validación cruzada estratificada de 5 pliegues | Cómo ordena el modelo a los pacientes por riesgo, sin depender de un umbral | **Criterio principal** (CEA-01) | No cambia con el umbral ni premia predecir siempre la clase mayoritaria [16] |
| Prueba de DeLong | Si la diferencia de AUCROC entre los dos mejores es real o fruto del azar | **Decide** si hay un ganador | Es la prueba que corresponde a dos AUCROC medidas sobre los mismos pacientes [8] |
| Sensibilidad | Proporción de incumplidores que el modelo detecta | **Desempate** cuando las AUCROC no difieren (CEA-02) | No detectar a un paciente que abandona es el error más costoso para una alerta temprana (RF05) |
| Especificidad, exactitud y F1-score | Falsas alarmas, aciertos globales y equilibrio entre precisión y sensibilidad | Se reportan; **no deciden** | Con clases desbalanceadas la exactitud engaña: XGBoost alcanza 0,825 detectando a uno de cada diez incumplidores |
| McNemar con umbral de 0,5 | Si los dos mejores alertarían sobre los mismos pacientes | Complementaria; **no decide** | Compara decisiones con un umbral, no la capacidad de ordenar |
| AUCROC en la prueba reservada, con IC95 y contraste frente al azar | Desempeño sobre pacientes que el modelo nunca vio | Evaluación final; **no interviene** en la elección | Evita elegir el modelo con los mismos datos con que se evalúa [4] |

**Por qué estas variables son suficientes para elegir el modelo.** La selección compara a los cuatro algoritmos en igualdad de condiciones: todos reciben las mismas variables, los mismos pliegues y la misma preparación —ajustada solo con datos de entrenamiento, para que no haya fuga de información [4]—, y la elección se toma sobre predicciones fuera de pliegue, sin tocar el conjunto de prueba. Las métricas responden a las dos preguntas que importan a una alerta temprana: si el modelo ordena bien a los pacientes por riesgo (AUCROC) y si detecta a quienes van a incumplir (sensibilidad), y la prueba de DeLong impide declarar un ganador por una diferencia que el azar explica. Las variables de entrenamiento cubren las cinco dimensiones del modelo de adherencia de la OMS [6] y coinciden con los predictores que la literatura reciente utiliza para el incumplimiento antihipertensivo [3], en enfermedades no transmisibles [14] y en población peruana [11]; ninguna depende de la etiqueta.

Conviene precisar el alcance de esta suficiencia. Las variables bastan para **elegir el mejor modelo entre los cuatro** con un criterio justo y reproducible; no garantizan que el modelo elegido **alcance la meta**. La ENDES lo muestra: sin las variables de terapia y de sistema de salud, ningún algoritmo supera un AUCROC de 0,60. Si la ficha completa del consultorio basta para alcanzar 0,80 es precisamente lo que contrastará el diseño anidado del apartado 1.1.8.e.

**Lectura del incumplimiento de la meta.** La comparación se ejecutó íntegra sobre datos reales y produjo un resultado negativo que se reporta como tal: ningún algoritmo alcanza AUCROC ≥ 0,80 con las variables que la ENDES registra. Lo que el resultado demuestra y lo que no se delimita en la Tabla 42: la convergencia de los cuatro modelos indica que la elección del algoritmo no es el factor limitante, pero el bajo desempeño admite tres explicaciones —variables insuficientes, ruido en la etiqueta y diferencia de población— que este análisis no separa. La extracción del Anexo n.° 03 permite contrastar la primera con un diseño ya fijado: comparar, sobre los mismos pacientes del consultorio, un modelo restringido a las variables de la encuesta frente a uno con la ficha completa. El protocolo, el código y el criterio de selección quedan verificados y se reejecutan con un comando sobre el conjunto real.

El protocolo está además en servicio a través del microservicio de inferencia, que explica cada predicción con SHAP y declara en cada respuesta la procedencia de los datos con los que se entrenó el modelo (CEA-08).

### 1.2.4. OE4 – Construir el sistema de soporte clínico

**Estado: cumplido.**

| Indicador | Meta | Resultado |
| :--- | :--- | :--- |
| Historias de usuario cumplidas | 100 % por sprint | Sprint 1: 100 %; Sprint 2: 92 %; Sprint 3: 95 %; Sprint 4: 100 % de lo que no depende del trabajo de campo |
| Módulos construidos frente a requeridos | Todos | **10 de 10** RF operativos (RF01–RF10) |
| Densidad de errores por sprint | Decreciente | 22 incidencias registradas y cerradas (Tabla 44); 282 pruebas en verde y 6 defectos de la verificación formal, todos corregidos (apartado 1.1.11) |
| Atributos ISO/IEC 25010 | Funcionalidad, eficiencia y usabilidad | **8 de 9 características verificadas** (Tabla 38); la capacidad de interacción queda pendiente de la escala SUS |

**Escenario de extremo a extremo operativo:** el médico registra al paciente y le genera su acceso; el paciente recibe recordatorios y registra sus tomas desde el celular, incluso sin conexión; un familiar las corrobora; y el médico recibe una alerta cuando ese paciente empieza a fallar, consulta en la ficha la adherencia y el riesgo predicho con su explicación SHAP, y ve en reportes la situación de todos sus pacientes.

La tabla siguiente verifica requisito por requisito cómo quedó realizado y con qué evidencia, de modo que el cumplimiento pueda comprobarse de forma individual y no solo en conjunto.

**Tabla 51.** Verificación del cumplimiento de los requisitos funcionales.

| Requisito | Realización implementada | Evidencia | Estado |
| :--- | :--- | :--- | :---: |
| RF01 Autenticación y autorización por perfiles | Sesión con testigo firmado y control de acceso por rol; el médico solo accede a sus pacientes, el familiar solo a la corroboración | Pruebas de seguridad (Tabla 33); CN-01 a CN-06 y CN-43 a CN-47; CB-04 | Implementado |
| RF02 Registro y gestión del paciente polimedicado | Ficha con las variables del Anexo n.° 03, comorbilidades por casillas, validación de polimedicación y coherencia de controles, y baja con confirmación que conserva el historial | Tabla 27; Tabla 43, paso 2; CN-07 a CN-21 y CN-49 | Implementado |
| RF03 Registro de la toma desde la aplicación | Pantalla del día con registro de cumplida u omitida y motivo; ventana de registro de 60 minutos antes a 3 horas después de la hora programada; cola local que sincroniza sin duplicar al recuperar la conexión | 62 pruebas móviles; Tabla 43, paso 4; CN-22 a CN-29; CB-01, CB-08 a CB-11 | Implementado |
| RF04 Cálculo y presentación del riesgo | Microservicio de inferencia independiente que devuelve probabilidad, nivel y procedencia del modelo | 25 pruebas del microservicio; Tabla 37; CN-30 a CN-32; CB-05 y CB-06 | Implementado |
| RF05 Alertas tempranas al médico | Tres reglas —omisiones seguidas, caída del cumplimiento y riesgo predicho alto— con ventanas de silencio y reapertura ante evidencia que empeora | 17 pruebas de alertas (Tabla 32); CN-33 y CN-34; CB-03 | Implementado |
| RF06 Explicación de la predicción | Contribución de cada variable en puntos porcentuales, con verificación de la propiedad aditiva de SHAP | Tabla 30 | Implementado |
| RF07 Panel clínico con reportes exportables | Panel de auditoría priorizado por riesgo y reportes generales con exportación a CSV | Tabla 43, paso 11; CN-35 y CN-36 | Implementado |
| RF08 Recordatorios de toma | Avisos locales programados en el teléfono según el horario prescrito | Pruebas de notificaciones | Implementado |
| RF09 Corroboración por grupo familiar | Invitación de un solo uso, confirmación de la toma y columna de testigo en el historial | Tabla 43, paso 6; CN-37 a CN-40 | Implementado |
| RF10 Restablecimiento de contraseña | Enlace de un solo uso con vencimiento a los 30 minutos enviado por correo | Pruebas de recuperación; CN-41 y CN-42 | Implementado |

### 1.2.5. OE5 – Evaluar la usabilidad del sistema mediante la escala SUS

**Estado: pendiente de aplicación con usuarios.** El sistema ya está completo y el recorrido que se evaluará es el de la Tabla 43.

| Indicador | Meta | Estado |
| :--- | :--- | :--- |
| Usabilidad con la escala SUS [9] | ≥ 80 puntos | Pendiente |
| Tasa de éxito en tareas | Medida con usuarios | Pendiente |
| Tiempo promedio de aprendizaje | Medido con usuarios | Pendiente |

El instrumento SUS (Anexo n.° 04) y la ficha de observación (Anexo n.° 05) están preparados, y el guion de la sesión —qué hace el usuario, en qué orden y qué se observa— es el del apartado 1.1.9. Participarán el médico, sobre el panel web, y una muestra de pacientes polimedicados, sobre la aplicación móvil. **Es el único resultado del proyecto que no depende del desarrollo, sino de la disponibilidad de los participantes.**

---

## 1.3. Limitaciones del estudio y trabajo futuro

Declarar los límites del trabajo forma parte del resultado: sin ellos, cualquier lectura del sistema sería más optimista de lo que la evidencia permite.

**Tabla 52.** Limitaciones reconocidas y su alcance.

| Limitación | Por qué existe | Qué implica para la interpretación |
| :--- | :--- | :--- |
| El modelo desplegado se entrenó con un conjunto de demostración | La extracción documental del Anexo n.° 03 no ha concluido | Las métricas publicadas verifican el protocolo y el sistema, **no** la capacidad predictiva sobre pacientes reales. El sistema lo declara en pantalla y en la ficha del modelo |
| Un solo consultorio y una muestra prevista de unos 50 pacientes | Es el universo del estudio y el alcance de una tesis de pregrado | Los resultados no son extrapolables a otras poblaciones; describen a los pacientes polimedicados de este consultorio |
| La adherencia observada procede del autorreporte del paciente | Los métodos menos expuestos a ese sesgo —la monitorización del fármaco en sangre o los dispositivos que registran la apertura del envase— quedan fuera del alcance del estudio [17] | La corroboración familiar (RF09) añade un segundo testigo, pero no convierte el dato en una medida objetiva |
| Variables limitadas a las del instrumento | El Anexo n.° 03 se fijó a partir de lo que la historia clínica registra de forma sistemática | Factores como la creencia sobre la enfermedad o el costo del tratamiento no están representados, ni las mediciones fisiológicas —presión arterial, glucemia— (Tabla 13) |
| La explicación SHAP se calcula frente a un paciente de referencia | El modelo seleccionado no tiene coeficientes interpretables | Las contribuciones indican asociación dentro del modelo, no causalidad clínica |
| Infraestructura en planes gratuitos | El proyecto no dispone de servidores propios | Los servicios se suspenden sin tráfico; la latencia de arranque no es del sistema y debe descontarse al medir |
| Usabilidad sin medir al cierre del desarrollo | La escala SUS requiere usuarios reales | El RNF03 queda verificado por diseño, no por evidencia empírica, hasta aplicar el instrumento |
| El conjunto externo ENDES no sustituye a la población del estudio | Es una encuesta nacional y no registra cinco de las variables del instrumento (1.1.8.b) | Su resultado valida el protocolo de comparación sobre datos reales y fija una línea base nacional; el modelo que describe es el de la población encuestada, no el del consultorio |
| La etiqueta de la ENDES es una sola pregunta de autorreporte | La encuesta no aplica el test de Morisky completo | La prevalencia obtenida (13,7 %) es comparable con la literatura peruana [11], pero la etiqueta es menos fina que la del instrumento del estudio |

**Trabajo futuro.** Más allá del alcance de esta tesis quedan: la atribución de causalidad mediante un diseño experimental —el sistema predice, no demuestra que la intervención mejore la adherencia—; el reentrenamiento periódico del modelo con los datos que el propio sistema genera; la integración con la historia clínica institucional; la incorporación de mediciones fisiológicas —presión arterial y glucemia— desde dispositivos conectados, que el paciente no pueda alterar; y la extensión del acompañamiento a mensajería con el paciente.

---

## 1.4. Cierre del desarrollo y trabajo de campo pendiente

El desarrollo está cerrado. Lo que resta son tres mediciones con personas, cada una con su instrumento formalizado y su cálculo automatizado, de modo que obtener el resultado no requiere programar nada más.

**Tabla 53.** Qué falta, qué lo produce y qué resultado cierra.

| Pendiente | Instrumento | Cómo se obtiene el resultado | Objetivo que cierra |
| :--- | :--- | :--- | :---: |
| Extracción de historias clínicas | Anexo n.° 03 y su plantilla CSV | `python src/preprocess.py --entrada <csv>` valida el esquema y reporta faltantes | OE1, OE3 |
| Test de Morisky-Green | Anexo n.° 04 (parte A) | Aporta la etiqueta de cada paciente y la línea base del consultorio | OE1 |
| Comparación de algoritmos sobre las historias del consultorio | `train_evaluate.py` | Un comando produce la tabla comparativa, el contraste de DeLong y el modelo listo para desplegar. Sobre la ENDES ya está ejecutada (1.1.8); sobre el consultorio cierra CEA-01 y CEA-06 | OE3 |
| Evaluación de usabilidad | Anexo n.° 04 (parte B) y ficha de observación | `python documentacion/herramientas/calcular_sus.py <respuestas.csv>` devuelve el puntaje por participante y el promedio frente a la meta de 80 | OE5 |
| Juicio de expertos | Anexo n.° 19 | Tres evaluadores completan el expediente | OE2 |

El recorrido que se somete a la evaluación de usabilidad es el del apartado 1.1.9, y el manual de usuario del Anexo n.° 23 se entrega a los participantes antes de la sesión.

**Estado de los criterios de éxito al cierre del desarrollo.** De los trece criterios declarados en 1.1.2.i, nueve se cumplen y están verificados: CEN-01, CEN-02, CEN-03 y CEN-05 por el escenario operativo (1.1.9), y CEA-03, CEA-04, CEA-05, CEA-07 y CEA-08 por el protocolo y las pruebas. **Cuatro no se cumplen a la fecha y se declaran como tales**: CEA-01 y CEA-02, porque la comparación sobre la ENDES alcanza AUCROC 0,591 y sensibilidad 0,450 con las variables que esa fuente registra (1.1.8.d); CEA-06, porque el conjunto del consultorio aún no reúne las 50 fichas del universo previsto; y CEN-04, porque la escala SUS requiere usuarios. Los cuatro dependen del mismo trabajo de campo y ninguno exige modificar el software.

---

# REFERENCIAS BIBLIOGRÁFICAS

[1] M. Pastrana, H. Ordoñez, C. A. Cobos-Lozada y M. Muñoz, «Best Practices Evidenced for Software Development Based on DevOps and Scrum: A Literature Review», *Appl. Sci.*, vol. 15, n.º 10, art. 5421, may. 2025, doi: 10.3390/app15105421.

[2] A. M. Shimaoka, R. C. Ferreira y A. Goldman, «The evolution of CRISP-DM for Data Science: Methods, Processes and Frameworks», *SBC Rev. Comput. Sci.*, vol. 4, n.º 1, pp. 28-43, oct. 2024, doi: 10.5753/reviews.2024.3757.

[3] C. D. Marineci, A. Valeanu, C. Chiriță, S. Negreș, C. Stoicescu y V. Chioncel, «Desarrollo y validación de modelos predictivos del incumplimiento terapéutico con la medicación antihipertensiva», *Medicina (Mex.)*, vol. 61, n.º 7, p. 1313, jul. 2025, doi: 10.3390/medicina61071313.

[4] S. Kapoor y A. Narayanan, «Leakage and the reproducibility crisis in machine-learning-based science», *Patterns*, vol. 4, n.º 9, art. 100804, sep. 2023, doi: 10.1016/j.patter.2023.100804.

[5] A. V. Ponce-Bobadilla, V. Schmitt, C. S. Maier, S. Mensing y S. Stodtmann, «Practical guide to SHAP analysis: Explaining supervised machine learning model predictions in drug development», *Clin. Transl. Sci.*, vol. 17, n.º 11, art. e70056, nov. 2024, doi: 10.1111/cts.70056.

[6] P. D. Ferreira, J. A. Simões y D. C. Velho, «Adherence to Antihypertensive Therapy and Its Determinants: A Systematic Review», *Cureus*, vol. 16, n.º 5, art. e59532, may. 2024, doi: 10.7759/cureus.59532.

[7] D. Elreedy, A. F. Atiya y F. Kamalov, «A theoretical distribution analysis of synthetic minority oversampling technique (SMOTE) for imbalanced learning», *Mach. Learn.*, vol. 113, n.º 7, pp. 4903-4923, jul. 2024, doi: 10.1007/s10994-022-06296-4.

[8] H. Zhu, S. Liu, W. Xu, J. Dai y M. Benbouzid, «Linearithmic and unbiased implementation of DeLong's algorithm for comparing the areas under correlated ROC curves», *Expert Syst. Appl.*, vol. 246, art. 123194, jul. 2024, doi: 10.1016/j.eswa.2024.123194.

[9] P. C. Lim, Y. L. Lim, R. Rajah y H. Zainal, «Usability questionnaire for standalone or interactive mobile health applications: a systematic review», *BMC Digit. Health*, vol. 3, n.º 1, art. 11, abr. 2025, doi: 10.1186/s44247-025-00150-y.

[10] V. A. Soto-Cáceres, R. A. Picón-Reátegui y E. R. Sencie-Delgado, «Asociación entre nivel socioeconómico y adherencia farmacológica en adultos mayores con hipertensión arterial, Centro de Salud Pimentel - Chiclayo, Perú, 2024», *Rev. Exp. En Med. Hosp. Reg. Lambayeque*, vol. 11, n.º 3, oct. 2025, doi: 10.37065/rem.v11i3.835.

[11] P. M. Calderon-Ramirez, E. Huamani-Merma, M. G. Mirano-Ortiz-de-Orue, D. Fernandez-Guzman y C. J. Toro-Huamanchumo, «Factores asociados a la falta de adherencia al tratamiento farmacológico en pacientes con diabetes e hipertensión en Perú: resultados de un análisis combinado de seis años de encuestas poblacionales», *Public Health*, vol. 231, pp. 108-115, jun. 2024, doi: 10.1016/j.puhe.2024.03.012.

[12] C. M. Carrasco Bermeo y C. B. Cerna Chacón, «Polifarmacia y adherencia terapéutica en pacientes con enfermedades crónicas en un centro de salud de Lambayeque - 2024», Tesis de grado, Universidad Señor de Sipán, Pimentel, Perú, 2024. [En línea]. Disponible en: https://hdl.handle.net/20.500.12802/12280. [Accedido: 31 oct. 2026].

[13] *Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — Product quality model*, ISO/IEC 25010:2023, 2.ª ed., Ginebra, Suiza: International Organization for Standardization, nov. 2023. [En línea]. Disponible en: https://www.iso.org/standard/78176.html. [Accedido: 31 oct. 2026].

[14] W. Kanyongo, A. E. Ezugwu, T. Moyo y J. V. Fonou Dombeu, «Clasificación basada en el aprendizaje automático del cumplimiento terapéutico en pacientes con enfermedades no transmisibles», *Inform. Med. Unlocked*, vol. 52, p. 101611, 2025, doi: 10.1016/j.imu.2024.101611.

[15] Instituto Nacional de Estadística e Informática, «Encuesta Demográfica y de Salud Familiar (ENDES): microdatos, módulos de salud y de hogar, 2014-2017» [Conjunto de datos]. Lima, Perú: INEI. [En línea]. Disponible en: https://proyectos.inei.gob.pe/microdatos/. [Accedido: 29 sep. 2026].

[16] A. de la Cruz Huayanay, J. L. Bazán y C. M. Russo, «Performance of evaluation metrics for classification in imbalanced data», *Comput. Stat.*, vol. 40, pp. 1447-1473, 2025, doi: 10.1007/s00180-024-01539-5.

[17] P. Schnorrerova, P. Matalova y M. Wawruch, «Medication adherence: measurement methods and approaches», *Bratisl. Med. J.*, vol. 125, n.º 4, pp. 264-273, 2024, doi: 10.4149/BLL_2024_40.

---

# ANEXOS

| Anexo | Título |
| :---: | :--- |
| N.° 01 | Carta de aceptación para ejecutar la tesis |
| N.° 02 | Guía de entrevista semiestructurada al personal médico |
| N.° 03 | Ficha de recolección de datos clínicos |
| N.° 04 | Test de Morisky-Green y escala SUS |
| N.° 05 | Ficha de observación de pruebas con usuarios |
| N.° 06 | Repositorio de código del producto |
| N.° 07 | Product Backlog e historias de usuario |
| N.° 08 | Matriz de trazabilidad |
| N.° 09 | Actas de Sprint Review y retrospectiva (Sprints 1 a 4) |
| N.° 10 | Plantilla de captura de la ficha de extracción |
| N.° 11 | Guía de despliegue del sistema |
| N.° 12 | Plantilla y cálculo de la escala SUS |
| N.° 13 | Capturas del panel médico: auditoría, ficha, riesgo y explicación |
| N.° 14 | Capturas de las alertas tempranas y su cierre |
| N.° 15 | Capturas del control de acceso y de las validaciones |
| N.° 16 | Capturas de la aplicación móvil |
| N.° 17 | Capturas de los reportes generales |
| N.° 18 | Evidencia de desarrollo: servicios desplegados |
| N.° 19 | Expediente de juicio de expertos |
| N.° 20 | Descripción de actividades, técnicas y herramientas de desarrollo |
| N.° 21 | Productos, artefactos y entregables del desarrollo |
| N.° 22 | Evidencia del modelo: comparación de algoritmos y ficha de procedencia |
| N.° 23 | Manual de usuario del sistema |
| N.° 24 | Pruebas de caja negra |
| N.° 25 | Pruebas de caja blanca |
| N.° 26 | Matriz de consistencia del proyecto |
