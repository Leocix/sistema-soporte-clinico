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
`reporte_modelado.json` y `models/risk_model_v1.pkl`.

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
tanto no recibe la alerta temprana. El contraste entre los dos mejores modelos
usa la prueba de McNemar, en su versión binomial exacta cuando hay pocos casos
discordantes.

## Nota sobre los datos

`data/` está excluido del control de versiones. Los datos clínicos reales se
extraen con la ficha del Anexo n.° 04 de forma anonimizada y no se versionan.
