"""Grafos de flujo de las funciones analizadas en las pruebas de caja blanca.

    python grafos.py

Cada grafo se declara como nodos (número → qué ocurre) y aristas. El script
comprueba que V(G) = A − N + 2 coincide con la complejidad declarada (la que
mide `radon cc` o la que se cuenta a mano en JavaScript y Dart) y dibuja el
grafo en `grafos/CB-XX.png`. Las condiciones compuestas (a and b) se separan
en un nodo por condición, como exige el análisis de caminos básicos.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch  # noqa: E402

SALIDA = Path(__file__).resolve().parent / "grafos"

GRAFOS = {
    "CB-01": {
        "titulo": "RegistroTomaCreate._coherencia_clinica",
        "vg": 10,
        "nodos": {
            1: "inicio", 2: "¿estado cumplido?", 3: "¿sin hora de registro?",
            4: "error: falta la hora", 5: "¿estado cumplido?", 6: "¿con hora de registro?",
            7: "¿desfase < −60 min?", 8: "¿desfase > 3 h?", 9: "error: fuera de la ventana",
            10: "¿hora > ahora + 5 min?", 11: "error: hora futura", 12: "¿estado omitida?",
            13: "¿con hora de registro?", 14: "error: omitida con hora", 15: "devuelve el registro",
            16: "salida",
        },
        "aristas": [(1, 2), (2, 3), (2, 5), (3, 4), (3, 5), (4, 16), (5, 6), (5, 12), (6, 7),
                    (6, 12), (7, 9), (7, 8), (8, 9), (8, 10), (9, 16), (10, 11), (10, 12),
                    (11, 16), (12, 13), (12, 15), (13, 14), (13, 15), (14, 16), (15, 16)],
    },
    "CB-02": {
        "titulo": "riesgo.clasificar",
        "vg": 6,
        "nodos": {1: "inicio", 2: "¿tasa nula?", 3: "sin_datos", 4: "¿tasa < 60?", 5: "¿racha ≥ 3?",
                  6: "alto", 7: "¿tasa < 80?", 8: "¿racha ≥ 2?", 9: "medio", 10: "bajo", 11: "salida"},
        "aristas": [(1, 2), (2, 3), (2, 4), (3, 11), (4, 6), (4, 5), (5, 6), (5, 7), (6, 11),
                    (7, 9), (7, 8), (8, 9), (8, 10), (9, 11), (10, 11)],
    },
    "CB-03": {
        "titulo": "alertas.evaluar_paciente",
        "vg": 11,
        "nodos": {1: "indicadores y alertas abiertas", 2: "¿racha ≥ 3?", 3: "registrar omisiones",
                  4: "¿tasa no nula?", 5: "¿≥ 5 tomas resueltas?", 6: "¿tasa < 60?",
                  7: "registrar adherencia baja", 8: "¿hay predicción?", 9: "¿nivel alto?",
                  10: "registrar riesgo predicho", 11: "¿quedan alertas abiertas?",
                  12: "¿sigue vigente?", 13: "¿es de riesgo predicho?", 14: "¿falta la predicción?",
                  15: "marcar resuelta", 16: "devuelve las abiertas"},
        "aristas": [(1, 2), (2, 3), (2, 4), (3, 4), (4, 5), (4, 8), (5, 6), (5, 8), (6, 7), (6, 8),
                    (7, 8), (8, 9), (8, 11), (9, 10), (9, 11), (10, 11), (11, 12), (11, 16),
                    (12, 11), (12, 13), (13, 14), (13, 15), (14, 11), (14, 15), (15, 11)],
    },
    "CB-04": {
        "titulo": "acceso.obtener_paciente_autorizado",
        "vg": 6,
        "nodos": {1: "buscar la ficha", 2: "¿no existe?", 3: "404", 4: "¿es médico?",
                  5: "¿es de otro médico?", 6: "403", 7: "devuelve la ficha", 8: "¿es familiar?",
                  9: "403", 10: "¿es ficha ajena?", 11: "403", 12: "devuelve la ficha", 13: "salida"},
        "aristas": [(1, 2), (2, 3), (2, 4), (3, 13), (4, 5), (4, 8), (5, 6), (5, 7), (6, 13),
                    (7, 13), (8, 9), (8, 10), (9, 13), (10, 11), (10, 12), (11, 13), (12, 13)],
    },
    "CB-05": {
        "titulo": "modelo.predecir (componente de IA)",
        "vg": 9,
        "nodos": {1: "inicio", 2: "¿lote vacío?", 3: "devuelve []", 4: "¿quedan fichas por convertir?",
                  5: "construir fila", 6: "probabilidades · ¿quedan factores (≤ 5)?",
                  7: "añadir factor global", 8: "¿quedan fichas por predecir?",
                  9: "¿con explicación?", 10: "SHAP · ¿quedan variables?", 11: "añadir contribución",
                  12: "ordenar por |contribución|", 13: "¿quedan campos?", 14: "¿valor ausente?",
                  15: "añadir imputada", 16: "añadir predicción", 17: "devuelve la lista", 18: "salida"},
        "aristas": [(1, 2), (2, 3), (2, 4), (3, 18), (4, 5), (5, 4), (4, 6), (6, 7), (7, 6), (6, 8),
                    (8, 9), (8, 17), (9, 10), (9, 13), (10, 11), (11, 10), (10, 12), (12, 13),
                    (13, 14), (13, 16), (14, 15), (14, 13), (15, 13), (16, 8), (17, 18)],
    },
    "CB-06": {
        "titulo": "modelo.nivel",
        "vg": 3,
        "nodos": {1: "inicio", 2: "¿p ≥ umbral alto?", 3: "alto", 4: "¿p ≥ umbral medio?",
                  5: "medio", 6: "bajo", 7: "salida"},
        "aristas": [(1, 2), (2, 3), (2, 4), (3, 7), (4, 5), (4, 6), (5, 7), (6, 7)],
    },
    "CB-07a": {
        "titulo": "limpiarAlEscribir (panel web)",
        "vg": 7,
        "nodos": {1: "inicio", 2: "¿campo numérico?", 3: "limpiarNumero", 4: "¿nombres?",
                  5: "¿apellidos?", 6: "solo letras", 7: "¿documento?", 8: "alfanumérico",
                  9: "¿teléfono?", 10: "dígitos y + -", 11: "¿código?", 12: "P-000",
                  13: "sin cambios", 14: "salida"},
        "aristas": [(1, 2), (2, 3), (2, 4), (3, 14), (4, 6), (4, 5), (5, 6), (5, 7), (6, 14),
                    (7, 8), (7, 9), (8, 14), (9, 10), (9, 11), (10, 14), (11, 12), (11, 13),
                    (12, 14), (13, 14)],
    },
    "CB-07b": {
        "titulo": "limpiarNumero (panel web)",
        "vg": 5,
        "nodos": {1: "inicio", 2: "¿admite decimales? (filtro)", 3: "quitar todo salvo dígitos y punto",
                  4: "quitar todo salvo dígitos", 5: "recortar la parte entera",
                  6: "¿sin decimales?", 7: "¿sin punto?", 8: "devuelve la parte entera",
                  9: "¿parte entera vacía?", 10: "antepone 0", 11: "entera.decimal", 12: "salida"},
        "aristas": [(1, 2), (2, 3), (2, 4), (3, 5), (4, 5), (5, 6), (6, 8), (6, 7), (7, 8),
                    (7, 9), (8, 12), (9, 10), (9, 11), (10, 11), (11, 12)],
    },
    "CB-08": {
        "titulo": "TarjetaToma.build + _Acciones (app móvil)",
        "vg": 5,
        "nodos": {1: "inicio", 2: "¿pendiente de envío?", 3: "ícono nube tachada",
                  4: "¿ya respondida?", 5: "muestra la respuesta", 6: "¿antes de la ventana?",
                  7: "«Podrá registrarla desde…»", 8: "¿ventana cerrada?",
                  9: "aviso del plazo + «No la tomé»", 10: "«Ya la tomé» + «No la tomé»", 11: "salida"},
        "aristas": [(1, 2), (2, 3), (2, 4), (3, 4), (4, 5), (4, 6), (5, 11), (6, 7), (6, 8),
                    (7, 11), (8, 9), (8, 10), (9, 11), (10, 11)],
    },
    "CB-09": {
        "titulo": "_Respuesta.build (app móvil)",
        "vg": 5,
        "nodos": {1: "estado", 2: "¿con hora?", 3: "«Registrada a las…»", 4: "¿hay motivo?",
                  5: "¿motivo no vacío?", 6: "«Motivo: …»", 7: "¿corroborada?",
                  8: "«Confirmada por su familia»", 9: "salida"},
        "aristas": [(1, 2), (2, 3), (2, 4), (3, 4), (4, 5), (4, 7), (5, 6), (5, 7), (6, 7),
                    (7, 8), (7, 9), (8, 9)],
    },
    "CB-10": {
        "titulo": "ServicioSincronizacion.registrar (app móvil)",
        "vg": 4,
        "nodos": {1: "encolar", 2: "enviar al API", 3: "¿enviado?", 4: "quitar de la cola · true",
                  5: "¿sin conexión?", 6: "false (queda en cola)", 7: "¿sesión vencida?",
                  8: "quitar de la cola", 9: "propagar el error", 10: "salida"},
        "aristas": [(1, 2), (2, 3), (3, 4), (3, 5), (4, 10), (5, 6), (5, 7), (6, 10), (7, 8),
                    (7, 9), (8, 9), (9, 10)],
    },
    "CB-11": {
        "titulo": "ServicioSincronizacion.sincronizar (app móvil)",
        "vg": 6,
        "nodos": {1: "inicio", 2: "¿ya en curso?", 3: "devuelve pendientes", 4: "leer la cola",
                  5: "¿cola vacía?", 6: "nada que enviar", 7: "¿quedan en la cola?",
                  8: "enviar lote y descartar", 9: "todo enviado", 10: "¿sin conexión?",
                  11: "informa el fallo", 12: "¿rechazo del API?", 13: "salida"},
        "aristas": [(1, 2), (2, 3), (2, 4), (3, 13), (4, 5), (5, 6), (5, 7), (6, 13), (7, 8),
                    (7, 9), (8, 7), (8, 10), (9, 13), (10, 11), (10, 12), (12, 11), (11, 13)],
    },
}


def capas(nodos, aristas):
    """Capa de cada nodo: el camino más largo desde el inicio, sin aristas de retorno."""
    sucesores = {n: [] for n in nodos}
    for a, b in aristas:
        sucesores[a].append(b)
    retorno, visitando, hechos = set(), set(), set()

    def dfs(n):
        visitando.add(n)
        for m in sucesores[n]:
            if m in visitando:
                retorno.add((n, m))
            elif m not in hechos:
                dfs(m)
        visitando.discard(n)
        hechos.add(n)

    dfs(min(nodos))
    capa = {n: 0 for n in nodos}
    for _ in nodos:
        for a, b in aristas:
            if (a, b) not in retorno:
                capa[b] = max(capa[b], capa[a] + 1)
    return capa, retorno


def dibujar(clave, g):
    nodos, aristas = g["nodos"], g["aristas"]
    vg = len(aristas) - len(nodos) + 2
    assert vg == g["vg"], f"{clave}: A − N + 2 = {vg}, se declaró {g['vg']}"
    capa, retorno = capas(nodos, aristas)
    filas = {}
    for n in sorted(nodos):
        filas.setdefault(capa[n], []).append(n)
    pos = {}
    for c, ns in filas.items():
        for i, n in enumerate(ns):
            pos[n] = ((i - (len(ns) - 1) / 2) * 3.4, -c * 1.0)

    ancho = max(len(ns) for ns in filas.values())
    fig, ax = plt.subplots(figsize=(max(7.5, ancho * 3.6), 0.9 * len(filas) + 1.2))
    for a, b in aristas:
        (x1, y1), (x2, y2) = pos[a], pos[b]
        curva = "arc3,rad=0.45" if (a, b) in retorno else ("arc3,rad=0.15" if x1 == x2 and abs(y1 - y2) > 1.3 else "arc3,rad=0")
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), connectionstyle=curva, arrowstyle="-|>",
                                     mutation_scale=12, color="#444", lw=1, shrinkA=13, shrinkB=13))
    for n, (x, y) in pos.items():
        decision = nodos[n].startswith("¿") or "¿" in nodos[n]
        ax.scatter([x], [y], s=600, color="#dbe9f4" if decision else "white",
                   edgecolors="#17608f", linewidths=1.6, zorder=3,
                   marker="D" if decision else "o")
        ax.text(x, y, str(n), ha="center", va="center", fontsize=10, fontweight="bold", zorder=4)
        ax.text(x + 0.34, y - 0.30, nodos[n], fontsize=9, color="#222", zorder=4)
    ax.set_title(f"{clave} · {g['titulo']}   —   N = {len(nodos)}, A = {len(aristas)}, "
                 f"V(G) = A − N + 2 = {vg}", fontsize=11)
    ax.axis("off")
    ax.set_aspect("equal", adjustable="datalim")
    fig.tight_layout()
    fig.savefig(SALIDA / f"{clave}.png", dpi=170)
    plt.close(fig)
    return len(nodos), len(aristas), vg


def main():
    SALIDA.mkdir(exist_ok=True)
    for clave, g in GRAFOS.items():
        n, a, vg = dibujar(clave, g)
        print(f"{clave}: N={n} A={a} V(G)={vg}")


if __name__ == "__main__":
    main()
