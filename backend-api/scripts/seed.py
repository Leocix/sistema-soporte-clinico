"""Carga inicial de la base de datos.

Crea la cuenta del medico del consultorio y, opcionalmente, un conjunto de
pacientes y registros de demostracion para poder recorrer el panel clinico y
la app movil sin esperar a la extraccion documental.

    python scripts/seed.py                 # solo la cuenta del medico
    python scripts/seed.py --demo          # ademas, 5 pacientes de ejemplo

Los pacientes de demostracion son ficticios y llevan codigos de la serie
D-0NN para distinguirlos a simple vista de los pacientes reales (P-0NN): no
deben incluirse en el dataset de entrenamiento ni en los resultados de la
investigacion.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from app.core.security import hash_password  # noqa: E402
from app.db.database import SessionLocal  # noqa: E402
from app.db.models import (  # noqa: E402
    Aseguramiento,
    Diagnostico,
    EstadoToma,
    NivelSocioeconomico,
    OrigenRegistro,
    Paciente,
    RegistroAdherencia,
    Rol,
    Sexo,
    Usuario,
    ZonaResidencia,
)

CORREO_MEDICO = "milko.ugaz@consultorio.pe"

# Nombres ficticios, coherentes con el codigo D- de demostracion.
PACIENTES_DEMO = [
    # codigo, nombres, apellidos, edad, sexo, diagnostico, nse, aseg, zona,
    # anios, comorb, farm, tomas, prog, perd, morisky
    ("D-001", "Jose Luis", "Vasquez Rios", 68, Sexo.MASCULINO, Diagnostico.AMBAS,
     NivelSocioeconomico.BAJO, Aseguramiento.SIS, ZonaResidencia.URBANA, 12.0, 2, 7, 5, 6, 3, 1),
    ("D-002", "Maria Elena", "Rios Chavez", 72, Sexo.FEMENINO, Diagnostico.HTA,
     NivelSocioeconomico.BAJO, Aseguramiento.SIS, ZonaResidencia.RURAL, 15.5, 3, 9, 6, 6, 4, 0),
    ("D-003", "Carlos Alberto", "Diaz Mendoza", 65, Sexo.MASCULINO, Diagnostico.DM2,
     NivelSocioeconomico.MEDIO, Aseguramiento.ESSALUD, ZonaResidencia.URBANA, 8.0, 1, 5, 3, 6, 1, 3),
    ("D-004", "Lucia", "Fernandez Paz", 59, Sexo.FEMENINO, Diagnostico.AMBAS,
     NivelSocioeconomico.MEDIO, Aseguramiento.ESSALUD, ZonaResidencia.URBANA, 6.5, 0, 6, 4, 6, 0, 4),
    ("D-005", "Ricardo", "Campos Leon", 70, Sexo.MASCULINO, Diagnostico.HTA,
     NivelSocioeconomico.BAJO, Aseguramiento.NINGUNO, ZonaResidencia.RURAL, 20.0, 4, 8, 6, 6, 2, 2),
]


def crear_medico(db, clave: str) -> Usuario:
    medico = db.query(Usuario).filter(Usuario.correo == CORREO_MEDICO).first()
    if medico is not None:
        print(f"La cuenta {CORREO_MEDICO} ya existe; no se modifica.")
        return medico

    medico = Usuario(
        nombres="Milko",
        apellidos="Ugaz Zegarra",
        correo=CORREO_MEDICO,
        hash_contrasena=hash_password(clave),
        rol=Rol.MEDICO,
    )
    db.add(medico)
    db.commit()
    db.refresh(medico)
    print(f"Cuenta de medico creada: {CORREO_MEDICO}")
    return medico


def crear_demo(db, medico: Usuario) -> None:
    if db.query(Paciente).filter(Paciente.codigo_anonimizado.like("D-%")).first():
        print("Los pacientes de demostracion ya existen; no se duplican.")
        return

    ahora = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)

    for (codigo, nombres, apellidos, edad, sexo, dx, nse, aseg, zona, anios, comorb,
         farmacos, tomas, programados, perdidos, morisky) in PACIENTES_DEMO:
        paciente = Paciente(
            codigo_anonimizado=codigo,
            nombres=nombres, apellidos=apellidos,
            # `.local` es un dominio reservado que el validador rechaza.
            correo=f"{codigo.lower()}@ejemplo.pe",
            telefono="9" + codigo.replace("D-", "").rjust(8, "0"),
            id_medico_tratante=medico.id_usuario,
            edad=edad, sexo=sexo, diagnostico=dx,
            nivel_socioeconomico=nse, aseguramiento=aseg, zona_residencia=zona,
            tiempo_enfermedad_anios=anios, comorbilidades=comorb,
            numero_farmacos=farmacos, tomas_dia=tomas,
            controles_programados_6m=programados, controles_perdidos_6m=perdidos,
            puntaje_morisky=morisky,
            # Clasificacion segun el patron del test de Morisky-Green: el
            # paciente adherente responde correctamente las cuatro preguntas.
            incumplimiento_basal=morisky < 4,
        )
        db.add(paciente)
        db.flush()

        # Catorce dias de historial: cuanto mayor es la inasistencia a
        # controles, mayor es la proporcion de omisiones, para que el panel
        # muestre perfiles de riesgo distinguibles.
        omite_cada = 2 if perdidos >= 3 else (4 if perdidos >= 1 else 0)
        for dia in range(14):
            programada = ahora - timedelta(days=13 - dia, hours=ahora.hour - 8)
            omitida = omite_cada and dia % omite_cada == 0
            db.add(
                RegistroAdherencia(
                    id_paciente=paciente.id_paciente,
                    medicamento="Losartan 50 mg",
                    dosis="1 tableta",
                    fecha_hora_programada=programada,
                    fecha_hora_registro=None if omitida else programada + timedelta(minutes=15 * (dia % 4)),
                    estado=EstadoToma.OMITIDA if omitida else EstadoToma.TOMADA,
                    origen=OrigenRegistro.APP_MOVIL,
                    motivo_omision="Olvido" if omitida else None,
                )
            )

    db.commit()
    print(f"{len(PACIENTES_DEMO)} pacientes de demostracion creados con 14 dias de historial.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Carga inicial de la base clinica.")
    parser.add_argument("--demo", action="store_true",
                        help="Crea tambien pacientes y registros de ejemplo.")
    args = parser.parse_args()

    clave = os.environ.get("SEED_PASSWORD")
    if not clave:
        print(
            "Defina la contrasena de la cuenta antes de ejecutar:\n"
            '    PowerShell:  $env:SEED_PASSWORD = "SuClaveSegura123"\n'
            "No se usa una contrasena por defecto para no dejar una credencial\n"
            "conocida en un despliegue publico (RNF01).",
            file=sys.stderr,
        )
        return 1
    if len(clave) < 8:
        print("La contrasena debe tener al menos 8 caracteres.", file=sys.stderr)
        return 1

    db = SessionLocal()
    try:
        medico = crear_medico(db, clave)
        if args.demo:
            crear_demo(db, medico)
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
