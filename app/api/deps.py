from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings


class PaginationParams:
    """Parâmetros de paginação reutilizáveis."""

    def __init__(
            self,
            skip: int = Query(0, ge=0, description="Número de registros a pular"),
            limit: int = Query(
                settings.DEFAULT_PAGE_SIZE,
                ge=1,
                le=settings.MAX_PAGE_SIZE,
                description="Número máximo de registros a retornar"
            )
    ):
        self.skip = skip
        self.limit = limit


def get_pagination_params() -> PaginationParams:
    """Dependency para parâmetros de paginação."""
    return PaginationParams()


async def get_db_session() -> AsyncSession:
    """Dependency para sessão do banco de dados."""
    async for session in get_db():
        yield session


class SearchParams:
    """Parâmetros de busca reutilizáveis."""

    def __init__(
            self,
            q: Optional[str] = Query(None, description="Termo de busca"),
            sort_by: Optional[str] = Query("id", description="Campo para ordenação"),
            sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$", description="Ordem de classificação")
    ):
        self.query = q
        self.sort_by = sort_by
        self.sort_order = sort_order


def get_search_params() -> SearchParams:
    """Dependency para parâmetros de busca."""
    return SearchParams()