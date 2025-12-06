from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.membro import Membro
from app.models.associations import membros_subgrupos, publicacao_autores
from app.schemas.membro import MembroCreate, MembroUpdate


class CRUDMembro(CRUDBase[Membro, MembroCreate, MembroUpdate]):
    """CRUD para Membros com operações específicas."""

    # 👇 MÉTODO GET SOBRESCRITO - CARREGA SUBGRUPOS COM ÍCONE E BG
    async def get(self, db: AsyncSession, *, id: int) -> Optional[Membro]:
        """Buscar membro por ID com subgrupos carregados."""
        query = (
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(self.model.subgrupos))  # 👈 Carrega subgrupos
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_nome(self, db: AsyncSession, *, nome: str) -> Optional[Membro]:
        """Buscar membro por nome exato."""
        query = (
            select(self.model)
            .where(self.model.nome == nome)
            .options(selectinload(self.model.subgrupos))  # 👈 Carrega subgrupos
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def search_by_nome(
            self,
            db: AsyncSession,
            *,
            nome_partial: str,
            skip: int = 0,
            limit: int = 100
    ) -> tuple[List[Membro], int]:
        """Buscar membros por nome parcial."""
        filters = {"nome": nome_partial}
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            load_relations=["subgrupos", "publicacoes"]
        )

    async def get_subgrupos(
            self,
            db: AsyncSession,
            *,
            membro_id: int
    ) -> List[Any]:
        """Obter todos os subgrupos de um membro."""
        membro = await db.get(
            self.model,
            membro_id,
            options=[selectinload(self.model.subgrupos)]
        )
        return membro.subgrupos if membro else []

    async def get_publicacoes(
            self,
            db: AsyncSession,
            *,
            membro_id: int
    ) -> List[Any]:
        """Obter todas as publicações de um membro."""
        membro = await db.get(
            self.model,
            membro_id,
            options=[selectinload(self.model.publicacoes)]
        )
        return membro.publicacoes if membro else []

    async def get_by_subgrupo(
            self,
            db: AsyncSession,
            *,
            subgrupo_id: int,
            skip: int = 0,
            limit: int = 100
    ) -> tuple[List[Membro], int]:
        """Obter membros de um subgrupo específico."""
        query = (
            select(self.model)
            .join(membros_subgrupos)
            .where(membros_subgrupos.c.subgrupo_id == subgrupo_id)
            .options(selectinload(self.model.subgrupos))  # 👈 Carrega subgrupos
            .offset(skip)
            .limit(limit)
        )

        count_query = (
            select(self.model.id)
            .join(membros_subgrupos)
            .where(membros_subgrupos.c.subgrupo_id == subgrupo_id)
        )

        result = await db.execute(query)
        count_result = await db.execute(count_query)

        items = result.scalars().all()
        total = len(count_result.scalars().all())

        return list(items), total

    async def search(
            self,
            db: AsyncSession,
            *,
            query_text: str,
            skip: int = 0,
            limit: int = 100
    ) -> tuple[List[Membro], int]:
        """Busca textual em membros (nome, descrição, experiência)."""
        query = (
            select(self.model)
            .where(
                or_(
                    self.model.nome.ilike(f"%{query_text}%"),
                    self.model.descricao.ilike(f"%{query_text}%"),
                    self.model.experiencia.ilike(f"%{query_text}%")
                )
            )
            .options(selectinload(self.model.subgrupos))  # 👈 Carrega subgrupos
            .offset(skip)
            .limit(limit)
        )

        count_query = (
            select(self.model.id)
            .where(
                or_(
                    self.model.nome.ilike(f"%{query_text}%"),
                    self.model.descricao.ilike(f"%{query_text}%"),
                    self.model.experiencia.ilike(f"%{query_text}%")
                )
            )
        )

        result = await db.execute(query)
        count_result = await db.execute(count_query)

        items = result.scalars().all()
        total = len(count_result.scalars().all())

        return list(items), total


membro = CRUDMembro(Membro)