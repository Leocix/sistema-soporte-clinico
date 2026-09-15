# Guía de despliegue

Sistema de soporte clínico con aprendizaje automático — consultorio médico
Milko Ugaz Zegarra.

| Componente | Plataforma | Estado |
| :--- | :--- | :--- |
| Modelo predictivo | Artefacto versionado en el repositorio | Cargado por el API al primer uso |
| Base de datos PostgreSQL | Aiven (o PostgreSQL de Render) | Listo para aprovisionar |
| API Gateway (FastAPI) | Render | Configurado (`render.yaml`) |
| Panel médico (React + Vite) | Vercel | Configurado (`frontend-web/vercel.json`) |
| App del paciente y su familia (Flutter) | APK / Play Store interno | APK de publicación construido |

El orden importa: **base de datos → API → panel web**. Cada paso necesita la
URL que produce el anterior.

---

## 1. Base de datos PostgreSQL

### 1.1. Aprovisionar el servicio

En Aiven, crear un servicio **PostgreSQL** en el plan gratuito, región la más
cercana a Perú. Al terminar, la consola entrega el *Service URI* con esta
forma:

```
postgres://avnadmin:CONTRASENA@nombre-proyecto.aivencloud.com:PUERTO/defaultdb?sslmode=require
```

Guárdala: es el valor de `DATABASE_URL`. El parámetro `sslmode=require` cifra
la conexión en tránsito y **no debe quitarse** (RNF01).

> El API normaliza el prefijo automáticamente. Tanto `postgres://` como
> `postgresql://` funcionan: `app/core/config.py` los reescribe al formato con
> controlador explícito que exige SQLAlchemy 2.x.

### 1.2. Conectar DBeaver

En DBeaver: **Nueva conexión → PostgreSQL**, y completar con los datos del
Service URI:

| Campo | Valor |
| :--- | :--- |
| Host | `nombre-proyecto.aivencloud.com` |
| Puerto | el que indica Aiven (no es 5432) |
| Base de datos | `defaultdb` |
| Usuario | `avnadmin` |
| Contraseña | la del Service URI |

En la pestaña **SSL**: marcar *Use SSL* y fijar *SSL mode* en `require`. Sin
esto, Aiven rechaza la conexión.

### 1.3. Crear el esquema

Con Alembic, que es el que mantiene el historial de cambios del esquema:

```bash
cd backend-api
alembic upgrade head
```

Apunta `DATABASE_URL` a Aiven antes de ejecutarlo (en `.env` o como variable
de entorno).

> No se versiona un script DDL aparte. Existió uno generado desde los
> modelos, pero quedó desfasado en cuanto el esquema creció con el grupo
> familiar y el restablecimiento de contraseña: un `.sql` que describe un
> esquema que ya no existe es peor que no tenerlo. Para inspeccionar la
> estructura en DBeaver, conéctese a la base ya migrada.

### 1.4. Cargar la cuenta del médico

```bash
# PowerShell
$env:SEED_PASSWORD = "SuClaveSegura123"
cd backend-api
python scripts/seed.py
```

Añade `--demo` si quieres además cinco pacientes ficticios con historial para
recorrer el panel. Se distinguen por el prefijo `D-` frente a los reales `P-`.

Ese mismo `--demo` deja preparado el grupo familiar (RF09): crea la cuenta
`rosa.d-001@ejemplo.pe`, acompañante del paciente D-001, con parte de su
historial ya corroborado y alguna toma pendiente de confirmar. Sirve para
mostrar el acompañamiento desde un solo teléfono, sin necesitar un segundo
dispositivo que canjee el código. El script puede ejecutarse las veces que
haga falta: completa lo que falte y no duplica nada.

### 1.5. Verificar en DBeaver

```sql
SELECT codigo_anonimizado, sexo, diagnostico, nivel_educativo, comorbilidades,
       numero_farmacos, puntaje_morisky, incumplimiento_basal
FROM pacientes
ORDER BY codigo_anonimizado;
```

Los valores deben aparecer con los códigos del Anexo n.° 04 (`M`, `ambas`,
`bajo`), no con los nombres internos en mayúsculas. Es lo que permite exportar
el CSV del dataset directamente desde una consulta.

---

## 2. API Gateway en Render

### 2.1. Crear el servicio

En Render: **New → Blueprint**, conectar el repositorio. Render detecta
`render.yaml` en la raíz y propone el servicio `cdss-adherencia-api` con:

- Directorio raíz `backend-api/`
- `pip install -r requirements.txt`
- `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Sonda de salud en `/health`

Las migraciones se aplican en cada arranque. Alembic es idempotente: si no hay
nada pendiente, no hace nada. Si `DATABASE_URL` está mal, el servicio no
arranca y el fallo aparece en los *logs* de Render: es deliberado, preferible a
un API en pie que no puede leer datos.

> `requirements.txt` incluye scikit-learn, imbalanced-learn, numpy, pandas
> y joblib **con las versiones exactas del entorno de entrenamiento**: el
> artefacto serializado es un pipeline de imbalanced-learn y solo se puede
> abrir con esas librerías y esas versiones. XGBoost no está: pesa cientos de
> megabytes y solo hace falta para entrenar, de modo que el modelo desplegado
> se produce con `--sin-xgboost`. Si la comparación sobre el dataset real
> seleccionara XGBoost, habría que añadirlo a `requirements.txt` con la versión
> de `ml-pipeline/requirements.txt`.

### 2.2. Completar las variables de entorno

Las cuatro variables marcadas `sync: false` no se versionan; se completan a
mano en **Environment** del panel de Render:

| Variable | Valor |
| :--- | :--- |
| `DATABASE_URL` | El Service URI de Aiven, con `?sslmode=require` |
| `SECRET_KEY` | `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `CORS_ORIGINS` | La URL del panel en Vercel (paso 3). Déjala vacía en el primer despliegue y complétala después |
| `ALLOWED_HOSTS` | El host que asigna Render, p. ej. `cdss-adherencia-api.onrender.com` |

### 2.2.1. Correo saliente para el restablecimiento (opcional)

Sin estas variables la recuperación de contraseña queda desactivada: el API lo
dice con claridad y remite al consultorio, en vez de fingir un envío. Para
activarla:

| Variable | Valor |
| :--- | :--- |
| `FRONTEND_URL` | La URL del panel en Vercel, sin barra final |
| `SMTP_HOST` | El servidor de su proveedor, p. ej. `smtp.gmail.com` |
| `SMTP_PORT` | `587` (STARTTLS) o `465` (TLS directo) |
| `SMTP_USUARIO` | La cuenta con la que autenticarse |
| `SMTP_CONTRASENA` | Su contraseña o, en Gmail, una **contraseña de aplicación** |
| `SMTP_REMITENTE` | La dirección que verá el paciente como remitente |

Con Gmail hace falta verificación en dos pasos y una contraseña de aplicación
—la contraseña normal de la cuenta no sirve para SMTP—. Se genera en
<https://myaccount.google.com/apppasswords>. Un servicio transaccional
(Brevo, Resend, Mailgun) funciona igual y evita que los mensajes acaben en
correo no deseado, que es el riesgo real de enviar desde Gmail.

Escriba esos valores **solo en el panel de Render**: no los pegue en el
repositorio ni en una conversación.

`ENVIRONMENT=produccion` ya viene fijado en el blueprint. Eso activa HSTS y
**oculta `/docs`, `/redoc` y `/openapi.json`**: la documentación interactiva no
queda expuesta en un servicio público.

### 2.3. Verificar

```bash
curl https://cdss-adherencia-api.onrender.com/health
```

Debe responder `{"estado":"ok","version":"0.2.0"}`.

> **Plan gratuito de Render:** el servicio se suspende tras 15 minutos sin
> tráfico y la primera petición posterior tarda unos 50 segundos en responder.
> Tenlo en cuenta el día de la sustentación: entra al `/health` unos minutos
> antes para despertarlo. Es también la razón por la que la meta de RNF02
> (≤ 2 s) debe medirse con el servicio ya activo, no en el arranque en frío.

---

## 3. Panel médico en Vercel

### 3.1. Probarlo en local primero

```bash
cd frontend-web
npm install
```

Copia `.env.example` como `.env` (por defecto apunta a `http://127.0.0.1:8000`) y arranca:

```bash
npm run dev
```

Necesitas el API corriendo en paralelo. En otra terminal, desde `backend-api/`:

```bash
python run.py
```

El panel queda en <http://localhost:5173>. Entra con el correo del médico y la
contraseña que definiste en `SEED_PASSWORD`.

### 3.2. Desplegar

1. En Vercel: **Add New → Project**, importar el repositorio.
2. **Root Directory:** `frontend-web`. El framework (Vite) se detecta solo y
   `vercel.json` ya fija el comando de construcción y la reescritura de rutas
   que necesita el enrutador del lado del cliente.
3. Variable de entorno **`VITE_API_URL`** con la URL del servicio de Render,
   sin barra final: `https://cdss-adherencia-api.onrender.com`.
4. Tras el primer despliegue, copiar el dominio asignado y ponerlo en
   `CORS_ORIGINS` en Render.

> `VITE_API_URL` se incrusta en el paquete durante la construcción, no se lee
> en tiempo de ejecución: si la cambias, hay que volver a desplegar para que
> tenga efecto.

Los despliegues de vista previa (uno por cada *commit*) ya están autorizados
sin configuración adicional: `CORS_ORIGIN_REGEX` cubre cualquier subdominio
`*.vercel.app`.

### 3.3. Qué incluye el panel al corte

| Vista | Requisito | Contenido |
| :--- | :---: | :--- |
| Inicio de sesión | RF01 | Acceso exclusivo del perfil médico |
| Panel de auditoría | RF02, RF07 | Indicadores, listado ordenado por prioridad clínica, filtros y alta de pacientes |
| Ficha del paciente | RF02, RF03 | Variables del Anexo n.° 04 por dimensión OMS, indicadores de adherencia e historial de tomas |

La clasificación de riesgo que muestra el panel es **provisional**: se calcula
sobre la adherencia ya observada, no con el modelo predictivo. La predicción
del modelo (RF04) y los factores influyentes con SHAP (RF06) la sustituyen en
el Sprint 3.

---

## Lista de verificación antes de la sustentación

- [ ] `SECRET_KEY` de producción distinta de la de desarrollo
- [ ] `.env` fuera del control de versiones (ya está en `.gitignore`)
- [ ] `ENVIRONMENT=produccion` en Render (oculta `/docs`)
- [ ] `sslmode=require` en la cadena de conexión
- [ ] `CORS_ORIGINS` apuntando al dominio real del panel
- [ ] Servicio de Render despierto
- [ ] Pacientes de demostración (`D-`) retirados si se muestran datos reales
- [ ] APK reconstruido tras el último cambio: `flutter build apk --release`
- [ ] `FRONTEND_URL` apuntando al dominio real del panel, si se activó el correo
