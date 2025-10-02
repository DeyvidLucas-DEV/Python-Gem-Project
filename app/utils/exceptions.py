from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)


class CustomHTTPException(HTTPException):
    """Exceção HTTP customizada com mais detalhes."""

    def __init__(
            self,
            status_code: int,
            detail: Any = None,
            headers: Optional[Dict[str, Any]] = None,
            error_code: Optional[str] = None,
    ) -> None:
        super().__init__(status_code, detail, headers)
        self.error_code = error_code


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler para erros de validação."""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Erro de validação",
            "detail": str(exc),
            "error_code": "VALIDATION_ERROR"
        }
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Handler para erros de integridade do banco."""
    logger.error(f"Database integrity error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Erro de integridade do banco de dados",
            "detail": "Violação de restrição de integridade",
            "error_code": "INTEGRITY_ERROR"
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler geral para exceções não tratadas."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Erro interno do servidor",
            "detail": "Ocorreu um erro inesperado",
            "error_code": "INTERNAL_ERROR"
        }
    )