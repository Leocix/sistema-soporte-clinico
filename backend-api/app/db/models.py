"""Modelo relacional del sistema de soporte clinico (SQLAlchemy 2.0).

Implementa el modelo de datos disenado en el Sprint 1 y refinado en el
Sprint 2. Las tres entidades cubren el nucleo funcional RF01-RF03:

  * ``Usuario``            -> RF01 (autenticacion y RBAC medico / paciente).
  * ``Paciente``           -> RF02 (gestion del paciente polimedicado) y, a la
                              vez, fila de caracteristicas del dataset segun el
                              Anexo n.o 04, organizada por las dimensiones del
                              modelo multidimensional de adherencia de la OMS.
  * ``RegistroAdherencia`` -> RF03 (registro de la toma desde la app movil) y
                              fuente de las variables conductuales que
                              alimentan el modelo predictivo (RF04).

Los datos de salud se almacenan seudonimizados: ``Paciente.codigo_anonimizado``
(P-001, P-002, ...) es la unica clave usada en el dataset de entrenamiento, de
modo que la extraccion para el pipeline de ML no arrastra identificadores
directos (RNF01).
"""
from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


def _enum(enum_cls, nombre: str) -> SAEnum:
    """Columna enumerada que persiste el VALOR del miembro, no su nombre.

    Por defecto SQLAlchemy almacena el nombre del miembro (``MASCULINO``,
    ``BAJO``), mientras que el API y el instrumento de recoleccion usan el
    valor (``M``, ``bajo``). Esa discrepancia rompe la cadena base de datos ->
    exportacion CSV -> pipeline de ML, que valida las categoricas contra el
    catalogo del Anexo n.o 04. Con ``values_callable`` la base guarda
    exactamente los codigos del instrumento, y lo que se ve en el gestor de
    base de datos coincide con lo que espera `preprocess.py`.
    """
    return SAEnum(enum_cls, name=nombre, values_callable=lambda e: [m.value for m in e])


# ---------------------------------------------------------------------------
# Enumeraciones del dominio clinico (Anexo n.o 04)
# ---------------------------------------------------------------------------
class Rol(str, enum.Enum):
    """Perfiles del control de acceso basado en roles (RBAC).

    ``FAMILIAR`` es el acompanante del paciente en el hogar (RF09). Se modela
    como un perfil propio y no como un paciente con permisos anadidos: no
    tiene ficha clinica, no registra tomas y solo puede corroborar las que el
    paciente ya reporto. Confundir ambos perfiles permitiria a un tercero
    reportar tomas en nombre del paciente, que es justo lo contrario de lo que
    busca la corroboracion.
    """

    MEDICO = "medico"
    PACIENTE = "paciente"
    FAMILIAR = "familiar"


class Sexo(str, enum.Enum):
    MASCULINO = "M"
    FEMENINO = "F"


class NivelSocioeconomico(str, enum.Enum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"


class Aseguramiento(str, enum.Enum):
    SIS = "sis"
    ESSALUD = "essalud"
    NINGUNO = "ninguno"


class ZonaResidencia(str, enum.Enum):
    URBANA = "urbana"
    RURAL = "rural"


class Diagnostico(str, enum.Enum):
    HTA = "hta"
    DM2 = "dm2"
    AMBAS = "ambas"


class Parentesco(str, enum.Enum):
    """Vinculo del acompanante con el paciente.

    Es una variable de la dimension *social y familiar* del modelo
    multidimensional de la OMS: el apoyo del entorno es uno de los factores
    que la literatura asocia a la adherencia, de modo que el parentesco no es
    un adorno de la interfaz sino un dato del estudio.
    """

    CONYUGE = "conyuge"
    HIJO = "hijo"
    HERMANO = "hermano"
    CUIDADOR = "cuidador"
    OTRO = "otro"


class EstadoAcompanante(str, enum.Enum):
    """Ciclo de vida de la pertenencia al grupo familiar."""

    INVITADO = "invitado"
    ACTIVO = "activo"
    REVOCADO = "revocado"


class EstadoToma(str, enum.Enum):
    """Resultado del evento de toma reportado por el paciente (RF03)."""

    TOMADA = "tomada"
    TOMADA_TARDE = "tomada_tarde"
    OMITIDA = "omitida"
    POSPUESTA = "pospuesta"


class OrigenRegistro(str, enum.Enum):
    APP_MOVIL = "app_movil"
    PANEL_WEB = "panel_web"
    IMPORTACION = "importacion"


# ---------------------------------------------------------------------------
# RF01 - Usuario
# ---------------------------------------------------------------------------
class Usuario(Base):
    """Credencial de acceso al sistema, con perfil diferenciado (RF01).

    Criterio de aceptacion (Tabla V del proyecto): "Acceso por rol con
    credenciales validas". La contrasena se persiste unicamente como hash
    bcrypt; el campo ``rol`` se embebe en el JWT para resolver el RBAC.
    """

    __tablename__ = "usuarios"

    id_usuario: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    nombres: Mapped[str] = mapped_column(String(120), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(120), nullable=False)
    correo: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)
    hash_contrasena: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[Rol] = mapped_column(_enum(Rol, "rol_usuario"), nullable=False, index=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_ahora
    )
    ultimo_acceso: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Ficha clinica asociada cuando el usuario tiene rol PACIENTE.
    ficha: Mapped[Paciente | None] = relationship(
        back_populates="usuario",
        foreign_keys="Paciente.id_usuario",
        uselist=False,
    )

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellidos}".strip()

    def __repr__(self) -> str:  # pragma: no cover - ayuda de depuracion
        return f"<Usuario correo={self.correo} rol={self.rol.value}>"


# ---------------------------------------------------------------------------
# RF02 - Paciente polimedicado (y fila del dataset, Anexo n.o 04)
# ---------------------------------------------------------------------------
class Paciente(Base):
    """Paciente hipertenso y/o diabetico polimedicado bajo seguimiento (RF02).

    Cada columna del bloque de variables corresponde a una fila del Anexo
    n.o 04 y se agrupa segun la dimension del modelo multidimensional de
    adherencia de la OMS (2003) a la que pertenece, conservando la
    trazabilidad entre el instrumento de recoleccion y las caracteristicas
    del modelo predictivo.
    """

    __tablename__ = "pacientes"
    __table_args__ = (
        # Criterio de elegibilidad del Anexo n.o 04: polimedicacion >= 5 farmacos.
        CheckConstraint("numero_farmacos >= 5", name="ck_paciente_polimedicado"),
        CheckConstraint("edad >= 18 AND edad <= 120", name="ck_paciente_edad_valida"),
        CheckConstraint(
            "puntaje_morisky IS NULL OR (puntaje_morisky >= 0 AND puntaje_morisky <= 4)",
            name="ck_paciente_morisky_rango",
        ),
        CheckConstraint(
            "controles_perdidos_6m <= controles_programados_6m",
            name="ck_paciente_controles_coherentes",
        ),
        Index("ix_paciente_medico_activo", "id_medico_tratante", "activo"),
    )

    id_paciente: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    # Seudonimo usado en el dataset de entrenamiento (P-001, P-002, ...).
    codigo_anonimizado: Mapped[str] = mapped_column(
        String(12), unique=True, index=True, nullable=False
    )

    # Vinculos de identidad y de responsabilidad clinica.
    id_usuario: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("usuarios.id_usuario", ondelete="SET NULL"), unique=True
    )
    id_medico_tratante: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("usuarios.id_usuario", ondelete="SET NULL"), index=True
    )

    # --- Identificacion clinica -------------------------------------------
    # La seudonimizacion protege el DATASET, no la ficha: el medico necesita
    # saber a quien llamar cuando el sistema marca un riesgo alto. Estos campos
    # viven en la historia clinica y nunca salen hacia el pipeline de
    # aprendizaje automatico, que solo recibe `codigo_anonimizado` (RNF01).
    nombres: Mapped[str] = mapped_column(String(120), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(120), nullable=False)
    documento_identidad: Mapped[str | None] = mapped_column(String(20), index=True)
    correo: Mapped[str | None] = mapped_column(String(180))
    telefono: Mapped[str | None] = mapped_column(String(25))

    # --- Dimension: paciente ---------------------------------------------
    edad: Mapped[int] = mapped_column(Integer, nullable=False)
    sexo: Mapped[Sexo] = mapped_column(_enum(Sexo, "sexo_paciente"), nullable=False)

    # --- Dimension: socioeconomica ---------------------------------------
    nivel_socioeconomico: Mapped[NivelSocioeconomico | None] = mapped_column(
        _enum(NivelSocioeconomico, "nivel_socioeconomico")
    )
    aseguramiento: Mapped[Aseguramiento | None] = mapped_column(
        _enum(Aseguramiento, "aseguramiento_salud")
    )
    zona_residencia: Mapped[ZonaResidencia | None] = mapped_column(
        _enum(ZonaResidencia, "zona_residencia")
    )

    # --- Dimension: enfermedad -------------------------------------------
    diagnostico: Mapped[Diagnostico] = mapped_column(
        _enum(Diagnostico, "diagnostico_base"), nullable=False
    )
    tiempo_enfermedad_anios: Mapped[float | None] = mapped_column(Numeric(4, 1))
    comorbilidades: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # --- Dimension: terapia (carga terapeutica) --------------------------
    numero_farmacos: Mapped[int] = mapped_column(Integer, nullable=False)
    tomas_dia: Mapped[int] = mapped_column(Integer, nullable=False)

    # --- Dimension: sistema de salud -------------------------------------
    controles_programados_6m: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    controles_perdidos_6m: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # --- Linea base de adherencia (test de Morisky-Green, Anexo n.o 05) --
    puntaje_morisky: Mapped[int | None] = mapped_column(Integer)
    # Variable objetivo del modelo: 0 = adherente, 1 = incumplimiento.
    incumplimiento_basal: Mapped[bool | None] = mapped_column(Boolean)
    fecha_evaluacion_morisky: Mapped[date | None] = mapped_column(Date)

    # --- Metadatos de gestion --------------------------------------------
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_ahora
    )
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_ahora, onupdate=_ahora
    )

    usuario: Mapped[Usuario | None] = relationship(
        back_populates="ficha", foreign_keys=[id_usuario]
    )
    medico_tratante: Mapped[Usuario | None] = relationship(foreign_keys=[id_medico_tratante])
    registros: Mapped[list[RegistroAdherencia]] = relationship(
        back_populates="paciente",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    acompanantes: Mapped[list[Acompanante]] = relationship(
        back_populates="paciente",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellidos}".strip()

    @property
    def tiene_acceso_movil(self) -> bool:
        """La ficha tiene detras una cuenta con la que entrar en la aplicacion.

        Ficha y cuenta son entidades distintas: hay pacientes que no usan el
        telefono y su ficha existe igual. El panel necesita distinguirlo para
        ofrecer «generar acceso» o «restablecer la contrasena».
        """
        return self.id_usuario is not None

    @property
    def es_polimedicado(self) -> bool:
        """Criterio de inclusion del estudio: cinco o mas farmacos."""
        return self.numero_farmacos >= 5

    def __repr__(self) -> str:  # pragma: no cover - ayuda de depuracion
        # El repr acaba en los logs: se identifica por el seudonimo, nunca por el
        # nombre del paciente.
        return f"<Paciente codigo={self.codigo_anonimizado} farmacos={self.numero_farmacos}>"


# ---------------------------------------------------------------------------
# RF03 - Registro de la toma de medicamentos
# ---------------------------------------------------------------------------
class RegistroAdherencia(Base):
    """Evento de toma de un medicamento reportado por el paciente (RF03).

    Sustituye el autorreporte verbal detectado en el diagnostico (OE1) por una
    traza digital entre citas. La restriccion unica sobre
    (paciente, medicamento, horario programado) hace idempotente la
    sincronizacion de la app movil: un reintento tras una perdida de
    conectividad no duplica el evento.
    """

    __tablename__ = "registros_adherencia"
    __table_args__ = (
        UniqueConstraint(
            "id_paciente",
            "medicamento",
            "fecha_hora_programada",
            name="uq_registro_toma_programada",
        ),
        Index("ix_registro_paciente_fecha", "id_paciente", "fecha_hora_programada"),
    )

    id_registro: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    id_paciente: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("pacientes.id_paciente", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    medicamento: Mapped[str] = mapped_column(String(150), nullable=False)
    dosis: Mapped[str | None] = mapped_column(String(60))

    fecha_hora_programada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    fecha_hora_registro: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    estado: Mapped[EstadoToma] = mapped_column(
        _enum(EstadoToma, "estado_toma"), nullable=False, index=True
    )
    origen: Mapped[OrigenRegistro] = mapped_column(
        _enum(OrigenRegistro, "origen_registro"),
        nullable=False,
        default=OrigenRegistro.APP_MOVIL,
    )
    motivo_omision: Mapped[str | None] = mapped_column(Text)

    # --- Corroboracion por el grupo familiar (RF09) -----------------------
    # El autorreporte es el punto debil reconocido de toda medicion de
    # adherencia: el paciente puede marcar una toma que no ocurrio, por olvido
    # de lo que hizo o por deseo de agradar a su medico. Que un conviviente
    # confirme el evento no lo convierte en una medida objetiva, pero anade un
    # segundo testigo y permite distinguir en el analisis las tomas
    # corroboradas de las que solo tienen la palabra del paciente.
    id_confirmante: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("usuarios.id_usuario", ondelete="SET NULL")
    )
    fecha_confirmacion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Trazabilidad de la sincronizacion offline de la app Flutter.
    sincronizado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    fecha_sincronizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_ahora
    )

    paciente: Mapped[Paciente] = relationship(back_populates="registros")
    confirmante: Mapped[Usuario | None] = relationship(foreign_keys=[id_confirmante])

    @property
    def corroborada(self) -> bool:
        """La toma cuenta con el testimonio de un acompanante, no solo el propio."""
        return self.id_confirmante is not None

    @property
    def cumplida(self) -> bool:
        """Un evento cuenta como cumplido si la toma ocurrio, aun con retraso."""
        return self.estado in (EstadoToma.TOMADA, EstadoToma.TOMADA_TARDE)

    @property
    def minutos_de_retraso(self) -> float | None:
        """Retraso frente al horario prescrito. Insumo de la ingenieria de
        caracteristicas conductuales del modelo predictivo (RF04)."""
        if self.fecha_hora_registro is None:
            return None
        delta = self.fecha_hora_registro - self.fecha_hora_programada
        return round(delta.total_seconds() / 60, 1)

    def __repr__(self) -> str:  # pragma: no cover - ayuda de depuracion
        return f"<RegistroAdherencia medicamento={self.medicamento} estado={self.estado.value}>"


# ---------------------------------------------------------------------------
# RF09 - Grupo familiar de acompanamiento
# ---------------------------------------------------------------------------
class Acompanante(Base):
    """Familiar o cuidador que acompana al paciente en el domicilio (RF09).

    Responde a la debilidad de fondo del registro de adherencia: hasta ahora
    la unica fuente de la toma era el propio paciente. El acompanante corrobora
    lo reportado, de modo que el evento pase de autorreporte a reporte con
    testigo.

    La invitacion y la pertenencia son **la misma fila** en dos momentos de su
    ciclo de vida, no dos tablas. El paciente crea la fila con un codigo y sin
    usuario (``INVITADO``); cuando el familiar canjea ese codigo, la misma fila
    recibe la cuenta recien creada y pasa a ``ACTIVO``. Separarlas obligaria a
    mantener sincronizados dos estados que siempre describen lo mismo.

    El codigo es ademas la unica puerta de alta de cuentas del sistema: no hay
    registro abierto: sin una invitacion vigente emitida por un paciente no se
    puede crear ninguna cuenta de familiar.
    """

    __tablename__ = "acompanantes"
    __table_args__ = (
        # Un mismo familiar no puede figurar dos veces en el grupo del mismo
        # paciente. Las invitaciones sin canjear llevan `id_usuario` nulo y no
        # colisionan entre si, que es lo deseable: pueden coexistir varias.
        UniqueConstraint(
            "id_paciente", "id_usuario", name="uq_acompanante_paciente_usuario"
        ),
        # Una invitacion no canjeada no tiene cuenta detras; una pertenencia ya
        # establecida no puede quedarse sin ella.
        CheckConstraint(
            "(estado = 'invitado' AND id_usuario IS NULL) "
            "OR (estado <> 'invitado' AND id_usuario IS NOT NULL)",
            name="ck_acompanante_vinculo_coherente",
        ),
        Index("ix_acompanante_paciente_estado", "id_paciente", "estado"),
    )

    id_acompanante: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_uuid
    )
    id_paciente: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("pacientes.id_paciente", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Nulo mientras la invitacion no se canjea.
    id_usuario: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("usuarios.id_usuario", ondelete="CASCADE")
    )

    # Como llama el paciente a quien invita, para que la invitacion pendiente
    # sea legible antes de que exista la cuenta.
    nombre_invitado: Mapped[str] = mapped_column(String(120), nullable=False)
    parentesco: Mapped[Parentesco] = mapped_column(
        _enum(Parentesco, "parentesco_acompanante"), nullable=False
    )
    estado: Mapped[EstadoAcompanante] = mapped_column(
        _enum(EstadoAcompanante, "estado_acompanante"),
        nullable=False,
        default=EstadoAcompanante.INVITADO,
    )

    codigo_invitacion: Mapped[str] = mapped_column(
        String(12), unique=True, index=True, nullable=False
    )
    # Una invitacion que no caduca es una credencial permanente circulando por
    # WhatsApp: el codigo deja de servir aunque nadie lo revoque.
    expira_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    fecha_invitacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_ahora
    )
    fecha_vinculacion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    paciente: Mapped[Paciente] = relationship(back_populates="acompanantes")
    usuario: Mapped[Usuario | None] = relationship(foreign_keys=[id_usuario])

    @property
    def vigente(self) -> bool:
        """La invitacion todavia admite ser canjeada."""
        if self.estado is not EstadoAcompanante.INVITADO:
            return False
        expira = self.expira_en
        if expira.tzinfo is None:
            # SQLite devuelve la marca sin zona; se interpreta en UTC, que es
            # como se escribio.
            expira = expira.replace(tzinfo=timezone.utc)
        return expira > _ahora()

    def __repr__(self) -> str:  # pragma: no cover - ayuda de depuracion
        return (
            f"<Acompanante paciente={self.id_paciente} "
            f"parentesco={self.parentesco.value} estado={self.estado.value}>"
        )


# ---------------------------------------------------------------------------
# RF10 - Restablecimiento de la contrasena
# ---------------------------------------------------------------------------
class Restablecimiento(Base):
    """Permiso de un solo uso para fijar una contrasena nueva (RF10).

    Del enlace que recibe el usuario **no se guarda nada legible**: la columna
    conserva el SHA-256 del testigo, igual que la tabla de usuarios conserva el
    hash de la contrasena y no la contrasena. Quien consiguiera leer esta tabla
    obtendria una lista de resumenes inservibles para entrar en ninguna cuenta.

    Tres condiciones lo invalidan y las tres importan: que caduque, porque un
    enlace de recuperacion vive en una bandeja de correo que puede quedar
    abierta; que solo sirva una vez, para que reenviar el mismo mensaje no
    conceda un segundo acceso; y que emitir uno nuevo anule los anteriores, de
    modo que quien no recuerda si ya lo pidio no deje varios activos a la vez.
    """

    __tablename__ = "restablecimientos"
    __table_args__ = (
        Index("ix_restablecimiento_usuario_uso", "id_usuario", "usado_en"),
    )

    id_restablecimiento: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_uuid
    )
    id_usuario: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("usuarios.id_usuario", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # SHA-256 en hexadecimal del testigo que viaja en el enlace.
    hash_testigo: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )

    expira_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    usado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fecha_solicitud: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_ahora
    )

    usuario: Mapped[Usuario] = relationship()

    @property
    def vigente(self) -> bool:
        if self.usado_en is not None:
            return False
        expira = self.expira_en
        if expira.tzinfo is None:
            expira = expira.replace(tzinfo=timezone.utc)
        return expira > _ahora()

    def __repr__(self) -> str:  # pragma: no cover - ayuda de depuracion
        # Nunca el testigo, ni siquiera su hash: este repr acaba en los logs.
        return f"<Restablecimiento usuario={self.id_usuario} usado={self.usado_en is not None}>"
