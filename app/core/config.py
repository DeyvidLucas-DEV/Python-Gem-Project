from pydantic_settings import BaseSettings
from typing import Optional


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
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Paginação
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()