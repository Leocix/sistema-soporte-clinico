"""Configuracion del microservicio de inferencia (RF04, RF06).

Todo lo sensible llega por variables de entorno (RNF01). La clave de servicio
es la que el API central envia en cada peticion: sin ella el microservicio no
responde, de modo que exponerlo en internet no expone el modelo.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CDSS-Adherencia - Microservicio de inferencia"
    app_version: str = "0.1.0"
    environment: Literal["local", "desarrollo", "produccion"] = "local"

    # Ruta del modelo, relativa a la raiz de `ml-service`.
    model_path: str = "../ml-pipeline/models/risk_model_v1.pkl"

    # Clave compartida con el API central. Vacia solo en local: en produccion
    # el servicio se niega a arrancar sin ella.
    clave_servicio: str = ""

    # Bandas de riesgo: alto desde este umbral, medio desde UMBRAL_MEDIO.
    umbral_riesgo_alto: float = 0.70
    umbral_riesgo_medio: float = 0.40

    # Evaluaciones del modelo por explicacion SHAP. Mas evaluaciones, mas
    # precision y mas latencia; 400 mantiene la respuesta por debajo de 1 s.
    evaluaciones_shap: int = 400

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore",
        protected_namespaces=("settings_",),
    )

    @property
    def es_produccion(self) -> bool:
        return self.environment == "produccion"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
