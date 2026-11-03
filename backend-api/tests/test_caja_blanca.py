"""Pruebas de caja blanca: un caso por cada camino independiente.

Cada clase corresponde a una función del núcleo funcional. Su complejidad
ciclomática V(G) la calcula `radon cc` y fija cuántos caminos independientes
hay que recorrer; cada prueba recorre uno, y su docstring dice cuál. El
análisis completo (grafo de flujo, decisiones y caminos) está en el anexo de
pruebas de caja blanca, que remite a estas pruebas por su identificador.

    python -m pytest tests/test_caja_blanca.py -v
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.core.exceptions import PermisoDenegadoError, RecursoNoEncontradoError
from app.core.security import hash_password
from app.db.models import (
    Alerta, EstadoAlerta, EstadoToma, OrigenRegistro, RegistroAdherencia, Rol,
    TipoAlerta, Usuario,
)
from app.schemas.adherencia_schema import RegistroTomaCreate
from app.services.acceso import obtener_paciente_autorizado
from app.services.alertas import evaluar_paciente
from app.services.riesgo import clasificar

T, TT, O, P = EstadoToma.TOMADA, EstadoToma.TOMADA_TARDE, EstadoToma.OMITIDA, EstadoToma.POSPUESTA


# ---------------------------------------------------------------------------
# CB-01 · RegistroTomaCreate._coherencia_clinica (ventana de registro, RF03)
# V(G) = 10
# ---------------------------------------------------------------------------
def _toma(estado, programada, registro=None, **extra):
    return RegistroTomaCreate(
        medicamento="Losartan 50 mg", estado=estado,
        fecha_hora_programada=programada, fecha_hora_registro=registro, **extra,
    )


class TestCB01VentanaDeRegistro:
    # Una hora programada en el pasado, para que la regla del reloj no
    # interfiera salvo en el camino que la recorre a propósito.
    PROG = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(hours=6)

    def test_c1_cumplida_sin_hora_se_rechaza(self):
        """C1: cumplida y sin hora de registro -> error."""
        with pytest.raises(ValidationError, match="requiere la hora real"):
            _toma(T, self.PROG)

    def test_c2_cumplida_dentro_de_la_ventana_es_valida(self):
        """C2: cumplida, con hora, dentro de la ventana y no futura -> válida."""
        assert _toma(T, self.PROG, self.PROG + timedelta(minutes=15)).estado is T

    def test_c3_antes_de_que_abra_la_ventana_se_rechaza(self):
        """C3: desfase < -60 min (primera condición del OR) -> fuera de ventana."""
        with pytest.raises(ValidationError, match="Fuera de la ventana"):
            _toma(T, self.PROG, self.PROG - timedelta(minutes=61))

    def test_c4_despues_de_que_cierre_la_ventana_se_rechaza(self):
        """C4: desfase > 3 h (segunda condición del OR) -> fuera de ventana."""
        with pytest.raises(ValidationError, match="Fuera de la ventana"):
            _toma(T, self.PROG, self.PROG + timedelta(hours=3, minutes=1))

    def test_c5_hora_de_registro_futura_se_rechaza(self):
        """C5: dentro de la ventana pero posterior a ahora + 5 min -> reloj adelantado."""
        futura = datetime.now(timezone.utc) + timedelta(minutes=30)
        with pytest.raises(ValidationError, match="posterior a la hora actual"):
            _toma(T, futura, futura)

    def test_c6_omitida_sin_hora_es_valida(self):
        """C6: omitida sin hora -> válida (ninguna regla de cumplida aplica)."""
        assert _toma(O, self.PROG, motivo_omision="olvido").estado is O

    def test_c7_omitida_con_hora_se_rechaza(self):
        """C7: omitida con hora de registro -> error."""
        with pytest.raises(ValidationError, match="no puede llevar hora"):
            _toma(O, self.PROG, self.PROG)

    def test_c8_pospuesta_no_recorre_ninguna_regla(self):
        """C8: pospuesta sin hora -> todas las decisiones en falso, válida."""
        assert _toma(P, self.PROG).estado is P

    def test_c9_tomada_tarde_comparte_las_reglas_de_cumplida(self):
        """C9: el segundo estado cumplido (tomada_tarde) entra por la misma rama."""
        assert _toma(TT, self.PROG, self.PROG + timedelta(hours=2)).estado is TT

    def test_c10_los_limites_exactos_de_la_ventana_se_aceptan(self):
        """C10: desfase = -60 min y = +3 h exactos -> válidos (comparación estricta)."""
        assert _toma(T, self.PROG, self.PROG - timedelta(minutes=60))
        assert _toma(T, self.PROG, self.PROG + timedelta(hours=3))


# ---------------------------------------------------------------------------
# CB-02 · riesgo.clasificar (riesgo observado)
# V(G) = 6
# ---------------------------------------------------------------------------
class TestCB02ClasificarRiesgo:
    def test_c1_sin_tomas_con_desenlace(self):
        """C1: tasa None -> sin_datos."""
        assert clasificar(None, 0) == "sin_datos"

    def test_c2_tasa_baja(self):
        """C2: tasa < 60 -> alto."""
        assert clasificar(59.9, 0) == "alto"

    def test_c3_racha_larga_con_buena_tasa(self):
        """C3: tasa >= 60 pero racha >= 3 -> alto."""
        assert clasificar(95.0, 3) == "alto"

    def test_c4_tasa_intermedia(self):
        """C4: 60 <= tasa < 80 y racha < 3 -> medio."""
        assert clasificar(60.0, 0) == "medio"

    def test_c5_racha_de_dos(self):
        """C5: tasa >= 80 pero racha = 2 -> medio."""
        assert clasificar(90.0, 2) == "medio"

    def test_c6_buena_adherencia(self):
        """C6: tasa >= 80 y racha < 2 -> bajo."""
        assert clasificar(80.0, 1) == "bajo"


# ---------------------------------------------------------------------------
# CB-03 · alertas.evaluar_paciente (alertas tempranas, RF05)
# V(G) = 11
# ---------------------------------------------------------------------------
def _historial(db, ficha, estados):
    inicio = datetime.now(timezone.utc) - timedelta(hours=len(estados) + 1)
    eventos = []
    for i, estado in enumerate(estados):
        programada = inicio + timedelta(hours=i)
        evento = RegistroAdherencia(
            id_paciente=ficha.id_paciente, medicamento="Losartan 50 mg",
            fecha_hora_programada=programada,
            fecha_hora_registro=programada if estado in (T, TT) else None,
            estado=estado, origen=OrigenRegistro.APP_MOVIL,
            motivo_omision="olvido" if estado is O else None,
        )
        db.add(evento)
        eventos.append(evento)
    db.commit()
    return eventos


def _tipos(alertas):
    return {a.tipo for a in alertas}


def _abrir(db, ficha, tipo):
    db.add(Alerta(id_paciente=ficha.id_paciente, tipo=tipo, motivo="previa",
                  valor=1, estado=EstadoAlerta.ABIERTA))
    db.commit()


class TestCB03EvaluarAlertas:
    def test_c1_sin_eventos_ni_prediccion(self, db_session, datos):
        """C1: todas las decisiones en falso y sin alertas abiertas -> []."""
        assert evaluar_paciente(db_session, datos["ficha"], []) == []
        # Mismo camino con otros datos: solo pospuestas, la tasa sigue siendo None.
        eventos = _historial(db_session, datos["ficha"], [P, P, P, P, P])
        assert evaluar_paciente(db_session, datos["ficha"], eventos) == []

    def test_c2_tres_omisiones_seguidas(self, db_session, datos):
        """C2: racha >= 3 -> OMISIONES_SEGUIDAS (y la tasa 0 % con 3 tomas no basta para la otra)."""
        eventos = _historial(db_session, datos["ficha"], [O, O, O])
        assert _tipos(evaluar_paciente(db_session, datos["ficha"], eventos)) == {
            TipoAlerta.OMISIONES_SEGUIDAS}

    def test_c3_cumplimiento_bajo_con_suficientes_tomas(self, db_session, datos):
        """C3: tasa < 60 con >= 5 tomas resueltas -> ADHERENCIA_BAJA."""
        eventos = _historial(db_session, datos["ficha"], [O, T, O, T, O, T])
        assert _tipos(evaluar_paciente(db_session, datos["ficha"], eventos)) == {
            TipoAlerta.ADHERENCIA_BAJA}

    def test_c4_cumplimiento_bajo_con_pocas_tomas(self, db_session, datos):
        """C4: tasa < 60 pero < 5 tomas resueltas -> sin alerta (condición 2 en falso)."""
        eventos = _historial(db_session, datos["ficha"], [O, T, O, T])
        assert evaluar_paciente(db_session, datos["ficha"], eventos) == []

    def test_c5_riesgo_predicho_abierto_y_el_modelo_ya_no_dice_alto(self, db_session, datos):
        """C5: RIESGO_PREDICHO abierto y la predicción llega con nivel medio -> RESUELTA."""
        _abrir(db_session, datos["ficha"], TipoAlerta.RIESGO_PREDICHO)
        assert evaluar_paciente(db_session, datos["ficha"], [], (0.45, "medio")) == []
        assert db_session.query(Alerta).one().estado is EstadoAlerta.RESUELTA

    def test_c6_buena_tasa_con_suficientes_tomas(self, db_session, datos):
        """C6: >= 5 tomas y tasa >= 60 (condición 3 en falso) -> sin alerta."""
        eventos = _historial(db_session, datos["ficha"], [T, T, T, T, O])
        assert evaluar_paciente(db_session, datos["ficha"], eventos) == []

    def test_c7_prediccion_alta(self, db_session, datos):
        """C7: predicción con nivel alto -> RIESGO_PREDICHO."""
        alertas = evaluar_paciente(db_session, datos["ficha"], [], (0.91, "alto"))
        assert _tipos(alertas) == {TipoAlerta.RIESGO_PREDICHO}

    def test_c8_prediccion_media(self, db_session, datos):
        """C8: predicción presente pero no alta -> sin alerta."""
        assert evaluar_paciente(db_session, datos["ficha"], [], (0.55, "medio")) == []

    def test_c9_alerta_abierta_que_sigue_vigente(self, db_session, datos):
        """C9: abierta y aún vigente -> se actualiza y continúa abierta."""
        _abrir(db_session, datos["ficha"], TipoAlerta.OMISIONES_SEGUIDAS)
        eventos = _historial(db_session, datos["ficha"], [O, O, O, O])
        alertas = evaluar_paciente(db_session, datos["ficha"], eventos)
        assert _tipos(alertas) == {TipoAlerta.OMISIONES_SEGUIDAS}
        assert alertas[0].valor == 4

    def test_c10_riesgo_predicho_abierto_sin_prediccion(self, db_session, datos):
        """C10: RIESGO_PREDICHO abierto y el modelo no respondió -> se conserva."""
        _abrir(db_session, datos["ficha"], TipoAlerta.RIESGO_PREDICHO)
        alertas = evaluar_paciente(db_session, datos["ficha"], [], None)
        assert _tipos(alertas) == {TipoAlerta.RIESGO_PREDICHO}

    def test_c11_alerta_abierta_que_dejo_de_cumplirse(self, db_session, datos):
        """C11: abierta y la condición ya no se cumple -> RESUELTA por el sistema."""
        _abrir(db_session, datos["ficha"], TipoAlerta.OMISIONES_SEGUIDAS)
        eventos = _historial(db_session, datos["ficha"], [O, O, O, T])
        assert evaluar_paciente(db_session, datos["ficha"], eventos) == []
        cerrada = db_session.query(Alerta).one()
        assert cerrada.estado is EstadoAlerta.RESUELTA


# ---------------------------------------------------------------------------
# CB-04 · acceso.obtener_paciente_autorizado (control de acceso, RNF01)
# V(G) = 6
# ---------------------------------------------------------------------------
def _usuario(db, rol, correo):
    u = Usuario(nombres="Prueba", apellidos="Caja Blanca", correo=correo,
                hash_contrasena=hash_password("Consultorio2026"), rol=rol)
    db.add(u)
    db.commit()
    return u


class TestCB04AccesoALaFicha:
    def test_c1_paciente_inexistente(self, db_session, datos):
        """C1: la ficha no existe -> 404."""
        with pytest.raises(RecursoNoEncontradoError):
            obtener_paciente_autorizado(db_session, datos["medico"], "no-existe")

    def test_c2_medico_tratante(self, db_session, datos):
        """C2: médico y tratante -> devuelve la ficha."""
        ficha = obtener_paciente_autorizado(db_session, datos["medico"], datos["ficha"].id_paciente)
        assert ficha.codigo_anonimizado == "P-001"

    def test_c3_otro_medico(self, db_session, datos):
        """C3: médico pero no tratante -> 403."""
        with pytest.raises(PermisoDenegadoError):
            obtener_paciente_autorizado(db_session, datos["otro_medico"], datos["ficha"].id_paciente)

    def test_c4_familiar(self, db_session, datos):
        """C4: familiar -> 403, nunca ve la ficha clínica."""
        familiar = _usuario(db_session, Rol.FAMILIAR, "familiar@correo.pe")
        with pytest.raises(PermisoDenegadoError):
            obtener_paciente_autorizado(db_session, familiar, datos["ficha"].id_paciente)

    def test_c5_paciente_dueno_de_la_ficha(self, db_session, datos):
        """C5: paciente sobre su propia ficha -> devuelve la ficha."""
        ficha = obtener_paciente_autorizado(
            db_session, datos["cuenta_paciente"], datos["ficha"].id_paciente)
        assert ficha.id_usuario == datos["cuenta_paciente"].id_usuario

    def test_c6_paciente_sobre_ficha_ajena(self, db_session, datos):
        """C6: paciente sobre la ficha de otro -> 403."""
        otro = _usuario(db_session, Rol.PACIENTE, "otro.paciente@correo.pe")
        with pytest.raises(PermisoDenegadoError):
            obtener_paciente_autorizado(db_session, otro, datos["ficha"].id_paciente)
