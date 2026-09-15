"""Esquemas Pydantic de gestion de pacientes polimedicados (RF02).

Los limites declarados aqui replican, en el borde del API, las restricciones
de integridad de la tabla ``pacientes``. La duplicidad es deliberada: la
validacion de Pydantic devuelve un error legible por el panel medico antes de
tocar la base de datos, mientras que la restriccion SQL garantiza la regla
aunque el dato llegue por otra via (carga masiva, migracion, consola).
"""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from ..db.models import (
    Comorbilidad,
    Convivencia,
    Diagnostico,
    NivelEducativo,
    Sexo,
)

# Criterio de elegibilidad del estudio (Anexo n.o 04): polimedicacion.
MIN_FARMACOS = 5


class PacienteBase(BaseModel):
    """Ficha del paciente: identificacion y variables del Anexo n.o 04."""

    model_config = ConfigDict(extra="forbid")

    # --- Identificacion clinica ---
    # Estos datos permiten al medico contactar al paciente cuando el sistema
    # marca un riesgo alto. No forman parte del dataset: la exportacion hacia
    # el pipeline de aprendizaje automatico solo lleva el codigo seudonimizado.
    nombres: str = Field(min_length=2, max_length=120)
    apellidos: str = Field(min_length=2, max_length=120)
    documento_identidad: str | None = Field(default=None, max_length=20)
    correo: EmailStr | None = None
    telefono: str | None = Field(default=None, max_length=25)

    # --- Dimension: paciente ---
    edad: int = Field(ge=18, le=120, description="Edad en anios cumplidos")
    sexo: Sexo

    # --- Dimension: socioeconomica y de apoyo social ---
    nivel_educativo: NivelEducativo | None = None
    convivencia: Convivencia | None = None
    apoyo_familiar: bool | None = None

    # --- Dimension: enfermedad ---
    diagnostico: Diagnostico
    tiempo_enfermedad_anios: float | None = Field(default=None, ge=0, le=80)
    # El medico marca enfermedades concretas; el total lo calcula el sistema.
    lista_comorbilidades: list[Comorbilidad] = Field(default_factory=list, max_length=15)

    # --- Dimension: terapia (carga terapeutica) ---
    numero_farmacos: int = Field(
        ge=MIN_FARMACOS,
        le=30,
        description="Farmacos prescritos simultaneamente; minimo 5 (polimedicacion)",
    )
    tomas_dia: int = Field(ge=1, le=20, description="Complejidad del regimen")

    # --- Dimension: sistema de salud ---
    controles_programados_6m: int = Field(default=0, ge=0, le=30)
    controles_perdidos_6m: int = Field(default=0, ge=0, le=30)

    # --- Linea base de adherencia (test de Morisky-Green, Anexo n.o 05) ---
    puntaje_morisky: int | None = Field(default=None, ge=0, le=4)
    # La clasificacion proviene del patron de respuestas del instrumento, no de
    # un umbral automatico sobre el puntaje: se registra tal como la determino
    # el encuestador.
    incumplimiento_basal: bool | None = None
    fecha_evaluacion_morisky: date | None = None

    @model_validator(mode="after")
    def _normalizar_identidad(self) -> PacienteBase:
        # Los nombres se teclean a mano: se colapsan los espacios sobrantes
        # para que "Jose  Luis " y "Jose Luis" no sean fichas distintas.
        object.__setattr__(self, "nombres", " ".join(self.nombres.split()))
        object.__setattr__(self, "apellidos", " ".join(self.apellidos.split()))
        return self

    @model_validator(mode="after")
    def _sin_comorbilidades_repetidas(self) -> PacienteBase:
        object.__setattr__(
            self, "lista_comorbilidades", list(dict.fromkeys(self.lista_comorbilidades))
        )
        return self

    @model_validator(mode="after")
    def _controles_coherentes(self) -> PacienteBase:
        if self.controles_perdidos_6m > self.controles_programados_6m:
            raise ValueError(
                "Los controles perdidos no pueden superar a los programados."
            )
        return self


class PacienteCreate(PacienteBase):
    """Alta de un paciente en el seguimiento (HU02)."""

    # Si se omite, el API asigna el siguiente correlativo P-00N.
    codigo_anonimizado: str | None = Field(
        default=None, pattern=r"^P-\d{3,6}$", examples=["P-001"]
    )
    # Cuenta de la app movil, cuando el paciente ya fue dado de alta como usuario.
    id_usuario: str | None = None


class PacienteUpdate(BaseModel):
    """Actualizacion parcial: solo se modifican los campos enviados."""

    model_config = ConfigDict(extra="forbid")

    nombres: str | None = Field(default=None, min_length=2, max_length=120)
    apellidos: str | None = Field(default=None, min_length=2, max_length=120)
    documento_identidad: str | None = Field(default=None, max_length=20)
    correo: EmailStr | None = None
    telefono: str | None = Field(default=None, max_length=25)
    edad: int | None = Field(default=None, ge=18, le=120)
    sexo: Sexo | None = None
    nivel_educativo: NivelEducativo | None = None
    convivencia: Convivencia | None = None
    apoyo_familiar: bool | None = None
    diagnostico: Diagnostico | None = None
    tiempo_enfermedad_anios: float | None = Field(default=None, ge=0, le=80)
    lista_comorbilidades: list[Comorbilidad] | None = Field(default=None, max_length=15)
    numero_farmacos: int | None = Field(default=None, ge=MIN_FARMACOS, le=30)
    tomas_dia: int | None = Field(default=None, ge=1, le=20)
    controles_programados_6m: int | None = Field(default=None, ge=0, le=30)
    controles_perdidos_6m: int | None = Field(default=None, ge=0, le=30)
    puntaje_morisky: int | None = Field(default=None, ge=0, le=4)
    incumplimiento_basal: bool | None = None
    fecha_evaluacion_morisky: date | None = None
    id_usuario: str | None = None
    activo: bool | None = None

    def campos_enviados(self) -> dict:
        """Solo los campos presentes en el cuerpo de la peticion.

        ``exclude_unset`` distingue "no enviado" de "enviado como null", lo que
        permite borrar un dato opcional sin sobrescribir el resto de la ficha.
        """
        cambios = self.model_dump(exclude_unset=True)
        if "lista_comorbilidades" in cambios:
            # Codigos del catalogo sin repetir; enviar null equivale a ninguna.
            cambios["lista_comorbilidades"] = list(dict.fromkeys(
                c.value for c in cambios["lista_comorbilidades"] or []
            ))
        return cambios


class PacienteOut(PacienteBase):
    """Ficha devuelta al panel medico.

    El correo se declara como texto y no como `EmailStr`, al reves que en el
    alta. La validacion estricta corresponde a la entrada; aplicarla tambien a
    la salida significa que una direccion mal formada —heredada de una carga
    masiva o de una migracion— haria fallar el listado **entero** en lugar de
    mostrar esa ficha con un dato imperfecto. Estricto al entrar, tolerante al
    salir.
    """

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    correo: str | None = None

    # Si la ficha tiene ya una cuenta con la que entrar en la aplicacion. No se
    # expone el identificador de la cuenta: al panel solo le hace falta saber
    # si el boton debe decir «generar acceso» o «restablecer contrasena».
    tiene_acceso_movil: bool = False

    # Total de comorbilidades marcadas: la variable que recibe el modelo.
    comorbilidades: int = 0

    id_paciente: str
    codigo_anonimizado: str
    id_usuario: str | None = None
    id_medico_tratante: str | None = None
    activo: bool
    fecha_registro: datetime
    fecha_actualizacion: datetime


class PaginaPacientes(BaseModel):
    """Respuesta paginada del listado del panel clinico."""

    total: int
    pagina: int
    tamano: int
    items: list[PacienteOut]


class AccesoMovilOut(BaseModel):
    """Credenciales recién generadas para la aplicación del paciente.

    La contraseña viaja **una sola vez**, en esta respuesta, y no vuelve a
    estar disponible: en la base solo queda su hash. Si el paciente la pierde,
    el médico genera otra; no hay forma de recuperarla, que es justamente lo
    que se espera de una contraseña bien guardada.
    """

    correo: str
    contrasena_temporal: str
    nombre_completo: str
    # Distingue el alta de la regeneración, para que la interfaz pueda decir
    # con precisión qué acaba de ocurrir.
    creada: bool
