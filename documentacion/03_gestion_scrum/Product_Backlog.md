# Product Backlog priorizado

**Proyecto:** Sistema de soporte clínico con aprendizaje automático para prevenir
el incumplimiento terapéutico en pacientes hipertensos y diabéticos polimedicados.
**Consultorio médico Milko Ugaz Zegarra — Chiclayo.**

**Product Owner:** Dr. Milko Ugaz Zegarra (médico internista)
**Equipo de desarrollo:** Leonardo Guzmán Salazar
**Técnica de priorización:** MoSCoW
**Última actualización:** semana 7 del ciclo 2026-II (avance al 90 %)

---

## 1. Criterio de priorización

Las prioridades no se asignaron por dificultad técnica sino por su relación con
las brechas del diagnóstico (OE1). Un requisito es **Must** cuando sin él el
sistema no resuelve el problema que motivó la investigación: la ausencia de
trazabilidad digital de la adherencia y la imposibilidad de anticipar el
incumplimiento.

| Prioridad | Significado en este proyecto |
| :--- | :--- |
| **Must** | Sin él la hipótesis no puede contrastarse |
| **Should** | Aporta valor clínico sustancial; su ausencia no invalida el estudio |
| **Could** | Mejora la experiencia; se implementa si el cronograma lo permite |
| **Won't** | Fuera del alcance de esta tesis; se documenta como trabajo futuro |

---

## 2. Pila de producto

| ID | Historia / requisito | Prioridad | Brecha | Objetivo | Sprint | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| RF01 | Autenticar y autorizar a médicos y pacientes con perfiles diferenciados | Must | — | OE2/OE4 | 1 | **Terminado** |
| RF02 | Registrar y gestionar pacientes polimedicados y su esquema farmacológico | Must | B2 | OE4 | 2 | **Terminado** |
| RF03 | Registrar la toma de medicamentos desde la app móvil del paciente | Must | B1, B2 | OE4 | 2 | **Terminado** |
| RF04 | Calcular y mostrar la predicción de riesgo de incumplimiento por paciente | Must | B3 | OE3/OE5 | 3 | **Terminado** |
| RF05 | Generar alertas tempranas al médico ante riesgo alto | Must | B4 | OE4 | 3 | **Terminado** |
| RF06 | Explicar la predicción mediante factores influyentes (SHAP) | Should | B3 | OE3 | 3 | **Terminado** |
| RF07 | Auditar la adherencia mediante panel clínico con reportes exportables | Should | B1 | OE2/OE4 | 2–3 | **Terminado** |
| RF08 | Enviar recordatorios de toma al paciente | Could | B4 | OE4 | 3 | **Terminado** |
| RF09 | Corroborar la toma mediante un grupo familiar de acompañamiento | Should | B1 | OE4 | 3 | **Terminado** |
| RF10 | Restablecer la contraseña mediante un enlace enviado por correo | Should | B4 | OE4 | 3 | **Terminado** |

**Brechas del diagnóstico (OE1):** B1 ausencia de registro estructurado ·
B2 inexistencia de trazabilidad entre citas · B3 falta de analítica predictiva ·
B4 ausencia de alertas y recordatorios.

RF06 quedó **terminado** al 65 %: el microservicio de inferencia calcula con SHAP cuánto aporta cada variable al riesgo de cada paciente, y la ficha lo muestra con barras que suben o bajan la probabilidad.

RF07 quedó **terminado** en el Sprint 3: al panel de auditoría del Sprint 2 se
sumó la sección de reportes generales, con indicadores de todos los pacientes,
distribución del riesgo observado y predicho, y exportación a CSV.

**Refinamiento de las variables de la ficha (RF02, Sprint 3).** Al tratarse de
una clínica privada, el nivel socioeconómico, el aseguramiento y la zona de
residencia casi no varían entre pacientes y no ayudan a distinguir quién
incumple. Se reemplazaron por nivel educativo, convivencia y apoyo familiar en
la medicación. Las comorbilidades pasaron de un número a una lista de
enfermedades; el modelo usa su total.

RF10 tampoco figuraba en la pila inicial, y su origen es una observación de
usabilidad: la pantalla de acceso remitía al consultorio a quien olvidara su
contraseña. Para una población de adultos mayores, buena parte de ella rural,
eso convierte un olvido en un desplazamiento; y para el consultorio, en una
intervención manual sobre la base de datos. La recuperación por correo elimina
las dos cosas. Es **Should** y no **Must** porque el sistema funciona sin ella,
pero su ausencia degrada RNF03 de forma medible en la escala SUS.

RF09 no estaba en la pila inicial. Se incorporó al detectar, durante la
construcción de RF03, que la brecha B1 quedaba solo a medias: el sistema
sustituye el recuerdo verbal por una traza digital fechada, pero la fuente de
esa traza sigue siendo únicamente el paciente. La corroboración por un
conviviente añade un segundo testigo al evento y permite distinguir, en el
análisis, las tomas respaldadas por dos personas de las que solo tienen la
palabra del paciente. Se clasifica como **Should**: la hipótesis puede
contrastarse sin ella, pero la calidad de la evidencia mejora con ella.

---

## 3. Requisitos no funcionales

| ID | Requisito | Atributo ISO/IEC 25010 | Estado |
| :---: | :--- | :--- | :--- |
| RNF01 | Cifrado en tránsito (TLS) y en reposo (AES-256) | Seguridad | **Verificado** |
| RNF01 | Credenciales y enlaces de recuperación persistidos solo como resumen | Seguridad | **Verificado** |
| RNF02 | Inferencia del modelo en tiempo aceptable (≤ 2 s) | Eficiencia de desempeño | Instrumentado |
| RNF03 | Interfaz usable para personal médico y adultos mayores | Usabilidad | Barra inferior rotulada; medición SUS en el Sprint 4 |
| RNF04 | Disponibilidad continua para la consulta clínica | Fiabilidad | **Verificado** |
| RNF05 | Código modular y mantenible | Mantenibilidad | **Verificado** |
| RNF06 | Escalado ante mayor concurrencia | Eficiencia / Portabilidad | Arquitectura preparada |

---

## 4. Historias de usuario del escenario principal

### HU01 — Acceso diferenciado por perfil

> Como **médico o paciente**, quiero iniciar sesión con mi perfil, para acceder
> solo a la información que me corresponde.

**Criterios de aceptación**

- El acceso se concede únicamente con credenciales válidas **y** perfil coincidente.
- Un mensaje de error idéntico para credencial inexistente, contraseña incorrecta
  y perfil equivocado, de modo que no se puedan enumerar usuarios registrados.
- El token de sesión expira.

**Estado:** terminado · Verificado en `tests/test_pacientes.py` y `test_adherencia.py`.

### HU02 — Gestión del paciente polimedicado

> Como **médico**, quiero registrar y actualizar la ficha del paciente
> polimedicado y su esquema farmacológico, para mantener trazable su carga
> terapéutica.

**Criterios de aceptación**

- El alta y la edición quedan persistidas y consultables.
- Se rechaza el alta de un paciente con menos de cinco fármacos.
- Un médico solo accede a los pacientes que tiene a su cargo.
- La baja es lógica: el historial permanece disponible para el análisis.

**Estado:** terminado · 8 pruebas.

### HU03 — Registro de la toma desde el móvil

> Como **paciente**, quiero registrar desde mi celular cada toma de medicamento,
> para que mi médico conozca mi cumplimiento real entre citas.

**Criterios de aceptación**

- Cada toma queda registrada y sincronizada.
- Un reintento de envío tras pérdida de conectividad no duplica el evento.
- Una toma marcada como cumplida exige la hora real; una omitida no la admite.
- El paciente no puede registrar tomas de un tercero.

**Estado:** terminado · 12 pruebas en el API y 14 en la aplicación.

### HU04 — Corroboración de la toma por un familiar

> Como **paciente**, quiero que un familiar mío pueda confirmar que tomé mi
> medicación, para que el registro no dependa solo de mi palabra.

**Criterios de aceptación**

- Solo el paciente invita, y puede retirar a cualquier miembro cuando quiera.
- El código de invitación es de un solo uso y caduca a los siete días.
- Sin un código vigente no se crea ninguna cuenta: no hay registro abierto.
- El acompañante solo corrobora tomas que el paciente reportó como cumplidas,
  de los pacientes que acompaña y dentro de las 48 horas siguientes.
- El acompañante no accede a la ficha clínica ni puede registrar tomas.

**Estado:** terminado · 19 pruebas en el API y 7 en la aplicación.

### HU05 — Recuperación del acceso

> Como **usuario del sistema**, quiero recuperar mi contraseña desde mi propio
> teléfono, para no tener que acercarme al consultorio por un olvido.

**Criterios de aceptación**

- La respuesta es idéntica exista o no la cuenta, de modo que la ruta no
  permita averiguar qué direcciones están registradas.
- El enlace caduca a los treinta minutos y solo puede usarse una vez.
- Pedir un enlace nuevo anula los anteriores que siguieran sin usar.
- Del enlace se persiste únicamente su resumen SHA-256.
- Sin servidor de correo configurado, el sistema lo dice y remite al
  consultorio en lugar de simular un envío.

**Estado:** terminado · 13 pruebas en el API y 3 en la aplicación.

---

## 4 bis. Dónde vive cada artefacto

Para que el repositorio y la memoria no se contradigan:

| Artefacto | Este archivo | Pre informe |
| :--- | :--- | :--- |
| Product Backlog general | Sección 2 (pila viva, se edita) | Apartado 1.1.2, Tabla 5 (corte del 50 %) |
| Sprint Backlog de cada sprint | — | Apartados 1.1.3 a 1.1.6, Tablas 6, 11, 17 y 21 |
| Registro de incidencias | — | Tablas 10, 16 y 20; consolidado en 1.1.7, Tabla 22 |
| Actas de ceremonias | `Actas_Sprint.md` | Resumen en el cierre de cada sprint |

Este archivo es la **pila viva**: se edita al refinar. El pre informe congela el
estado al corte que evidencia y no debe editarse para reflejar cambios
posteriores.

---

## 5. Pila pendiente por sprint

**Sprint 3 (semanas 5–6)**

- Ejecutar `train_evaluate.py` sobre las historias clínicas reales y confirmar el algoritmo.

**Sprint 4 (semanas 7–8)**

- Pruebas de usabilidad con la escala SUS (OE5): requiere al médico y a una
  muestra de pacientes.
- Ejecución de la comparación de algoritmos sobre las historias clínicas
  reales, cuando concluya la extracción del Anexo n.° 04.

Ya ejecutados en este sprint: prueba de rendimiento y carga (RNF02, RNF06),
verificación de los atributos ISO/IEC 25010, guion de demostración y
consolidación del repositorio.

---

## 6. Fuera del alcance (*Won't*)

Se documentan para delimitar la investigación y como trabajo futuro:

- Prescripción electrónica y gestión del esquema farmacológico desde el panel
  (hoy el plan de tomas lo declara el paciente en su dispositivo).
- Integración con historia clínica electrónica institucional.
- Reentrenamiento automático del modelo en producción.
- Mensajería bidireccional médico–paciente.
