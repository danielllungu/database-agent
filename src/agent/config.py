from __future__ import annotations
import os
from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = (Path(__file__).resolve().parents[2] / "keys.env")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = os.getenv('OPENAI_API_KEY')
    openai_model: str = os.getenv('OPENAI_MODEL')
    openai_api_base: Optional[str] = None

    db_host: str = os.getenv('DB_HOST')
    db_port: int = os.getenv('DB_PORT')
    db_name: str = os.getenv('DB_NAME')
    db_user: str = os.getenv('DB_USER')
    db_password: str = os.getenv('DB_PASSWORD')
    db_schema: str = os.getenv('DB_SCHEMA')

    app_timezone: str = os.getenv('APP_TIMEZONE')

settings = Settings()