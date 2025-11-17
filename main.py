from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from datetime import datetime
from pathlib import Path
import logging

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import engine
from app.utils.exceptions import (
    validation_exception_handler,
    integrity_error_handler,
    general_exception_handler
)
from app.utils.metrics import get_all_metrics

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

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
    async def health_check(detailed: bool = False):
        """
        Endpoint de verificação de saúde da aplicação.
        Verifica a API e a conexão com o banco de dados.

        Args:
            detailed: Se True, retorna métricas detalhadas de infraestrutura
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.VERSION,
            "service": settings.PROJECT_NAME,
            "checks": {
                "api": "healthy",
                "database": "unknown"
            }
        }

        # Verificar conexão com o banco de dados
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            health_status["checks"]["database"] = "healthy"
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["checks"]["database"] = "unhealthy"
            health_status["error"] = str(e)
            logger.error(f"Health check failed - Database error: {e}")

        # Adicionar métricas detalhadas se solicitado
        if detailed:
            try:
                health_status["metrics"] = get_all_metrics()
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                health_status["metrics_error"] = str(e)

        return health_status

    @app.get("/health/ui", response_class=HTMLResponse)
    async def health_ui():
        """
        Dashboard completo para visualização de métricas de saúde e infraestrutura.
        """
        dashboard_path = Path(__file__).parent / "app" / "templates" / "dashboard.html"
        return HTMLResponse(content=dashboard_path.read_text())


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
