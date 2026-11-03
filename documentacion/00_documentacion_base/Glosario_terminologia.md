# Glosario de terminología de la tesis

Sistema de soporte clínico con aprendizaje automático para prevenir el
incumplimiento terapéutico en pacientes hipertensos y diabéticos polimedicados
del consultorio médico Milko Ugaz Zegarra.

Cada término se explica en dos partes: **qué es**, en lenguaje llano, y **para
qué se usa en esta tesis**, con el lugar concreto donde aparece. No es un
diccionario general: solo están los términos que el proyecto emplea y que un
jurado puede pedir que se expliquen.

---

# 1. Metodologías de desarrollo

**SCRUM**

*Qué es:* marco de trabajo ágil que organiza el desarrollo en ciclos cortos
llamados sprints, cada uno de los cuales termina en algo utilizable.

*En la tesis:* es el **marco anfitrión**. El sprint es la unidad de
planificación, de entrega y de rendición de cuentas. Los cuatro sprints del
proyecto están en la Tabla 1.

**CRISP-DM** *(Cross-Industry Standard Process for Data Mining)*
*Qué es:* proceso de referencia para proyectos de minería de datos, con seis
fases: comprensión del negocio, comprensión de los datos, preparación,
modelado, evaluación y despliegue.

*En la tesis:* ordena el trabajo del **modelo predictivo**. No organiza el
documento: sus fases se ejecutan dentro de los sprints de SCRUM.

**Integración de ambos marcos**

*Qué es:* la decisión de usar dos metodologías complementarias sin que
compitan.

*En la tesis:* SCRUM decide qué se construye, cuándo está terminado y qué se
acepta; CRISP-DM decide cómo se entienden, preparan, modelan y evalúan los
datos. El reparto está en la Tabla 2.

**Sprint**

*Qué es:* ciclo de trabajo de duración fija que termina en un incremento.

*En la tesis:* cuatro sprints de dos semanas, de la semana 2 a la 8.

**Incremento potencialmente entregable**

*Qué es:* el resultado de un sprint: software que funciona y se puede usar, no
código a medio integrar.

*En la tesis:* cada sprint cerró con el sistema desplegado y demostrable al
médico, no con una rama sin integrar.

---

# 2. Artefactos, roles y eventos de SCRUM

**Product Backlog**

*Qué es:* la lista priorizada de todo lo que el producto necesita.

*En la tesis:* diez requisitos funcionales, seis no funcionales y el elemento
PBI-11, cada uno vinculado a la brecha del diagnóstico y al objetivo específico
que atiende.

**Sprint Backlog**

*Qué es:* el subconjunto del Product Backlog que el equipo se compromete a
entregar en un sprint, desglosado en tareas.

*En la tesis:* una tabla por sprint, con tarea, componente, estimación y
estado.

**Definición de Terminado** *(Definition of Done)*
*Qué es:* la lista de condiciones que un elemento debe cumplir para
considerarse terminado. Es única y no admite excepciones.

*En la tesis:* siete condiciones (Tabla 5). La cuarta —desplegado, no solo en
local— se incorporó tras la retrospectiva del Sprint 3, porque tres defectos
solo aparecieron sobre el servicio publicado.

**Historia de usuario**

*Qué es:* la descripción de una necesidad desde el punto de vista de quien la
tiene: *como [rol], quiero [algo] para [un fin]*.

*En la tesis:* cada requisito funcional está redactado así, con su criterio de
aceptación.

**Criterio de aceptación**

*Qué es:* la condición verificable que decide si una historia se cumplió.

*En la tesis:* es lo que convierte «el sistema debe alertar» en algo que se
puede comprobar: *la bandeja muestra el motivo y la cifra que lo sustenta*.

**MoSCoW**

*Qué es:* técnica de priorización que clasifica en *Must* (imprescindible),
*Should* (importante), *Could* (deseable) y *Won't* (fuera de alcance).
*En la tesis:* un requisito es *Must* si sin él no se puede contrastar la
hipótesis.

**Puntos de historia**

*Qué es:* unidad relativa de esfuerzo, no de horas. Se estima con la serie de
Fibonacci porque obliga a distinguir magnitudes en lugar de afinar cifras
falsas.

*En la tesis:* la estimación de cada elemento del Sprint Backlog.

**Velocidad**

*Qué es:* los puntos que el equipo termina realmente en un sprint. Sirve para
planificar el siguiente con un dato y no con un deseo.

*En la tesis:* 24, 58, 99 y 19 puntos (Tabla 7).

**Product Owner**

*Qué es:* quien es dueño del problema: aporta las necesidades, prioriza la pila
y acepta o rechaza cada incremento.

*En la tesis:* el médico del consultorio.

**Scrum Master**

*Qué es:* quien facilita los eventos, mantiene los artefactos y retira
impedimentos.

*En la tesis:* el tesista. Con un equipo de una persona el rol no es de
coordinación sino de disciplina de proceso.

**Sprint Review**

*Qué es:* reunión de cierre donde se demuestra el incremento y el Product Owner
lo acepta o lo observa.

*En la tesis:* se condujo sobre el entorno publicado, no sobre capturas.

**Retrospectiva**

*Qué es:* reunión donde el equipo examina cómo trabajó y acuerda **una** mejora
concreta para el siguiente sprint.

*En la tesis:* de la del Sprint 3 salió la condición 4 de la Definición de
Terminado; de la del Sprint 4 salió PBI-11.

**Refinamiento del Backlog**

*Qué es:* la revisión continua de la pila: aclarar, estimar, dividir o
incorporar elementos.

*En la tesis:* así entraron RF09 y RF10, que no estaban en la pila inicial.

**Impedimento**

*Qué es:* un obstáculo que bloquea el avance y que el equipo registra en lugar
de rodear en silencio.

*En la tesis:* las veintidós incidencias, con su causa y su corrección.

---

# 3. Las seis fases de CRISP-DM

| Fase | Qué resuelve | Dónde está en la tesis |
| :--- | :--- | :--- |
| **Comprensión del negocio** | Entender el problema y fijar criterios de éxito | Sprint 1: entrevista, brechas y criterios CEN y CEA |
| **Comprensión de los datos** | Inventariar fuentes, describir y explorar | Sprint 1: variables del Anexo 04 y su origen |
| **Preparación de los datos** | Limpiar, transformar, particionar y balancear | Sprint 2: pipeline de preparación |
| **Modelado** | Entrenar y comparar algoritmos | Sprints 2 y 3: los cuatro candidatos |
| **Evaluación** | Contrastar con los criterios de éxito | Sprint 3 y PBI-11: comparación sobre la ENDES |
| **Despliegue** | Poner el modelo en servicio | Sprint 3 y 4: microservicio de inferencia |

---

# 4. Terminología clínica

**Adherencia terapéutica**

*Qué es:* el grado en que el comportamiento de un paciente —tomar la
medicación— coincide con las indicaciones acordadas con su médico.

*En la tesis:* es la variable que el sistema vigila y el modelo predice.

**Incumplimiento terapéutico**

*Qué es:* lo contrario: que el paciente no siga el tratamiento prescrito.

*En la tesis:* es la **variable objetivo** del modelo, codificada como 1.

**Polimedicación**

*Qué es:* el uso simultáneo de cinco o más medicamentos.

*En la tesis:* es el criterio de elegibilidad del estudio. El sistema rechaza
registrar a un paciente con menos de cinco fármacos, porque entraría en el
conjunto de entrenamiento alguien que no pertenece a la población estudiada.

**Hipertensión arterial (HTA) y diabetes mellitus tipo 2 (DM2)**

*Qué es:* las dos enfermedades crónicas del estudio, ambas de tratamiento
prolongado y control periódico.

*En la tesis:* definen la población. La variable `diagnostico` toma los valores
*hta*, *dm2* o *ambas*.

**Comorbilidad**

*Qué es:* la presencia de otra enfermedad además de la principal.

*En la tesis:* se registra como lista de enfermedades marcadas, no como un
número suelto, para que la ficha sea específica.

**Test de Morisky-Green**

*Qué es:* cuestionario breve y validado que mide la adherencia mediante
preguntas sobre olvido, horario, abandono al sentirse bien y abandono por
efectos adversos.

*En la tesis:* es la **fuente de la etiqueta**: su puntaje clasifica a cada
paciente como adherente o no. No se usa como predictor, porque determina por
completo la etiqueta y produciría métricas falsamente perfectas.

**Modelo multidimensional de adherencia de la OMS**

*Qué es:* marco que atribuye la adherencia a cinco dimensiones: el paciente, la
enfermedad, la terapia, el sistema de salud y el contexto socioeconómico.

*En la tesis:* organiza las variables de la ficha del Anexo 04. Cada variable
pertenece a una dimensión, lo que impide que la selección parezca arbitraria.

**Autorreporte**

*Qué es:* el dato que declara el propio paciente, sin verificación externa.

*En la tesis:* es la fuente del registro de tomas, y una limitación declarada.
La corroboración familiar añade un segundo testigo, pero no lo convierte en
medida objetiva.

**Línea base**

*Qué es:* la medición del estado inicial, antes de la intervención.

*En la tesis:* el nivel de adherencia del consultorio antes del sistema, contra
el cual se comparará después.

---

# 5. Preparación de datos

**Variable objetivo (etiqueta)**

*Qué es:* lo que el modelo debe predecir.

*En la tesis:* `incumplimiento`, con valores 0 y 1.

**Predictor (característica)**

*Qué es:* cada variable de entrada con la que el modelo hace su predicción.

*En la tesis:* edad, sexo, nivel educativo, convivencia, apoyo familiar,
diagnóstico, tiempo de enfermedad, comorbilidades, número de fármacos, tomas
por día y controles programados y perdidos.

**Variable derivada**

*Qué es:* una característica construida a partir de otras.

*En la tesis:* `carga_terapeutica` (fármacos × tomas), `tasa_inasistencia` y
`cronicidad_relativa`.

**Imputación**

*Qué es:* reemplazar un valor faltante por una estimación, en lugar de
descartar el registro completo.

*En la tesis:* mediana para las numéricas y valor más frecuente para las
categóricas. Se prefiere a descartar al paciente, porque perder una ficha
entera por un dato vacío reduce una muestra ya pequeña.

**Codificación one-hot**

*Qué es:* convertir una variable categórica sin orden en varias columnas de
0 y 1.

*En la tesis:* para sexo, convivencia, apoyo familiar y diagnóstico.

**Codificación ordinal**

*Qué es:* asignar números a categorías que **sí** tienen orden.

*En la tesis:* para nivel educativo, donde *superior* es más que *primaria*.

**Estandarización (escalado)**

*Qué es:* llevar las variables numéricas a una escala común.

*En la tesis:* es indispensable para SVM y Regresión Logística, que miden
distancias; es inocuo para Random Forest y XGBoost.

**Desbalance de clases**

*Qué es:* que una clase sea mucho más frecuente que la otra.

*En la tesis:* los adherentes superan ampliamente a los incumplidores. Sin
corregirlo, un modelo puede acertar mucho prediciendo siempre «adherente» y no
detectar a nadie en riesgo.

**SMOTE** *(Synthetic Minority Over-sampling Technique)*
*Qué es:* técnica que genera ejemplos sintéticos de la clase minoritaria
interpolando entre casos reales cercanos.

*En la tesis:* equilibra el entrenamiento. Se aplica **dentro** de cada pliegue
de la validación cruzada, nunca antes de particionar.

**Partición estratificada**

*Qué es:* dividir en entrenamiento y prueba conservando en ambos lados la misma
proporción de clases.

*En la tesis:* 80 % y 20 %, para que el conjunto de prueba represente la
prevalencia real.

**Fuga de información** *(data leakage)*
*Qué es:* que información del conjunto de prueba influya en el entrenamiento,
inflando las métricas.

*En la tesis:* se evita ajustando imputador, codificador, escalador y SMOTE
**solo** con el entrenamiento. Es la decisión metodológica central del
pipeline.

**Anonimización**

*Qué es:* eliminar los datos que identifican a una persona.

*En la tesis:* el modelo recibe un código anonimizado, nunca nombre ni
documento de identidad.

---

# 6. Algoritmos

**Aprendizaje supervisado**

*Qué es:* entrenar con ejemplos que ya traen la respuesta correcta.

*En la tesis:* cada ficha viene con su etiqueta de adherencia obtenida del test
de Morisky.

**Clasificación binaria**

*Qué es:* predecir a cuál de dos categorías pertenece un caso.

*En la tesis:* adherente o incumplidor.

**Por qué cuatro algoritmos y no uno**

*Qué es:* la comparación no mezcla cuatro variantes parecidas, sino cuatro
**familias distintas** de aprendizaje: un modelo lineal, uno de ensamble por
promediado, uno de ensamble secuencial y uno de margen máximo.

*En la tesis:* cubrir las cuatro familias es lo que permite afirmar algo sobre
el problema y no solo sobre un algoritmo. Cuando los cuatro convergen en un
desempeño parecido —entre 0,586 y 0,591 de AUCROC sobre la ENDES—, la elección
del algoritmo no es el factor limitante. Lo que el resultado no permite es
atribuir el bajo desempeño a una sola causa: puede deberse a las variables, a
una etiqueta ruidosa o a la diferencia de población, y separar esas
explicaciones requiere los datos del consultorio.

**Árbol de decisión**

*Qué es:* una secuencia de preguntas sobre las variables que va partiendo a los
pacientes en grupos cada vez más homogéneos: *¿toma más de 6 fármacos?*, y
según la respuesta, *¿faltó a más de 2 controles?* Cada hoja final es una
predicción.

*En la tesis:* no se usa suelto, pero es la pieza con la que están construidos
Random Forest y XGBoost. Un árbol solo es fácil de leer pero inestable:
cambiando unos pocos pacientes, el árbol resultante puede ser muy distinto.

**Regresión Logística**

*Qué es:* modelo lineal que asigna un peso a cada variable, suma esos aportes y
convierte el total en una probabilidad entre 0 y 1. El peso dice cuánto empuja
cada variable hacia el incumplimiento.

*En la tesis:* es el candidato más interpretable y la referencia de
comparación: si un modelo complejo no supera a la regresión logística, su
complejidad no se justifica. Exige escalar las variables. Sobre la ENDES
obtuvo AUCROC 0,588 con `C = 0,1`.

**Random Forest** *(bosque aleatorio)*

*Qué es:* un conjunto de muchos árboles de decisión que votan. Cada árbol se
entrena con una muestra distinta de pacientes y, en cada división, solo puede
mirar un subconjunto al azar de las variables. Esa doble aleatoriedad hace que
los árboles se equivoquen en cosas distintas, y al promediar sus votos los
errores individuales se cancelan. Es lo que se llama **ensamble por
promediado** o *bagging*.

*En la tesis:* fue el **modelo seleccionado** en la comparación sobre la ENDES,
con AUCROC 0,591 y sensibilidad 0,450. Sus hiperparámetros ajustados fueron
`n_estimators = 200` (doscientos árboles), `max_depth = 8` y
`min_samples_leaf = 5`.

Los dos últimos merecen explicación porque un jurado puede preguntarlos:
`max_depth = 8` limita la profundidad de cada árbol para que no memorice casos
concretos, y `min_samples_leaf = 5` obliga a que cada hoja agrupe al menos
cinco pacientes, de modo que ninguna regla del modelo se construya sobre un
único caso. Ambos son medidas contra el sobreajuste.

*Por qué es buen candidato aquí:* captura interacciones entre variables sin que
haya que declararlas —por ejemplo, que el número de fármacos pese distinto
según la edad—, tolera variables de distinta naturaleza y no necesita escalado.
*Su límite:* con clases desbalanceadas tiende a favorecer a la mayoritaria, y
no extrapola fuera del rango de datos que vio.

**XGBoost** *(potenciado por gradiente extremo)*

*Qué es:* también usa árboles, pero de forma opuesta a Random Forest. En lugar
de entrenarlos en paralelo e independientes, los construye **en secuencia**:
cada árbol nuevo se especializa en corregir los errores que cometió el conjunto
de los anteriores. Es lo que se llama **ensamble secuencial** o *boosting*.
Incorpora además regularización para frenar el sobreajuste que esa corrección
acumulada podría producir.

*En la tesis:* candidato, con `learning_rate = 0,05`, `max_depth = 3` y
`n_estimators = 400`. Se incluyó porque la literatura lo señala como el
referente en datos tabulares clínicos; excluirlo habría dejado la comparación
sin la familia más competitiva.

*Y es el caso más instructivo del cuadro:* obtuvo **exactitud 0,825 con
sensibilidad 0,097**. Detecta a uno de cada diez pacientes que incumplen. La
causa es que optimiza el error global y, con un 86 % de pacientes adherentes,
la forma más barata de reducir ese error es responder «adherente» casi siempre.
Reportado por su exactitud parecería el mejor modelo del cuadro; como alerta
temprana es el más inservible. Es la razón concreta de que el protocolo
seleccione por AUCROC y desempate por sensibilidad, y no por exactitud.

**Diferencia entre Random Forest y XGBoost**

*Qué es:* ambos son conjuntos de árboles, pero con lógicas contrarias. Random
Forest entrena árboles **independientes** y promedia para **reducir la
varianza**: combate la inestabilidad. XGBoost entrena árboles **dependientes**,
cada uno sobre los errores del anterior, para **reducir el sesgo**: combate la
imprecisión.

*En la tesis:* esa diferencia explica sus resultados opuestos. Random Forest
reparte su atención y detecta al 45 % de los incumplidores; XGBoost persigue el
error global y se desploma al 9,7 % de detección. La prueba de McNemar entre
ambos —con el umbral de 0,5— encuentra 2 034 pacientes en los que discrepan
(*p* < 0,001), aunque la prueba de DeLong indica que **ordenan a los pacientes con
la misma capacidad** (*p* = 0,742). Dos modelos pueden ordenar igual de bien y,
con el mismo umbral, alertar sobre pacientes distintos.

**SVM (máquina de vectores de soporte) con núcleo RBF**

*Qué es:* busca la frontera que separa las dos clases dejando el mayor margen
posible a cada lado. El núcleo RBF le permite que esa frontera sea curva en
lugar de recta, proyectando los datos a un espacio donde sí son separables.

*En la tesis:* candidato; fue el seleccionado en la corrida de verificación
sobre el conjunto de demostración, por su mayor sensibilidad. Exige escalado y
no tiene coeficientes legibles, lo que obliga a explicar sus predicciones con
SHAP.

**Hiperparámetros**

*Qué es:* los ajustes del algoritmo que no se aprenden de los datos y hay que
fijar antes de entrenar: cuántos árboles, qué profundidad, qué tasa de
aprendizaje.

*En la tesis:* se eligen con **búsqueda en rejilla**, que prueba todas las
combinaciones declaradas y se queda con la mejor según la validación cruzada.
La búsqueda se hace solo sobre el conjunto de entrenamiento, nunca sobre el de
prueba.

**Tasa de aprendizaje** *(learning rate)*

*Qué es:* en los modelos secuenciales, cuánto se deja corregir a cada árbol
nuevo. Valores bajos avanzan más despacio pero generalizan mejor.

*En la tesis:* 0,05 en XGBoost, compensado con 400 árboles: muchos pasos
pequeños en lugar de pocos grandes.

---

# 7. Validación y métricas

**Validación cruzada estratificada de k pliegues**

*Qué es:* dividir el entrenamiento en k partes, entrenar k veces dejando una
fuera cada vez y promediar. Da una estimación más estable que una sola
partición.

*En la tesis:* cinco pliegues, conservando la proporción de clases.

**Matriz de confusión**

*Qué es:* tabla que cruza lo predicho con lo real: verdaderos y falsos,
positivos y negativos.

*En la tesis:* es la base de todas las métricas siguientes.

**Exactitud**

*Qué es:* proporción de aciertos sobre el total.

*En la tesis:* **se reporta pero no se usa para seleccionar.** Con clases
desbalanceadas es engañosa.

**Sensibilidad** *(recall)*
*Qué es:* de todos los que realmente incumplen, cuántos detecta el modelo.

*En la tesis:* es el criterio de desempate, porque el error costoso es el falso
negativo: un paciente en riesgo que el sistema no detecta y que por tanto no
recibe la alerta.

**Especificidad**

*Qué es:* de todos los adherentes, cuántos identifica correctamente como tales.

*En la tesis:* protege de saturar al médico con avisos innecesarios.

**F1-score**

*Qué es:* media armónica entre precisión y sensibilidad; resume ambas en un
número.

*En la tesis:* métrica de contraste cuando las clases están desbalanceadas.

**AUCROC**

*Qué es:* área bajo la curva ROC. Mide la capacidad de ordenar correctamente a
los pacientes por riesgo, independientemente del umbral elegido. 0,5 equivale
al azar; 1,0 a la separación perfecta.

*En la tesis:* es el **criterio principal de selección**, con meta de ≥ 0,80.
Sobre la ENDES el mejor fue 0,591, por lo que el criterio no se cumple.

**Prueba de DeLong**

*Qué es:* contraste estadístico que compara las AUCROC de dos modelos evaluados
sobre los mismos pacientes, teniendo en cuenta que ambas medidas están
correlacionadas. Responde a la pregunta: ¿alguno ordena mejor a los pacientes
por riesgo?

*En la tesis:* es la prueba que **decide el empate** entre los dos mejores
algoritmos, porque el criterio de selección es el AUCROC. Sobre la ENDES,
Random Forest y XGBoost no difieren (*p* = 0,742), así que decidió la
sensibilidad.

**Prueba de McNemar**

*Qué es:* contraste que compara dos clasificadores sobre los mismos casos,
mirando solo aquellos en los que uno acierta y el otro falla, con un umbral de
decisión fijo.

*En la tesis:* se reporta como complemento y **no decide la selección**:
responde a si los dos modelos, con el umbral de 0,5, alertarían sobre los mismos
pacientes. Confundirla con un contraste de AUCROC fue el error que señaló la
evaluación del pre informe y que se corrigió.

**Sobreajuste**

*Qué es:* que el modelo memorice el entrenamiento y falle con datos nuevos.

*En la tesis:* se vigila comparando el desempeño en validación cruzada con el
del conjunto de prueba reservado.

---

# 8. Explicabilidad

**Modelo de caja negra**

*Qué es:* un modelo cuya decisión no se puede leer directamente de sus
parámetros.

*En la tesis:* es el problema que SHAP resuelve. Un médico no puede actuar
sobre un número sin saber de dónde sale.

**SHAP** *(SHapley Additive exPlanations)*
*Qué es:* método que reparte la predicción entre las variables, indicando
cuánto aportó cada una en puntos porcentuales.

*En la tesis:* materializa el RF06. En la ficha se ve como barras: rojas suben
el riesgo, verdes lo bajan.

**Propiedad aditiva**

*Qué es:* la garantía de que la probabilidad del paciente de referencia más
todas las contribuciones da exactamente la probabilidad del paciente.

*En la tesis:* es lo que distingue a SHAP de una explicación aproximada, y está
verificada con error menor a 0,001.

**Importancia por permutación**

*Qué es:* medir cuánto empeora el modelo al desordenar una variable. Describe
el modelo **en conjunto**, no a un paciente.

*En la tesis:* se usa para la ficha del modelo; no sustituye a SHAP, que es
individual.

---

# 9. Arquitectura y software

**API REST**

*Qué es:* interfaz que permite a otros programas pedir y enviar datos por
HTTP.

*En la tesis:* el API central, que concentra la autenticación y las reglas
clínicas.

**Microservicio**

*Qué es:* un servicio pequeño e independiente, con su propio despliegue y
versiones.

*En la tesis:* el servicio de inferencia. Separarlo evita que el API cargue las
bibliotecas del modelo en cada arranque y permite reentrenar sin redesplegar
todo. Si falla, el resto del sistema sigue operando.

**JWT** *(token de sesión firmado)*
*Qué es:* credencial firmada que el cliente presenta en cada petición para
acreditar su sesión.

*En la tesis:* sostiene el RF01.

**Control de acceso por roles (RBAC)**

*Qué es:* restringir las operaciones según el perfil de quien las pide.

*En la tesis:* el médico ve solo a sus pacientes; el familiar solo corrobora
tomas; el paciente no entra al panel.

**ORM y migraciones**

*Qué es:* el ORM traduce entre objetos del programa y tablas; las migraciones
son cambios de esquema versionados y reversibles.

*En la tesis:* el esquema clínico cambió cinco veces, y cada cambio quedó como
una migración aplicable y reversible.

**Pipeline serializado**

*Qué es:* guardar en un solo archivo la preparación de datos y el modelo, de
modo que la inferencia aplique exactamente las transformaciones del
entrenamiento.

*En la tesis:* evita el desfase entre entrenamiento y servicio.

**Cola sin conexión y sincronización**

*Qué es:* guardar localmente lo que no se pudo enviar y reintentarlo al
recuperar la red, sin duplicar.

*En la tesis:* el paciente registra su toma aunque no tenga señal.

**Idempotencia**

*Qué es:* que repetir una operación no cambie el resultado.

*En la tesis:* impide que una toma reenviada se registre dos veces.

**Despliegue continuo**

*Qué es:* publicar automáticamente desde el repositorio en cada cambio.

*En la tesis:* el API y el microservicio en Render, el panel en Vercel.

---

# 10. Calidad y verificación

**Requisito funcional (RF)**

*Qué es:* lo que el sistema debe hacer.

*En la tesis:* diez, de RF01 a RF10.

**Requisito no funcional (RNF)**

*Qué es:* cómo debe comportarse: rapidez, seguridad, fiabilidad.

*En la tesis:* seis, de RNF01 a RNF06, cada uno asociado a un atributo de la
norma ISO/IEC 25010.

**ISO/IEC 25010**

*Qué es:* norma internacional que define el modelo de calidad del producto de
software. Su edición de 2023 lo organiza en nueve características: adecuación
funcional, eficiencia de desempeño, compatibilidad, capacidad de interacción
(antes usabilidad), fiabilidad, seguridad, mantenibilidad, flexibilidad (antes
portabilidad) y protección, que es nueva y se refiere a que el producto no
ponga en riesgo la salud o la vida de las personas.

*En la tesis:* el marco con el que se verifican los RNF. Ocho de las nueve
características están verificadas; la capacidad de interacción requiere
usuarios. La protección es especialmente pertinente en un sistema de soporte
clínico: el sistema no muestra un riesgo que no calculó y declara con qué
datos se entrenó el modelo.

**Escala SUS** *(System Usability Scale)*
*Qué es:* cuestionario de diez afirmaciones con respuesta de 1 a 5, cuyo
puntaje va de 0 a 100. Los ítems impares aportan *respuesta − 1*, los pares
*5 − respuesta*, y la suma se multiplica por 2,5.
*En la tesis:* instrumento del OE5, con meta de ≥ 80 puntos.

**Prueba unitaria y prueba de integración**

*Qué es:* la unitaria verifica una pieza aislada; la de integración, que varias
funcionen juntas.

*En la tesis:* 193 pruebas automatizadas entre API, microservicio y aplicación
móvil.

**Prueba de carga y percentil 95**

*Qué es:* medir el comportamiento con varios usuarios simultáneos. El percentil
95 indica el tiempo que el 95 % de las peticiones no supera, y describe la
experiencia peor mejor que el promedio.

*En la tesis:* con diez usuarios, todas las operaciones bajo 1,4 segundos.

**Matriz de trazabilidad**

*Qué es:* tabla que conecta objetivos, requisitos, implementación y pruebas.

*En la tesis:* permite demostrar que cada objetivo se materializó en código
verificado, y es la evidencia de la correspondencia que pide la rúbrica.

---

# 11. Fuentes de datos e instrumentos

**Ficha de recolección (Anexo n.° 04)**

*Qué es:* el instrumento con el que se extraen, de forma anonimizada, las
variables de cada paciente de la historia clínica.

*En la tesis:* es la **fuente definitiva** del conjunto de entrenamiento.

**ENDES** *(Encuesta Demográfica y de Salud Familiar)*
*Qué es:* encuesta nacional del INEI, de periodicidad anual, con un módulo de
enfermedades no transmisibles. Sus microdatos son públicos.

*En la tesis:* **conjunto externo** con el que se ejecutó la comparación de
algoritmos sobre datos reales mientras la extracción documental concluye. No
sustituye a la población del estudio.

**Microdatos**

*Qué es:* los registros individuales de una encuesta, no sus resúmenes
publicados.

*En la tesis:* permiten reconstruir las variables paciente por paciente.

**Juicio de expertos**

*Qué es:* validación de un instrumento por especialistas que lo califican en
claridad, coherencia, relevancia y suficiencia.

*En la tesis:* tres evaluadores validan los instrumentos y califican la
alineación de la arquitectura con estándares, con meta de ≥ 4/5.

**Consentimiento informado**

*Qué es:* la autorización que da una persona tras conocer en qué consiste su
participación.

*En la tesis:* condición para la recolección de datos clínicos, junto con la
anonimización.
