# Microservicio de inferencia — CDSS Adherencia

Carga el modelo predictivo y calcula, para cada paciente, la **probabilidad de
incumplimiento** (RF04) y su **explicación individual con SHAP** (RF06). Es un
servicio independiente del API central, como establece la arquitectura de
microservicios del proyecto: se puede reentrenar, reemplazar o escalar sin tocar
la parte transaccional (RNF06).

Solo lo consume el API central, que le envía las variables del Anexo n.° 04 con
el código anonimizado y la clave de servicio. Nunca recibe nombres, documentos
ni contactos.

## Rutas

| Método | Ruta | Qué devuelve |
| :--- | :--- | :--- |
| `GET` | `/health` | Disponibilidad (pública, para Render) |
| `GET` | `/modelo` | Algoritmo, fecha, procedencia de los datos y AUCROC |
| `POST` | `/predicciones` | Probabilidad, nivel, variables imputadas y contribuciones SHAP |
| `POST` | `/predicciones/lote` | Probabilidad y nivel de varios pacientes, sin SHAP (reportes) |

Todas salvo `/health` exigen la cabecera `X-Clave-Servicio`.

## Cómo se explica cada predicción

SHAP reparte la diferencia entre la probabilidad del paciente y la del
**paciente de referencia** entre sus variables: el valor base más la suma de las
contribuciones da exactamente la probabilidad. Una contribución positiva empuja
hacia el incumplimiento; una negativa, en contra.

- Se usa el explicador por permutaciones de `shap`, agnóstico al algoritmo (el
  modelo seleccionado es un SVM, sin coeficientes interpretables).
- La referencia son 12 centroides de k-medias del conjunto de entrenamiento,
  guardados en `risk_model_v1.json` por `ml-pipeline`. No son fichas reales.
- Las columnas codificadas de una variable (`convivencia_solo`) se suman para
  devolver una contribución por variable del Anexo n.° 04.

Verificación: la suma cuadra con la probabilidad (prueba automatizada) y los
valores coinciden con el explicador *Kernel* de SHAP (correlación 0,993). Con el
servicio activo, una explicación tarda unos 90 ms.

## Ejecutar en local

```bash
pip install -r requirements.txt
uvicorn app.main:app --port 8001
```

Variables: `CLAVE_SERVICIO` (la misma que `ML_SERVICE_CLAVE` en el API),
`MODEL_PATH` (por defecto `../ml-pipeline/models/risk_model_v1.pkl`) y
`ENVIRONMENT`. En producción el servicio no arranca sin clave.

## Pruebas

```bash
python -m pytest -q
```

13 casos contra el modelo realmente desplegado: contrato REST y clave de
servicio, predicción con fichas completas e incompletas, lote, propiedad aditiva
de SHAP, reproducibilidad y versiones de las librerías del artefacto.
