# Guion de la demostración del producto acreditable

Sistema de soporte clínico con aprendizaje automático — consultorio médico
Milko Ugaz Zegarra.

Este guion recorre el **escenario principal completo** y, en cada paso, indica
el requisito y el objetivo al que responde. Está pensado para ejecutarse de
principio a fin en unos 12 minutos, sin depender de funciones no implementadas.

---

## 0. Antes de empezar (5 minutos antes, imprescindible)

El plan gratuito suspende los servicios tras 15 minutos sin tráfico y la
primera petición tarda hasta 50 segundos. **Despiértelos antes de la
demostración**, no durante:

```bash
python backend-api/scripts/despertar.py
```

Debe responder que los tres servicios están listos. Si alguno no responde,
consulte «Si el despliegue falla» en `DESPLIEGUE.md`.

Tenga abiertas dos ventanas:

| Ventana | Qué mostrar |
| :--- | :--- |
| Navegador | Panel médico, con la sesión ya iniciada |
| Teléfono o emulador | Aplicación del paciente, con la sesión ya iniciada |

---

## 1. Qué resuelve el producto (1 minuto)

> «El consultorio se entera de que un paciente dejó su tratamiento cuando ya se
> descompensó. Este sistema lo anticipa: registra la toma real desde el
> celular, predice el riesgo de incumplimiento con un modelo entrenado sobre
> las variables del Anexo n.° 04 y avisa al médico antes del próximo control.»

Muestre el **panel de auditoría** con la lista de pacientes ordenada por
prioridad clínica. *(RF02, RF07 · OE4)*

---

## 2. Alta del paciente y acceso a la aplicación (2 minutos)

| Paso | Qué mostrar | Requisito · Objetivo |
| :--- | :--- | :--- |
| 2.1 | **Registrar paciente**: complete la ficha con las variables del Anexo n.° 04 | RF02 · OE4 |
| 2.2 | Escriba 3 fármacos y muestre el aviso: el estudio solo admite pacientes polimedicados (≥ 5) | RF02 · OE2 |
| 2.3 | Escriba más controles perdidos que programados y muestre el error | RF02 · OE2 |
| 2.4 | Corrija y guarde: aparece la confirmación «Paciente P-00N registrado» | RF02 |
| 2.5 | En la ficha, **Generar acceso móvil**: se muestra una contraseña temporal, una sola vez | RF01, RF02 |

> El paso 2.2 y el 2.3 son la demostración de **control de errores previsibles**:
> el sistema no acepta datos que invalidarían el conjunto de entrenamiento.

---

## 3. El paciente registra su toma (2 minutos)

| Paso | Qué mostrar | Requisito · Objetivo |
| :--- | :--- | :--- |
| 3.1 | En el teléfono, pantalla **Hoy** con las tomas del día | RF03 · OE4 |
| 3.2 | Marcar una toma como cumplida; aparece confirmada | RF03 |
| 3.3 | **Active el modo avión** y marque otra toma: la app la guarda y avisa de que se enviará | RF03 · RNF04 |
| 3.4 | Desactive el modo avión: la toma se sincroniza sola, sin duplicarse | RF03 |
| 3.5 | Pantalla **Medicinas**: recordatorio programado en el teléfono | RF08 |
| 3.6 | Pantalla **Familia**: código de invitación de un solo uso | RF09 |

> El paso 3.3 demuestra que el núcleo funcional **se conserva sin conexión**:
> es el escenario en el que más falta hace, y la razón de la cola local.

---

## 4. El familiar corrobora (1 minuto)

Entre como el familiar (cuenta `rosa.d-001@ejemplo.pe` en la demostración) y
confirme una toma cumplida. En el panel, la columna **Testigo** del historial
pasa de «Autorreporte» a «Familiar». *(RF09 · OE4)*

---

## 5. El modelo: predicción y explicación (3 minutos)

| Paso | Qué mostrar | Requisito · Objetivo |
| :--- | :--- | :--- |
| 5.1 | Abra la ficha del paciente: tarjeta **Riesgo predicho por el modelo**, con la probabilidad y el nivel | RF04 · OE3 |
| 5.2 | Lea el aviso de procedencia: el modelo está entrenado con el conjunto de demostración | RF04 · OE3 |
| 5.3 | **Por qué este paciente tiene este riesgo**: las barras rojas suben el riesgo y las verdes lo bajan | RF06 · OE3 |
| 5.4 | Explique la propiedad: la probabilidad del paciente de referencia más las contribuciones da exactamente la probabilidad del paciente | RF06 |
| 5.5 | Compare con **Riesgo observado**: uno resume lo que el paciente hizo; el otro anticipa lo que hará | RF04, RF07 |

> Si el jurado pregunta por la validez: el protocolo compara cuatro algoritmos
> con validación cruzada de 5 pliegues y prueba de McNemar; el modelo en
> servicio es el ganador de esa comparación, serializado con su preparación.

---

## 6. La alerta temprana (1 minuto)

| Paso | Qué mostrar | Requisito · Objetivo |
| :--- | :--- | :--- |
| 6.1 | Sección **Alertas tempranas**, con el contador de pendientes | RF05 · OE4 |
| 6.2 | Una alerta con su motivo y la cifra que la sustenta | RF05 |
| 6.3 | **Registrar lo que hice** → escriba la nota → **Atendida** | RF05 |
| 6.4 | La alerta desaparece de pendientes y queda en «Atendidas» con su nota | RF05 |

---

## 7. Reportes y exportación (1 minuto)

Sección **Reportes generales**: indicadores de todos los pacientes,
distribución del riesgo observado y predicho, comorbilidades y motivos de
omisión más frecuentes. Pulse **Exportar CSV** y abra el archivo. *(RF07 · OE4)*

---

## 8. Lo que el sistema no permite (1 minuto)

Esta parte es tan importante como la anterior: son datos de salud.

| Prueba | Resultado esperado |
| :--- | :--- |
| Copie la dirección de la ficha de un paciente y ábrala con la sesión de **otro médico** | El sistema responde que no tiene permiso (403) |
| Entre como paciente e intente abrir el panel del médico | El sistema lo impide (403) |
| Cierre sesión y abra una dirección del panel | Vuelve al acceso |

> Con la sesión del médico abierta, muestre también que el historial del
> paciente permanece tras recargar la página: la información **se conserva**.

---

## 9. Rendimiento (30 segundos)

Muestre la tabla de la prueba de carga del pre informe (Tabla 23) o ejecútela
en vivo:

```bash
python backend-api/scripts/prueba_carga.py --url <URL del API> --correo <medico> --usuarios 10
```

Con 10 usuarios simultáneos, todas las operaciones responden en menos de
1,4 segundos; la meta del RNF02 es 2 segundos.

---

## 10. Si algo falla durante la demostración

| Problema | Qué decir y qué hacer |
| :--- | :--- |
| La primera pantalla tarda | «El plan gratuito suspende el servicio sin tráfico»; espere: la app reintenta sola |
| La ficha no muestra el riesgo | El microservicio de inferencia está dormido; el resto del sistema sigue operando —es el comportamiento previsto— y se recupera al despertarlo |
| Un dato no se guarda | Muestre el mensaje de validación: el sistema rechaza datos incoherentes a propósito |

---

## Correspondencia con los objetivos

| Objetivo | Dónde se demuestra |
| :--- | :--- |
| **OE1** Diagnóstico y factores de incumplimiento | Variables de la ficha (paso 2.1), agrupadas por las dimensiones de la OMS |
| **OE2** Requisitos y arquitectura | Validaciones (2.2, 2.3), separación panel / API / microservicio |
| **OE3** Algoritmo con mayor capacidad predictiva | Predicción y explicación (paso 5) |
| **OE4** Sistema construido | Todo el recorrido: pasos 2 a 7 |
| **OE5** Usabilidad | Pendiente: se evalúa con la escala SUS sobre este mismo recorrido |
