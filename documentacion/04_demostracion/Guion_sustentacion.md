# Guion de sustentación del pre informe y del producto acreditable

Sistema de soporte clínico con aprendizaje automático para prevenir el incumplimiento terapéutico en pacientes hipertensos y diabéticos polimedicados del consultorio médico Milko Ugaz Zegarra.

Lo que se evalúa (RA2, IND5 del sílabo) es que el pre informe se sustente **en relación al producto acreditable**, con evidencias de la correspondencia entre **los objetivos, la metodología aplicada, las actividades ejecutadas y los resultados obtenidos**. Todo el guion está ordenado para mostrar esa correspondencia, no para leer el documento.

## 1. Disposiciones obligatorias

Incumplir cualquiera puede afectar drásticamente el puntaje. Revíselas la noche anterior y otra vez antes de entrar.

| Disposición | Cómo cumplirla |
| :--- | :--- |
| Duración total de 25 minutos | Siga la tabla del apartado 3; el reloj del celular, a la vista y en silencio |
| Video de hasta 8 minutos | El archivo editado debe durar 8:00 o menos; verifique la duración exacta antes del día |
| Corrida completa según la rúbrica del producto | La da el video (`Guion_video_8min`): los siete criterios en orden |
| Una diapositiva con título, problema y objetivos | Apartado 4; abierta en pantalla completa al iniciar |
| Cámara encendida durante toda la sesión | Cámara probada, buena luz de frente, fondo ordenado |
| Pantalla completa compartida durante toda la exposición y defensa | Comparta **la pantalla entera**, no una ventana ni una pestaña |
| Vestimenta formal | Camisa (y, si desea, saco) |
| Software en modo local | `python iniciar_local.py` en marcha; nada en la nube |
| Asistencia obligatoria | Conéctese 15 minutos antes; el sorteo de los seis estudiantes es el mismo día |
| Manual y pruebas de caja negra y caja blanca como anexos | Anexos n.° 23, 24 y 25 del pre informe |

## 2. Preparación (45 minutos antes)

**El sistema en modo local**

1. Terminal A: `python iniciar_local.py`. Espere el recuadro «SISTEMA EN MODO LOCAL».
2. Terminal C: `python iniciar_local.py movil`. Espere a ver la pantalla de acceso de la app en el emulador.
3. Inicie sesión **antes** de la sustentación: el médico en el panel y P-001 en la app. No escriba contraseñas con la pantalla compartida.

**Ventanas abiertas, en este orden**

| N.° | Ventana | Para qué |
| :---: | :--- | :--- |
| 1 | La diapositiva, en pantalla completa | Inicio de la sustentación |
| 2 | El video, en un reproductor con el volumen probado | Bloque 2 |
| 3 | El pre informe en Word, en la Tabla 47 (estado de los objetivos) | Bloque 3 y preguntas |
| 4 | El panel en http://localhost:5173 con la ficha de P-001 | Si piden ver el sistema en vivo |
| 5 | El emulador con la app abierta | Si piden ver la app en vivo |
| 6 | VS Code con el repositorio | Si piden ver o cambiar código |

**Antes de compartir la pantalla**

- Cierre `local.env`, `.env`, el panel de Render, el correo y cualquier chat. **Nada secreto en pantalla.**
- Windows en «No molestar», para que no aparezcan notificaciones.
- En la plataforma de la reunión, active **compartir el audio del equipo**. Si no, el jurado verá el video sin sonido.
- Haga una prueba de 10 segundos del video compartiendo la pantalla con alguien, o grabándose.

## 3. Distribución de los 25 minutos

| Tiempo | Bloque | Qué ocurre |
| :--- | :--- | :--- |
| 0:00 – 1:30 | 1 · Apertura con la diapositiva | Título, problema y objetivos |
| 1:30 – 9:30 | 2 · Video del producto | Corrida completa por los siete criterios de la rúbrica |
| 9:30 – 13:30 | 3 · Correspondencia pre informe – producto | Objetivos → metodología → actividades → resultados |
| 13:30 – 25:00 | 4 · Defensa y preguntas | Banco de preguntas del apartado 7 |

Si el jurado empieza a preguntar al terminar el video, **pase directamente al bloque 4** y use las frases del bloque 3 como respuestas. Lo que nunca debe recortarse es la presentación honesta del resultado del OE3 (apartado 6.4).

## 4. Bloque 1 · Apertura con la diapositiva (1,5 min)

**Contenido exacto de la diapositiva**

> **Título.** Sistema de soporte clínico con aprendizaje automático para prevenir el incumplimiento terapéutico en pacientes hipertensos y diabéticos polimedicados del consultorio médico Milko Ugaz Zegarra.
>
> **Problema.** En el Perú, el 37,1 % de los pacientes con hipertensión y diabetes no cumple su tratamiento, y en Lambayeque la cifra llega al 44,7 % entre pacientes crónicos; la polimedicación agrava el riesgo. En el consultorio Milko Ugaz Zegarra, los cerca de 50 pacientes polimedicados se siguen solo con lo que cuentan en la consulta: no se registra lo que ocurre entre una cita y otra, no se analizan sus datos clínicos para anticipar quién va a dejar el tratamiento, no hay alertas tempranas y el médico no sabe en qué se basaría ese riesgo. El incumplimiento se descubre tarde, cuando el paciente ya se descompensó, con riesgo de complicaciones, reconsultas y hospitalizaciones.
>
> **Formulación.** ¿En qué medida un sistema de soporte clínico con aprendizaje automático permite prevenir el incumplimiento terapéutico y apoyar la toma de decisiones clínicas en pacientes polimedicados con hipertensión y diabetes tipo 2 del consultorio médico Milko Ugaz Zegarra de Chiclayo?
>
> **Objetivo general.** Desarrollar un sistema de soporte clínico con aprendizaje automático para prevenir el incumplimiento terapéutico en pacientes hipertensos y diabéticos polimedicados del consultorio médico Milko Ugaz Zegarra.
>
> **Objetivos específicos.**
> OE1. Caracterizar el proceso actual de seguimiento terapéutico y los factores de incumplimiento.
> OE2. Determinar los requisitos funcionales y no funcionales del sistema.
> OE3. Determinar el algoritmo de aprendizaje automático con mayor capacidad predictiva.
> OE4. Construir el sistema de soporte clínico.
> OE5. Evaluar la usabilidad del sistema mediante la escala SUS.
>
> Autor: Leonardo Jesús Guzmán Salazar · Seminario de Tesis I · USAT 2026-II

**Decir**

> «Buenos días. Soy Leonardo Guzmán y presento el sistema de soporte clínico para prevenir el incumplimiento terapéutico en pacientes hipertensos y diabéticos polimedicados del consultorio Milko Ugaz Zegarra.
>
> El problema tiene una magnitud medida: en el Perú, más de un tercio de los pacientes con hipertensión y diabetes no cumple su tratamiento, y en Lambayeque casi la mitad de los pacientes crónicos. En el consultorio, los cerca de cincuenta pacientes polimedicados se siguen solo con lo que cuentan en la consulta. Faltan cuatro cosas: un registro de lo que ocurre entre citas, el análisis de los datos clínicos para anticipar quién va a abandonar, una alerta temprana al médico y una explicación de en qué se basa ese riesgo. Por eso el incumplimiento se descubre tarde, cuando el paciente ya se descompensó.
>
> El objetivo general es desarrollar un sistema que anticipe ese incumplimiento. Para lograrlo planteé cinco objetivos específicos: caracterizar el proceso actual, determinar los requisitos, elegir el algoritmo con mayor capacidad predictiva, construir el sistema y evaluar su usabilidad.
>
> A continuación, el video con la corrida completa del producto, ejecutado en modo local y organizado según los siete criterios de la rúbrica.»

## 5. Bloque 2 · Video del producto (8 min)

1. Cambie al reproductor y póngalo en pantalla completa con `F`, o con doble clic.
2. Mientras corre, **no hable**: el video ya tiene su narración.
3. Al terminar, salga de la pantalla completa con `Esc` y cambie al Word.

> «Ese es el producto funcionando en local. Ahora les muestro cómo cada parte corresponde al pre informe.»

Si el video falla, haga la misma corrida en vivo con el panel y la app ya abiertos: escenas 1a – 1e del guion del video, unos 2 minutos. Luego siga con el bloque 3.

## 6. Bloque 3 · Correspondencia entre el pre informe y el producto (4 min)

Cada frase tiene al lado la tabla del pre informe que debe mostrar. **Muéstrela y diga la frase; no la lea.**

### 6.1. Objetivos → estado real (Tabla 47) · 45 s

> «Los cinco objetivos con su estado real, sin maquillar. El OE4 está cumplido: el sistema funciona y está verificado. El OE3 se ejecutó sobre datos reales, pero no alcanza la meta, y lo explico en un momento. El OE1 y el OE2 están parciales y el OE5 pendiente, por la misma razón: necesitan trabajo de campo con personas, no programación. Un objetivo con un indicador sin dato figura como parcial, nunca como cumplido.»

### 6.2. Metodología → cómo se aplicó (Tablas 2, 3 y 5) · 1 min

> «La metodología es SCRUM como marco del desarrollo y CRISP-DM para el ciclo de vida del modelo, con sus fases dentro de los sprints. La Tabla 2 fija qué decide cada uno: SCRUM decide qué se construye, en qué orden y cuándo está terminado; CRISP-DM ordena cómo se entienden, preparan, modelan y evalúan los datos.
>
> El Product Owner es el médico del consultorio: prioriza y acepta cada incremento. Y la Definición de Terminado tiene siete condiciones; la cuarta, “desplegado y no solo en local”, la agregué tras la retrospectiva del Sprint 3, porque tres defectos solo aparecían en el servidor publicado. Es la Definición de Terminado cambiando por evidencia, como espera SCRUM.»

### 6.3. Actividades ejecutadas → sprints e incrementos (Tablas 1 y 7) · 45 s

> «Cuatro sprints. El primero: diagnóstico del consultorio y autenticación. El segundo: el registro clínico y la preparación de los datos. El tercero cierra el núcleo funcional: modelo como microservicio, explicación SHAP y alertas tempranas. El cuarto: rendimiento, calidad ISO/IEC 25010 y cierre. Después, una verificación formal con pruebas de caja negra y caja blanca.»

### 6.4. Resultados → evidencia (Tablas 37, 45, 46, 41 y 42) · 1,5 min

**Lo que se consiguió**

> «El sistema cumple los diez requisitos funcionales y los seis no funcionales. Lo respaldan 282 pruebas automatizadas, 59 casos de caja negra diseñados con partición de equivalencia, valores límite, tablas de decisión y transición de estados, todos conformes, y el análisis de caja blanca de doce funciones críticas, con su complejidad ciclomática y sus caminos independientes. La verificación encontró seis defectos y los seis se corrigieron, cada uno con su prueba de regresión. Con diez usuarios simultáneos, todas las operaciones responden por debajo de la meta de dos segundos.»

**El resultado que no alcanza la meta: preséntelo usted, antes de que se lo pregunten**

> «La comparación de algoritmos del OE3 se ejecutó sobre datos reales: 8 422 pacientes peruanos con hipertensión o diabetes de los microdatos públicos de la ENDES. Cuatro algoritmos, validación cruzada de cinco pliegues y prueba de DeLong. El mejor AUCROC es 0,591; la meta era 0,80. **No se alcanza.**
>
> Los cuatro algoritmos quedan entre 0,586 y 0,591. Cuando familias tan distintas convergen, el algoritmo no es lo que limita. La encuesta no tiene las variables que más pesan en mi instrumento —número de fármacos, tomas, controles perdidos, apoyo familiar—. Hay señal real, débil: 0,571 en la prueba reservada, mayor que el azar con p = 0,0002. Y el contraste que separa esa explicación de las otras ya está diseñado sobre los pacientes del consultorio.»

### 6.5. Cierre del bloque · 15 s

> «El desarrollo está cerrado y verificado. Lo que queda —la extracción de historias clínicas, el test de Morisky-Green, el juicio de expertos y la escala SUS— son mediciones con personas, y ninguna exige modificar el software. Quedo atento a sus preguntas.»

## 7. Bloque 4 · Banco de preguntas (11,5 min)

**Cómo responder:** primero la respuesta directa en una frase, después la evidencia, nombrando la tabla o el anexo. Si piden verlo, muéstrelo en el sistema o en el Word.

### Sobre el problema y los objetivos

**¿Cómo sabe que el problema existe en el consultorio?**
> Por la entrevista semiestructurada al médico (Anexo n.° 02): ninguno de los cuatro subprocesos de seguimiento tiene soporte digital, y las brechas están en la Tabla 19. La prevalencia de referencia es 37,1 % de no adherencia a nivel nacional y 44,7 % en Lambayeque. La línea base propia sale del test de Morisky-Green, pendiente.

**¿Por qué cinco o más fármacos?**
> Es el criterio de polimedicación del estudio. El sistema lo hace cumplir: rechaza el registro de un paciente con menos de cinco fármacos, en el panel y también en el API.

### Sobre la metodología

**¿Por qué dos metodologías?**
> SCRUM ordena la construcción del software, pero no dice cómo entender y preparar datos ni cómo evaluar un modelo; CRISP-DM sí. El proyecto aprobado las integra: las fases de CRISP-DM se ejecutan dentro de los sprints (Tabla 1).

**¿Quién es el Product Owner si usted trabaja solo?**
> El Dr. Milko Ugaz Zegarra: aporta las necesidades, prioriza el backlog y acepta cada incremento en la Sprint Review. Yo asumo el Scrum Master y el equipo de desarrollo (Tabla 3).

**¿Por qué el Sprint 4 cerró en 59 %?**
> Ningún elemento de desarrollo quedó sin terminar. Los 13 puntos restantes son trabajo de campo con personas; los mantuve en el backlog para no ocultar lo que falta (Tabla 7).

**¿Por qué la predicción se entregó en el Sprint 3 y no en el 2?**
> Por dependencia técnica: el riesgo se calcula sobre la traza de tomas que produce el registro del Sprint 2. Entregarlo antes habría sido un modelo sin entrada (Tabla 8).

### Sobre el modelo

**¿Qué modelos probó y con qué variables?**
> Cuatro: Regresión Logística, Random Forest, XGBoost y SVM. Todos reciben las mismas variables, los mismos pliegues y la misma preparación (Tablas 48 y 49). Se miden con AUCROC, sensibilidad, especificidad, F1 y exactitud (Tabla 50).

**¿Por qué AUCROC y no exactitud?**
> Mire XGBoost en la Tabla 41: exactitud de 0,825 con sensibilidad de 0,097. Detecta a uno de cada diez pacientes que incumplen. Por exactitud sería «el mejor», y como alerta temprana no serviría. Por eso se selecciona por AUCROC y se desempata por sensibilidad.

**¿Por qué DeLong y no McNemar?**
> El criterio de selección es el AUCROC, y DeLong compara dos AUCROC medidas sobre los mismos pacientes. McNemar compara aciertos con un umbral fijo. En la versión anterior usé McNemar para decidir; la observación del evaluador era correcta, así que lo corregí en el código y repetí la comparación. El modelo elegido no cambió.

**¿Por qué el modelo en servicio es un SVM y el de la ENDES un Random Forest?**
> Son dos corridas distintas, y el sistema lo declara en pantalla. El modelo en servicio se entrenó con un conjunto de demostración simulado, solo para que el sistema funcione mientras concluye la extracción; su ficha dice «datos reales: no». La comparación con datos reales es la de la ENDES, donde ganó Random Forest. El modelo definitivo saldrá de la misma comparación sobre las historias clínicas del consultorio.

**¿Cómo explica una predicción al médico?**
> Con SHAP: cada variable aporta una contribución que sube o baja el riesgo. La probabilidad de referencia más las contribuciones da exactamente la probabilidad del paciente; está verificado con un error menor a 0,001 (Tabla 30).

**¿Por qué esas variables son suficientes?**
> Cubren las cinco dimensiones de adherencia de la OMS (Tabla 20). Y la evidencia propia lo respalda: en el modelo en servicio, las que más pesan son la inasistencia, el número de fármacos y los controles perdidos, precisamente las que la ENDES no registra (Anexo n.° 22).

**Si no llega a 0,80, ¿el sistema sirve?**
> El sistema sirve y está operativo; lo que aún no está validado es su capacidad predictiva en la población del estudio. Por eso declara la procedencia del modelo en cada predicción y el informe lo reporta como criterio no cumplido, no como logrado. Además, el médico tiene las alertas por reglas, que no dependen del modelo.

### Sobre el producto y la verificación

**¿Qué diferencia hay entre caja negra y caja blanca en su proyecto?**
> Caja negra: 59 casos diseñados desde los requisitos, sin mirar el código, ejecutados sobre el sistema en marcha (Anexo n.° 24). Caja blanca: doce funciones críticas analizadas por dentro, con su grafo de flujo, la complejidad ciclomática V(G) = E − N + 2 y una prueba por cada camino independiente, más la cobertura: 92 % en el API y 94 % en el microservicio (Anexo n.° 25).

**¿Qué defectos encontró la verificación?**
> Seis (Tabla 46). Por ejemplo, `predecir([])` con una lista vacía fallaba con un error interno; ahora devuelve una lista vacía. Cada corrección tiene su prueba de regresión.

**¿Qué pasa si el paciente no tiene internet?**
> La app guarda la toma en el teléfono y la envía sola al volver la conexión, sin duplicarla aunque la reenvíe. Se ve en el video, escena 4a.

**¿Por qué un microservicio aparte para el modelo?**
> Las bibliotecas del modelo tardan segundos en cargar y el modelo debe poder cambiarse sin tocar el API. Además, si el microservicio falla el resto sigue operando, como se vio en el video.

**¿Por qué estas tecnologías?**
> Cada una se contrastó con una alternativa viable y se descartó la otra por una razón verificable (Tabla 11).

### Sobre los datos y la ética

**¿Cómo protege los datos de los pacientes?**
> Acceso por perfil: el médico ve solo a sus pacientes y el familiar solo la corroboración de tomas, nunca la ficha. Las contraseñas se guardan cifradas. El modelo recibe los datos sin nombre ni documento, con un código anonimizado. Hay una política de privacidad conforme a la Ley N.° 29733. Las pruebas CN-43 a CN-48 lo verifican.

**¿Los pacientes del video son reales?**
> No. Son datos de demostración, y el sistema declara en pantalla que el modelo en servicio se entrenó con datos simulados.

**¿Cómo hará la evaluación SUS y el juicio de expertos?**
> La SUS, con la ficha de observación, al médico sobre el panel y a una muestra de pacientes y familiares sobre la app, con consentimiento informado; el puntaje se calcula con `calcular_sus.py` frente a la meta de 80. El juicio de expertos, con tres especialistas —clínico, metodológico y de software— sobre el expediente del Anexo n.° 19.

### Si le piden un cambio en vivo

Abra VS Code, haga el cambio, guarde y muestre el efecto. El API y el panel se recargan solos; en la app pulse `r` en la terminal C.

| Si piden cambiar… | Archivo | Qué tocar |
| :--- | :--- | :--- |
| Los umbrales del riesgo predicho (alto ≥ 70 %, medio ≥ 40 %) | `ml-service/app/config.py` | `umbral_riesgo_alto`, `umbral_riesgo_medio`; reinicie el lanzador |
| Los umbrales del riesgo observado (60 % y 80 %, tres omisiones seguidas) | `backend-api/app/services/riesgo.py` y `frontend-web/src/services/riesgo.js` | `TASA_ALTA`, `TASA_MEDIA`, `RACHA_ALTA` y su par `UMBRALES` |
| El mínimo de fármacos (5) | `backend-api/app/schemas/paciente_schema.py` y `frontend-web/src/services/validacionPaciente.js` | `MIN_FARMACOS` y el mensaje del campo |
| La ventana de registro (1 h antes, 3 h después) | `backend-api/app/schemas/adherencia_schema.py` y `app-movil/lib/utils/constantes.dart` | `VENTANA_ANTES`, `VENTANA_DESPUES` y `ventanaAntes`, `ventanaDespues` |
| Un texto del menú del panel | `frontend-web/src/components/Layout.jsx` | El texto del `NavLink` |

Al terminar, deshaga el cambio y diga: «el cambio pasa también por las pruebas automatizadas, que lo verifican antes de darlo por terminado».

## 8. Errores que conviene no cometer

1. **No lea el documento ni la diapositiva en voz alta.** El jurado los tiene; su trabajo es mostrar la correspondencia.
2. **No esconda el 0,591.** Si lo presenta usted, con su diagnóstico, es rigor. Si lo encuentran ellos, cuenta en su contra.
3. **No diga que el modelo en servicio usa datos reales.** Se entrenó con datos simulados, y el sistema lo dice.
4. **No escriba contraseñas con la pantalla compartida,** ni abra archivos de configuración.
5. **No deje de compartir la pantalla ni apague la cámara** en ningún momento, aunque cambie de ventana.
