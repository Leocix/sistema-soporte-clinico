# Descripción de actividades, técnicas y herramientas de desarrollo

La tabla siguiente indica en qué apartados del pre informe se desarrollan las actividades, las técnicas y las herramientas empleadas para construir el producto acreditable. Las tablas posteriores las detallan.

| Ítem | ¿Qué se espera? | Dónde se desarrolla en el pre informe |
| :--- | :--- | :--- |
| Actividades | La descripción de las actividades de desarrollo es exhaustiva, delimitada, justificada y evidencia dominio técnico del proceso | Marco SCRUM y núcleo funcional (1.1.1); Sprints 1 a 4 con su Sprint Backlog, incremento, pruebas, incidencias, Review y retrospectiva (1.1.4 a 1.1.7); PBI-11, comparación sobre datos reales (1.1.8); PBI-12, verificación formal (1.1.11); resultados por objetivo (1.2) |
| Técnicas | Las técnicas de desarrollo descritas son totalmente coherentes con el producto acreditable | Priorización MoSCoW, historias de usuario y Definición de Terminado (1.1.1 y 1.1.3); preparación de datos, SMOTE dentro de los pliegues y validación cruzada (1.1.2.g y 1.1.5.b); contraste de DeLong y análisis de errores (1.1.8); explicación SHAP (1.1.6.b); reglas de alerta (1.1.6.f); pruebas de caja negra y caja blanca (1.1.11) |
| Herramientas de desarrollo | Se explica detalladamente cómo las herramientas apoyan el desarrollo del producto acreditable | Justificación de cada tecnología frente a su alternativa (1.1.2.d); arquitectura (1.1.2.c); microservicio de inferencia (1.1.6.a); prueba de carga (1.1.7.a); herramientas de verificación (Anexos n.° 24 y 25) |

## Actividades por sprint

| Sprint | Fase CRISP-DM | Actividades principales | Resultado | Apartado |
| :--- | :--- | :--- | :--- | :--- |
| Sprint 1 | Business y Data Understanding | Entrevista al médico; clasificación de factores por dimensión OMS; Product Backlog priorizado; modelo de datos; autenticación por perfil | Diagnóstico, brechas B1 a B4 y RF01 | 1.1.4 |
| Sprint 2 | Data Preparation y Modeling inicial | Requisitos no funcionales y arquitectura; ficha clínica con reglas en la base; registro de tomas sin duplicados; pipeline de preparación; configuración de la comparación; despliegue | RF02, RF03 y pipeline | 1.1.5 |
| Sprint 3 | Modeling y Evaluation | Microservicio de inferencia; SHAP; alertas tempranas; reportes; app del paciente y del familiar; recuperación de acceso; corrida de verificación del protocolo; batería de seguridad | Núcleo funcional completo (RF04 a RF10) | 1.1.6 |
| Sprint 4 | Deployment | Prueba de carga; verificación ISO/IEC 25010; APK de publicación; consolidación de evidencias | Atributos de calidad verificados | 1.1.7 |
| PBI-11 | Evaluation | Construcción del conjunto ENDES; comparación de cuatro algoritmos con DeLong; análisis de errores | OE3 ejecutado sobre datos reales | 1.1.8 |
| PBI-12 | Evaluation y Deployment | Pruebas de caja negra y caja blanca; corrección de defectos con regresión; ventana de registro; baja de pacientes; descarga de la app y textos legales; manual de usuario | Producto verificado formalmente | 1.1.11 |

## Técnicas empleadas

| Técnica | Para qué se usó | Apartado o anexo |
| :--- | :--- | :--- |
| Entrevista semiestructurada | Diagnosticar el seguimiento terapéutico actual (OE1) | 1.1.4.a · Anexo n.° 02 |
| Análisis documental | Construir el conjunto de datos con las historias clínicas | 1.1.2.f · Anexo n.° 03 |
| Encuesta (Morisky-Green y SUS) | Etiqueta de adherencia, línea base y usabilidad | 1.2.1 y 1.2.5 · Anexo n.° 04 |
| Priorización MoSCoW y puntos de Fibonacci | Ordenar y estimar el Product Backlog | 1.1.3 |
| Historias de usuario con criterio de aceptación | Especificar requisitos verificables | Tabla 17 · Anexo n.° 07 |
| Definición de Terminado | Condición única para dar por terminado un elemento | Tabla 5 |
| Limpieza, imputación, codificación y estandarización | Preparar los datos sin introducir valores imposibles | 1.1.5.b |
| Variables derivadas | Carga terapéutica, tasa de inasistencia y cronicidad relativa | 1.1.2.e |
| SMOTE dentro de cada pliegue | Balancear la clase minoritaria sin fuga de información | 1.1.2.g |
| Validación cruzada estratificada y búsqueda en rejilla | Estimar el desempeño y ajustar hiperparámetros | 1.1.5.c |
| Prueba de DeLong y prueba de McNemar | Contrastar las AUCROC y las decisiones de los dos mejores modelos | 1.1.8.c |
| SHAP por permutaciones | Explicar cada predicción al médico | 1.1.6.b |
| Arquitectura de microservicios | Aislar el modelo del resto del sistema | 1.1.2.c |
| Cola local e idempotencia | Registrar tomas sin conexión y sin duplicarlas | 1.1.5.d |
| Token firmado y control de acceso por rol | Proteger los datos clínicos | 1.1.6.g |
| Prueba de carga con usuarios simultáneos | Medir la eficiencia de desempeño | 1.1.7.a |
| Pruebas de caja negra | Verificar los requisitos desde fuera | 1.1.11 · Anexo n.° 24 |
| Pruebas de caja blanca | Verificar la lógica interna y la cobertura | 1.1.11 · Anexo n.° 25 |

## Herramientas de desarrollo y cómo apoyan al producto

| Herramienta | Cómo apoya el desarrollo | Apartado |
| :--- | :--- | :--- |
| FastAPI | API central con validación de cada ficha en el borde del sistema | 1.1.2.d |
| PostgreSQL, SQLAlchemy y Alembic | Reglas clínicas como restricciones de la base y esquema versionado | 1.1.2.d |
| React y Vite | Panel del médico con ficha, alertas y reportes | 1.1.2.d |
| Flutter | Aplicación del paciente y del familiar con avisos locales y cola sin conexión | 1.1.2.d |
| scikit-learn, imbalanced-learn y XGBoost | Preparación, balanceo, comparación de algoritmos y modelo en servicio | 1.1.2.d |
| SHAP | Explicación individual de cada predicción | 1.1.6.b |
| Render, Vercel y Aiven | Publicación del API, del microservicio, del panel y de la base | 1.1.2.d |
| pytest, flutter test y el ejecutor de pruebas de Node.js | Pruebas automatizadas de cada componente | Tabla 34 |
| coverage.py y radon | Cobertura de sentencias y ramas, y complejidad ciclomática | Anexo n.° 25 |
| Playwright | Casos de caja negra sobre la interfaz y capturas del manual | Anexos n.° 23 y 24 |
| PostgreSQL local, pgAdmin y emulador de Android | Ejecución del sistema completo en modo local | Anexo n.° 23, sección 4 |
