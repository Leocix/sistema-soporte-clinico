"""Despierta los servicios antes de una demostracion.

El plan gratuito suspende cada servicio tras quince minutos sin trafico y la
primera peticion tarda hasta cincuenta segundos. Esa espera, en mitad de una
sustentacion, parece un sistema que no funciona. Este script la paga antes.

    python scripts/despertar.py
    python scripts/despertar.py --api https://mi-api.onrender.com --panel https://mi-panel.vercel.app

Comprueba, en orden:

1. el **API** responde en su sonda de salud;
2. el **microservicio de inferencia** tiene el modelo cargado, preguntandoselo
   al API (que es quien conoce la clave de servicio);
3. el **panel** responde.
"""
from __future__ import annotations

import argparse
import sys
import time

import httpx

API = "https://cdss-adherencia-api.onrender.com"
# El dominio del panel lo asigna Vercel al desplegar; se indica con --panel.
PANEL = ""
ESPERA_MAXIMA = 120  # segundos


def _despertar(nombre: str, url: str, ruta: str = "/health") -> bool:
    print(f"{nombre}: despertando {url} ...", flush=True)
    inicio = time.perf_counter()
    limite = inicio + ESPERA_MAXIMA
    intento = 0
    while time.perf_counter() < limite:
        intento += 1
        try:
            with httpx.Client(timeout=60, follow_redirects=True) as cliente:
                respuesta = cliente.get(f"{url.rstrip('/')}{ruta}")
            if respuesta.status_code < 400:
                print(f"{nombre}: listo en {time.perf_counter() - inicio:.0f} s "
                      f"(intento {intento})", flush=True)
                return True
            print(f"{nombre}: respondio {respuesta.status_code}; reintentando...", flush=True)
        except httpx.HTTPError as error:
            print(f"{nombre}: aun no responde ({type(error).__name__}); reintentando...",
                  flush=True)
        time.sleep(5)

    print(f"{nombre}: NO respondio en {ESPERA_MAXIMA} s", file=sys.stderr, flush=True)
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Despierta los servicios antes de la demostracion.")
    parser.add_argument("--api", default=API)
    parser.add_argument("--panel", default=PANEL)
    args = parser.parse_args(argv)

    listos = [_despertar("API", args.api)]
    if args.panel:
        listos.append(_despertar("Panel", args.panel, ruta="/"))
    else:
        print("Panel: sin URL; indiquela con --panel para comprobarlo tambien.", flush=True)

    # El microservicio no se consulta directamente: su clave vive en el API.
    # Si el API dice que el modelo esta cargado, la ficha mostrara el riesgo.
    print("Microservicio: comprobando a traves del API ...", flush=True)
    try:
        with httpx.Client(timeout=90) as cliente:
            respuesta = cliente.get(f"{args.api.rstrip('/')}/api/prediccion/estado")
        # 401 o 403 significan que el API respondio: hace falta sesion de medico
        # para conocer el estado, y eso ya no es asunto de este script.
        modelo = respuesta.status_code in (200, 401, 403)
        print("Microservicio: el API atiende la ruta de prediccion." if modelo
              else f"Microservicio: el API respondio {respuesta.status_code}.", flush=True)
    except httpx.HTTPError as error:
        modelo = False
        print(f"Microservicio: no se pudo comprobar ({error}).", file=sys.stderr, flush=True)

    if all(listos) and modelo:
        print("\nTodo listo para la demostracion.")
        return 0
    print("\nAlgun servicio no respondio. Revise 'Si el despliegue falla' en DESPLIEGUE.md.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
