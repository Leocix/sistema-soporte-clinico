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

En Windows también sirve un doble clic sobre `dev.bat`.

Una vez arriba: <http://127.0.0.1:8000/docs> (documentación interactiva) y
<http://127.0.0.1:8000/health> (sonda de disponibilidad).

## Instalación

```bash
pip install -r requirements.txt
```

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

### Esquema para DBeaver

```bash
python scripts/generar_ddl.py
```

Regenera `schema_postgresql.sql` desde los modelos. Sirve para inspeccionar la
estructura o crear el esquema a mano en DBeaver. La fuente de verdad siguen
siendo los modelos y las migraciones: no edites ese `.sql` directamente.

## Pruebas

```bash
python -m pytest -q
```

25 casos sobre una base en memoria: reglas clínicas, idempotencia de la
sincronización y control de acceso por rol.

## Estructura

```
app/
├── main.py              # CORS, middlewares de seguridad, manejo global de errores
├── api/                 # Controladores: auth, pacientes, adherencia
├── core/                # config, security (JWT + RBAC), exceptions
├── db/                  # database (motor y sesión), models (SQLAlchemy)
├── schemas/             # Validación estricta de entrada y salida (Pydantic)
└── services/            # Reglas de negocio: acceso a la ficha del paciente
alembic/                 # Migraciones versionadas del esquema clínico
scripts/                 # seed.py, generar_ddl.py
tests/                   # Batería de pruebas del núcleo funcional
```

## Despliegue

Ver [`../DESPLIEGUE.md`](../DESPLIEGUE.md).
