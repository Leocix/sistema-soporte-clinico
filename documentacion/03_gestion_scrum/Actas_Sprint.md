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
