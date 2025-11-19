from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations para User"""

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """Buscar usuário por email"""
        query = select(self.model).where(self.model.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        """Buscar usuário por username"""
        query = select(self.model).where(self.model.username == username)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def authenticate(
        self, db: AsyncSession, *, username: str, password: str
    ) -> Optional[User]:
        """Autenticar usuário (será implementado com as utilidades de segurança)"""
        user = await self.get_by_username(db, username=username)
        if not user:
            return None
        # A verificação de senha será feita no endpoint usando as utils de segurança
        return user

    async def is_active(self, user: User) -> bool:
        """Verificar se o usuário está ativo"""
        return user.is_active

    async def is_superuser(self, user: User) -> bool:
        """Verificar se o usuário é superusuário"""
        return user.is_superuser


# Instância global do CRUD de User
user = CRUDUser(User)
