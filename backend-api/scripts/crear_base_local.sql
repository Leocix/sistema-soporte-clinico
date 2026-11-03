-- =====================================================================
-- Base de datos LOCAL del sistema de soporte clinico (modo sustentacion)
-- PostgreSQL 18 · se ejecuta en pgAdmin
-- =====================================================================
--
-- COMO EJECUTARLO
--   1. En pgAdmin, clic derecho sobre la base "postgres" -> Query Tool.
--   2. Reemplace CAMBIE_ESTA_CONTRASENA por la contrasena que usted elija.
--      Use solo letras, numeros, guiones y guiones bajos: la contrasena va
--      dentro de una URL en local.env, y caracteres como @ : / # ? la rompen.
--   3. Ejecute UNA SENTENCIA A LA VEZ: seleccionela con el raton y pulse F5.
--      pgAdmin envia todo lo que hay en el editor como un solo bloque, y
--      CREATE DATABASE no puede ejecutarse dentro de un bloque.
--
-- QUE NO HACE ESTE SCRIPT
--   No crea las tablas. Las crean las migraciones del proyecto con
--      python iniciar_local.py preparar
--   para que la base local tenga exactamente el mismo esquema que produccion
--   y quede registrada su version. Si las tablas se crearan aqui a mano, las
--   migraciones no las reconocerian.
-- =====================================================================


-- 1. Usuario de la aplicacion -----------------------------------------
--    Puede iniciar sesion y nada mas: no es superusuario, no crea bases
--    ni otros usuarios. Es el principio de minimo privilegio: si alguien
--    obtuviera sus credenciales, no podria salir de su propia base.
CREATE ROLE cdss_app WITH
    LOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    PASSWORD 'CAMBIE_ESTA_CONTRASENA';


-- 2. Base de datos de la aplicacion -----------------------------------
--    cdss_app es su dueno: puede crear y modificar sus tablas, que es lo
--    que necesitan las migraciones. template0 garantiza la codificacion
--    UTF8 aunque el servidor se haya instalado con otra.
CREATE DATABASE cdss_local
    WITH OWNER = cdss_app
         ENCODING = 'UTF8'
         TEMPLATE = template0;

COMMENT ON DATABASE cdss_local IS
    'Sistema de soporte clinico (modo local de demostracion). Datos ficticios.';


-- 3. Nadie mas se conecta ---------------------------------------------
--    Por defecto PostgreSQL deja conectarse a cualquier usuario. Se retira
--    ese permiso: solo entran el dueno (cdss_app) y el administrador.
REVOKE ALL ON DATABASE cdss_local FROM PUBLIC;


-- =====================================================================
-- VERIFICACION — despues de "python iniciar_local.py preparar"
-- Conectese a la base cdss_local (usuario cdss_app) y ejecute:
-- =====================================================================
--
-- Tablas creadas por las migraciones (deben ser 7: las 6 del sistema
-- y alembic_version, que registra la version del esquema):
--   SELECT table_name FROM information_schema.tables
--   WHERE table_schema = 'public' ORDER BY table_name;
--
-- Version del esquema aplicada:
--   SELECT version_num FROM alembic_version;
--
-- Cuentas por perfil (1 medico, 5 pacientes, 1 familiar):
--   SELECT rol, COUNT(*) FROM usuarios GROUP BY rol ORDER BY rol;
--
-- Pacientes de demostracion:
--   SELECT codigo_anonimizado, edad, diagnostico, numero_farmacos, tomas_dia
--   FROM pacientes ORDER BY codigo_anonimizado;
--
-- Las contrasenas se guardan cifradas, nunca en claro:
--   SELECT correo, LEFT(hash_contrasena, 7) || '...' AS hash FROM usuarios;


-- =====================================================================
-- DESHACER — solo si necesita empezar de cero
-- Conectado como postgres a la base "postgres":
-- =====================================================================
--   DROP DATABASE IF EXISTS cdss_local;
--   DROP ROLE IF EXISTS cdss_app;
