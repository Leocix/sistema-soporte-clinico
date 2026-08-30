# Ficha de Recolección de Datos Clínicos (Anexo 04)

**Objetivo:** Extraer variables clínicas y sociodemográficas de las historias clínicas de pacientes hipertensos y diabéticos polimedicados (≥5 fármacos), garantizando la anonimización de la información para el entrenamiento del modelo de Machine Learning.

## Parte A: Criterios de Elegibilidad (Filtro)
- [ ] ¿Diagnóstico de HTA o DM2 confirmado?
- [ ] ¿Polimedicación (≥ 5 fármacos prescritos simultáneamente)?
- [ ] ¿Historia clínica con antigüedad mínima de 6 meses?
*Si todas las respuestas son afirmativas, proceder con la extracción.*

## Parte B: Extracción de Variables
**1. Identificación Anonimizada**
*   **Código de Paciente:** P-____ (Ej. P-001)

**2. Variables Sociodemográficas**
*   **Edad:** ____ años
*   **Sexo:** [ ] Masculino  [ ] Femenino

**3. Enfermedades y Comorbilidades**
*   **Hipertensión Arterial (HTA):** [ ] Sí  [ ] No
*   **Diabetes Mellitus tipo 2 (DM2):** [ ] Sí  [ ] No
*   **Número de comorbilidades adicionales:** ____

**4. Variables de Tratamiento (Carga Terapéutica)**
*   **Número total de fármacos prescritos:** ____
*   **Frecuencia total de tomas diarias (Complejidad del régimen):** ____ tomas/día

**5. Variables del Sistema de Salud (Seguimiento)**
*   **Número de controles médicos programados en los últimos 6 meses:** ____
*   **Número de inasistencias a controles (Controles perdidos):** ____

**6. Variable Objetivo (Adherencia)**
*   **Puntaje Test de Morisky (obtenido mediante encuesta directa):** ____
*   **Clasificación:** [ ] Adherente (0)  [ ] Incumplimiento (1)