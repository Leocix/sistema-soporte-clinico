"""Reporte general de los pacientes a cargo del medico (RF07)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.api.reportes import clasificar_riesgo_observado
from app.db.models import EstadoToma, OrigenRegistro, RegistroAdherencia


def _tomas(db_session, ficha, estados):
    inicio = datetime.now(timezone.utc) - timedelta(days=len(estados))
    for dia, estado in enumerate(estados):
        programada = inicio + timedelta(days=dia)
        db_session.add(RegistroAdherencia(
            id_paciente=ficha.id_paciente, medicamento="Losartan 50 mg",
            fecha_hora_programada=programada,
            fecha_hora_registro=None if estado is EstadoToma.OMITIDA else programada,
            estado=estado, origen=OrigenRegistro.APP_MOVIL,
            motivo_omision="olvido" if estado is EstadoToma.OMITIDA else None,
        ))
    db_session.commit()


def test_umbrales_del_riesgo_observado():
    assert clasificar_riesgo_observado(None, 0) == "sin_datos"
    assert clasificar_riesgo_observado(50, 0) == "alto"
    assert clasificar_riesgo_observado(90, 3) == "alto"
    assert clasificar_riesgo_observado(75, 0) == "medio"
    assert clasificar_riesgo_observado(95, 2) == "medio"
    assert clasificar_riesgo_observado(95, 1) == "bajo"


def test_el_reporte_resume_a_los_pacientes_del_medico(client, cab_medico, datos, db_session):
    T, O = EstadoToma.TOMADA, EstadoToma.OMITIDA
    _tomas(db_session, datos["ficha"], [T, T, O, T, O, O, EstadoToma.POSPUESTA])

    respuesta = client.get("/api/reportes/general", headers=cab_medico)
    assert respuesta.status_code == 200, respuesta.text
    reporte = respuesta.json()

    ind = reporte["indicadores"]
    assert ind["pacientes_activos"] == 1
    assert ind["tomas_cumplidas"] == 3 and ind["tomas_omitidas"] == 3
    # 3 cumplidas de 6 con desenlace: la pospuesta no cuenta.
    assert ind["adherencia_promedio"] == 50.0
    fila = reporte["pacientes"][0]
    assert fila["omisiones_consecutivas"] == 2
    assert fila["riesgo_observado"] == "alto"
    assert reporte["riesgo_observado"]["alto"] == 1
    assert reporte["por_diagnostico"]["ambas"] == 1
    assert {"comorbilidad": "dislipidemia", "pacientes": 1} in reporte["comorbilidades_frecuentes"]
    assert reporte["motivos_omision"] == [{"motivo": "Olvido", "veces": 3}]


def test_un_paciente_sin_tomas_figura_sin_datos(client, cab_medico, datos):
    reporte = client.get("/api/reportes/general", headers=cab_medico).json()
    assert reporte["pacientes"][0]["riesgo_observado"] == "sin_datos"
    assert reporte["indicadores"]["adherencia_promedio"] is None


def test_otro_medico_no_ve_pacientes_ajenos(client, cab_otro_medico, datos):
    reporte = client.get("/api/reportes/general", headers=cab_otro_medico).json()
    assert reporte["indicadores"]["pacientes_activos"] == 0
    assert reporte["pacientes"] == []


def test_el_paciente_no_accede_al_reporte(client, cab_paciente):
    assert client.get("/api/reportes/general", headers=cab_paciente).status_code == 403


def test_exportacion_csv(client, cab_medico, datos, db_session):
    _tomas(db_session, datos["ficha"], [EstadoToma.TOMADA, EstadoToma.OMITIDA])
    respuesta = client.get("/api/reportes/general.csv", headers=cab_medico)

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"].startswith("text/csv")
    lineas = respuesta.content.decode("utf-8-sig").strip().splitlines()
    assert lineas[0].startswith("Codigo,Paciente,Edad")
    assert lineas[1].startswith("P-001,Jose Vasquez,68,ambas")
