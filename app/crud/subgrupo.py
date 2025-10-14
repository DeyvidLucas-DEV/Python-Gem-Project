from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.subgrupo import Subgrupo
from app.models.associations import membros_subgrupos
from app.schemas.subgrupo import SubgrupoCreate, SubgrupoUpdate


class CRUDSubgrupo(CRUDBase[Subgrupo, SubgrupoCreate, SubgrupoUpdate]):
    """CRUD para Subgrupos com operações específicas."""

    async def get_by_nome(self, db: AsyncSession, *, nome_grupo: str) -> Optional[Subgrupo]:
        """Buscar subgrupo por nome."""
        query = select(self.model).where(self.model.nome_grupo == nome_grupo)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def add_membro(
            self,
            db: AsyncSession,
            *,
            subgrupo_id: int,
            membro_id: int
    ) -> bool:
        """Adicionar membro ao subgrupo."""
        query = select(membros_subgrupos).where(
            and_(
                membros_subgrupos.c.subgrupo_id == subgrupo_id,
                membros_subgrupos.c.membro_id == membro_id
            )
        )
        result = await db.execute(query)

        if result.first():
            return False  # Associação já existe

        stmt = membros_subgrupos.insert().values(
            subgrupo_id=subgrupo_id,
            membro_id=membro_id
        )
        await db.execute(stmt)
        await db.flush()
        return True

    async def remove_membro(
            self,
            db: AsyncSession,
            *,
            subgrupo_id: int,
            membro_id: int
    ) -> bool:
        """Remover membro do subgrupo."""
        stmt = membros_subgrupos.delete().where(
            and_(
                membros_subgrupos.c.subgrupo_id == subgrupo_id,
                membros_subgrupos.c.membro_id == membro_id
            )
        )
        result = await db.execute(stmt)
        await db.flush()
        return result.rowcount > 0

    async def get_membros(
            self,
            db: AsyncSession,
            *,
            subgrupo_id: int
    ) -> List[Any]:
        """Obter todos os membros de um subgrupo."""
        subgrupo = await db.get(
            self.model,
            subgrupo_id,
            options=[selectinload(self.model.membros)]
        )
        return subgrupo.membros if subgrupo else []

    async def search(
            self,
            db: AsyncSession,
            *,
            query_text: str,
            skip: int = 0,
            limit: int = 100
    ) -> tuple[List[Subgrupo], int]:
        """Busca textual em subgrupos."""
        filters = {
            "nome_grupo": query_text,
            "descricao": query_text
        }
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters
        )


subgrupo = CRUDSubgrupo(Subgrupo)