from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, extract
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.publicacao import Publicacao, TipoPublicacaoEnum
from app.models.associations import publicacao_autores, publicacao_subgrupos
from app.schemas.publicacao import PublicacaoCreate, PublicacaoUpdate


class CRUDPublicacao(CRUDBase[Publicacao, PublicacaoCreate, PublicacaoUpdate]):
    """CRUD para Publicações com operações específicas."""

    async def create_with_relations(
            self,
            db: AsyncSession,
            *,
            obj_in: PublicacaoCreate
    ) -> Publicacao:
        """Criar publicação com autores e subgrupos."""
        # Extrair dados dos relacionamentos
        autor_ids = obj_in.autor_ids
        subgrupo_ids = obj_in.subgrupo_ids

        # Criar objeto sem os relacionamentos
        obj_data = obj_in.model_dump(exclude={'autor_ids', 'subgrupo_ids'})
        db_obj = self.model(**obj_data)

        db.add(db_obj)
        await db.flush()  # Para obter o ID

        # Adicionar autores
        if autor_ids:
            for autor_id in autor_ids:
                stmt = publicacao_autores.insert().values(
                    publicacao_id=db_obj.id,
                    membro_id=autor_id
                )
                await db.execute(stmt)

        # Adicionar subgrupos
        if subgrupo_ids:
            for subgrupo_id in subgrupo_ids:
                stmt = publicacao_subgrupos.insert().values(
                    publicacao_id=db_obj.id,
                    subgrupo_id=subgrupo_id
                )
                await db.execute(stmt)

        await db.flush()
        await db.refresh(db_obj)

        return db_obj

    async def update_with_relations(
            self,
            db: AsyncSession,
            *,
            db_obj: Publicacao,
            obj_in: PublicacaoUpdate
    ) -> Publicacao:
        """Atualizar publicação com relacionamentos."""
        update_data = obj_in.model_dump(exclude_unset=True)

        # Atualizar campos básicos
        basic_data = {k: v for k, v in update_data.items()
                      if k not in ['autor_ids', 'subgrupo_ids']}

        for field, value in basic_data.items():
            setattr(db_obj, field, value)

        # Atualizar autores se fornecido
        if 'autor_ids' in update_data:
            # Remover autores existentes
            delete_stmt = publicacao_autores.delete().where(
                publicacao_autores.c.publicacao_id == db_obj.id
            )
            await db.execute(delete_stmt)

            # Adicionar novos autores
            for autor_id in update_data['autor_ids']:
                stmt = publicacao_autores.insert().values(
                    publicacao_id=db_obj.id,
                    membro_id=autor_id
                )
                await db.execute(stmt)

        # Atualizar subgrupos se fornecido
        if 'subgrupo_ids' in update_data:
            # Remover subgrupos existentes
            delete_stmt = publicacao_subgrupos.delete().where(
                publicacao_subgrupos.c.publicacao_id == db_obj.id
            )
            await db.execute(delete_stmt)

            # Adicionar novos subgrupos
            for subgrupo_id in update_data['subgrupo_ids']:
                stmt = publicacao_subgrupos.insert().values(
                    publicacao_id=db_obj.id,
                    subgrupo_id=subgrupo_id
                )
                await db.execute(stmt)

        await db.flush()
        await db.refresh(db_obj)

        return db_obj

    async def get_by_tipo(
            self,
            db: AsyncSession,
            *,
            tipo: TipoPublicacaoEnum,
            skip: int = 0,
            limit: int = 100
    ) -> tuple[List[Publicacao], int]:
        """Obter publicações por tipo."""
        filters = {"type": tipo}
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            load_relations=True
        )

    async def get_by_year(
            self,
            db: AsyncSession,
            *,
            year: int,
            skip: int = 0,
            limit: int = 100
    ) -> tuple[List[Publicacao], int]:
        """Obter publicações por ano."""
        query = (
            select(self.model)
            .where(extract('year', self.model.year) == year)
            .offset(skip)
            .limit(limit)
        )

        count_query = (
            select(self.model.id)
            .where(extract('year', self.model.year) == year)
        )

        result = await db.execute(query)
        count_result = await db.execute(count_query)

        items = result.scalars().all()
        total = len(count_result.scalars().all())

        return list(items), total

    async def get_by_autor(
            self,
            db: AsyncSession,
            *,
            autor_id: int,
            skip: int = 0,
            limit: int = 100
    ) -> tuple[List[Publicacao], int]:
        """Obter publicações de um autor específico."""
        query = (
            select(self.model)
            .join(publicacao_autores)
            .where(publicacao_autores.c.membro_id == autor_id)
            .offset(skip)
            .limit(limit)
        )

        count_query = (
            select(self.model.id)
            .join(publicacao_autores)
            .where(publicacao_autores.c.membro_id == autor_id)
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
            tipo: Optional[TipoPublicacaoEnum] = None,
            year: Optional[int] = None,
            skip: int = 0,
            limit: int = 100
    ) -> tuple[List[Publicacao], int]:
        """Busca avançada em publicações."""
        query = select(self.model).where(
            or_(
                self.model.title.ilike(f"%{query_text}%"),
                self.model.description.ilike(f"%{query_text}%")
            )
        )

        count_query = select(self.model.id).where(
            or_(
                self.model.title.ilike(f"%{query_text}%"),
                self.model.description.ilike(f"%{query_text}%")
            )
        )

        # Filtros adicionais
        if tipo:
            query = query.where(self.model.type == tipo)
            count_query = count_query.where(self.model.type == tipo)

        if year:
            query = query.where(extract('year', self.model.year) == year)
            count_query = count_query.where(extract('year', self.model.year) == year)

        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        count_result = await db.execute(count_query)

        items = result.scalars().all()
        total = len(count_result.scalars().all())

        return list(items), total


publicacao = CRUDPublicacao(Publicacao)