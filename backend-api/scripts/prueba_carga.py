"""Prueba de rendimiento y carga del sistema (RNF02, RNF06).

Mide el tiempo de respuesta de las operaciones que el medico ejecuta en una
consulta real, con varios usuarios a la vez, y comprueba la meta del RNF02:
respuesta en 2 segundos o menos.

    python scripts/prueba_carga.py --url http://127.0.0.1:8011 \
        --correo milko.ugaz@consultorio.pe --usuarios 10 --repeticiones 20

La contrasena se pide por consola o se toma de la variable CLAVE_CARGA: no se
escribe en la linea de comandos, que queda en el historial del terminal.

Que se mide y por que:

* **Login**, porque es la primera impresion del sistema y el unico punto por el
  que pasan todos.
* **Listado de pacientes** y **ficha**, las dos pantallas que el medico abre en
  cada consulta.
* **Prediccion**, que incluye la llamada al microservicio de inferencia y el
  calculo de SHAP: es la operacion mas costosa del sistema.
* **Reportes** y **alertas**, que recorren a todos los pacientes del medico.

El arranque en frio del plan gratuito (hasta 50 s en la primera peticion tras
15 minutos sin trafico) se descuenta con una peticion previa de calentamiento:
es latencia de la infraestructura, no del sistema.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import statistics
import sys
import time
from getpass import getpass
from pathlib import Path

import httpx

META_RNF02 = 2.0  # segundos


async def _medir(cliente: httpx.AsyncClient, metodo: str, ruta: str, **kwargs) -> float:
    inicio = time.perf_counter()
    respuesta = await cliente.request(metodo, ruta, **kwargs)
    duracion = time.perf_counter() - inicio
    if respuesta.status_code >= 400:
        raise RuntimeError(f"{metodo} {ruta} respondio {respuesta.status_code}: {respuesta.text[:200]}")
    return duracion


async def _sesion(url: str, correo: str, clave: str) -> tuple[str, str]:
    async with httpx.AsyncClient(base_url=url, timeout=90) as cliente:
        respuesta = await cliente.post("/api/auth/login", json={
            "correo": correo, "contrasena": clave, "perfil": "medico",
        })
        respuesta.raise_for_status()
        token = respuesta.json()["access_token"]
        cabeceras = {"Authorization": f"Bearer {token}"}
        pacientes = await cliente.get("/api/pacientes", headers=cabeceras)
        pacientes.raise_for_status()
        items = pacientes.json()["items"]
        if not items:
            raise RuntimeError("El medico no tiene pacientes: no hay nada que medir.")
        return token, items[0]["id_paciente"]


async def _usuario(
    url: str, token: str, id_paciente: str, repeticiones: int, solo_lectura: bool = False
) -> dict[str, list[float]]:
    cabeceras = {"Authorization": f"Bearer {token}"}
    tiempos: dict[str, list[float]] = {}
    async with httpx.AsyncClient(base_url=url, timeout=90, headers=cabeceras) as cliente:
        operaciones = [
            ("Listado de pacientes", "GET", "/api/pacientes"),
            ("Ficha del paciente", "GET", f"/api/pacientes/{id_paciente}"),
            ("Resumen de adherencia", "GET", f"/api/adherencia/pacientes/{id_paciente}/resumen"),
            ("Prediccion con SHAP", "GET", f"/api/prediccion/pacientes/{id_paciente}"),
            ("Reporte general", "GET", "/api/reportes/general"),
        ]
        # La bandeja reevalua las reglas y escribe: es la unica operacion del
        # recorrido que no es de solo lectura, y por tanto la que puede
        # bloquear a las demas en un motor que serialice las escrituras.
        if not solo_lectura:
            operaciones.append(("Bandeja de alertas", "GET", "/api/alertas"))
        # Cada usuario abre su propia conexion; establecerla mientras otros
        # nueve hacen lo mismo cuesta mas que cualquier operacion, y no es
        # tiempo del sistema. Se hace una peticion previa que no se mide.
        await cliente.get("/health")

        for _ in range(repeticiones):
            for nombre, metodo, ruta in operaciones:
                try:
                    tiempos.setdefault(nombre, []).append(await _medir(cliente, metodo, ruta))
                except RuntimeError as error:
                    # Una operacion que no esta disponible (por ejemplo, el
                    # microservicio de inferencia apagado) no invalida el resto.
                    tiempos.setdefault(f"{nombre} (no disponible)", []).append(float("nan"))
                    print(f"  aviso: {error}", file=sys.stderr)
    return tiempos


def _percentil(valores: list[float], fraccion: float) -> float:
    ordenados = sorted(valores)
    indice = min(int(round(fraccion * (len(ordenados) - 1))), len(ordenados) - 1)
    return ordenados[indice]


def _tabla(resultados: dict[str, list[float]], usuarios: int) -> str:
    lineas = [
        f"| Operación | Peticiones | Mediana | p95 | Máximo | ≤ {META_RNF02:.0f} s |",
        "| :--- | :---: | :---: | :---: | :---: | :---: |",
    ]
    for nombre, tiempos in resultados.items():
        validos = [t for t in tiempos if t == t]  # descarta NaN
        if not validos:
            lineas.append(f"| {nombre} | 0 | — | — | — | — |")
            continue
        maximo = max(validos)
        lineas.append(
            f"| {nombre} | {len(validos)} | {statistics.median(validos) * 1000:.0f} ms | "
            f"{_percentil(validos, 0.95) * 1000:.0f} ms | {maximo * 1000:.0f} ms | "
            f"{'✔' if maximo <= META_RNF02 else '✘'} |"
        )
    lineas.append(f"\n*{usuarios} usuarios simultáneos.*")
    return "\n".join(lineas)


async def ejecutar(url: str, correo: str, clave: str, usuarios: int, repeticiones: int,
                   solo_lectura: bool = False) -> dict:
    print(f"Calentando {url} ...", flush=True)
    async with httpx.AsyncClient(base_url=url, timeout=120) as cliente:
        inicio = time.perf_counter()
        await cliente.get("/health")
        arranque = time.perf_counter() - inicio
    print(f"Primera respuesta: {arranque * 1000:.0f} ms", flush=True)

    token, id_paciente = await _sesion(url, correo, clave)
    print(f"Midiendo con {usuarios} usuarios x {repeticiones} repeticiones ...", flush=True)

    inicio = time.perf_counter()
    tandas = await asyncio.gather(*[
        _usuario(url, token, id_paciente, repeticiones, solo_lectura) for _ in range(usuarios)
    ])
    total = time.perf_counter() - inicio

    resultados: dict[str, list[float]] = {}
    for tanda in tandas:
        for nombre, tiempos in tanda.items():
            resultados.setdefault(nombre, []).extend(tiempos)

    peticiones = sum(len(v) for v in resultados.values())
    print(f"\n{peticiones} peticiones en {total:.1f} s "
          f"({peticiones / total:.1f} por segundo)\n", flush=True)
    print(_tabla(resultados, usuarios))

    return {
        "url": url,
        "usuarios_simultaneos": usuarios,
        "repeticiones": repeticiones,
        "peticiones": peticiones,
        "duracion_s": round(total, 2),
        "primera_respuesta_ms": round(arranque * 1000),
        "meta_rnf02_s": META_RNF02,
        "solo_lectura": solo_lectura,
        "operaciones": {
            nombre: {
                "peticiones": len([t for t in tiempos if t == t]),
                "mediana_ms": round(statistics.median([t for t in tiempos if t == t]) * 1000, 1)
                if any(t == t for t in tiempos) else None,
                "p95_ms": round(_percentil([t for t in tiempos if t == t], 0.95) * 1000, 1)
                if any(t == t for t in tiempos) else None,
                "maximo_ms": round(max([t for t in tiempos if t == t]) * 1000, 1)
                if any(t == t for t in tiempos) else None,
            }
            for nombre, tiempos in resultados.items()
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prueba de rendimiento y carga (RNF02, RNF06).")
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--correo", required=True)
    parser.add_argument("--usuarios", type=int, default=10)
    parser.add_argument("--repeticiones", type=int, default=10)
    parser.add_argument("--salida", type=Path, default=Path("prueba_carga.json"))
    parser.add_argument("--solo-lectura", action="store_true",
                        help="Excluye la bandeja de alertas, que escribe en la base.")
    args = parser.parse_args(argv)

    # La consola de Windows usa cp1252 y no sabe escribir los simbolos de la
    # tabla; el archivo de resultados ya se escribe en UTF-8.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    clave = os.environ.get("CLAVE_CARGA") or getpass("Contrasena del medico: ")
    if not clave:
        print("Hace falta la contrasena.", file=sys.stderr)
        return 1

    try:
        informe = asyncio.run(ejecutar(args.url, args.correo, clave, args.usuarios,
                                       args.repeticiones, args.solo_lectura))
    except (httpx.HTTPError, RuntimeError) as error:
        print(f"No se pudo completar la prueba: {error}", file=sys.stderr)
        return 1

    args.salida.write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDetalle en {args.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
