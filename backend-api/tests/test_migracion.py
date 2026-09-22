"""El arranque no se cae por un corte pasajero de la base (RNF04).

El despliegue ejecuta las migraciones antes de levantar el API. Si la base
gestionada no responde en ese segundo, el servicio entero quedaba caido hasta
que alguien lo reintentaba a mano: fue la incidencia I-22 en produccion.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from sqlalchemy.exc import OperationalError

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def migrar():
    spec = importlib.util.spec_from_file_location("migrar", RAIZ / "scripts" / "migrar.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def _fallo(mensaje: str) -> OperationalError:
    return OperationalError("SELECT 1", {}, Exception(mensaje))


def test_reintenta_antes_de_rendirse(migrar, monkeypatch):
    intentos = []

    def falla_siempre(configuracion, revision):
        intentos.append(revision)
        raise _fallo('could not translate host name "base.ejemplo" to address')

    monkeypatch.setattr(migrar, "ESPERAS", (0, 0))
    monkeypatch.setattr(migrar.command, "upgrade", falla_siempre)

    assert migrar.migrar() == 1
    assert len(intentos) == 3  # dos esperas + el intento final


def test_un_corte_pasajero_no_tumba_el_arranque(migrar, monkeypatch):
    """Si la base vuelve en el segundo intento, el servicio arranca igual."""
    llamadas = []

    def falla_una_vez(configuracion, revision):
        llamadas.append(revision)
        if len(llamadas) == 1:
            raise _fallo("connection timed out")

    monkeypatch.setattr(migrar, "ESPERAS", (0, 0))
    monkeypatch.setattr(migrar.command, "upgrade", falla_una_vez)

    assert migrar.migrar() == 0
    assert len(llamadas) == 2


def test_una_migracion_rota_no_se_reintenta(migrar, monkeypatch):
    """Repetir algo que esta mal escrito solo retrasa el diagnostico."""
    llamadas = []

    def falla(configuracion, revision):
        llamadas.append(revision)
        raise ValueError("revision duplicada")

    monkeypatch.setattr(migrar, "ESPERAS", (0, 0))
    monkeypatch.setattr(migrar.command, "upgrade", falla)

    with pytest.raises(ValueError):
        migrar.migrar()
    assert len(llamadas) == 1


@pytest.mark.parametrize("mensaje,esperado", [
    ('could not translate host name "x" to address', "no se pudo resolver"),
    ("password authentication failed for user", "contrasena incorrectos"),
    ('database "otra" does not exist', "no existe"),
    ("connection timed out", "no respondio a tiempo"),
])
def test_cada_fallo_dice_que_revisar(migrar, mensaje, esperado):
    assert esperado in migrar._pista(_fallo(mensaje))


def test_el_registro_no_muestra_la_contrasena(migrar, monkeypatch, capsys):
    monkeypatch.setattr(migrar.settings, "database_url",
                        "postgresql://usuario:ClaveSecreta@base.ejemplo:5432/clinica")
    monkeypatch.setattr(migrar.command, "upgrade", lambda *_: None)

    migrar.migrar()

    salida = capsys.readouterr().out
    assert "base.ejemplo:5432/clinica" in salida
    assert "ClaveSecreta" not in salida and "usuario" not in salida
