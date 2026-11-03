# Guion del video del producto acreditable (8 minutos)

Video de demostración según la **Rúbrica para Evaluar el Producto Acreditable**: siete criterios de la norma ISO/IEC 25010 que suman 14 puntos. Se graba **por escenas cortas**, una o varias por criterio, y se unen al final. Cada escena indica qué grabar, qué decir y qué descriptor del nivel **Bueno** de la rúbrica deja demostrado.

## 1. Mapa del video

| Escena | Tiempo | Criterio de la rúbrica (puntaje) | Qué se ve |
| :---: | :---: | :--- | :--- |
| 0 | 0:00 – 0:20 | Presentación | Título, problema y arquitectura en modo local |
| 1 | 0:20 – 2:10 | **Adecuación funcional** (1,5) | Corrida completa: médico → paciente → familiar → riesgo con IA → alerta → reporte |
| 2 | 2:10 – 2:55 | **Eficiencia de desempeño** (2,0) | Tiempos medidos en el navegador y prueba de carga |
| 3 | 2:55 – 4:00 | **Capacidad de interacción** (2,5) | Navegación, prevención de errores, mensajes y manual |
| 4 | 4:00 – 5:00 | **Fiabilidad** (1,5) | Registro sin conexión que sincroniza; el modelo cae y el sistema sigue |
| 5 | 5:00 – 6:05 | **Seguridad** (2,5) | Acceso por perfil, permisos, contraseñas cifradas y registro de responsables |
| 6 | 6:05 – 6:50 | **Flexibilidad** (1,5) | Microservicios, modelo reemplazable, mismo código en local y en la nube |
| 7 | 6:50 – 7:40 | **Protección** (2,5) | Operaciones que el sistema impide y riesgos documentados |
| 8 | 7:40 – 8:00 | Cierre | Resultados de las pruebas y conclusión |

**Ritmo de narración:** unas 140 palabras por minuto. Los textos de «Decir» ya están medidos para su escena; si una toma se alarga, recorte la narración, no la demostración.

## 2. Preparación antes de grabar

**Sistema en modo local**

1. `python iniciar_local.py preparar --rehacer` (base limpia con P-001 a P-005).
2. `python iniciar_local.py` en una terminal y `python iniciar_local.py movil` en otra. Espere a que el emulador muestre la app.
3. Con la base recién preparada, entre una vez a **Alertas tempranas** para que existan alertas pendientes.

**Ventanas abiertas, en este orden**

| Ventana | Contenido |
| :--- | :--- |
| Navegador, pestaña 1 | http://localhost:5173 (inicio de sesión del panel) |
| Navegador, pestaña 2 | http://localhost:5173/descargar |
| Navegador, pestaña 3 | http://localhost:8000/docs (documentación del API, solo en local) |
| Emulador de Android | App «Mi tratamiento» en la pantalla de inicio de sesión |
| Terminal A | La del lanzador (`iniciar_local.py`), con los registros del API visibles |
| Terminal B | En `backend-api`, lista para la prueba de carga (escena 2) |
| Terminal C | La de la aplicación móvil (`iniciar_local.py movil`), con la línea «Instalando la aplicacion en emulator-5554, conectada a http://10.0.2.2:8000» visible |
| pgAdmin | Base `cdss_local`, consulta preparada (escena 5) |
| Visor de documentos | Manual de usuario (Anexo n.° 23) abierto en su índice |

**Antes de pulsar «grabar»**

- Cierre o minimice `local.env`, `.env`, el panel de Render y la cadena de conexión de pgAdmin. **Nada secreto en pantalla.**
- Escriba las contraseñas con la grabación en pausa, o haga un corte justo después de escribirlas.
- Notificaciones de Windows en «No molestar»; zoom del navegador al 110 %; resolución 1920 × 1080.
- Grabación: Xbox Game Bar (`Win + Alt + R`) u OBS; edición y unión de cortes: Clipchamp (incluido en Windows 11).

## 3. Escenas

### Escena 0 · Presentación (0:00 – 0:20)

Tres planos seguidos; la narración va pegada a cada uno.

| Plano | Grabar | Decir |
| :--- | :--- | :--- |
| 1 (6 s) | Pantalla de inicio de sesión del panel | «Presento el sistema de soporte clínico para prevenir el incumplimiento terapéutico en pacientes hipertensos y diabéticos polimedicados del consultorio Milko Ugaz Zegarra.» |
| 2 (7 s) | Terminal A con el recuadro «SISTEMA EN MODO LOCAL» | «Corre en modo local: un panel web para el médico, un API central, un microservicio con el modelo de aprendizaje automático y la base de datos.» |
| 3 (7 s) | Terminal C junto al emulador, con la línea «conectada a http://10.0.2.2:8000» | «Y una aplicación Android para el paciente y su familia, conectada a ese mismo API.» |

La terminal A no menciona la aplicación móvil porque esta se instala y se ejecuta en la terminal C. La dirección `10.0.2.2` es la forma en que el emulador ve al computador: la aplicación habla con el mismo API de la terminal A.

### Escena 1 · Adecuación funcional (0:20 – 2:10)

Es la **corrida completa** que pide el sílabo. Se graba en cinco cortes seguidos; en cada tabla, la frase de «Decir» se pronuncia mientras se ve lo que indica «Grabar» en la misma fila.

**Corte 1a · El médico registra al paciente (25 s)**

| Plano | Grabar | Decir |
| :--- | :--- | :--- |
| 1 | Inicie sesión como médico → **Registrar paciente** → complete la ficha (por ejemplo, 64 años, ambas enfermedades, 7 fármacos, 4 tomas, 6 controles y 2 perdidos) | «El médico registra al paciente polimedicado con las variables clínicas del estudio.» |
| 2 | **Registrar paciente** → mensaje «Paciente P-006 registrado» | «El sistema le asigna un código anonimizado.» |
| 3 | **Ver ficha** → **Generar acceso** | «Y desde su ficha le genera el acceso a la aplicación.» |

**Corte 1b · El paciente registra sus tomas (35 s)**

| Plano | Grabar | Decir |
| :--- | :--- | :--- |
| 1 | En el emulador, inicie sesión como paciente P-001 | «Para seguir con un paciente que ya tiene historial, entro como P-001.» |
| 2 | **Medicinas** → **Agregar** un medicamento con su hora | «El paciente registra sus medicamentos con su horario, y el teléfono le recordará cada dosis.» |
| 3 | **Hoy** → en una dosis, **Ya la tomé** | «A la hora de cada toma confirma si la tomó.» |
| 4 *(3 s, opcional)* | Pantalla dividida con la terminal A: aparece `peticion metodo=POST ruta=/api/adherencia/registros estado=201` | «La toma llega al instante al API.» |
| 5 | En otra dosis, **No la tomé** con el motivo «No tenía el medicamento» | «Si no la tomó, indica por qué.» |

**Corte 1c · El familiar confirma (15 s)**

| Plano | Grabar | Decir |
| :--- | :--- | :--- |
| 1 | Cierre sesión → **Soy familiar** con la cuenta de demostración rosa.p-001 | «Un familiar de confianza entra con su propia cuenta…» |
| 2 | **Sí, la tomó** → «Confirmado. Gracias.» | «…y confirma las tomas que presenció, para que el registro no dependa solo de la palabra del paciente.» |

**Corte 1d · El componente inteligente (25 s)**

| Plano | Grabar | Decir |
| :--- | :--- | :--- |
| 1 | En el panel, ficha de P-001 → recuadro **Riesgo predicho por el modelo** | «El modelo estima la probabilidad de que este paciente incumpla antes del próximo control…» |
| 2 | Acerque el cursor a las barras SHAP | «…y explica, variable por variable, por qué: aquí los controles perdidos suben el riesgo y el apoyo familiar lo baja.» |
| 3 | Baje al **Historial de tomas** y muestre la columna **Testigo** con la toma recién confirmada | «El historial muestra las tomas que acaba de registrar el paciente y quién las respaldó.» |

Antes de grabar el plano 2, mire qué variables muestran realmente las barras de P-001 y nombre esas; si son otras, cambie la frase.

**Corte 1e · Alerta y reporte (10 s)**

| Plano | Grabar | Decir |
| :--- | :--- | :--- |
| 1 | **Alertas tempranas** → una alerta pendiente | «Cuando un paciente empieza a fallar, el médico recibe una alerta sin revisar ficha por ficha…» |
| 2 | **Reportes generales** → **Exportar CSV** | «…y puede auditar y exportar la situación de todos sus pacientes.» |

**Descriptor del nivel Bueno que demuestra:** cubre todas las funciones de su propósito; ofrece **capacidades adicionales que aportan valor** (explicación SHAP, corroboración familiar, registro sin conexión); resultados fiables y exactos; responde a necesidades reales del consultorio.

### Escena 2 · Eficiencia de desempeño (2:10 – 2:55)

| Plano | Grabar | Decir |
| :--- | :--- | :--- |
| 1 | En el panel, `F12` → pestaña **Red** → filtro `api/prediccion` → recargue la ficha de P-001 → clic en la petición → pestaña **Timing**: señale la barra verde **Waiting for server response** | «El servidor calcula la predicción con su explicación en menos de un cuarto de segundo.» |
| 2 | Corte a la terminal B con la tabla final de la prueba de carga, ejecutada antes de grabar: `python scripts/prueba_carga.py --url http://127.0.0.1:8000 --correo milko.ugaz@consultorio.pe --usuarios 10 --repeticiones 20` (la contraseña se pide aparte) | «Con diez usuarios simultáneos, todas las operaciones del médico responden por debajo de la meta de dos segundos del requisito, lejos del límite de cinco.» |
| 3 | En el panel, con `F12` → **Red** y el filtro `api/reportes`: abra **Reportes generales**, vaya a otra sección y vuelva antes de un minuto. Señale el tiempo de las dos peticiones `general`: la segunda es menor | «El modelo trabaja en su propio servicio y las predicciones se guardan en memoria durante un minuto, de modo que los reportes no recalculan a todos los pacientes en cada apertura.» |

En **Timing**, la barra gris **Stalled** es el tiempo que el navegador espera para enviar la petición mientras atiende las demás de la ficha; no es tiempo del sistema. La que mide al servidor es **Waiting for server response**.

**Descriptor:** sin demoras críticas (menos de 5 s); uso eficiente de recursos; estable bajo carga.

### Escena 3 · Capacidad de interacción (2:55 – 4:00)

Cortes de 10 a 15 segundos.

| Plano | Grabar | Decir |
| :--- | :--- | :--- |
| 1 | Recorra el menú lateral del panel: Panel de auditoría, Alertas, Reportes | «La interfaz guía al usuario en cada paso, con un menú rotulado y siempre visible.» |
| 2 | **Registrar paciente** → edad **17** y **4** fármacos → **Registrar** → mensajes rojos junto a cada campo; el formulario no se envía | «Previene errores antes de que ocurran: avisa junto a cada campo qué corregir y no deja pasar datos imposibles.» |
| 3 | En el campo de edad, teclee «6a4»: la letra no entra y queda «64» | «Tampoco admite letras donde va un número.» |
| 4 | En la ficha, **Dar de baja** → aparece la confirmación → **Cancelar** | «Y pide confirmación en las acciones delicadas.» |
| 5 | En el emulador, una dosis de la noche: «Podrá registrarla desde las 19:00.» | «La aplicación está pensada para adultos mayores: letra grande, una sola tarea por pantalla y mensajes en lenguaje llano que le dicen qué puede hacer y cuándo.» |
| 6 | El manual de usuario abierto en su índice → página **/descargar** con su código QR | «Un manual por perfil y una página de descarga con código QR acompañan al usuario.» |

**Descriptor:** intuitiva y accesible; tareas complejas sin capacitación extensa; **previene errores**; retroalimentación oportuna y clara; **documentación de ayuda detallada**.

### Escena 4 · Fiabilidad (4:00 – 5:00)

**Corte 4a · Sin conexión, sin pérdida de datos (35 s)**

| Plano | Grabar | Decir |
| :--- | :--- | :--- |
| 1 | En el emulador, active el **modo avión** → **Ya la tomé** en una dosis → aparece la nube tachada («pendiente de enviar») | «Sin señal, la aplicación no pierde nada: guarda la toma en el teléfono.» |
| 2 | Desactive el modo avión → la nube desaparece | «Al volver la conexión, la envía sola.» |
| 3 | En el panel, la toma está en el historial **una sola vez** | «Y no la duplica aunque la reenvíe.» |

**Corte 4b · El modelo cae y el sistema sigue (25 s)**

| Plano | Grabar | Decir |
| :--- | :--- | :--- |
| 1 | En una terminal nueva, `netstat -ano`: busque la línea `127.0.0.1:8001 … LISTENING` y su último número (PID) → `taskkill /PID <PID> /F` → en la terminal A, el aviso de que el modelo se detuvo | «Simulo una falla: detengo el microservicio del modelo.» |
| 2 | Recargue la ficha: «El modelo predictivo no está disponible» | «El sistema lo dice con claridad…» |
| 3 | Abra **Alertas tempranas** (aviso «se muestran las alertas basadas en las tomas registradas») y **Reportes generales** (indicadores completos; solo el gráfico de riesgo predicho dice «El modelo no está disponible en este momento») | «…y todo lo demás sigue operando: la ficha, el historial, los reportes y las alertas por reglas.» |
| 4 | Corte: en la terminal A, `Ctrl+C` y `python iniciar_local.py` → espere el recuadro «SISTEMA EN MODO LOCAL» → recargue la ficha: el riesgo vuelve y el historial conserva las mismas tomas | «Al reiniciarlo, el modelo vuelve sin pérdida de datos.» |

El plano 4 deja el sistema listo para las escenas siguientes.

**Descriptor:** opera de forma estable; **tolera y gestiona los fallos** sin impacto visible; se recupera sin pérdida de datos ni interrupciones.

### Escena 5 · Seguridad (5:00 – 6:05)

| Plano | Grabar | Decir |
| :--- | :--- | :--- |
| 1 | Panel: inicie sesión con una contraseña errónea → «Usuario o contraseña incorrectos.» | «Un acceso con credenciales erróneas se rechaza sin revelar qué dato falló.» |
| 2 | App: intente entrar con la cuenta del médico eligiendo **Soy el paciente** → se rechaza | «El acceso es por perfil: médico, paciente y familiar entran cada uno por su lado y ven solo lo suyo.» |
| 3 | pgAdmin: `SELECT correo, rol, left(hash_contrasena, 25) AS hash FROM usuarios;` — **solo esa consulta**, nunca la conexión | «Las contraseñas se guardan cifradas y nadie puede leerlas, ni siquiera desde la base de datos.» |
| 4 | Ficha de P-001: columna **Testigo** → Alertas → **Atendidas**, con la nota del médico | «Cada toma registra quién la hizo y quién la confirmó, y cada alerta, qué hizo el médico.» |
| 5 | Terminal: líneas CN-43 a CN-48 de la última ejecución de caja negra, todas «Conforme» | «Las pruebas confirman que sin sesión, con un token alterado, pidiendo una ficha ajena o con una inyección SQL no se consigue nada.» |

**Descriptor:** legitimidad de accesos, protección de datos y autenticación segura; **roles y responsabilidades**; **registro de acciones que identifica a los responsables**; resistencia a amenazas.

### Escena 6 · Flexibilidad (6:05 – 6:50)

| Plano | Grabar | Decir |
| :--- | :--- | :--- |
| 1 | Pestaña http://localhost:8000/docs: desplace la lista de servicios del API | «La arquitectura es de microservicios: el panel y la aplicación hablan con un único API. Agregar una función nueva es agregar un servicio aquí, como se hizo con el grupo familiar o la recuperación de contraseña.» |
| 2 | La ficha: la línea «Modelo: SVM (RBF), entrenado el …» | «El modelo vive aparte: se puede reentrenar y reemplazar con un comando sin tocar el resto del sistema.» |
| 3 | El archivo `render.yaml` (no contiene secretos) junto a la terminal A | «Y el mismo código corre en esta computadora o en la nube.» |

**Descriptor:** flexible y escalable; soporta cambios y crecimiento sin degradar la calidad; permite **introducir funcionalidades nuevas**.

### Escena 7 · Protección (6:50 – 7:40)

| Plano | Grabar | Decir |
| :--- | :--- | :--- |
| 1 | App: una dosis con la ventana cerrada → solo queda **No la tomé** y el aviso del plazo | «El sistema impide los usos indebidos que pondrían en riesgo al paciente: no acepta marcar como tomada una dosis fuera de su horario…» |
| 2 | Terminal: líneas CN-23, CN-24 y CN-27 (fuera de la ventana y hora futura: rechazadas) y CN-49 (paciente dado de baja) | «…ni con una hora futura, ni registros de un paciente dado de baja.» |
| 3 | Ficha: el pie del recuadro de riesgo («… No constituye un diagnóstico») y la procedencia del modelo | «Nunca presenta un riesgo que no calculó, declara con qué datos se entrenó su modelo y recuerda que la decisión es del médico.» |
| 4 | Página **/privacidad** | «Su política de privacidad se ajusta a la Ley de Protección de Datos Personales.» |
| 5 | El pre informe abierto en la tabla de limitaciones y en el anexo de pruebas | «Y los riesgos y sus escenarios adversos están documentados en el informe.» |

**Descriptor:** **limita operaciones no autorizadas**, controla usos indebidos y aplica restricciones; **documenta los riesgos y los escenarios adversos**.

### Escena 8 · Cierre (7:40 – 8:00)

| Plano | Grabar | Decir |
| :--- | :--- | :--- |
| 1 | La salida de la última ejecución de caja negra con «59/59 conformes» | «El producto se verificó con 59 casos de caja negra, todos conformes, 282 pruebas automatizadas y el análisis de caja blanca de las funciones críticas.» |
| 2 | La ficha de P-001 con su riesgo | «Es un sistema funcional, verificado y listo para su validación con los pacientes del consultorio.» |

## 4. Lista de control de la rúbrica

Marque cada casilla al revisar el video editado.

| Criterio | Descriptor del nivel Bueno | Escena y corte |
| :--- | :--- | :--- |
| Adecuación funcional | Todas las funciones de su propósito | 1a – 1e |
| | Capacidades adicionales que aportan valor | 1b, 1c, 1d |
| | Resultados fiables y exactos | 1d |
| Eficiencia | Sin demoras críticas (< 5 s) | 2 |
| | Estable bajo carga | 2 |
| Capacidad de interacción | Intuitiva y accesible | 3.1, 3.5 |
| | Previene errores | 3.2, 3.3, 3.4 |
| | Retroalimentación clara | 3.2, 1a |
| | Documentación de ayuda | 3.6 |
| Fiabilidad | Tolera y gestiona los fallos | 4a, 4b |
| | Recuperación sin pérdida de datos | 4a |
| Seguridad | Accesos legítimos y autenticación segura | 5.1, 5.2 |
| | Protección de datos | 5.3 |
| | Roles y registro de responsables | 5.4 |
| | Resistencia a amenazas | 5.5 |
| Flexibilidad | Cambios y crecimiento sin degradar la calidad | 6 |
| Protección | Limita operaciones no autorizadas y usos indebidos | 7.1, 7.2 |
| | Riesgos y escenarios adversos documentados | 7.3 – 7.5 |

## 5. Si algo falla mientras graba

| Situación | Qué hacer |
| :--- | :--- |
| La app dice «No se pudo conectar» al abrirla | Espere unos segundos (se reintenta sola) o vuelva a grabar el corte |
| No hay alertas pendientes | Registre tres «No la tomé» seguidos con un paciente y abra Alertas |
| La dosis no ofrece «Ya la tomé» | Está fuera de la ventana: agregue un medicamento con una hora cercana a la actual |
| El emulador va lento | Grabe la app en cortes separados y únalos al editar |
| Se coló un dato sensible en pantalla | Vuelva a grabar ese corte; no lo tape con edición |
