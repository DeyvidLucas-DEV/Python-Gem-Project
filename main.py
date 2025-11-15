from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
import logging

from app.api.v1.api import api_router
from app.core.config import settings
from app.utils.exceptions import (
    validation_exception_handler,
    integrity_error_handler,
    general_exception_handler
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

klsdamfjgb ndjkrofepwqienjkgemrokpgmwkljergnfmewolpfokmwje

logger = logging.getLogger(__name__)



def create_application() -> FastAPI:
    """Factory para criar a aplicação FastAPI."""

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )

    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Incluir routers
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Handlers de exceção
    app.add_exception_handler(ValueError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    @app.get("/")
    async def root():
        """Endpoint de health check."""
        return {
            "message": f"Bem-vindo ao {settings.PROJECT_NAME}",
            "version": settings.VERSION,
            "docs": f"{settings.API_V1_STR}/docs"
        }

    @app.get("/health")
    async def health_check():
        """Endpoint de verificação de saúde."""
        return {"status": "healthy", "version": settings.VERSION}

    return app


app = create_application()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
