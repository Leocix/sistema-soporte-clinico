"""Pruebas de caja negra del producto acreditable.

Trata al sistema como una caja cerrada: solo conoce sus entradas y salidas
públicas (el API por HTTP y el panel en el navegador), nunca su código. Cada
caso declara el requisito que verifica, la técnica con que se diseñó, la
entrada, el resultado esperado y, al ejecutarse, el resultado obtenido.

Uso, con el sistema en marcha en modo local y los datos de demostración
(`python iniciar_local.py preparar` y `python iniciar_local.py`):

    set CLAVE_DEMO=<contraseña de las cuentas de demostración>
    python ejecutar_caja_negra.py            # casos del API
    python ejecutar_caja_negra.py --ui       # además, los casos del panel (Playwright + Edge)

Escribe `resultados_caja_negra.csv` y `resultados_caja_negra.md` junto a este
archivo. Crea pacientes y registros de prueba: ejecútelo sobre la base local de
demostración, nunca sobre una base con datos reales.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
API = os.environ.get("API_URL", "http://127.0.0.1:8000")
PANEL = os.environ.get("PANEL_URL", "http://localhost:5173")
MEDICO = "milko.ugaz@consultorio.pe"
PACIENTE = "p-001@ejemplo.pe"
FAMILIAR = "rosa.p-001@ejemplo.pe"


# ---------------------------------------------------------------------------
# Cliente HTTP mínimo (solo biblioteca estándar)
# ---------------------------------------------------------------------------
@dataclass
class Respuesta:
    estado: int
    cuerpo: object
    texto: str
    cabeceras: dict
    ms: float


def pedir(metodo: str, ruta: str, cuerpo=None, token: str | None = None) -> Respuesta:
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(API + ruta, data=datos, method=metodo)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    inicio = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            estado, crudo, cab = r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        estado, crudo, cab = e.code, e.read(), dict(e.headers)
    ms = (time.perf_counter() - inicio) * 1000
    texto = crudo.decode("utf-8", "replace")
    try:
        cuerpo_json = json.loads(texto) if texto else None
    except ValueError:
        cuerpo_json = None
    return Respuesta(estado, cuerpo_json, texto, cab, ms)


def mensaje(r: Respuesta) -> str:
    """Mensaje legible de una respuesta de error del API."""
    if isinstance(r.cuerpo, dict):
        detalles = r.cuerpo.get("detalles") or []
        if detalles and isinstance(detalles, list):
            return "; ".join(str(d.get("motivo", d)) for d in detalles)[:160]
        return str(r.cuerpo.get("mensaje", ""))[:160]
    return r.texto[:160]


def login(correo: str, perfil: str, clave: str) -> str:
    r = pedir("POST", "/api/auth/login", {"correo": correo, "contrasena": clave, "perfil": perfil})
    if r.estado != 200:
        sys.exit(f"No se pudo iniciar sesión como {correo}: {r.estado} {mensaje(r)}")
    return r.cuerpo["access_token"]


# ---------------------------------------------------------------------------
# Registro de casos
# ---------------------------------------------------------------------------
@dataclass
class Caso:
    id: str
    requisito: str
    tecnica: str
    descripcion: str
    entrada: str
    esperado: str
    obtenido: str = ""
    conforme: bool = False
    ms: float | None = None
    extra: dict = field(default_factory=dict)


CASOS: list[Caso] = []


def caso(id_, requisito, tecnica, descripcion, entrada, esperado, ejecutar):
    """Ejecuta un caso; `ejecutar` devuelve (conforme, obtenido[, ms])."""
    c = Caso(id_, requisito, tecnica, descripcion, entrada, esperado)
    try:
        resultado = ejecutar()
        c.conforme, c.obtenido = bool(resultado[0]), str(resultado[1])
        if len(resultado) > 2:
            c.ms = resultado[2]
    except Exception as e:  # el caso falla, la batería sigue
        c.conforme, c.obtenido = False, f"Excepción: {type(e).__name__}: {e}"
    CASOS.append(c)
    print(f"  {'OK ' if c.conforme else 'NO '} {c.id}  {c.descripcion}")
    return c


def esperar_estado(r: Respuesta, esperado: int, texto: str | None = None):
    ok = r.estado == esperado and (texto is None or texto.lower() in r.texto.lower())
    return ok, f"HTTP {r.estado}. {mensaje(r) or 'Sin mensaje'}", r.ms


# ---------------------------------------------------------------------------
# Datos de prueba
# ---------------------------------------------------------------------------
_contador = [0]


def ficha(**cambios) -> dict:
    """Ficha válida (clase de equivalencia válida) con los cambios indicados."""
    _contador[0] += 1
    base = {
        "nombres": "Prueba", "apellidos": "Caja Negra",
        "correo": f"cn{_contador[0]}.{int(time.time())}@correo.pe",
        "edad": 64, "sexo": "F", "diagnostico": "ambas",
        "tiempo_enfermedad_anios": 8, "lista_comorbilidades": ["dislipidemia"],
        "numero_farmacos": 7, "tomas_dia": 4,
        "controles_programados_6m": 6, "controles_perdidos_6m": 2,
        "nivel_educativo": "secundaria", "convivencia": "acompanado",
        "apoyo_familiar": True, "puntaje_morisky": 2, "incumplimiento_basal": True,
    }
    base.update(cambios)
    return {k: v for k, v in base.items() if v is not ...}


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Casos del API
# ---------------------------------------------------------------------------
def casos_api(clave: str) -> None:
    ahora = datetime.now(timezone.utc).replace(microsecond=0)

    print("\nRF01 · Autenticación")
    caso("CN-01", "RF01", "Partición de equivalencia (clase válida)",
         "Médico con credenciales correctas", f"{MEDICO} · contraseña correcta · perfil médico",
         "HTTP 200 y token de sesión",
         lambda: (lambda r: (r.estado == 200 and "access_token" in (r.cuerpo or {}),
                             f"HTTP {r.estado}. Token emitido" if r.estado == 200 else mensaje(r), r.ms))(
             pedir("POST", "/api/auth/login", {"correo": MEDICO, "contrasena": clave, "perfil": "medico"})))
    caso("CN-02", "RF01", "Partición de equivalencia (clase no válida)",
         "Contraseña incorrecta", f"{MEDICO} · contraseña errónea",
         "HTTP 401 «Usuario o contraseña incorrectos.»",
         lambda: esperar_estado(pedir("POST", "/api/auth/login",
                                      {"correo": MEDICO, "contrasena": "incorrecta-123", "perfil": "medico"}),
                                401, "Usuario o contraseña incorrectos"))
    caso("CN-03", "RF01", "Partición de equivalencia (clase no válida)",
         "Correo no registrado", "noexiste@correo.pe",
         "HTTP 401 con el mismo mensaje que CN-02 (no revela qué cuentas existen)",
         lambda: esperar_estado(pedir("POST", "/api/auth/login",
                                      {"correo": "noexiste@correo.pe", "contrasena": "incorrecta-123",
                                       "perfil": "medico"}), 401, "Usuario o contraseña incorrectos"))
    caso("CN-04", "RF01", "Tabla de decisión (rol × perfil declarado)",
         "Paciente que intenta entrar con perfil médico", f"{PACIENTE} · perfil médico",
         "HTTP 401: el perfil no corresponde a la cuenta",
         lambda: esperar_estado(pedir("POST", "/api/auth/login",
                                      {"correo": PACIENTE, "contrasena": clave, "perfil": "medico"}), 401))
    caso("CN-05", "RF01", "Tabla de decisión (rol × perfil declarado)",
         "Médico que intenta entrar a la app como paciente", f"{MEDICO} · perfil paciente",
         "HTTP 401",
         lambda: esperar_estado(pedir("POST", "/api/auth/login",
                                      {"correo": MEDICO, "contrasena": clave, "perfil": "paciente"}), 401))
    caso("CN-06", "RF01", "Partición de equivalencia (formato no válido)",
         "Correo con formato inválido", "«milko.ugaz» sin dominio",
         "HTTP 422: validación de formato",
         lambda: esperar_estado(pedir("POST", "/api/auth/login",
                                      {"correo": "milko.ugaz", "contrasena": clave, "perfil": "medico"}), 422))

    t_med = login(MEDICO, "medico", clave)
    t_pac = login(PACIENTE, "paciente", clave)

    print("\nRF02 · Registro del paciente polimedicado")
    creados: dict[str, dict] = {}

    def alta(cuerpo, esperado, texto=None, clave_guardar=None):
        r = pedir("POST", "/api/pacientes", cuerpo, t_med)
        if r.estado == 201 and clave_guardar:
            creados[clave_guardar] = r.cuerpo
        if esperado == 201:
            cod = (r.cuerpo or {}).get("codigo_anonimizado", "") if r.estado == 201 else ""
            return r.estado == 201, f"HTTP {r.estado}. {('Código asignado ' + cod) if cod else mensaje(r)}", r.ms
        return esperar_estado(r, esperado, texto)

    caso("CN-07", "RF02", "Partición de equivalencia (clase válida)",
         "Ficha completa y coherente", "Edad 64, 7 fármacos, 4 tomas, 6/2 controles, Morisky 2",
         "HTTP 201 y código P-xxx asignado", lambda: alta(ficha(), 201, clave_guardar="valida"))
    for id_, valor, esp, desc in (("CN-08", 17, 422, "Edad 17 (límite inferior − 1)"),
                                  ("CN-09", 18, 201, "Edad 18 (límite inferior)"),
                                  ("CN-10", 120, 201, "Edad 120 (límite superior)"),
                                  ("CN-11", 121, 422, "Edad 121 (límite superior + 1)")):
        caso(id_, "RF02", "Valores límite", desc, f"edad = {valor}",
             "HTTP 201 (aceptada)" if esp == 201 else "HTTP 422 (rechazada)",
             lambda v=valor, e=esp: alta(ficha(edad=v, tiempo_enfermedad_anios=None), e))
    for id_, valor, esp, desc in (("CN-12", 4, 422, "4 fármacos (no polimedicado)"),
                                  ("CN-13", 5, 201, "5 fármacos (límite de polimedicación)"),
                                  ("CN-14", 30, 201, "30 fármacos (límite superior)"),
                                  ("CN-15", 31, 422, "31 fármacos (límite superior + 1)")):
        caso(id_, "RF02", "Valores límite", desc, f"numero_farmacos = {valor}",
             "HTTP 201 (aceptada)" if esp == 201 else "HTTP 422 (rechazada)",
             lambda v=valor, e=esp: alta(ficha(numero_farmacos=v), e))
    caso("CN-16", "RF02", "Tabla de decisión (coherencia entre campos)",
         "Controles perdidos mayores que los programados", "programados 4 · perdidos 6",
         "HTTP 422 «Los controles perdidos no pueden superar a los programados.»",
         lambda: alta(ficha(controles_programados_6m=4, controles_perdidos_6m=6), 422, "no pueden superar"))
    caso("CN-17", "RF02", "Partición de equivalencia (clave duplicada)",
         "Código anonimizado ya existente", "codigo_anonimizado = P-001",
         "HTTP 409: el código ya existe",
         lambda: alta(ficha(codigo_anonimizado="P-001"), 409))
    caso("CN-18", "RF02", "Partición de equivalencia (clase no válida)",
         "Nombres con dígitos", "nombres = «Ana3»",
         "HTTP 422: los nombres solo admiten letras",
         lambda: alta(ficha(nombres="Ana3"), 422))
    caso("CN-19", "RF02", "Tabla de decisión (coherencia entre campos)",
         "Tiempo de enfermedad mayor que la edad", "edad 30 · tiempo de enfermedad 40",
         "HTTP 422: no puede superar la edad",
         lambda: alta(ficha(edad=30, tiempo_enfermedad_anios=40), 422))
    caso("CN-20", "RF02", "Valores límite",
         "Puntaje Morisky-Green fuera de rango", "puntaje_morisky = 5",
         "HTTP 422", lambda: alta(ficha(puntaje_morisky=5), 422))
    caso("CN-21", "RF02", "Partición de equivalencia (campo obligatorio ausente)",
         "Ficha sin diagnóstico", "diagnostico omitido",
         "HTTP 422", lambda: alta(ficha(diagnostico=...), 422))

    print("\nRF03 · Registro de tomas (ventana de registro)")
    prog = ahora - timedelta(hours=1)

    def toma(estado, programada, registro=None, medicamento="Metformina 850 mg", **extra):
        cuerpo = {"medicamento": medicamento, "estado": estado,
                  "fecha_hora_programada": iso(programada), **extra}
        if registro is not None:
            cuerpo["fecha_hora_registro"] = iso(registro)
        return pedir("POST", "/api/adherencia/registros", cuerpo, t_pac)

    caso("CN-22", "RF03", "Transición de estados (ventana abierta)",
         "Toma marcada 15 min después de su hora", "tomada · registro = programada + 15 min",
         "HTTP 201 y retraso de 15 min",
         lambda: (lambda r: (r.estado == 201 and (r.cuerpo or {}).get("minutos_de_retraso") == 15,
                             f"HTTP {r.estado}. Retraso calculado: {(r.cuerpo or {}).get('minutos_de_retraso')} min"
                             if r.estado == 201 else f"HTTP {r.estado}. {mensaje(r)}", r.ms))(
             toma("tomada", prog, prog + timedelta(minutes=15), medicamento="CN Prueba ventana")))
    caso("CN-23", "RF03", "Valores límite (apertura de la ventana)",
         "Toma marcada 61 min antes de su hora", "tomada · registro = programada − 61 min",
         "HTTP 422 «Fuera de la ventana de registro…»",
         lambda: esperar_estado(toma("tomada", prog, prog - timedelta(minutes=61)), 422, "ventana"))
    caso("CN-24", "RF03", "Valores límite (cierre de la ventana)",
         "Toma marcada 3 h 01 min después", "tomada · registro = programada + 3 h 1 min",
         "HTTP 422 «Fuera de la ventana de registro…»",
         lambda: esperar_estado(toma("tomada", ahora - timedelta(hours=4),
                                     ahora - timedelta(minutes=59)), 422, "ventana"))
    caso("CN-25", "RF03", "Partición de equivalencia (omisión válida)",
         "Toma omitida con motivo", "omitida · motivo «olvido»",
         "HTTP 201",
         lambda: esperar_estado(toma("omitida", prog, motivo_omision="olvido",
                                     medicamento="CN Prueba omision"), 201))
    caso("CN-26", "RF03", "Tabla de decisión (estado × hora)",
         "Toma omitida con hora de toma", "omitida · con fecha_hora_registro",
         "HTTP 422", lambda: esperar_estado(toma("omitida", prog, prog), 422))
    caso("CN-27", "RF03", "Partición de equivalencia (reloj adelantado)",
         "Hora de registro en el futuro", "tomada · registro = ahora + 30 min",
         "HTTP 422 «posterior a la hora actual»",
         lambda: esperar_estado(toma("tomada", ahora + timedelta(minutes=30), ahora + timedelta(minutes=30)),
                                422, "posterior a la hora actual"))

    def idempotencia():
        p = ahora - timedelta(minutes=30)
        a = toma("tomada", p, p + timedelta(minutes=5), medicamento="CN Idempotencia")
        b = toma("tomada", p, p + timedelta(minutes=6), medicamento="CN Idempotencia")
        regs = pedir("GET", "/api/adherencia/mis-registros?limite=100", token=t_pac).cuerpo or []
        n = sum(1 for x in regs if x.get("medicamento") == "CN Idempotencia")
        return (a.estado in (200, 201) and b.estado in (200, 201) and n == 1,
                f"Envíos: HTTP {a.estado} y {b.estado}. Registros resultantes: {n}")
    caso("CN-28", "RF03", "Partición de equivalencia (reenvío)",
         "La misma toma enviada dos veces (cola sin conexión)", "Dos envíos del mismo medicamento y hora",
         "Un solo registro (el segundo actualiza al primero)", idempotencia)

    def lote():
        regs = [{"medicamento": f"CN Lote {i}", "estado": "omitida",
                 "fecha_hora_programada": iso(ahora - timedelta(hours=2, minutes=i)),
                 "motivo_omision": "olvido"} for i in range(3)]
        r = pedir("POST", "/api/adherencia/registros/lote", regs, t_pac)
        c = r.cuerpo or {}
        return (r.estado in (200, 201) and c.get("creados") == 3,
                f"HTTP {r.estado}. Creados: {c.get('creados')}, actualizados: {c.get('actualizados')}", r.ms)
    caso("CN-29", "RF03", "Caso de uso (sincronización diferida)",
         "Envío en lote de tres tomas guardadas sin conexión", "Lote de 3 tomas omitidas",
         "HTTP 200/201 con 3 creados", lote)

    print("\nRF04 y RF06 · Predicción de riesgo y explicación (componente de IA)")
    p1 = (pedir("GET", "/api/pacientes?busqueda=P-001", token=t_med).cuerpo or {}).get("items", [{}])[0]
    id_p1 = p1.get("id_paciente", "")

    def prediccion():
        r = pedir("GET", f"/api/prediccion/pacientes/{id_p1}", token=t_med)
        c = r.cuerpo or {}
        prob, nivel = c.get("probabilidad"), c.get("nivel")
        contrib = c.get("contribuciones") or []
        ok = (r.estado == 200 and isinstance(prob, (int, float)) and 0 <= prob <= 1
              and nivel in ("bajo", "medio", "alto") and len(contrib) > 0)
        return ok, (f"HTTP {r.estado}. Probabilidad {prob}, nivel «{nivel}», "
                    f"{len(contrib)} contribuciones SHAP"), r.ms
    caso("CN-30", "RF04 · RF06", "Caso de uso (escenario principal)",
         "Riesgo y explicación de la ficha P-001", "GET predicción de P-001",
         "Probabilidad entre 0 y 1, nivel bajo/medio/alto y contribuciones SHAP", prediccion)

    def determinismo():
        a = pedir("GET", f"/api/prediccion/pacientes/{id_p1}", token=t_med).cuerpo or {}
        b = pedir("GET", f"/api/prediccion/pacientes/{id_p1}", token=t_med).cuerpo or {}
        return (a.get("probabilidad") == b.get("probabilidad") is not None,
                f"Consultas: {a.get('probabilidad')} y {b.get('probabilidad')}")
    caso("CN-31", "RF04", "Partición de equivalencia (misma entrada)",
         "La misma ficha consultada dos veces", "Dos consultas de P-001",
         "La misma probabilidad (resultado reproducible)", determinismo)

    def imputadas():
        cuerpo = ficha(nivel_educativo=..., convivencia=..., apoyo_familiar=...,
                       tiempo_enfermedad_anios=...)
        r = pedir("POST", "/api/pacientes", cuerpo, t_med)
        idp = (r.cuerpo or {}).get("id_paciente")
        c = pedir("GET", f"/api/prediccion/pacientes/{idp}", token=t_med).cuerpo or {}
        imp = c.get("variables_imputadas") or []
        return (len(imp) >= 3, f"Variables imputadas declaradas: {', '.join(imp) or 'ninguna'}")
    caso("CN-32", "RF04", "Partición de equivalencia (datos opcionales ausentes)",
         "Ficha sin datos sociales ni tiempo de enfermedad", "Ficha mínima obligatoria",
         "La predicción declara qué variables imputó", imputadas)

    print("\nRF05 · Alertas tempranas")
    estado_alerta: dict = {}

    def alerta_omisiones():
        r = pedir("POST", "/api/pacientes", ficha(), t_med)
        nuevo = r.cuerpo
        acc = pedir("POST", f"/api/pacientes/{nuevo['id_paciente']}/acceso", token=t_med).cuerpo
        t_nuevo = login(acc["correo"], "paciente", acc["contrasena_temporal"])
        for i in range(3):
            pedir("POST", "/api/adherencia/registros",
                  {"medicamento": "CN Alerta", "estado": "omitida", "motivo_omision": "olvido",
                   "fecha_hora_programada": iso(ahora - timedelta(hours=6 - i))}, t_nuevo)
        bandeja = pedir("GET", "/api/alertas", token=t_med).cuerpo or {}
        lista = bandeja.get("alertas", bandeja) if isinstance(bandeja, dict) else bandeja
        propias = [a for a in lista if a.get("id_paciente") == nuevo["id_paciente"]]
        estado_alerta.update(paciente=nuevo, token=t_nuevo, alertas=propias)
        tipos = sorted({a.get("tipo") for a in propias})
        return ("omisiones_seguidas" in tipos,
                f"Alertas del paciente {nuevo['codigo_anonimizado']}: {', '.join(tipos) or 'ninguna'}")
    caso("CN-33", "RF05", "Caso de uso (regla de negocio)",
         "Tres omisiones seguidas de un paciente", "3 tomas omitidas consecutivas",
         "Aparece la alerta «omisiones seguidas» en la bandeja del médico", alerta_omisiones)

    def atender():
        alerta = next(a for a in estado_alerta["alertas"] if a.get("tipo") == "omisiones_seguidas")
        r = pedir("POST", f"/api/alertas/{alerta['id_alerta']}/atender",
                  {"nota": "Llamada al paciente; se reforzó la pauta."}, t_med)
        bandeja = pedir("GET", "/api/alertas", token=t_med).cuerpo or {}
        lista = bandeja.get("alertas", bandeja) if isinstance(bandeja, dict) else bandeja
        sigue = any(a.get("id_alerta") == alerta["id_alerta"] for a in lista)
        return (r.estado == 200 and not sigue,
                f"HTTP {r.estado}. Estado: {(r.cuerpo or {}).get('estado')}. "
                f"{'Sigue' if sigue else 'Ya no está'} en pendientes")
    caso("CN-34", "RF05", "Transición de estados (abierta → atendida)",
         "El médico registra lo que hizo", "Nota de atención",
         "Estado «atendida» y sale de la bandeja de pendientes", atender)

    print("\nRF07 · Reportes generales")
    caso("CN-35", "RF07", "Caso de uso",
         "Indicadores generales del consultorio", "GET reporte general",
         "HTTP 200 con indicadores",
         lambda: (lambda r: (r.estado == 200 and "indicadores" in (r.cuerpo or {}),
                             f"HTTP {r.estado}. Pacientes activos: "
                             f"{((r.cuerpo or {}).get('indicadores') or {}).get('pacientes_activos')}", r.ms))(
             pedir("GET", "/api/reportes/general", token=t_med)))

    def csv_():
        r = pedir("GET", "/api/reportes/general.csv", token=t_med)
        primera = r.texto.splitlines()[0] if r.texto else ""
        return (r.estado == 200 and "text/csv" in r.cabeceras.get("content-type", "")
                and "Codigo" in primera,
                f"HTTP {r.estado}. {r.cabeceras.get('content-type')}. "
                f"{len(r.texto.splitlines()) - 1} filas. Encabezado: {primera[:60]}…")
    caso("CN-36", "RF07", "Caso de uso", "Exportación del reporte", "GET reporte CSV",
         "Archivo CSV con encabezado y una fila por paciente", csv_)

    print("\nRF09 · Acompañamiento familiar")
    familia: dict = {}

    def invitar():
        r = pedir("POST", "/api/familiares/invitaciones",
                  {"nombre_invitado": "Carlos", "parentesco": "hijo"}, t_pac)
        codigo = (r.cuerpo or {}).get("codigo_invitacion") or ""
        familia["codigo"] = codigo
        return r.estado == 201 and len(codigo) == 8, f"HTTP {r.estado}. Código de {len(codigo)} caracteres"
    caso("CN-37", "RF09", "Caso de uso", "El paciente invita a un familiar", "Carlos · hijo",
         "HTTP 201 y código de invitación de 8 caracteres", invitar)

    def registrar_familiar():
        r = pedir("POST", "/api/familiares/registro",
                  {"codigo": familia["codigo"], "nombres": "Carlos", "apellidos": "Vasquez",
                   "correo": f"carlos.cn{int(time.time())}@correo.pe", "contrasena": "Familiar-2026"})
        familia["token"] = (r.cuerpo or {}).get("access_token")
        return r.estado == 201 and familia["token"], f"HTTP {r.estado}. {'Cuenta creada con sesión' if r.estado == 201 else mensaje(r)}"
    caso("CN-38", "RF09", "Partición de equivalencia (código válido)",
         "Alta del familiar con el código", "Código vigente + datos válidos",
         "HTTP 201 y sesión iniciada", registrar_familiar)
    caso("CN-39", "RF09", "Partición de equivalencia (código no válido)",
         "Alta con un código inexistente", "codigo = ZZZZ9999",
         "Rechazo «El código no es válido o ya venció»",
         lambda: (lambda r: (r.estado in (400, 404, 409, 422) and "código" in r.texto.lower(),
                             f"HTTP {r.estado}. {mensaje(r)}"))(
             pedir("POST", "/api/familiares/registro",
                   {"codigo": "ZZZZ9999", "nombres": "Luis", "apellidos": "Perez",
                    "correo": "luis.cn@correo.pe", "contrasena": "Familiar-2026"})))

    def confirmar():
        t_fam = login(FAMILIAR, "familiar", clave)
        pendientes = pedir("GET", "/api/familiares/tomas-por-confirmar", token=t_fam).cuerpo or []
        if not pendientes:
            return False, "No había tomas por confirmar"
        r = pedir("POST", f"/api/familiares/tomas/{pendientes[0]['id_registro']}/confirmacion", token=t_fam)
        return r.estado in (200, 201, 204), f"HTTP {r.estado}. Confirmada la toma de {pendientes[0].get('medicamento')}"
    caso("CN-40", "RF09", "Caso de uso", "El familiar confirma una toma que presenció",
         f"{FAMILIAR} · primera toma pendiente", "Confirmación aceptada", confirmar)

    print("\nRF10 · Recuperación de contraseña")
    caso("CN-41", "RF10", "Partición de equivalencia (correo desactivado en modo local)",
         "Solicitud de enlace sin servidor de correo", MEDICO,
         "HTTP 202 que remite al consultorio, sin fingir un envío",
         lambda: (lambda r: (r.estado == 202 and (r.cuerpo or {}).get("correo_habilitado") is False,
                             f"HTTP {r.estado}. {mensaje(r)}"))(
             pedir("POST", "/api/auth/recuperacion", {"correo": MEDICO})))
    caso("CN-42", "RF10", "Partición de equivalencia (enlace no válido)",
         "Confirmación con un enlace inventado", "testigo aleatorio",
         "Rechazo «El enlace no es válido o ya venció»",
         lambda: (lambda r: (r.estado in (400, 401, 404, 422) and "enlace" in r.texto.lower(),
                             f"HTTP {r.estado}. {mensaje(r)}"))(
             pedir("POST", "/api/auth/recuperacion/confirmar",
                   {"testigo": "x" * 43, "contrasena": "NuevaClave-2026"})))

    print("\nRNF01 · Seguridad y protección")
    caso("CN-43", "RNF01", "Partición de equivalencia (sin credenciales)",
         "Listado de pacientes sin iniciar sesión", "Sin token",
         "HTTP 401", lambda: esperar_estado(pedir("GET", "/api/pacientes"), 401))
    caso("CN-44", "RNF01", "Partición de equivalencia (token alterado)",
         "Token manipulado", "Token del médico con la firma alterada",
         "HTTP 401", lambda: esperar_estado(pedir("GET", "/api/pacientes", token=t_med[:-4] + "AAAA"), 401))
    caso("CN-45", "RNF01", "Tabla de decisión (rol × recurso)",
         "Un paciente pide el listado del médico", "Token de paciente → /api/pacientes",
         "HTTP 403", lambda: esperar_estado(pedir("GET", "/api/pacientes", token=t_pac), 403))

    def ficha_ajena():
        otro = (pedir("GET", "/api/pacientes?busqueda=P-002", token=t_med).cuerpo or {}).get("items", [{}])[0]
        return esperar_estado(pedir("GET", f"/api/pacientes/{otro.get('id_paciente')}", token=t_pac), 403)
    caso("CN-46", "RNF01", "Tabla de decisión (rol × recurso)",
         "Un paciente pide la ficha de otro paciente", "Token de P-001 → ficha de P-002",
         "HTTP 403", ficha_ajena)
    caso("CN-47", "RNF01", "Tabla de decisión (rol × recurso)",
         "El familiar pide la ficha clínica", "Token de familiar → ficha de P-001",
         "HTTP 403", lambda: esperar_estado(
             pedir("GET", f"/api/pacientes/{id_p1}", token=login(FAMILIAR, "familiar", clave)), 403))

    def inyeccion():
        r = pedir("GET", "/api/pacientes?busqueda=%27%20OR%201%3D1%20--", token=t_med)
        total = (r.cuerpo or {}).get("total")
        return r.estado == 200 and total == 0, f"HTTP {r.estado}. Resultados: {total}"
    caso("CN-48", "RNF01", "Partición de equivalencia (entrada maliciosa)",
         "Inyección SQL en la búsqueda", "busqueda = «' OR 1=1 --»",
         "HTTP 200 sin resultados: el texto se trata como dato", inyeccion)

    print("\nRF02 · Baja del paciente")

    def baja():
        nuevo, t_nuevo = estado_alerta["paciente"], estado_alerta["token"]
        r = pedir("DELETE", f"/api/pacientes/{nuevo['id_paciente']}", token=t_med)
        lista = pedir("GET", f"/api/pacientes?busqueda={nuevo['codigo_anonimizado']}", token=t_med).cuerpo or {}
        intento = pedir("POST", "/api/adherencia/registros",
                        {"medicamento": "CN Baja", "estado": "omitida", "motivo_omision": "olvido",
                         "fecha_hora_programada": iso(ahora - timedelta(hours=1))}, t_nuevo)
        ok = r.estado in (200, 204) and lista.get("total") == 0 and intento.estado >= 400
        return ok, (f"Baja: HTTP {r.estado}. En el listado: {lista.get('total')}. "
                    f"Nuevo registro de toma: HTTP {intento.estado} ({mensaje(intento)[:60]})")
    caso("CN-49", "RF02", "Transición de estados (activo → dado de baja)",
         "Dar de baja a un paciente", "DELETE ficha del paciente de CN-33",
         "Sale del listado y ya no puede registrar tomas; el historial se conserva", baja)

    print("\nRNF02 · Desempeño (tiempo de respuesta, 10 repeticiones)")
    operaciones = {
        "Inicio de sesión": lambda: pedir("POST", "/api/auth/login",
                                         {"correo": MEDICO, "contrasena": clave, "perfil": "medico"}),
        "Listado del panel": lambda: pedir("GET", "/api/pacientes", token=t_med),
        "Ficha con predicción y SHAP": lambda: pedir("GET", f"/api/prediccion/pacientes/{id_p1}", token=t_med),
        "Registro de una toma": lambda: toma("omitida", ahora - timedelta(hours=1, minutes=40),
                                             motivo_omision="olvido", medicamento="CN Desempeño"),
    }
    for n, (nombre, op) in enumerate(operaciones.items(), start=50):
        def medir(op=op):
            tiempos = [op().ms for _ in range(10)]
            p95 = sorted(tiempos)[int(0.95 * len(tiempos)) - 1]
            media = statistics.mean(tiempos)
            return p95 <= 2000, f"Media {media:.0f} ms · p95 {p95:.0f} ms · máx {max(tiempos):.0f} ms", media
        caso(f"CN-{n}", "RNF02", "Prueba de desempeño", nombre, "10 peticiones seguidas",
             "p95 ≤ 2000 ms", medir)


# ---------------------------------------------------------------------------
# Casos del panel (interfaz)
# ---------------------------------------------------------------------------
def casos_ui(clave: str) -> None:
    from playwright.sync_api import sync_playwright

    print("\nInterfaz del panel (validaciones en pantalla)")
    with sync_playwright() as p:
        nav = p.chromium.launch(channel="msedge")
        pg = nav.new_page(viewport={"width": 1366, "height": 860})

        def entrar(contrasena):
            pg.goto(PANEL)
            pg.fill("input[name=correo]", MEDICO)
            pg.fill("input[name=contrasena]", contrasena)
            pg.get_by_role("button", name="Ingresar").click()

        def login_erroneo():
            entrar("contrasena-erronea")
            pg.wait_for_selector(".mensaje--error")
            texto = pg.locator(".mensaje--error").first.inner_text()
            return "incorrectos" in texto, f"Aviso en pantalla: «{texto}»"
        caso("CN-54", "RF01", "Partición de equivalencia (UI)",
             "Aviso de credenciales incorrectas en el panel", "Contraseña errónea",
             "Mensaje visible «Usuario o contraseña incorrectos.»", login_erroneo)

        entrar(clave)
        pg.wait_for_url("**/panel")

        def formulario(cambios: dict, campo: str, fragmento: str):
            pg.goto(PANEL + "/panel")
            pg.get_by_role("button", name="Registrar paciente").click()
            pg.fill("input[name=nombres]", "Prueba")
            pg.fill("input[name=apellidos]", "Interfaz")
            for k, v in {"edad": "64", "numero_farmacos": "7", "tomas_dia": "4", **cambios}.items():
                pg.fill(f"input[name={k}]", v)
            pg.get_by_role("button", name="Registrar paciente").last.click()
            pg.wait_for_timeout(500)
            aviso = pg.locator(f"input[name={campo}]").locator(
                "xpath=ancestor::label[1]").inner_text()
            sigue_abierto = pg.locator(".modal").count() > 0
            return (fragmento.lower() in aviso.lower() and sigue_abierto,
                    f"Mensaje junto al campo: «{aviso.splitlines()[-1]}». Formulario sin enviar: {sigue_abierto}")

        caso("CN-55", "RF02", "Valores límite (UI)", "Edad 17 en el formulario", "edad = 17",
             "Mensaje junto al campo y el formulario no se envía",
             lambda: formulario({"edad": "17"}, "edad", "entre 18 y 120"))
        caso("CN-56", "RF02", "Valores límite (UI)", "4 fármacos en el formulario", "numero_farmacos = 4",
             "Mensaje «solo incluye pacientes polimedicados» y no se envía",
             lambda: formulario({"numero_farmacos": "4"}, "numero_farmacos", "polimedicados"))
        caso("CN-57", "RF02", "Tabla de decisión (UI)", "Controles perdidos > programados",
             "programados 4 · perdidos 6", "Mensaje «No puede superar a los programados» y no se envía",
             lambda: formulario({"controles_programados_6m": "4", "controles_perdidos_6m": "6"},
                                "controles_perdidos_6m", "superar"))

        def solo_digitos():
            pg.goto(PANEL + "/panel")
            pg.get_by_role("button", name="Registrar paciente").click()
            pg.fill("input[name=edad]", "")
            pg.type("input[name=edad]", "6a4")
            valor = pg.input_value("input[name=edad]")
            return valor == "64", f"Tecleado «6a4», queda «{valor}»"
        caso("CN-58", "RF02", "Partición de equivalencia (UI, carácter no válido)",
             "Letra tecleada en un campo numérico", "edad: «6a4»",
             "La letra no se admite; queda «64»", solo_digitos)

        def descarga():
            pg.goto(PANEL + "/descargar")
            enlace = pg.get_by_role("link", name="Descargar para Android (APK)")
            href = enlace.get_attribute("href")
            qr = pg.locator("img[alt='Código QR de esta página']").count()
            return bool(href) and qr == 1, f"Enlace al APK: {href}. Código QR visible: {qr == 1}"
        caso("CN-59", "Descarga", "Caso de uso (UI)", "Página pública de descarga de la app",
             "/descargar sin iniciar sesión", "Botón de descarga y código QR visibles", descarga)
        nav.close()


# ---------------------------------------------------------------------------
# Informe
# ---------------------------------------------------------------------------
def informe(inicio: datetime) -> None:
    con_ms = [c for c in CASOS]
    with open(AQUI / "resultados_caja_negra.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["ID", "Requisito", "Técnica", "Caso", "Entrada", "Resultado esperado",
                    "Resultado obtenido", "Estado"])
        for c in con_ms:
            w.writerow([c.id, c.requisito, c.tecnica, c.descripcion, c.entrada, c.esperado,
                        c.obtenido, "Conforme" if c.conforme else "No conforme"])
    total, ok = len(CASOS), sum(c.conforme for c in CASOS)
    lineas = [
        f"Ejecución: {inicio:%d/%m/%Y %H:%M} · API {API} · panel {PANEL}",
        f"Casos: {total} · conformes: {ok} · no conformes: {total - ok}",
        "",
        "| ID | Req. | Técnica | Caso | Entrada | Resultado esperado | Resultado obtenido | Estado |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for c in CASOS:
        celdas = [c.id, c.requisito, c.tecnica, c.descripcion, c.entrada, c.esperado, c.obtenido,
                  "Conforme" if c.conforme else "**No conforme**"]
        lineas.append("| " + " | ".join(s.replace("|", "/") for s in celdas) + " |")
    (AQUI / "resultados_caja_negra.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"\n{ok}/{total} conformes. Resultados en {AQUI / 'resultados_caja_negra.md'}")


def main() -> int:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(description="Pruebas de caja negra del sistema.")
    parser.add_argument("--ui", action="store_true", help="Incluye los casos del panel (Playwright).")
    args = parser.parse_args()
    clave = os.environ.get("CLAVE_DEMO")
    if not clave:
        print("Defina CLAVE_DEMO con la contraseña de las cuentas de demostración.", file=sys.stderr)
        return 2
    inicio = datetime.now()
    casos_api(clave)
    if args.ui:
        casos_ui(clave)
    informe(inicio)
    return 0 if all(c.conforme for c in CASOS) else 1


if __name__ == "__main__":
    sys.exit(main())
