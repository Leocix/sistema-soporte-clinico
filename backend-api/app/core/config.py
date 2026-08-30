"""Carga y validacion de la configuracion del API Gateway.

Corresponde a la capa "Logica de negocio / Servicios" de la arquitectura de
microservicios descrita en el proyecto de investigacion (Fig. 5). Toda la
configuracion sensible (cadena de conexion cifrada a PostgreSQL, clave de
firma JWT) se carga desde variables de entorno y nunca queda embebida en el
codigo fuente, en cumplimiento de RNF01 (seguridad).
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Parametros de ejecucion del microservicio de API."""

    # --- Identidad del servicio -------------------------------------------
    app_name: str = "CDSS-Adherencia - API Gateway"
    app_version: str = "0.2.0"
    environment: Literal["local", "desarrollo", "produccion"] = "local"

    # --- Persistencia (RNF01: conexion cifrada) ---------------------------
    # En produccion apunta a PostgreSQL gestionado (Aiven) con sslmode=require.
    database_url: str = "sqlite:///./cdss_adherencia.db"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_recycle_seconds: int = 1800

    # --- Seguridad / JWT (RF01, RNF01) ------------------------------------
    secret_key: str = "CAMBIAR-EN-PRODUCCION-POR-UNA-CLAVE-SECRETA-ROBUSTA"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # --- CORS: consumidores autorizados del API ---------------------------
    # Panel medico React+Vite desplegado en Vercel y entorno local de trabajo.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    # Los despliegues de vista previa de Vercel generan un subdominio distinto
    # por cada commit; se autorizan por expresion regular en lugar de listarlos.
    cors_origin_regex: str = r"^https://([a-z0-9-]+\.)*vercel\.app$"

    # --- Cabecera Host permitida (mitigacion de Host header injection) ----
    allowed_hosts: str = "*"

    # --- Microservicio de inferencia (RF04, RF06) -------------------------
    model_path: str = "../ml-pipeline/models/risk_model_v1.pkl"
    umbral_riesgo_alto: float = 0.70

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=("settings_",),
    )

    @field_validator("database_url")
    @classmethod
    def _normalizar_url(cls, v: str) -> str:
        """Adapta la URL que entregan los proveedores gestionados.

        Render y Aiven publican la cadena con el prefijo historico
        ``postgres://``, que SQLAlchemy 2.x ya no reconoce. Se reescribe al
        prefijo con controlador explicito para que el despliegue no falle por
        un detalle de formato ajeno al codigo.
        """
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+psycopg2://", 1)
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v

    # --- Derivados --------------------------------------------------------
    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def allowed_hosts_list(self) -> list[str]:
        return [h.strip() for h in self.allowed_hosts.split(",") if h.strip()]

    @property
    def es_produccion(self) -> bool:
        return self.environment == "produccion"


@lru_cache
def get_settings() -> Settings:
    """Devuelve una unica instancia de configuracion por proceso."""
    return Settings()


settings = get_settings()
