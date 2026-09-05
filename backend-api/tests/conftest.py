"""Entorno de pruebas del API: base en memoria y sesiones preautenticadas."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.database import Base, get_db
from app.db.models import Diagnostico, Paciente, Rol, Sexo, Usuario
from app.main import app

CLAVE = "Consultorio2026"


@pytest.fixture()
def db_session():
    """Base SQLite en memoria, recreada para cada prueba.

    StaticPool mantiene una unica conexion, de modo que el esquema creado en
    la preparacion siga visible para el cliente HTTP.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    sesion = Session()
    try:
        yield sesion
    finally:
        sesion.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def datos(db_session):
    """Consultorio minimo: dos medicos, una cuenta de paciente y su ficha."""
    medico = Usuario(
        nombres="Milko", apellidos="Ugaz Zegarra",
        correo="milko.ugaz@consultorio.pe",
        hash_contrasena=hash_password(CLAVE), rol=Rol.MEDICO,
    )
    otro_medico = Usuario(
        nombres="Ana", apellidos="Reyes", correo="ana.reyes@consultorio.pe",
        hash_contrasena=hash_password(CLAVE), rol=Rol.MEDICO,
    )
    cuenta_paciente = Usuario(
        nombres="Jose", apellidos="Vasquez", correo="jose.vasquez@correo.pe",
        hash_contrasena=hash_password(CLAVE), rol=Rol.PACIENTE,
    )
    db_session.add_all([medico, otro_medico, cuenta_paciente])
    db_session.flush()

    ficha = Paciente(
        codigo_anonimizado="P-001",
        nombres="Jose", apellidos="Vasquez",
        correo="jose.vasquez@correo.pe", telefono="987654321",
        id_usuario=cuenta_paciente.id_usuario,
        id_medico_tratante=medico.id_usuario,
        edad=68, sexo=Sexo.MASCULINO, diagnostico=Diagnostico.AMBAS,
        comorbilidades=2, numero_farmacos=7, tomas_dia=5,
        controles_programados_6m=6, controles_perdidos_6m=3,
    )
    db_session.add(ficha)
    db_session.commit()

    return {
        "medico": medico,
        "otro_medico": otro_medico,
        "cuenta_paciente": cuenta_paciente,
        "ficha": ficha,
    }


@pytest.fixture()
def client(db_session):
    def _get_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_db
    # Sin gestor de contexto a proposito: asi no se ejecuta el ciclo de vida
    # de la aplicacion, que crearia el archivo SQLite de desarrollo. Las
    # pruebas trabajan unicamente contra la base en memoria.
    cliente = TestClient(app, raise_server_exceptions=False)
    yield cliente
    app.dependency_overrides.clear()


def _token(client: TestClient, correo: str, perfil: str) -> str:
    respuesta = client.post(
        "/api/auth/login",
        json={"correo": correo, "contrasena": CLAVE, "perfil": perfil},
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()["access_token"]


@pytest.fixture()
def cab_medico(client, datos) -> dict:
    return {"Authorization": f"Bearer {_token(client, 'milko.ugaz@consultorio.pe', 'medico')}"}


@pytest.fixture()
def cab_otro_medico(client, datos) -> dict:
    return {"Authorization": f"Bearer {_token(client, 'ana.reyes@consultorio.pe', 'medico')}"}


@pytest.fixture()
def cab_paciente(client, datos) -> dict:
    return {"Authorization": f"Bearer {_token(client, 'jose.vasquez@correo.pe', 'paciente')}"}
