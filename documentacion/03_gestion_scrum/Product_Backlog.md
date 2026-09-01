# Product Backlog priorizado

**Proyecto:** Sistema de soporte clínico con aprendizaje automático para prevenir
el incumplimiento terapéutico en pacientes hipertensos y diabéticos polimedicados.
**Consultorio médico Milko Ugaz Zegarra — Chiclayo.**

**Product Owner:** Dr. Milko Ugaz Zegarra (médico internista)
**Equipo de desarrollo:** Leonardo Guzmán Salazar
**Técnica de priorización:** MoSCoW
**Última actualización:** semana 4 del ciclo 2026-II

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
| RF04 | Calcular y mostrar la predicción de riesgo de incumplimiento por paciente | Must | B3 | OE3/OE5 | 3 | Pendiente |
| RF05 | Generar alertas tempranas al médico ante riesgo alto | Must | B4 | OE4 | 3 | Pendiente |
| RF06 | Explicar la predicción mediante factores influyentes (SHAP) | Should | B3 | OE3 | 3 | Pendiente |
| RF07 | Auditar la adherencia mediante panel clínico con reportes exportables | Should | B1 | OE2/OE4 | 3 | **Parcial** |
| RF08 | Enviar recordatorios de toma al paciente | Could | B4 | OE4 | 4 | Pendiente |

**Brechas del diagnóstico (OE1):** B1 ausencia de registro estructurado ·
B2 inexistencia de trazabilidad entre citas · B3 falta de analítica predictiva ·
B4 ausencia de alertas y recordatorios.

RF07 figura como **parcial**: el panel de auditoría existe con indicadores,
listado priorizado por riesgo y ficha individual, pero la exportación de
reportes queda para el Sprint 3.

---

## 3. Requisitos no funcionales

| ID | Requisito | Atributo ISO/IEC 25010 | Estado |
| :---: | :--- | :--- | :--- |
| RNF01 | Cifrado en tránsito (TLS) y en reposo (AES-256) | Seguridad | **Verificado** |
| RNF02 | Inferencia del modelo en tiempo aceptable (≤ 2 s) | Eficiencia de desempeño | Instrumentado |
| RNF03 | Interfaz usable para personal médico y adultos mayores | Usabilidad | Sprint 4 (SUS) |
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

---

## 5. Pila pendiente por sprint

**Sprint 3 (semanas 5–6)**

- Ejecutar `train_evaluate.py` sobre el dataset definitivo y seleccionar el algoritmo.
- Microservicio de inferencia y endpoint de predicción (RF04).
- Explicabilidad SHAP en la ficha del paciente (RF06).
- Alertas tempranas al médico (RF05).
- Exportación de reportes del panel (RF07).
- Endpoint agregado de resúmenes de adherencia, para evitar una petición por
  paciente en el panel.

**Sprint 4 (semanas 7–8)**

- Recordatorios locales en la app (RF08).
- Pruebas de rendimiento y carga (RNF02, RNF06).
- Pruebas de usabilidad con escala SUS (OE5).
- Verificación de atributos ISO/IEC 25010.

---

## 6. Fuera del alcance (*Won't*)

Se documentan para delimitar la investigación y como trabajo futuro:

- Prescripción electrónica y gestión del esquema farmacológico desde el panel
  (hoy el plan de tomas lo declara el paciente en su dispositivo).
- Integración con historia clínica electrónica institucional.
- Reentrenamiento automático del modelo en producción.
- Mensajería bidireccional médico–paciente.
