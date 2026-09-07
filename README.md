# Sistema de soporte clínico con aprendizaje automático

Prevención del incumplimiento terapéutico en pacientes hipertensos y diabéticos
polimedicados del consultorio médico Milko Ugaz Zegarra, Chiclayo.

Producto acreditable de tesis — Escuela de Ingeniería de Sistemas y Computación,
Universidad Católica Santo Toribio de Mogrovejo (USAT), ciclo 2026-II.
Autor: **Leonardo Guzmán Salazar**.

## Qué resuelve

El seguimiento de la adherencia en el consultorio se hace hoy por autorreporte
verbal durante la consulta: no hay registro digital del consumo real entre
citas, y el incumplimiento se detecta de forma reactiva, cuando el paciente ya
presenta una descompensación. El sistema sustituye ese vacío por una traza
digital de cada toma y, sobre ella, un modelo predictivo que anticipa el riesgo
antes de la cita.

## Componentes

| Directorio | Componente | Estado |
| :--- | :--- | :--- |
| [`backend-api/`](backend-api/) | API Gateway (FastAPI + PostgreSQL) | RF01–RF03 operativos |
| [`frontend-web/`](frontend-web/) | Panel médico (React + Vite) | Acceso, auditoría y ficha clínica |
| [`app-movil/`](app-movil/) | App del paciente y su familia (Flutter) | Acceso, registro de tomas sin conexión, alertas y grupo familiar |
| [`ml-pipeline/`](ml-pipeline/) | Pipeline CRISP-DM | Preparación, comparación de algoritmos y modelo en servicio |
| [`documentacion/`](documentacion/) | Evidencias académicas USAT | Pre informe al 50 % |

## Requisitos funcionales

| ID | Requisito | Prioridad | Estado |
| :---: | :--- | :---: | :--- |
| RF01 | Autenticación y autorización por perfil (médico / paciente) | Must | Implementado |
| RF02 | Gestión de pacientes polimedicados y esquema farmacológico | Must | Implementado |
| RF03 | Registro de la toma de medicamentos desde la app móvil | Must | Implementado |
| RF04 | Predicción del riesgo de incumplimiento | Must | Implementado |
| RF05 | Alertas tempranas al médico | Must | Sprint 3 |
| RF06 | Explicabilidad de la predicción (SHAP) | Should | Parcial: importancia global |
| RF07 | Panel de auditoría con reportes exportables | Should | Parcial |
| RF08 | Recordatorios de toma al paciente | Could | Implementado |
| RF09 | Corroboración de la toma por el grupo familiar | Should | Implementado |

## Puesta en marcha

Requiere Python 3.12+, Node 20+ y una base PostgreSQL (o SQLite en local).

```bash
cd backend-api && pip install -r requirements.txt && alembic upgrade head && python run.py
```

```bash
cd frontend-web && npm install && npm run dev
```

Copia los `.env.example` de cada componente como `.env` antes de arrancar.
Detalle completo en [`backend-api/README.md`](backend-api/README.md),
[`frontend-web/README.md`](frontend-web/README.md) y, para el despliegue en
Aiven, Render y Vercel, en [`DESPLIEGUE.md`](DESPLIEGUE.md).

## Pruebas

```bash
cd backend-api && python -m pytest -q
```

```bash
cd app-movil && flutter test
```

## Metodología

SCRUM integrado con CRISP-DM: las fases de CRISP-DM se ejecutan como sprints
especializados dentro del flujo iterativo, sincronizando los entregables de
software con los del modelo predictivo (enfoque MLOps).

## Grupo familiar

Toda la traza de adherencia del sistema es autorreporte: el paciente marca su
propia toma. Es una mejora sustancial frente al recuerdo verbal en consulta,
pero conserva el sesgo del autorreporte. El paciente puede invitar hasta cinco
familiares con un código de un solo uso; el acompañante corrobora desde su
propio teléfono las dosis que el paciente ya reportó, dentro de una ventana de
48 horas.

El acompañante **no** puede registrar tomas, cambiar su estado ni ver la ficha
clínica: solo da fe de lo que el paciente declaró. La invitación es además la
única vía de alta de cuentas del sistema; no existe registro abierto.

## Nota sobre los datos

Los datos clínicos se almacenan seudonimizados: el código `P-0NN` es la única
clave que viaja al pipeline de aprendizaje automático. Los pacientes de la
serie `D-0NN` que genera `scripts/seed.py --demo` son **ficticios** y no deben
incluirse en el dataset de entrenamiento ni en los resultados de la
investigación. El directorio `ml-pipeline/data/` está excluido del control de
versiones.
