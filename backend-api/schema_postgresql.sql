-- ---------------------------------------------------------------------------
-- Sistema de soporte clinico con aprendizaje automatico para prevenir el
-- incumplimiento terapeutico en hipertensos y diabeticos polimedicados.
-- Consultorio medico Milko Ugaz Zegarra - Chiclayo.
--
-- Esquema relacional del nucleo funcional (RF01-RF03).
-- Generado automaticamente desde los modelos SQLAlchemy el 30/08/2026
-- por scripts/generar_ddl.py. NO editar a mano: modificar los modelos y
-- regenerar, o crear una migracion de Alembic.
-- ---------------------------------------------------------------------------

-- === Tipos enumerados del dominio clinico ===
CREATE TYPE rol_usuario AS ENUM ('medico', 'paciente');
CREATE TYPE sexo_paciente AS ENUM ('M', 'F');
CREATE TYPE nivel_socioeconomico AS ENUM ('bajo', 'medio', 'alto');
CREATE TYPE aseguramiento_salud AS ENUM ('sis', 'essalud', 'ninguno');
CREATE TYPE zona_residencia AS ENUM ('urbana', 'rural');
CREATE TYPE diagnostico_base AS ENUM ('hta', 'dm2', 'ambas');
CREATE TYPE estado_toma AS ENUM ('tomada', 'tomada_tarde', 'omitida', 'pospuesta');
CREATE TYPE origen_registro AS ENUM ('app_movil', 'panel_web', 'importacion');

-- === Tabla: usuarios ===
CREATE TABLE usuarios (
	id_usuario VARCHAR(36) NOT NULL, 
	nombres VARCHAR(120) NOT NULL, 
	apellidos VARCHAR(120) NOT NULL, 
	correo VARCHAR(180) NOT NULL, 
	hash_contrasena VARCHAR(255) NOT NULL, 
	rol rol_usuario NOT NULL, 
	activo BOOLEAN NOT NULL, 
	fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL, 
	ultimo_acceso TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id_usuario)
);

CREATE UNIQUE INDEX ix_usuarios_correo ON usuarios (correo);
CREATE INDEX ix_usuarios_rol ON usuarios (rol);

-- === Tabla: pacientes ===
CREATE TABLE pacientes (
	id_paciente VARCHAR(36) NOT NULL, 
	codigo_anonimizado VARCHAR(12) NOT NULL, 
	id_usuario VARCHAR(36), 
	id_medico_tratante VARCHAR(36), 
	edad INTEGER NOT NULL, 
	sexo sexo_paciente NOT NULL, 
	nivel_socioeconomico nivel_socioeconomico, 
	aseguramiento aseguramiento_salud, 
	zona_residencia zona_residencia, 
	diagnostico diagnostico_base NOT NULL, 
	tiempo_enfermedad_anios NUMERIC(4, 1), 
	comorbilidades INTEGER NOT NULL, 
	numero_farmacos INTEGER NOT NULL, 
	tomas_dia INTEGER NOT NULL, 
	controles_programados_6m INTEGER NOT NULL, 
	controles_perdidos_6m INTEGER NOT NULL, 
	puntaje_morisky INTEGER, 
	incumplimiento_basal BOOLEAN, 
	fecha_evaluacion_morisky DATE, 
	activo BOOLEAN NOT NULL, 
	fecha_registro TIMESTAMP WITH TIME ZONE NOT NULL, 
	fecha_actualizacion TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id_paciente), 
	CONSTRAINT ck_paciente_polimedicado CHECK (numero_farmacos >= 5), 
	CONSTRAINT ck_paciente_edad_valida CHECK (edad >= 18 AND edad <= 120), 
	CONSTRAINT ck_paciente_morisky_rango CHECK (puntaje_morisky IS NULL OR (puntaje_morisky >= 0 AND puntaje_morisky <= 4)), 
	CONSTRAINT ck_paciente_controles_coherentes CHECK (controles_perdidos_6m <= controles_programados_6m), 
	UNIQUE (id_usuario), 
	FOREIGN KEY(id_usuario) REFERENCES usuarios (id_usuario) ON DELETE SET NULL, 
	FOREIGN KEY(id_medico_tratante) REFERENCES usuarios (id_usuario) ON DELETE SET NULL
);

CREATE INDEX ix_paciente_medico_activo ON pacientes (id_medico_tratante, activo);
CREATE UNIQUE INDEX ix_pacientes_codigo_anonimizado ON pacientes (codigo_anonimizado);
CREATE INDEX ix_pacientes_id_medico_tratante ON pacientes (id_medico_tratante);

-- === Tabla: registros_adherencia ===
CREATE TABLE registros_adherencia (
	id_registro VARCHAR(36) NOT NULL, 
	id_paciente VARCHAR(36) NOT NULL, 
	medicamento VARCHAR(150) NOT NULL, 
	dosis VARCHAR(60), 
	fecha_hora_programada TIMESTAMP WITH TIME ZONE NOT NULL, 
	fecha_hora_registro TIMESTAMP WITH TIME ZONE, 
	estado estado_toma NOT NULL, 
	origen origen_registro NOT NULL, 
	motivo_omision TEXT, 
	sincronizado BOOLEAN NOT NULL, 
	fecha_sincronizacion TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id_registro), 
	CONSTRAINT uq_registro_toma_programada UNIQUE (id_paciente, medicamento, fecha_hora_programada), 
	FOREIGN KEY(id_paciente) REFERENCES pacientes (id_paciente) ON DELETE CASCADE
);

CREATE INDEX ix_registro_paciente_fecha ON registros_adherencia (id_paciente, fecha_hora_programada);
CREATE INDEX ix_registros_adherencia_estado ON registros_adherencia (estado);
CREATE INDEX ix_registros_adherencia_id_paciente ON registros_adherencia (id_paciente);

