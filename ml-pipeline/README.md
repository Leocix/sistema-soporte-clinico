# Pipeline CRISP-DM — modelo predictivo de incumplimiento

Preparación de datos y comparación de algoritmos para el OE3: determinar el
algoritmo con mayor capacidad predictiva del incumplimiento terapéutico en
pacientes hipertensos y diabéticos polimedicados.

## Instalación

```bash
pip install -r requirements.txt
```

## 1. Preparación de datos

```bash
python src/preprocess.py --entrada data/raw/dataset_clinico.csv
```

Valida el esquema contra el Anexo n.° 04, depura, imputa nulos, deriva
características, parte de forma estratificada y balancea con SMOTE. Produce
`data/processed/train_balanceado.csv`, `test.csv`, el preprocesador
serializado y `reporte_preparacion.json` con la trazabilidad de cada
transformación.

## 2. Comparación de algoritmos

```bash
python src/train_evaluate.py --entrada data/raw/dataset_clinico.csv
```

Compara Regresión Logística, Random Forest, XGBoost y SVM con validación
cruzada estratificada de 5 pliegues. Produce
`data/processed/tabla_comparativa.md` (lista para el pre informe),
`reporte_modelado.json`, `models/risk_model_v1.pkl` y su ficha
`risk_model_v1.json`, que incluye los centroides de referencia que usa el
microservicio (`ml-service/`) para la explicación SHAP.

Opciones útiles:

```bash
python src/train_evaluate.py --sin-busqueda
```

Omite el ajuste de hiperparámetros; útil para una pasada rápida.

```bash
python src/train_evaluate.py --generar-muestra 300
```

Genera datos sintéticos y ejecuta sobre ellos. **Solo sirve para comprobar que
el flujo corre**: ningún resultado obtenido así puede reportarse como hallazgo
de la investigación.

## 3. Conjunto externo: ENDES (INEI)

Mientras se completa la extracción documental, la comparación del OE3 puede
ejecutarse sobre datos reales usando los microdatos públicos de la Encuesta
Demográfica y de Salud Familiar:

```bash
python src/endes.py
python src/train_evaluate.py --perfil endes --entrada data/raw/endes_adherencia.csv
```

`endes.py` descarga del INEI el módulo de salud y el del hogar de cada año,
selecciona a quienes tienen diagnóstico médico de hipertensión o diabetes y
declararon si tomaron los medicamentos como se los indicó el médico, y traduce
las variables al esquema que el resto del pipeline ya lee. Los ZIP quedan en
`data/externo/endes/` y no se vuelven a descargar.

**Lo que este conjunto no es.** La encuesta no registra el número de fármacos,
las tomas diarias, los controles programados ni el apoyo familiar; tampoco
permite aplicar el criterio de polimedicación. El perfil `endes` recorta el
esquema a las nueve variables disponibles y escribe sus artefactos con el
sufijo `_endes`, de modo que `risk_model_v1.pkl` —el que carga el
microservicio— nunca se sobrescribe. El modelo que sale de aquí describe a la
población nacional encuestada, **no** a la del consultorio, y así debe
reportarse: sirve para validar la metodología de comparación sobre datos reales
y para fijar una línea base contrastable, no para sustituir al modelo del
estudio.

## Dos decisiones que sostienen la validez

**SMOTE va dentro de la validación cruzada, no antes.** Balancear el conjunto
de entrenamiento completo y luego dividirlo en pliegues reparte muestras
sintéticas —interpoladas entre casos reales— entre entrenamiento y validación,
de modo que el modelo evalúa casos derivados de los que ya vio. El AUCROC
resultante sería optimista y la comparación entre algoritmos, inválida. Por eso
`train_evaluate.py` parte del dataset crudo y arma un pipeline `imblearn` que
`cross_validate` reajusta entero en cada pliegue.

**El puntaje de Morisky se excluye de los predictores.** Es la fuente directa
de la etiqueta: incorporarlo produciría métricas artificialmente perfectas que
no reflejarían capacidad predictiva alguna.

## Criterio de selección

Se elige el mayor AUCROC, con la meta de ≥ 0,80 fijada en la hipótesis. Ante un
empate estadístico prevalece la **sensibilidad**: el error clínicamente costoso
es el falso negativo, un paciente en riesgo que el sistema no detecta y que por
tanto no recibe la alerta temprana.

**Qué prueba responde a qué pregunta.** El criterio es el AUCROC, que mide cómo
ordena el modelo a los pacientes por riesgo sin depender de un umbral. Por eso
la diferencia entre los dos mejores se contrasta con la **prueba de DeLong**,
que compara dos AUCROC medidas sobre los mismos pacientes. La prueba de
**McNemar** se reporta aparte: compara aciertos con el umbral de 0,5 y responde
otra pregunta —si los dos modelos alertarían sobre los mismos pacientes—, de
modo que no decide la selección.

Ambos contrastes se calculan sobre las **predicciones fuera de pliegue del
entrenamiento**. El conjunto de prueba no interviene en la selección: solo
aporta, al final, el AUCROC del modelo elegido con su intervalo de confianza
al 95 % y su contraste frente al azar.

## Nota sobre los datos

`data/` está excluido del control de versiones. Los datos clínicos reales se
extraen con la ficha del Anexo n.° 04 de forma anonimizada y no se versionan.
