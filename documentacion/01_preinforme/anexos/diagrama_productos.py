"""Diagrama del Anexo n.° 21: fases de SCRUM y CRISP-DM y sus productos.

    python diagrama_productos.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

FASES = [
    ("Sprint 1", "Business y Data\nUnderstanding", "#17608f", [
        "Diagnóstico del consultorio", "Factores por dimensión OMS", "Product Backlog (MoSCoW)",
        "Modelo de datos inicial", "Autenticación por perfil (RF01)"]),
    ("Sprint 2", "Data Preparation y\nModeling inicial", "#1f7a8c", [
        "Requisitos no funcionales", "Arquitectura de microservicios", "Ficha clínica (RF02)",
        "Tomas sin conexión (RF03)", "Pipeline preprocess.py", "Despliegue en la nube"]),
    ("Sprint 3", "Modeling y\nEvaluation", "#2a9d8f", [
        "Microservicio de inferencia (RF04)", "Explicación SHAP (RF06)", "Alertas tempranas (RF05)",
        "Reportes y CSV (RF07)", "Avisos y familia (RF08, RF09)", "Recuperación de acceso (RF10)",
        "Verificación del protocolo"]),
    ("Sprint 4", "Deployment", "#5a8f3c", [
        "Prueba de carga", "Verificación ISO/IEC 25010", "APK de publicación",
        "Actas de Review y retrospectiva"]),
    ("PBI-11", "Evaluation\n(datos reales)", "#b07d16", [
        "ENDES: 8 422 pacientes", "Comparación con DeLong", "Ficha de procedencia del modelo"]),
    ("PBI-12", "Evaluation y\nDeployment", "#b5482b", [
        "Pruebas de caja negra", "Pruebas de caja blanca", "Manual de usuario por perfil",
        "Ventana de registro y baja", "Descarga y textos legales"]),
]


def main():
    fig, ax = plt.subplots(figsize=(13, 7.2))
    ancho, sep = 2.0, 0.18
    for i, (sprint, fase, color, productos) in enumerate(FASES):
        x = i * (ancho + sep)
        ax.add_patch(FancyBboxPatch((x, 6.0), ancho, 0.9, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc=color, ec="none"))
        ax.text(x + ancho / 2, 6.62, sprint, ha="center", va="center", color="white", fontsize=11,
                fontweight="bold")
        ax.text(x + ancho / 2, 6.25, fase, ha="center", va="center", color="white", fontsize=7.6)
        for k, prod in enumerate(productos):
            y = 5.25 - k * 0.78
            ax.add_patch(FancyBboxPatch((x + 0.05, y), ancho - 0.1, 0.62,
                                        boxstyle="round,pad=0.02,rounding_size=0.08",
                                        fc="white", ec=color, lw=1.3))
            ax.text(x + ancho / 2, y + 0.31, prod, ha="center", va="center", fontsize=7.2, wrap=True)
        if i < len(FASES) - 1:
            ax.annotate("", xy=(x + ancho + sep - 0.01, 6.45), xytext=(x + ancho + 0.01, 6.45),
                        arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.2))
    total = len(FASES) * (ancho + sep) - sep
    ax.add_patch(FancyBboxPatch((0, 7.05), total, 0.42, boxstyle="round,pad=0.02,rounding_size=0.1",
                                fc="#eef3f7", ec="#17608f"))
    ax.text(total / 2, 7.26, "SCRUM: el sprint es la unidad de trabajo · CRISP-DM ordena el modelo "
            "predictivo dentro de cada sprint", ha="center", va="center", fontsize=9.5, color="#123")
    ax.set_xlim(-0.1, total + 0.1)
    ax.set_ylim(0.2, 7.6)
    ax.axis("off")
    fig.tight_layout()
    destino = Path(__file__).resolve().parent / "imagenes"
    destino.mkdir(exist_ok=True)
    fig.savefig(destino / "productos_por_fase.png", dpi=180)
    print("Generado:", destino / "productos_por_fase.png")


if __name__ == "__main__":
    main()
