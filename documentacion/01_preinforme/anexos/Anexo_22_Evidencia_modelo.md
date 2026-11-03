# Evidencia del modelo: comparación de algoritmos y ficha de procedencia

Salidas del pipeline de aprendizaje automático tal como las produce el código del repositorio. La comparación sobre la ENDES se reproduce con `python src/endes.py` y `python src/train_evaluate.py --perfil endes`; la corrida de verificación, con `python src/train_evaluate.py`.

## Comparación sobre la ENDES 2014-2017 (datos reales)

Validación cruzada estratificada de 5 pliegues; media ± desviación. 8 422 pacientes: 6 737 de entrenamiento y 1 685 de prueba; 7 267 adherentes y 1 155 con incumplimiento.

| Algoritmo | Exactitud | Sensibilidad | Especificidad | F1-score | AUCROC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Random Forest (seleccionado)** | 0,635 ± 0,011 | 0,450 ± 0,054 | 0,664 ± 0,021 | 0,252 ± 0,018 | 0,591 ± 0,018 |
| XGBoost | 0,825 ± 0,009 | 0,097 ± 0,017 | 0,941 ± 0,012 | 0,132 ± 0,018 | 0,589 ± 0,024 |
| Regresión Logística | 0,545 ± 0,007 | 0,590 ± 0,030 | 0,538 ± 0,012 | 0,262 ± 0,008 | 0,588 ± 0,017 |
| SVM (RBF) | 0,519 ± 0,025 | 0,622 ± 0,049 | 0,503 ± 0,036 | 0,262 ± 0,009 | 0,586 ± 0,021 |

| Contraste | Resultado |
| :--- | :--- |
| DeLong, Random Forest frente a XGBoost (predicciones fuera de pliegue) | AUCROC 0,5904 frente a 0,5885; diferencia +0,0019; IC95 −0,0093 a 0,0131; *p* = 0,742. Sin diferencia: decide la sensibilidad |
| McNemar con umbral de 0,5 (complementario) | 2 034 pacientes discordantes (375 solo Random Forest, 1 659 solo XGBoost); χ² = 809,29; *p* < 0,001 |
| AUCROC del elegido en la prueba reservada | 0,571; IC95 0,532 a 0,610; *p* frente al azar = 0,0002 |
| Métricas del elegido en la prueba reservada | Exactitud 0,626 · sensibilidad 0,455 · especificidad 0,653 · F1-score 0,250 |
| Cumple la meta de AUCROC ≥ 0,80 | No |

## Fichas de procedencia de los modelos

Cada modelo se guarda con una ficha que el microservicio publica junto a cada predicción, para que nadie confunda un modelo de demostración con uno entrenado con pacientes reales.

| Dato | Modelo en servicio | Modelo de la ENDES |
| :--- | :--- | :--- |
| Algoritmo | SVM (RBF) | Random Forest |
| Hiperparámetros | `C=1`, `gamma=0,01` | `n_estimators=200`, `max_depth=8`, `min_samples_leaf=5` |
| Fecha de entrenamiento | 15/09/2026 | 29/09/2026 |
| Origen de los datos | Conjunto de demostración simulado | ENDES (INEI), microdatos públicos |
| Datos reales | **No** | **Sí** |
| Filas de entrenamiento | 320 | 6 737 |
| AUCROC en validación cruzada | 0,856 | 0,591 |
| Sensibilidad en validación cruzada | 0,794 | 0,450 |
| AUCROC en la prueba reservada | 0,809 | 0,571 |
| Semilla | 42 | 42 |

## Variables más influyentes (importancia por permutación)

| Modelo en servicio | Importancia | Modelo de la ENDES | Importancia |
| :--- | :---: | :--- | :---: |
| Tasa de inasistencia | 0,087 | Edad | 0,035 |
| Número de fármacos | 0,056 | Tiempo de enfermedad | 0,026 |
| Controles perdidos | 0,044 | Nivel educativo | 0,009 |
| Carga terapéutica | 0,028 | Diagnóstico | 0,006 |
| Apoyo familiar | 0,018 | Cronicidad relativa | 0,005 |
| Tomas por día | 0,011 | Comorbilidades | −0,0001 |

Las variables que más pesan en el modelo en servicio —inasistencia, número de fármacos, controles perdidos— son precisamente las que la ENDES no registra. Esto no demuestra que su ausencia explique el bajo desempeño sobre la encuesta, porque el modelo en servicio se entrenó con datos simulados; es la razón por la que el apartado 1.1.8.e plantea el contraste anidado sobre los pacientes del consultorio.
