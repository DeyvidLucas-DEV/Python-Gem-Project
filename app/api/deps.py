from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.core.security import verify_token
from app.crud.user import user as user_crud
from app.models.user import User

# Security scheme para JWT
security = HTTPBearer()


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


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """
    Dependency para obter o usuário atual a partir do token JWT.
    Lança exceção se o token for inválido ou o usuário não existir.
    """
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_crud.get(db, id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency para obter o usuário atual ativo."""
    return current_user