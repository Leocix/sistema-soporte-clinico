"""Pruebas de caja blanca del componente inteligente.

CB-05 · modelo.predecir   V(G) = 9
CB-06 · modelo.nivel      V(G) = 3

Un caso por camino independiente, contra el modelo realmente desplegado.
El análisis (decisiones, grafo y caminos) está en el anexo de caja blanca.
"""
from __future__ import annotations

import pytest

from app import modelo
from app.config import settings
from app.esquemas import FichaEntrada

COMPLETA = {
    "codigo_anonimizado": "P-901", "edad": 68, "sexo": "M", "diagnostico": "ambas",
    "nivel_educativo": "secundaria", "convivencia": "solo", "apoyo_familiar": False,
    "tiempo_enfermedad_anios": 12.0, "comorbilidades": 2, "numero_farmacos": 7,
    "tomas_dia": 5, "controles_programados_6m": 6, "controles_perdidos_6m": 3,
}
# Sin los datos opcionales: el modelo los imputa y debe declararlo.
INCOMPLETA = {k: v for k, v in COMPLETA.items()
              if k not in ("nivel_educativo", "convivencia", "apoyo_familiar",
                           "tiempo_enfermedad_anios")} | {"codigo_anonimizado": "P-902"}


@pytest.fixture(autouse=True)
def _modelo_limpio():
    modelo.cargar.cache_clear()
    yield
    modelo.cargar.cache_clear()


def _ficha(datos):
    return FichaEntrada(**datos)


class TestCB05Predecir:
    def test_c1_lista_vacia(self):
        """C1: lote vacío -> lista vacía, sin llegar al modelo (defecto corregido)."""
        assert modelo.predecir([], con_explicacion=True) == []

    def test_c2_sin_explicacion(self):
        """C2: con_explicacion falso -> probabilidad sin SHAP."""
        [p] = modelo.predecir([_ficha(COMPLETA)], con_explicacion=False)
        assert 0 <= p.probabilidad <= 1
        assert p.valor_base is None and p.contribuciones == []

    def test_c3_con_explicacion(self):
        """C3: con_explicacion verdadero -> valor base y una contribución por variable."""
        [p] = modelo.predecir([_ficha(COMPLETA)], con_explicacion=True)
        assert p.valor_base is not None
        assert len(p.contribuciones) > 0

    def test_c4_contribuciones_ordenadas_por_magnitud(self):
        """C4: el ordenamiento usa |contribución| descendente."""
        [p] = modelo.predecir([_ficha(COMPLETA)], con_explicacion=True)
        magnitudes = [abs(c.contribucion) for c in p.contribuciones]
        assert magnitudes == sorted(magnitudes, reverse=True)

    def test_c5_ficha_completa_sin_imputadas(self):
        """C5: ningún valor ausente -> variables_imputadas vacía."""
        [p] = modelo.predecir([_ficha(COMPLETA)], con_explicacion=False)
        assert p.variables_imputadas == []

    def test_c6_ficha_incompleta_declara_imputadas(self):
        """C6: valores ausentes -> se listan, ordenados, como imputados."""
        [p] = modelo.predecir([_ficha(INCOMPLETA)], con_explicacion=False)
        assert p.variables_imputadas == sorted(p.variables_imputadas)
        assert {"nivel_educativo", "convivencia", "apoyo_familiar",
                "tiempo_enfermedad_anios"} <= set(p.variables_imputadas)

    def test_c7_factores_globales_recortados_a_cinco(self):
        """C7: la ficha del modelo trae más factores; se publican a lo sumo cinco."""
        [p] = modelo.predecir([_ficha(COMPLETA)], con_explicacion=False)
        assert 0 < len(p.factores_globales) <= 5

    def test_c8_varias_fichas_conservan_el_orden(self):
        """C8: el bucle itera n veces -> una predicción por ficha, en el mismo orden."""
        salida = modelo.predecir([_ficha(COMPLETA), _ficha(INCOMPLETA)], con_explicacion=False)
        assert [p.codigo_anonimizado for p in salida] == ["P-901", "P-902"]

    def test_c9_modelo_sin_factores_globales(self, monkeypatch):
        """C9: la ficha del modelo no trae factores -> el recorte no itera, lista vacía."""
        cargado = modelo.cargar()
        monkeypatch.setitem(cargado.ficha, "factores_influyentes", [])
        [p] = modelo.predecir([_ficha(COMPLETA)], con_explicacion=False)
        assert p.factores_globales == []


class TestCB06Nivel:
    def test_c1_alto(self):
        """C1: probabilidad >= umbral alto -> alto (límite incluido)."""
        assert modelo.nivel(settings.umbral_riesgo_alto) == "alto"

    def test_c2_medio(self):
        """C2: umbral medio <= p < umbral alto -> medio (límite incluido)."""
        assert modelo.nivel(settings.umbral_riesgo_medio) == "medio"

    def test_c3_bajo(self):
        """C3: p < umbral medio -> bajo."""
        assert modelo.nivel(settings.umbral_riesgo_medio - 0.0001) == "bajo"
