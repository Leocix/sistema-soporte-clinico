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

**3. Contexto Social** *(de la historia clínica o preguntado al aplicar el test de Morisky)*
*   **Nivel educativo:** [ ] Sin estudios  [ ] Primaria  [ ] Secundaria  [ ] Superior
*   **Convivencia:** [ ] Vive solo  [ ] Vive acompañado
*   **¿Un familiar o cuidador le ayuda o le recuerda la medicación?** [ ] Sí  [ ] No

**4. Enfermedades y Comorbilidades**
*   **Hipertensión Arterial (HTA):** [ ] Sí  [ ] No
*   **Diabetes Mellitus tipo 2 (DM2):** [ ] Sí  [ ] No
*   **Tiempo de enfermedad:** ____ años
*   **Comorbilidades (marque las que tenga):**
    [ ] Dislipidemia  [ ] Obesidad  [ ] Enfermedad renal crónica
    [ ] Cardiopatía isquémica  [ ] Insuficiencia cardiaca  [ ] Enfermedad cerebrovascular
    [ ] Hipotiroidismo  [ ] EPOC o asma  [ ] Artrosis  [ ] Depresión
    [ ] Otra enfermedad crónica: ______________
*   **Total de comorbilidades marcadas:** ____

**5. Variables de Tratamiento (Carga Terapéutica)**
*   **Número total de fármacos prescritos:** ____
*   **Frecuencia total de tomas diarias (Complejidad del régimen):** ____ tomas/día

**6. Variables del Sistema de Salud (Seguimiento)**
*   **Número de controles médicos programados en los últimos 6 meses:** ____
*   **Número de inasistencias a controles (Controles perdidos):** ____

**7. Variable Objetivo (Adherencia)**
*   **Puntaje Test de Morisky (obtenido mediante encuesta directa):** ____
*   **Clasificación:** [ ] Adherente (0)  [ ] Incumplimiento (1)

---

## Parte C: Captura digital de los datos

La extracción se vuelca en `Plantilla_Extraccion_Anexo_04.csv`, en esta misma
carpeta. Sus columnas son exactamente las que valida `ml-pipeline/src/preprocess.py`:
si un nombre o un valor no coincide, el script aborta indicando cuál falla, de
modo que un error de captura no llega silenciosamente al modelo.

**Valores admitidos por columna**

| Columna | Tipo | Valores admitidos |
| :--- | :--- | :--- |
| `codigo_paciente` | Texto | `P-001`, `P-002`, … (correlativo, sin datos identificatorios) |
| `edad` | Entero | 18 a 120 |
| `sexo` | Categórica | `M` · `F` |
| `nivel_educativo` | Ordinal | `sin_estudios` · `primaria` · `secundaria` · `superior` |
| `convivencia` | Categórica | `solo` · `acompanado` |
| `apoyo_familiar` | Categórica | `si` · `no` |
| `diagnostico` | Categórica | `hta` · `dm2` · `ambas` |
| `tiempo_enfermedad_anios` | Decimal | 0 a 80 (se admite `12.5`) |
| `comorbilidades` | Entero | 0 a 15: total de comorbilidades marcadas |
| `numero_farmacos` | Entero | **≥ 5** (criterio de elegibilidad) |
| `tomas_dia` | Entero | 1 a 20 |
| `controles_programados_6m` | Entero | 0 a 30 |
| `controles_perdidos_6m` | Entero | 0 a 30, nunca mayor que los programados |
| `puntaje_morisky` | Ordinal | 0 a 4 |
| `incumplimiento` | Binaria | `0` adherente · `1` incumplimiento |

**Reglas de captura**

- Todo en **minúsculas** salvo el sexo (`M` / `F`). El script normaliza, pero
  capturar de forma consistente evita revisiones posteriores.
- Una **celda vacía** es preferible a un valor inventado: el pipeline imputa los
  faltantes por mediana o moda y deja constancia del porcentaje imputado en
  `reporte_preparacion.json`. Un dato fabricado, en cambio, sesga el modelo sin
  dejar rastro.
- `incumplimiento` proviene del **patrón de respuestas** del test de
  Morisky-Green (Anexo n.° 05), no de un umbral automático sobre el puntaje.
- Un paciente por fila. Si una historia clínica no cumple los tres criterios de
  elegibilidad de la Parte A, no se incluye.

**Verificación antes de modelar**

```bash
python src/preprocess.py --entrada ../documentacion/02_instrumentos/Plantilla_Extraccion_Anexo_04.csv
```

El script informa cuántas filas sobrevivieron a la limpieza, qué valores quedaron
fuera de rango y qué porcentaje de celdas hubo que imputar. Conviene ejecutarlo
con las primeras diez fichas capturadas, antes de completar las cincuenta: si hay
un error sistemático de captura, aparece ahí y no cuando ya no hay tiempo.
