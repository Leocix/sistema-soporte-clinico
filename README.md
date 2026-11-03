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
| [`backend-api/`](backend-api/) | API central (FastAPI + PostgreSQL) | Acceso, pacientes, tomas, grupo familiar, reportes |
| [`ml-service/`](ml-service/) | Microservicio de inferencia (FastAPI + scikit-learn + SHAP) | Predicción y explicación individual |
| [`frontend-web/`](frontend-web/) | Panel médico (React + Vite) | Ficha, riesgo con SHAP, alertas tempranas y reportes |
| [`app-movil/`](app-movil/) | App del paciente y su familia (Flutter) | Acceso, registro de tomas sin conexión, alertas y grupo familiar |
| [`ml-pipeline/`](ml-pipeline/) | Pipeline CRISP-DM | Preparación, comparación de algoritmos y modelo en servicio |
| [`documentacion/`](documentacion/) | Evidencias académicas USAT | Pre informe de tesis (100 % del desarrollo) y guion de demostración |

## Estructura del repositorio

Cada componente se despliega por separado y trae su propio `README.md`, sus
dependencias y sus pruebas.

```
sistema-soporte-clinico/
├── backend-api/            API central (FastAPI)
│   ├── app/
│   │   ├── api/            Rutas: auth, pacientes, adherencia, familiares,
│   │   │                   prediccion, reportes, alertas
│   │   ├── core/           Configuracion, seguridad (JWT + RBAC), errores
│   │   ├── db/             Modelos SQLAlchemy y sesion
│   │   ├── schemas/        Validacion de entrada y salida (Pydantic)
│   │   └── services/       Reglas: acceso, riesgo, alertas, correo,
│   │                       cliente del microservicio de inferencia
│   ├── alembic/versions/   Migraciones versionadas del esquema clinico
│   ├── scripts/            Carga inicial, migracion con reintentos, carga
│   └── tests/              142 pruebas (pytest)
├── ml-service/             Microservicio de inferencia (FastAPI + SHAP)
│   ├── app/                Carga del modelo, prediccion y explicacion
│   └── tests/              13 pruebas contra el modelo desplegado
├── ml-pipeline/            Pipeline CRISP-DM
│   ├── src/                preprocess.py y train_evaluate.py
│   └── models/             Modelo en servicio y su ficha de procedencia
├── frontend-web/           Panel medico (React + Vite)
│   └── src/
│       ├── pages/          Panel, ficha, alertas, reportes, acceso
│       ├── components/     Formulario, prediccion, alertas de riesgo
│       └── services/       Cliente HTTP, etiquetas, validacion, riesgo
├── app-movil/              Aplicacion del paciente y del familiar (Flutter)
│   ├── lib/                Pantallas, servicios y modelos
│   └── test/               40 pruebas
├── documentacion/          Evidencias academicas
│   ├── 00_documentacion_base/  Proyecto de tesis, cronograma, silabo
│   ├── 01_preinforme/          Pre informe (Markdown y Word)
│   ├── 02_instrumentos/        Anexos 04 a 07 y plantilla de captura
│   ├── 03_gestion_scrum/       Product Backlog, trazabilidad, actas
│   ├── 04_demostracion/        Guion de la demostracion del producto
│   ├── 05_manual/              Manual de usuario (medico, paciente, familiar)
│   └── herramientas/           Generadores del Word desde el Markdown
├── render.yaml             Despliegue del API y del microservicio
└── DESPLIEGUE.md           Guia completa de puesta en produccion
```

## Requisitos funcionales

| ID | Requisito | Prioridad | Estado |
| :---: | :--- | :---: | :--- |
| RF01 | Autenticación y autorización por perfil (médico / paciente) | Must | Implementado |
| RF02 | Gestión de pacientes polimedicados y esquema farmacológico | Must | Implementado |
| RF03 | Registro de la toma de medicamentos desde la app móvil | Must | Implementado |
| RF04 | Predicción del riesgo de incumplimiento | Must | Implementado |
| RF05 | Alertas tempranas al médico | Must | Implementado |
| RF06 | Explicabilidad de la predicción (SHAP) | Should | Implementado |
| RF07 | Panel de auditoría con reportes exportables | Should | Implementado |
| RF08 | Recordatorios de toma al paciente | Could | Implementado |
| RF09 | Corroboración de la toma por el grupo familiar | Should | Implementado |
| RF10 | Restablecimiento de la contraseña por correo | Should | Implementado |

## Modo local (sustentación)

Un solo script levanta el sistema completo en el equipo, sobre una base
PostgreSQL local administrada con DBeaver. **No toca la base de producción**:
las variables que fija el script tienen prioridad sobre las de
`backend-api/.env`, y el script rechaza cualquier base que no esté en
`localhost`.

### 1. La base, una sola vez

Con el servidor PostgreSQL instalado y encendido, en DBeaver: conexión nueva →
PostgreSQL → `localhost:5432`, usuario `postgres`. Abra un editor SQL y ejecute,
eligiendo usted la contraseña:

```sql
CREATE ROLE cdss_app WITH LOGIN PASSWORD 'su-contraseña';
CREATE DATABASE cdss_local OWNER cdss_app ENCODING 'UTF8';
```

La aplicación se conecta con `cdss_app`, que es dueño de su base y nada más: no
usa el superusuario. Copie `local.env.example` como `local.env` y ponga ahí esa
contraseña. `local.env` no entra en git.

```bash
python iniciar_local.py preparar
```

Crea las tablas con las migraciones y carga el médico, cinco pacientes de
demostración y un familiar; le pide la contraseña de esas cuentas.
`preparar --rehacer` vacía la base y vuelve a empezar. Sin `local.env`, el
script usa una base SQLite como alternativa de ensayo.

### 2. Cada vez que se presenta

```bash
python iniciar_local.py
```

Arranca el microservicio (8001), el API (8000) y el panel
(<http://localhost:5173>), con recarga automática al guardar cambios. Ctrl+C
detiene todo.

```bash
python iniciar_local.py movil
```

En **otra** terminal: abre el emulador de Android e instala la aplicación
conectada al API local (`10.0.2.2:8000`). En esa terminal, `r` recarga los
cambios en caliente.

```bash
python iniciar_local.py apk
```

Construye el APK de publicación y lo deja en `frontend-web/public/descargas/`,
de donde lo sirve la página pública <http://localhost:5173/descargar> (con
código QR para escanear desde el celular). El panel también publica
`/privacidad` y `/terminos`, enlazadas desde el inicio de sesión y la app.

## Puesta en marcha manual

Requiere Python 3.12+, Node 20+ y una base PostgreSQL (o SQLite en local).

```bash
cd ml-service && pip install -r requirements.txt && uvicorn app.main:app --port 8001
```

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
cd ml-service && python -m pytest -q
```

Rendimiento con usuarios simultáneos (RNF02, RNF06):

```bash
python backend-api/scripts/prueba_carga.py --url http://127.0.0.1:8000 --correo <medico> --usuarios 10
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

## Recuperar el acceso

Olvidar la contraseña obligaba a acercarse al consultorio. Para el paciente
tipo del estudio —adulto mayor, con frecuencia de zona rural— eso no es un
trámite menor sino un viaje, y para el consultorio significaba ejecutar un
script a mano por cada olvido.

El sistema envía ahora un enlace de un solo uso, válido media hora, que sirve a
los tres perfiles. La respuesta del API es idéntica exista o no la cuenta, para
que la ruta no se convierta en un buscador de correos registrados; del enlace
solo se guarda su resumen SHA-256, nunca el enlace.

Requiere configurar un servidor de correo saliente (`SMTP_*` en
[`DESPLIEGUE.md`](DESPLIEGUE.md)). Sin él la función se desactiva sola y el
sistema remite al consultorio, en lugar de prometer un mensaje que nadie
enviará.

## Nota sobre los datos

Los datos clínicos se almacenan seudonimizados: el código `P-0NN` es la única
clave que viaja al pipeline de aprendizaje automático. Los pacientes de la
demostración (P-001 a P-005, con correos `@ejemplo.pe`) que genera
`scripts/seed.py --demo` son **ficticios** y no deben
incluirse en el dataset de entrenamiento ni en los resultados de la
investigación. El directorio `ml-pipeline/data/` está excluido del control de
versiones.
