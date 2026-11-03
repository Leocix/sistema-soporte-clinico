"""Código fuente numerado de cada función analizada por caja blanca.

    python codigo.py

Extrae la función tal como está en el repositorio y la dibuja con su número
de línea real en `codigo/CB-XX.png`. Se genera como imagen para que el anexo
muestre el código con letra de ancho fijo sin cambiar la fuente del documento.
Si el código cambia, basta con volver a ejecutarlo.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
SALIDA = AQUI / "codigo"

FUNCIONES = {
    "CB-01": ("backend-api/app/schemas/adherencia_schema.py", "_coherencia_clinica"),
    "CB-02": ("backend-api/app/services/riesgo.py", "clasificar"),
    "CB-03": ("backend-api/app/services/alertas.py", "evaluar_paciente"),
    "CB-04": ("backend-api/app/services/acceso.py", "obtener_paciente_autorizado"),
    "CB-05": ("ml-service/app/modelo.py", "predecir"),
    "CB-06": ("ml-service/app/modelo.py", "nivel"),
    "CB-07a": ("frontend-web/src/services/validacionPaciente.js", "export function limpiarAlEscribir("),
    "CB-07b": ("frontend-web/src/services/validacionPaciente.js", "function limpiarNumero("),
    "CB-08": ("app-movil/lib/widgets/tarjeta_toma.dart", "  Widget build(BuildContext context) {"),
    "CB-09": ("app-movil/lib/widgets/tarjeta_toma.dart", "class _Respuesta extends StatelessWidget {"),
    "CB-10": ("app-movil/lib/services/sincronizacion.dart", "  Future<bool> registrar(Toma toma) async {"),
    "CB-11": ("app-movil/lib/services/sincronizacion.dart", "  Future<ResultadoSincronizacion> sincronizar() async {"),
}


def rango_python(texto: str, nombre: str) -> tuple[int, int]:
    nodo = next(n for n in ast.walk(ast.parse(texto))
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == nombre)
    inicio = min([d.lineno for d in nodo.decorator_list] + [nodo.lineno])
    return inicio, nodo.end_lineno


def rango_llaves(lineas: list[str], firma: str) -> tuple[int, int]:
    """Desde la línea que contiene la firma hasta la llave que la cierra."""
    inicio = next(i for i, l in enumerate(lineas) if firma in l)
    nivel, abierto = 0, False
    for i in range(inicio, len(lineas)):
        sin_cadenas = re.sub(r"'[^']*'|\"[^\"]*\"|//.*", "", lineas[i])
        nivel += sin_cadenas.count("{") - sin_cadenas.count("}")
        abierto = abierto or "{" in sin_cadenas
        if abierto and nivel <= 0:
            return inicio + 1, i + 1
    raise ValueError(firma)


def dibujar(clave: str, archivo: str, lineas: list[str], inicio: int) -> None:
    ancho = max(len(l) for l in lineas) + 7
    fig = plt.figure(figsize=(max(7.5, ancho * 0.075), 0.17 * len(lineas) + 0.6))
    fig.text(0.01, 0.995, f"{clave} · {archivo}", va="top", fontsize=8.5, fontweight="bold",
             family="DejaVu Sans")
    for k, linea in enumerate(lineas):
        y = 1 - (k + 1.6) / (len(lineas) + 2)
        fig.text(0.01, y, f"{inicio + k:>4}", va="center", fontsize=7.5, family="DejaVu Sans Mono",
                 color="#777")
        fig.text(0.07, y, linea.replace("\t", "    "), va="center", fontsize=7.5,
                 family="DejaVu Sans Mono", color="#111")
    fig.savefig(SALIDA / f"{clave}.png", dpi=180, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def main() -> None:
    SALIDA.mkdir(exist_ok=True)
    for clave, (archivo, objetivo) in FUNCIONES.items():
        texto = (RAIZ / archivo).read_text(encoding="utf-8")
        lineas = texto.splitlines()
        if archivo.endswith(".py"):
            a, b = rango_python(texto, objetivo)
        else:
            a, b = rango_llaves(lineas, objetivo)
        dibujar(clave, archivo, lineas[a - 1:b], a)
        print(f"{clave}: {archivo} líneas {a}-{b}")


if __name__ == "__main__":
    main()
