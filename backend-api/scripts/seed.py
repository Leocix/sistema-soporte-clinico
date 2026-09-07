"""Carga inicial de la base de datos.

Crea la cuenta del medico del consultorio y, opcionalmente, un conjunto de
pacientes y registros de demostracion para poder recorrer el panel clinico y
la app movil sin esperar a la extraccion documental.

    python scripts/seed.py                 # solo la cuenta del medico
    python scripts/seed.py --demo          # ademas, 5 pacientes y un familiar

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
    Acompanante,
    Aseguramiento,
    Diagnostico,
    EstadoAcompanante,
    EstadoToma,
    NivelSocioeconomico,
    OrigenRegistro,
    Paciente,
    Parentesco,
    RegistroAdherencia,
    Rol,
    Sexo,
    Usuario,
    ZonaResidencia,
)

CORREO_MEDICO = "milko.ugaz@consultorio.pe"

# Acompanante de demostracion, vinculado al primer paciente ficticio. Permite
# recorrer el grupo familiar (RF09) con un solo dispositivo, sin necesidad de
# un segundo telefono para el familiar.
CORREO_ACOMPANANTE = "rosa.d-001@ejemplo.pe"

# Marca que deja la migracion de identidad en las fichas anteriores a ella.
# Una ficha con este valor esta a medio completar, no completa.
RELLENO_MIGRACION = "(por registrar)"

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


def crear_cuenta_de_paciente(db, paciente: Paciente, clave: str) -> Usuario | None:
    """Crea la cuenta con la que el paciente entra en la aplicacion movil.

    La ficha clinica y la cuenta de acceso son entidades distintas: se puede
    tener ficha sin cuenta —un paciente que no usa el telefono— pero no al
    reves. Sin este paso la aplicacion movil no tiene con que iniciar sesion.
    """
    if not paciente.correo:
        return None

    existente = db.query(Usuario).filter(Usuario.correo == paciente.correo).first()
    if existente is not None:
        return existente

    cuenta = Usuario(
        nombres=paciente.nombres,
        apellidos=paciente.apellidos,
        correo=paciente.correo,
        hash_contrasena=hash_password(clave),
        rol=Rol.PACIENTE,
    )
    db.add(cuenta)
    db.flush()
    paciente.id_usuario = cuenta.id_usuario
    return cuenta


def crear_demo(db, medico: Usuario, clave: str) -> None:
    """Crea o **completa** los pacientes de demostracion.

    No se limita a saltar lo que ya existe: una ficha creada antes de que la
    identidad fuera obligatoria quedo con el relleno de la migracion y sin
    cuenta movil, de modo que rendirse al encontrarla dejaria el sistema en
    ese estado intermedio para siempre. Cada paso comprueba lo que falta y lo
    completa, asi que el script puede ejecutarse las veces que haga falta.
    """
    ahora = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    creados = completados = cuentas = 0

    for (codigo, nombres, apellidos, edad, sexo, dx, nse, aseg, zona, anios, comorb,
         farmacos, tomas, programados, perdidos, morisky) in PACIENTES_DEMO:

        paciente = (
            db.query(Paciente).filter(Paciente.codigo_anonimizado == codigo).first()
        )

        if paciente is None:
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
            creados += 1
        else:
            # Ficha preexistente: se completa lo que la migracion dejo a medias.
            reparada = False
            if paciente.nombres in (RELLENO_MIGRACION, "", None):
                paciente.nombres, paciente.apellidos = nombres, apellidos
                reparada = True
            if not paciente.correo:
                paciente.correo = f"{codigo.lower()}@ejemplo.pe"
                paciente.telefono = "9" + codigo.replace("D-", "").rjust(8, "0")
                reparada = True
            completados += reparada

        if crear_cuenta_de_paciente(db, paciente, clave) is not None:
            cuentas += paciente.id_usuario is not None

        # El historial solo se genera una vez: repetirlo duplicaria eventos y
        # falsearia la tasa de adherencia observada.
        tiene_historial = (
            db.query(RegistroAdherencia)
            .filter(RegistroAdherencia.id_paciente == paciente.id_paciente)
            .first()
            is not None
        )
        if tiene_historial:
            continue

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

    if creados:
        print(f"{creados} paciente(s) de demostracion creado(s).")
    if completados:
        print(f"{completados} ficha(s) preexistente(s) completada(s) con su identidad.")
    print("Cuentas de la aplicacion movil (misma contrasena que el medico):")
    for codigo, *_ in PACIENTES_DEMO:
        print(f"  {codigo.lower()}@ejemplo.pe")


def crear_acompanante_demo(db, clave: str) -> None:
    """Vincula un familiar ficticio al paciente D-001 y corrobora sus tomas.

    Sin esto, mostrar el acompanamiento exigiria dos telefonos: uno que invite
    y otro que canjee el codigo. Aqui el vinculo nace ya establecido, de modo
    que baste con entrar como familiar para ver las tomas por confirmar.
    """
    paciente = (
        db.query(Paciente).filter(Paciente.codigo_anonimizado == "D-001").first()
    )
    if paciente is None:
        return

    cuenta = db.query(Usuario).filter(Usuario.correo == CORREO_ACOMPANANTE).first()
    if cuenta is None:
        cuenta = Usuario(
            nombres="Rosa",
            apellidos="Vasquez Diaz",
            correo=CORREO_ACOMPANANTE,
            hash_contrasena=hash_password(clave),
            rol=Rol.FAMILIAR,
        )
        db.add(cuenta)
        db.flush()

    vinculo = (
        db.query(Acompanante)
        .filter(
            Acompanante.id_paciente == paciente.id_paciente,
            Acompanante.id_usuario == cuenta.id_usuario,
        )
        .first()
    )
    if vinculo is None:
        db.add(
            Acompanante(
                id_paciente=paciente.id_paciente,
                id_usuario=cuenta.id_usuario,
                nombre_invitado="Rosa",
                parentesco=Parentesco.HIJO,
                estado=EstadoAcompanante.ACTIVO,
                # El vinculo nace ya canjeado, pero la columna es obligatoria:
                # el codigo forma parte de la historia de la fila.
                codigo_invitacion="DEMOD001",
                expira_en=datetime.now(timezone.utc) + timedelta(days=7),
                fecha_vinculacion=datetime.now(timezone.utc),
            )
        )
    elif vinculo.estado is not EstadoAcompanante.ACTIVO:
        vinculo.estado = EstadoAcompanante.ACTIVO

    # Se corroboran las tomas cumplidas mas antiguas y se dejan sin corroborar
    # las recientes: asi el panel del familiar tiene algo que confirmar y la
    # ficha del paciente ya muestra tomas con dos testigos.
    corroborables = (
        db.query(RegistroAdherencia)
        .filter(
            RegistroAdherencia.id_paciente == paciente.id_paciente,
            RegistroAdherencia.estado.in_((EstadoToma.TOMADA, EstadoToma.TOMADA_TARDE)),
            RegistroAdherencia.id_confirmante.is_(None),
        )
        .order_by(RegistroAdherencia.fecha_hora_programada.asc())
        .all()
    )
    for registro in corroborables[:-2]:
        registro.id_confirmante = cuenta.id_usuario
        registro.fecha_confirmacion = registro.fecha_hora_programada

    db.commit()
    print(f"Cuenta de acompanante familiar: {CORREO_ACOMPANANTE}  (paciente D-001)")


def crear_cuentas_pendientes(db, clave: str) -> None:
    """Crea la cuenta movil de toda ficha que tenga correo y aun no la tenga.

    Es lo que se ejecuta cuando el medico da de alta pacientes reales desde el
    panel: la ficha nace con su correo, pero la cuenta de acceso a la
    aplicacion es una entidad distinta y hay que crearla.
    """
    pendientes = (
        db.query(Paciente)
        .filter(Paciente.correo.isnot(None), Paciente.id_usuario.is_(None))
        .all()
    )
    if not pendientes:
        print("No hay fichas con correo pendientes de cuenta movil.")
        return

    for paciente in pendientes:
        cuenta = crear_cuenta_de_paciente(db, paciente, clave)
        if cuenta is not None:
            print(f"  cuenta creada: {paciente.correo}  ({paciente.codigo_anonimizado})")
    db.commit()


def main() -> int:
    parser = argparse.ArgumentParser(description="Carga inicial de la base clinica.")
    parser.add_argument("--demo", action="store_true",
                        help="Crea o completa los pacientes y registros de ejemplo.")
    parser.add_argument("--cuentas", action="store_true",
                        help="Crea la cuenta movil de las fichas que tengan correo.")
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
            crear_demo(db, medico, clave)
            crear_acompanante_demo(db, clave)
        if args.cuentas:
            crear_cuentas_pendientes(db, clave)
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
