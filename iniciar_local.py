"""Levanta el sistema completo en modo local para la sustentacion.

La sustentacion exige presentar el software en modo local. Este script arranca
los tres servicios en el propio equipo, sobre una base PostgreSQL local
administrada con pgAdmin, sin tocar la base de produccion:

    python iniciar_local.py preparar   # una sola vez: crea las tablas y los datos de demostracion
    python iniciar_local.py            # arranca microservicio, API y panel
    python iniciar_local.py movil      # en OTRA terminal: emulador y aplicacion movil
    python iniciar_local.py apk        # instalador para la pagina /descargar del panel

La base local
-------------
La base se crea en pgAdmin y su direccion se escribe en `local.env`, en la raiz
del repositorio (plantilla en `local.env.example`). Ese archivo esta excluido
de git: la contrasena de la base no sale del equipo.

    LOCAL_DATABASE_URL=postgresql://cdss_app:CONTRASENA@localhost:5432/cdss_local

Sin `local.env`, el script recurre a una base SQLite en `backend-api/`, util
para un ensayo rapido pero distinta del motor de produccion.

Por que no basta con `uvicorn app.main:app`
-------------------------------------------
`backend-api/.env` apunta a la base de produccion en Aiven. Arrancar el API
local con ese archivo haria que la demostracion —y cualquier cambio pedido
durante la evaluacion, migraciones incluidas— escribiera en la base real. Aqui
las variables de entorno sustituyen a las del `.env` (pydantic-settings les da
prioridad). Ademas, el script **rechaza cualquier base que no este en el propio
equipo**, de modo que copiar por error la direccion de Aiven no tiene efecto.

La clave de firma de sesiones y la clave entre el API y el microservicio se
generan al azar en cada arranque y no se guardan en ninguna parte. Al
reiniciar hay que volver a iniciar sesion, que es lo esperable.

Pensado para los cambios en vivo
--------------------------------
El API corre con recarga automatica y el panel con el servidor de Vite: al
guardar un archivo, el cambio se aplica solo. La aplicacion movil admite
recarga en caliente pulsando `r` en su terminal. Si un cambio necesita una
migracion nueva, basta con reiniciar este script: aplica las pendientes al
arrancar.
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import secrets
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

RAIZ = Path(__file__).resolve().parent
API = RAIZ / "backend-api"
ML = RAIZ / "ml-service"
PANEL = RAIZ / "frontend-web"
MOVIL = RAIZ / "app-movil"
CONFIG_LOCAL = RAIZ / "local.env"

SQLITE_LOCAL = API / "cdss_local.db"
PUERTO_API, PUERTO_ML, PUERTO_PANEL = 8000, 8001, 5173
EMULADOR = "Medium_Phone_API_36.0"
# El emulador de Android ve al equipo anfitrion en esta direccion.
URL_API_EMULADOR = f"http://10.0.2.2:{PUERTO_API}"
HOSTS_LOCALES = {"localhost", "127.0.0.1", "::1"}

EN_WINDOWS = os.name == "nt"


# ---------------------------------------------------------------------------
# Base de datos local
# ---------------------------------------------------------------------------
def _leer_config_local() -> dict:
    valores: dict[str, str] = {}
    if CONFIG_LOCAL.exists():
        for linea in CONFIG_LOCAL.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if linea and not linea.startswith("#") and "=" in linea:
                clave, valor = linea.split("=", 1)
                valores[clave.strip()] = valor.strip().strip('"').strip("'")
    return valores


def url_base() -> tuple[str, str]:
    """Direccion de la base local y una descripcion legible, sin contrasena."""
    url = os.environ.get("LOCAL_DATABASE_URL") or _leer_config_local().get("LOCAL_DATABASE_URL")
    if not url:
        return "sqlite:///./cdss_local.db", f"SQLite (backend-api/{SQLITE_LOCAL.name})"

    partes = urlsplit(url)
    if not partes.scheme.startswith("postgres"):
        sys.exit(f"LOCAL_DATABASE_URL debe ser una direccion PostgreSQL; se recibio '{partes.scheme}'.")
    if partes.hostname not in HOSTS_LOCALES:
        # La salvaguarda principal del modo local: nunca produccion.
        sys.exit(
            f"LOCAL_DATABASE_URL apunta a '{partes.hostname}', que no es este equipo.\n"
            "El modo local solo acepta bases en localhost, para no tocar la base de produccion."
        )
    base = partes.path.lstrip("/")
    return url, f"PostgreSQL local ({partes.username}@{partes.hostname}:{partes.port or 5432}/{base})"


def _es_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


def _base_tiene_esquema(url: str) -> bool:
    """True si la base ya tiene tablas creadas por las migraciones."""
    if _es_sqlite(url):
        return SQLITE_LOCAL.exists()
    from sqlalchemy import create_engine, inspect

    motor = create_engine(url.replace("postgres://", "postgresql://", 1))
    try:
        with motor.connect():
            return inspect(motor).has_table("alembic_version")
    except Exception as error:  # conexion rechazada, base inexistente, contrasena...
        sys.exit(
            "No se pudo conectar a la base local. Compruebe en DBeaver que el servidor\n"
            "PostgreSQL esta encendido, que la base existe y que local.env es correcto.\n"
            f"Detalle: {type(error).__name__}: {str(error).splitlines()[0]}"
        )
    finally:
        motor.dispose()


def _vaciar_base(url: str) -> None:
    if _es_sqlite(url):
        SQLITE_LOCAL.unlink(missing_ok=True)
        return
    from sqlalchemy import create_engine, text

    motor = create_engine(url.replace("postgres://", "postgresql://", 1))
    with motor.begin() as conexion:
        conexion.execute(text("DROP SCHEMA public CASCADE"))
        conexion.execute(text("CREATE SCHEMA public"))
    motor.dispose()


# ---------------------------------------------------------------------------
# Entorno de los servicios
# ---------------------------------------------------------------------------
def _python_ml() -> str:
    ruta = ML / ".venv" / ("Scripts/python.exe" if EN_WINDOWS else "bin/python")
    if not ruta.exists():
        sys.exit(
            "Falta el entorno del microservicio. Creelo una vez con:\n"
            "    cd ml-service\n    python -m venv .venv\n"
            "    .venv\\Scripts\\pip install -r requirements.txt"
        )
    return str(ruta)


def _ejecutable(nombre: str, alternativa: str | None = None) -> str:
    encontrado = shutil.which(nombre) or shutil.which(nombre + ".cmd") or shutil.which(nombre + ".bat")
    if encontrado:
        return encontrado
    if alternativa and Path(alternativa).exists():
        return alternativa
    sys.exit(f"No se encontro `{nombre}` en el PATH.")


def entorno_api(url: str, clave_ml: str) -> dict:
    """Variables que aislan el API local de la base de produccion."""
    env = dict(os.environ)
    env.update({
        "ENVIRONMENT": "local",
        "DATABASE_URL": url,
        "SECRET_KEY": secrets.token_urlsafe(48),
        "ML_SERVICE_URL": f"http://127.0.0.1:{PUERTO_ML}",
        "ML_SERVICE_CLAVE": clave_ml,
        "CORS_ORIGINS": f"http://localhost:{PUERTO_PANEL},http://127.0.0.1:{PUERTO_PANEL}",
        "FRONTEND_URL": f"http://localhost:{PUERTO_PANEL}",
        # En local no se envia correo real: el enlace de recuperacion se
        # muestra en la consola del API.
        "SMTP_HOST": "",
        "PYTHONIOENCODING": "utf-8",
    })
    return env


# ---------------------------------------------------------------------------
# preparar
# ---------------------------------------------------------------------------
def preparar(rehacer: bool) -> int:
    url, descripcion = url_base()
    print(f"Base de datos: {descripcion}")

    if _base_tiene_esquema(url):
        if not rehacer:
            print("La base ya tiene las tablas creadas. Use `preparar --rehacer` para empezar de cero.")
            return 0
        _vaciar_base(url)
        print("Contenido anterior eliminado.")

    clave = os.environ.get("SEED_PASSWORD")
    if not clave:
        print("Elija la contrasena de las cuentas de demostracion (medico, pacientes y familiar).")
        print("Es solo para esta base local; no la use en ningun otro sitio.")
        clave = getpass.getpass("Contrasena (minimo 8 caracteres): ")
        if getpass.getpass("Repitala: ") != clave:
            print("Las contrasenas no coinciden.", file=sys.stderr)
            return 1
    if len(clave) < 8:
        print("La contrasena debe tener al menos 8 caracteres.", file=sys.stderr)
        return 1

    env = entorno_api(url, clave_ml="")
    env["SEED_PASSWORD"] = clave
    print("\nCreando las tablas con las migraciones...")
    if subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=API, env=env).returncode:
        return 1
    print("\nCargando los datos de demostracion...")
    if subprocess.run([sys.executable, "scripts/seed.py", "--demo"], cwd=API, env=env).returncode:
        return 1
    print(f"\nListo. Base preparada: {descripcion}")
    print("Ahora arranque el sistema con:  python iniciar_local.py")
    return 0


# ---------------------------------------------------------------------------
# iniciar
# ---------------------------------------------------------------------------
def _reenviar(nombre: str, proceso: subprocess.Popen) -> None:
    """Muestra la salida de cada servicio con su prefijo."""
    for linea in iter(proceso.stdout.readline, ""):
        print(f"[{nombre}] {linea.rstrip()}", flush=True)


def _esperar(url: str, segundos: int = 120) -> bool:
    limite = time.time() + segundos
    while time.time() < limite:
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                if r.status < 500:
                    return True
        except Exception:
            time.sleep(1)
    return False


def _detener(procesos: list[subprocess.Popen]) -> None:
    for p in procesos:
        if p.poll() is None:
            if EN_WINDOWS:
                # Mata el arbol completo: npm y la recarga de uvicorn crean
                # procesos hijos que sobreviven a un terminate() simple.
                subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                p.terminate()


def iniciar() -> int:
    url, descripcion = url_base()
    if not _base_tiene_esquema(url):
        print(f"La base ({descripcion}) todavia no tiene tablas. Preparela una vez con:\n"
              "    python iniciar_local.py preparar")
        return 1

    clave_ml = secrets.token_urlsafe(32)
    env_api = entorno_api(url, clave_ml)
    env_ml = dict(os.environ, CLAVE_SERVICIO=clave_ml, PYTHONIOENCODING="utf-8")

    # Migraciones pendientes, por si un cambio en vivo agrego alguna.
    if subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=API, env=env_api,
                      stdout=subprocess.DEVNULL).returncode:
        print("Fallaron las migraciones; revise el mensaje anterior.", file=sys.stderr)
        return 1

    servicios = [
        ("ml", [_python_ml(), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1",
                "--port", str(PUERTO_ML)], ML, env_ml, f"http://127.0.0.1:{PUERTO_ML}/health"),
        ("api", [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1",
                 "--port", str(PUERTO_API), "--reload"], API, env_api, f"http://127.0.0.1:{PUERTO_API}/health"),
        ("panel", [_ejecutable("npm"), "run", "dev", "--", "--port", str(PUERTO_PANEL), "--strictPort"],
         PANEL, dict(os.environ), f"http://localhost:{PUERTO_PANEL}/"),
    ]

    procesos: list[subprocess.Popen] = []
    try:
        for nombre, comando, carpeta, env, salud in servicios:
            print(f"Arrancando {nombre}...", flush=True)
            p = subprocess.Popen(comando, cwd=carpeta, env=env, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                                 errors="replace", bufsize=1)
            procesos.append(p)
            threading.Thread(target=_reenviar, args=(nombre, p), daemon=True).start()
            if not _esperar(salud):
                print(f"\n{nombre} no respondio en {salud}. Revise sus mensajes arriba.", file=sys.stderr)
                _detener(procesos)
                return 1

        print("\n" + "=" * 64)
        print(" SISTEMA EN MODO LOCAL")
        print("=" * 64)
        print(f" Panel del medico ....... http://localhost:{PUERTO_PANEL}")
        print(f" API (documentacion) .... http://127.0.0.1:{PUERTO_API}/docs")
        print(f" Microservicio .......... http://127.0.0.1:{PUERTO_ML}/health")
        print(f" Base de datos .......... {descripcion}")
        print("\n Aplicacion movil, en OTRA terminal:  python iniciar_local.py movil")
        print(" Para detener todo: Ctrl+C")
        print("=" * 64 + "\n", flush=True)

        # Sin el API o sin el panel no hay sistema, y se detiene todo. Sin el
        # microservicio del modelo, en cambio, el sistema sigue: la ficha avisa
        # que la predicción no está disponible y las alertas por reglas
        # continúan. Detenerlo todo contradiría esa tolerancia a fallos.
        modelo, *esenciales = procesos
        aviso_dado = False
        while all(p.poll() is None for p in esenciales):
            if modelo.poll() is not None and not aviso_dado:
                print("\nEl microservicio del modelo se detuvo. El API y el panel siguen en marcha;"
                      " para recuperarlo, reinicie con Ctrl+C y `python iniciar_local.py`.\n",
                      file=sys.stderr, flush=True)
                aviso_dado = True
            time.sleep(1)
        print("Un servicio se detuvo; deteniendo el resto.", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nDeteniendo los servicios...")
        return 0
    finally:
        _detener(procesos)


# ---------------------------------------------------------------------------
# movil
# ---------------------------------------------------------------------------
def _emulador_conectado(flutter: str) -> str | None:
    salida = subprocess.run([flutter, "devices", "--machine"], capture_output=True, text=True,
                            encoding="utf-8", errors="replace").stdout
    try:
        dispositivos = json.loads(salida[salida.index("["):])
    except ValueError:
        return None
    for d in dispositivos:
        if d.get("emulator") and d.get("targetPlatform", "").startswith("android"):
            return d["id"]
    return None


def movil() -> int:
    flutter = _ejecutable("flutter", r"D:\flutter\bin\flutter.bat")
    if not _esperar(f"http://127.0.0.1:{PUERTO_API}/health", segundos=3):
        print("El API local no responde. Arranque antes el sistema con `python iniciar_local.py`.",
              file=sys.stderr)
        return 1

    dispositivo = _emulador_conectado(flutter)
    if not dispositivo:
        print(f"Abriendo el emulador {EMULADOR} (puede tardar un minuto)...", flush=True)
        subprocess.Popen([flutter, "emulators", "--launch", EMULADOR])
        limite = time.time() + 240
        while time.time() < limite and not dispositivo:
            time.sleep(5)
            dispositivo = _emulador_conectado(flutter)
        if not dispositivo:
            print("El emulador no arranco a tiempo. Abralo desde Android Studio y repita.", file=sys.stderr)
            return 1

    # El emulador aparece en la lista antes de que Android termine de arrancar;
    # si se instala en ese momento, el gestor de paquetes rechaza el APK.
    if not _arranque_completo(dispositivo):
        print("Android no termino de arrancar en el emulador. Espere a ver la pantalla de inicio y repita.",
              file=sys.stderr)
        return 1

    print(f"\nInstalando la aplicacion en {dispositivo}, conectada a {URL_API_EMULADOR}.")
    print("Recarga en caliente: pulse `r` en esta terminal. Reinicio completo: `R`. Salir: `q`.\n", flush=True)
    return subprocess.run([flutter, "run", "-d", dispositivo, f"--dart-define=API_URL={URL_API_EMULADOR}"],
                          cwd=MOVIL).returncode


def _adb() -> str:
    sdk = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT") \
        or str(Path(os.environ.get("LOCALAPPDATA", "")) / "Android" / "Sdk")
    return _ejecutable("adb", str(Path(sdk) / "platform-tools" / "adb.exe"))


def _arranque_completo(dispositivo: str, segundos: int = 240) -> bool:
    adb = _adb()
    limite = time.time() + segundos
    while time.time() < limite:
        estado = subprocess.run([adb, "-s", dispositivo, "shell", "getprop", "sys.boot_completed"],
                                capture_output=True, text=True).stdout.strip()
        if estado == "1":
            # El gestor de paquetes termina de iniciarse unos segundos despues.
            time.sleep(5)
            return True
        time.sleep(3)
    return False


def apk(api: str) -> int:
    """Construye el instalador y lo deja donde lo sirve la pagina /descargar.

    Con una direccion https se genera el APK de publicacion, que funciona en
    cualquier celular con internet. Una direccion http (el API local visto
    desde el emulador) solo la admite la compilacion de depuracion: Android
    bloquea el trafico sin cifrar en las de publicacion.
    """
    flutter = _ejecutable("flutter", r"D:\flutter\bin\flutter.bat")
    publicacion = api.startswith("https://")
    modo = "--release" if publicacion else "--debug"
    print(f"Construyendo el APK ({modo[2:]}) conectado a {api}...", flush=True)
    if subprocess.run([flutter, "build", "apk", modo, f"--dart-define=API_URL={api}"], cwd=MOVIL).returncode:
        return 1
    origen = MOVIL / "build" / "app" / "outputs" / "flutter-apk" / f"app-{modo[2:]}.apk"
    destino = PANEL / "public" / "descargas" / "mi-tratamiento.apk"
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(origen, destino)
    print(f"\nListo: {destino.relative_to(RAIZ)} ({destino.stat().st_size / 1e6:.0f} MB).")
    print(f"Se descarga desde http://localhost:{PUERTO_PANEL}/descargar mientras el panel este en marcha.")
    if not publicacion:
        print("Aviso: este APK solo funciona en el emulador. Para celulares reales use --api https://...")
    return 0


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Sistema completo en modo local.")
    parser.add_argument("orden", nargs="?", default="iniciar", choices=["iniciar", "preparar", "movil", "apk"])
    parser.add_argument("--rehacer", action="store_true", help="Con `preparar`: vacia la base local y la recrea.")
    parser.add_argument("--api", default="https://cdss-adherencia-api.onrender.com",
                        help="Con `apk`: API al que se conecta la aplicacion.")
    args = parser.parse_args()
    if args.orden == "preparar":
        return preparar(args.rehacer)
    if args.orden == "movil":
        try:
            return movil()
        except KeyboardInterrupt:
            print("\nAplicacion movil detenida.")
            return 0
    if args.orden == "apk":
        return apk(args.api)
    return iniciar()


if __name__ == "__main__":
    sys.exit(main())
