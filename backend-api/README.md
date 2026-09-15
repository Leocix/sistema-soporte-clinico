# API Gateway — CDSS Adherencia

Backend FastAPI del sistema de soporte clínico. Cubre RF01 (autenticación y
RBAC), RF02 (gestión de pacientes polimedicados) y RF03 (registro de tomas).

## Cómo ejecutar

> **No ejecutes `python app/main.py`.** Al hacerlo, Python carga `main.py`
> como módulo suelto, el paquete `app` deja de existir para el intérprete y
> los imports relativos fallan con
> `attempted relative import with no known parent package`.
> La aplicación debe cargarse **por su ruta de módulo**, desde `backend-api/`.

Desde la carpeta `backend-api/`:

```bash
python run.py
```

o, de forma equivalente:

```bash
uvicorn app.main:app --reload --port 8000
```


Una vez arriba: <http://127.0.0.1:8000/docs> (documentación interactiva) y
<http://127.0.0.1:8000/health> (sonda de disponibilidad).

## Instalación

```bash
pip install -r requirements.txt
```

El API no carga el modelo: lo consulta por REST al microservicio de
inferencia (`ml-service/`), que debe estar en marcha para ver el riesgo en la
ficha. Configure `ML_SERVICE_URL` y `ML_SERVICE_CLAVE` en `.env`. Si el
microservicio no responde, el resto del API funciona y la predicción devuelve
`503`.

Copia `.env.example` como `.env` y complétalo. La clave de firma se genera con:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Base de datos

El esquema lo gobierna Alembic. Para crear o actualizar las tablas:

```bash
alembic upgrade head
```

Para revertir la última migración:

```bash
alembic downgrade -1
```

Tras modificar `app/db/models.py`, genera la migración correspondiente:

```bash
alembic revision --autogenerate -m "descripcion del cambio"
```

`alembic/env.py` toma la conexión de `DATABASE_URL`, la misma que usa el API:
las credenciales nunca se escriben en `alembic.ini`.

### Carga inicial

```bash
# PowerShell
$env:SEED_PASSWORD = "SuClaveSegura123"
python scripts/seed.py --demo
```

Crea la cuenta del Dr. Milko Ugaz y, con `--demo`, cinco pacientes ficticios
(serie `D-0NN`) con catorce días de historial. Los pacientes de demostración
se distinguen a simple vista de los reales (`P-0NN`) y **no deben incluirse en
el dataset de entrenamiento ni en los resultados de la tesis**.

## Pruebas

```bash
python -m pytest -q
```

97 casos sobre una base en memoria: reglas clínicas, idempotencia de la
sincronización, control de acceso por rol, grupo familiar, recuperación de
contraseña, acceso móvil, reportes y cliente del microservicio. Los 2 de
`test_integracion_ml.py` conectan con el microservicio y el modelo reales y se
omiten si no están instaladas las dependencias de `ml-service`.

## Estructura

```
app/
├── main.py              # CORS, middlewares de seguridad, manejo global de errores
├── api/                 # auth, pacientes, adherencia, familiares, prediccion, reportes
├── core/                # config, security (JWT + RBAC), exceptions
├── db/                  # database (motor y sesión), models (SQLAlchemy)
├── schemas/             # Validación estricta de entrada y salida (Pydantic)
└── services/            # acceso a la ficha, cliente del microservicio, correo
alembic/                 # Migraciones versionadas del esquema clínico
scripts/                 # seed.py
tests/                   # Batería de pruebas del núcleo funcional
```

## Despliegue

Ver [`../DESPLIEGUE.md`](../DESPLIEGUE.md).
