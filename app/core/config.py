from pydantic_settings import BaseSettings
from typing import Optional, Union
from pydantic import field_validator
import json


class Settings(BaseSettings):
    """Configurações da aplicação usando Pydantic V2."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://root:!$GEM2026e@161.97.180.189:5432/gem_db"

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Sistema de Publicações Acadêmicas"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API para gerenciamento de publicações, membros e subgrupos"

    # CORS
    BACKEND_CORS_ORIGINS: Union[str, list[str]] = ["http://localhost:3000", "http://localhost:8080"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            # Se for "*", permitir todas as origens
            if v.strip() == "*":
                return ["*"]
            # Tentar parsear como JSON
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
            # Se falhar, dividir por vírgula
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Paginação
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()