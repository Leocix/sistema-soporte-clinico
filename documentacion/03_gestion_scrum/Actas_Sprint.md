# Actas de Sprint Review y Retrospectiva

**Proyecto:** Sistema de soporte clínico con aprendizaje automático para prevenir
el incumplimiento terapéutico en pacientes hipertensos y diabéticos polimedicados.
**Consultorio médico Milko Ugaz Zegarra — Chiclayo.**

---

# Sprint 1 — Planificación y primer incremento

**Semanas 2–3 · CRISP-DM: *Business Understanding* y *Data Understanding*
· Hito 30 %**

## Objetivo del sprint

Establecer el entendimiento compartido del problema clínico, construir la línea
base de adherencia, priorizar la pila de producto y entregar el primer
incremento funcional verificable.

## Sprint Review

**Incrementos presentados**

| Entregable | Resultado |
| :--- | :--- |
| Diagnóstico del consultorio (entrevista, Anexo n.° 03) | Aceptado |
| Clasificación de factores según el modelo OMS | Aceptado |
| Product Backlog priorizado con MoSCoW | Aceptado |
| Historias de usuario HU01–HU03 con criterios de aceptación | Aceptado |
| Modelo de datos clínico inicial | Aceptado |
| Módulo de autenticación (RF01) | Aceptado |
| Repositorio y entorno configurados | Aceptado |

**Observaciones del Product Owner**

El médico confirmó que la prioridad clínica es disponer de la alerta de riesgo
**antes** de la cita, no durante. Esa observación consolidó RF04 y RF05 como
*Must* y fijó el sentido del panel: ordenar a los pacientes por prioridad
clínica, no alfabéticamente.

## Retrospectiva

| Qué funcionó | Qué no funcionó | Acción correctiva |
| :--- | :--- | :--- |
| Derivar cada requisito de una brecha del diagnóstico dio una justificación explícita a toda la pila | Las validaciones clínicas quedaron repartidas entre el código y la base de datos, con riesgo de divergencia | Trasladarlas a restricciones declarativas de la base de datos (ejecutado en el Sprint 2) |
| El instrumento del Anexo n.° 04 se estructuró desde el inicio según las dimensiones OMS | — | — |

---

# Sprint 2 — Núcleo funcional y modelado inicial

**Semanas 3–4 · CRISP-DM: *Data Preparation* y *Modeling* inicial
· Hitos 40 % y 50 %**

## Objetivo del sprint

Especificar los requisitos y la arquitectura restantes, completar el núcleo
funcional RF01–RF03, dejar el dataset depurado y balanceado, y montar la
comparación de los cuatro algoritmos candidatos.

## Sprint Review

**Incrementos presentados**

| Entregable | Resultado | Evidencia |
| :--- | :--- | :--- |
| Especificación de 8 RF y 6 RNF | Aceptado | Tablas 4 y 6 del pre informe |
| API Gateway con CORS, seguridad y manejo global de errores | Aceptado | Servicio desplegado, `200` en `/health` |
| Gestión de pacientes polimedicados (RF02) | Aceptado | 8 pruebas |
| Registro de adherencia con sincronización idempotente (RF03) | Aceptado | 12 pruebas |
| Panel médico de auditoría | Aceptado | Desplegado en Vercel |
| Aplicación del paciente | Aceptado | 14 pruebas, análisis estático limpio |
| Pipeline de preparación de datos | Aceptado | Ejecutado de extremo a extremo |
| Comparación de cuatro algoritmos | Aceptado con reserva | Flujo verificado; falta el dataset real |
| Escenario ejecutable de inicio a fin | Aceptado | Alta → registro de toma → cálculo de adherencia |

**Reserva registrada.** El reporte comparativo de algoritmos queda pendiente de
la extracción documental del Anexo n.° 04. El instrumento y el script están
listos; lo que falta es trabajo de campo, no de desarrollo. Se acuerda que la
captura de las historias clínicas es la tarea de mayor prioridad de la semana 5.

**Observaciones del Product Owner**

El médico señaló que el panel debe distinguir con claridad entre la adherencia
que el paciente declara en consulta y la que el sistema observa a partir de los
registros. Se incorporó esa distinción: la ficha muestra ambas por separado y la
clasificación de riesgo se rotula explícitamente como observada, no predicha.

## Retrospectiva

| Qué funcionó | Qué no funcionó | Acción correctiva |
| :--- | :--- | :--- |
| Escribir las reglas clínicas como restricciones de la base de datos: los defectos aparecen al insertar, no al analizar | El tipo enumerado de SQLAlchemy guardaba el nombre del miembro (`MASCULINO`) y no su valor (`M`), lo que habría roto la exportación al pipeline | Persistir el valor con `values_callable`; la base ahora guarda los códigos del Anexo n.° 04 |
| Las pruebas automatizadas detectaron tres defectos que no se habrían visto por inspección | El escalado tipográfico global tumbaba la aplicación móvil al arrancar | Fijar el tamaño de forma explícita en cada texto |
| Verificar en el navegador y no solo con pruebas unitarias reveló un desbordamiento de maquetación | El cliente móvil capturaba un tipo de excepción de red que nunca llega | Capturar `ClientException`, que es el tipo que `package:http` propaga |
| — | El pipeline de datos se detenía con los nulos de las columnas de texto de pandas | Normalizar las categóricas antes de imputar |

**Defectos del sprint:** 4 detectados, 4 corregidos, 0 abiertos.

## Compromisos para el Sprint 3

1. Completar la extracción documental del Anexo n.° 04 (~50 historias clínicas).
2. Ejecutar la comparación de algoritmos y seleccionar el modelo.
3. Desarrollar el microservicio de inferencia y la explicabilidad SHAP.
4. Implementar las alertas tempranas y la exportación de reportes.

---

# Sprint 3 — Modelo integrado, alertas y estabilización

**Semanas 5–6 · CRISP-DM: *Modeling* (selección) y *Evaluation*
· Hitos 65 % y 80 %**

## Objetivo del sprint

Llevar el modelo del cuaderno de análisis al sistema en producción, explicar
cada predicción al médico, completar la aplicación del paciente con el
acompañamiento familiar y avisar al médico antes de que el paciente se
descompense.

## Sprint Review

**Incrementos presentados**

| Entregable | Resultado |
| :--- | :--- |
| Microservicio de inferencia independiente (RF04) | Aceptado |
| Explicación individual de cada predicción con SHAP (RF06) | Aceptado |
| Grupo familiar de acompañamiento y corroboración (RF09) | Aceptado |
| Recordatorios de toma en el dispositivo (RF08) | Aceptado |
| Restablecimiento de contraseña por correo (RF10) | Aceptado |
| Acceso móvil del paciente generado desde el panel | Aceptado |
| Alertas tempranas al médico (RF05) | Aceptado |
| Reportes generales con exportación (RF07) | Aceptado |
| Verificación de seguridad del API (RNF01) | Aceptado |
| Comparación de algoritmos sobre historias clínicas reales | **No entregado**: depende de la extracción documental |

**Observaciones del Product Owner**

Al revisar la ficha, el médico señaló que el nivel socioeconómico, el tipo de
seguro y la zona de residencia no distinguen a sus pacientes, porque en una
clínica privada apenas varían. Se refinaron las variables: nivel educativo,
convivencia y apoyo familiar en la medicación, que sí varían y se relacionan
con las causas que él mismo identificó —el olvido y la falta de comprensión—.
Las comorbilidades pasaron de un número a una lista de enfermedades concretas.

Sobre la bandeja de alertas, pidió expresamente que un mismo paciente no
generara avisos repetidos: «si me llega veinte veces lo mismo, dejo de
mirarla». De ahí el cierre automático y el plazo de silencio tras atender.

## Retrospectiva

| Qué funcionó | Qué no funcionó | Acción correctiva |
| :--- | :--- | :--- |
| Separar el modelo en un microservicio permitió reentrenarlo y medirlo sin tocar la parte clínica | La predicción no funcionaba en el servicio publicado: faltaba una librería y la versión de otra no era la del entrenamiento (I-14) | Fijar las versiones exactas y añadir pruebas que cargan el artefacto realmente desplegado |
| Probar sobre el teléfono y el servicio publicado, y no solo en local | Tres defectos (I-14, I-15, I-22) solo se manifestaban en el entorno publicado | Incorporar al procedimiento la verificación sobre el artefacto que se entrega |
| Escribir primero la regla de alerta y después su prueba evitó una bandeja inservible | El protocolo declaraba un desempate por sensibilidad que el código no aplicaba (I-18) | Contrastar con McNemar antes de seleccionar, y probarlo |

**Defectos del sprint:** 15 detectados, 15 corregidos, 0 abiertos.

## Compromisos para el Sprint 4

1. Medir el rendimiento con usuarios simultáneos (RNF02, RNF06).
2. Verificar los atributos de calidad ISO/IEC 25010.
3. Preparar la demostración del producto y el despertar de los servicios.
4. Aplicar la escala SUS con el médico y una muestra de pacientes (OE5).
5. Ejecutar la comparación de algoritmos cuando concluya la extracción.

---

# Sprint 4 — Cierre, rendimiento y validación

**Semanas 7–8 · CRISP-DM: *Deployment* y monitoreo · Hitos 90 % y 100 %**

## Objetivo del sprint

Verificar el producto contra sus requisitos no funcionales, dejarlo listo para
demostrarse sin sobresaltos y consolidar las evidencias de la investigación.

## Sprint Review

**Incrementos presentados**

| Entregable | Resultado |
| :--- | :--- |
| Prueba de rendimiento y carga con usuarios simultáneos (RNF02, RNF06) | Aceptado |
| Verificación de los atributos ISO/IEC 25010 | Aceptado: 7 de 8; la usabilidad depende de la escala SUS |
| Guion de demostración del producto y despertador de servicios | Aceptado |
| Arranque tolerante a cortes de la base de datos | Aceptado |
| Consolidación del repositorio, backlog, trazabilidad y actas | Aceptado |
| Evaluación de usabilidad con la escala SUS (OE5) | **Pendiente**: requiere la participación del médico y de los pacientes |
| Comparación de algoritmos sobre historias clínicas reales (OE3) | **Pendiente**: depende de la extracción documental |

**Observaciones del Product Owner**

La medición de rendimiento se revisó con el médico en términos de su consulta:
la ficha y el listado responden por debajo de un décimo de segundo, y la
predicción con explicación, en menos de un segundo. Su comentario fue que el
tiempo que percibe no es el del sistema sino el del servicio gratuito cuando
lleva horas sin usarse; de ahí que el guion de demostración empiece por
despertarlo.

## Retrospectiva

| Qué funcionó | Qué no funcionó | Acción correctiva |
| :--- | :--- | :--- |
| Medir antes de optimizar: la prueba de carga señaló dos costes que nadie habría adivinado leyendo el código | El cliente hacia el microservicio abría una conexión por consulta | Reutilizar la conexión |
| Descontar de la medición lo que no es tiempo del sistema —conexión y arranque en frío— evitó conclusiones falsas | Las vistas que recorren a todos los pacientes pedían la predicción de cada uno en cada apertura | Guardar la predicción sesenta segundos, con invalidación al editar la ficha |
| La evaluación externa del 50 % sirvió como retrospectiva real del producto | La demostración anterior se hizo sobre servicios suspendidos, y el componente de IA no llegó a mostrarse | Guion de demostración con despertar previo y recorrido paso a paso |

**Defectos del sprint:** 1 detectado (I-22), 1 corregido, 0 abiertos.

## Cierre del proyecto de desarrollo

El producto cubre los diez requisitos funcionales y los seis no funcionales
comprometidos. Lo que queda abierto no pertenece al desarrollo, sino al trabajo
de campo: la extracción documental del Anexo n.° 04, el test de Morisky-Green
que da la etiqueta y la evaluación de usabilidad con usuarios reales. Los tres
tienen su instrumento formalizado y su procedimiento automatizado, de modo que
al disponer de los datos el resultado se obtiene ejecutando el pipeline y la
hoja de cálculo del SUS.
