from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from fastapi import HTTPException, status
import enum  # Necessário para a checagem de filtro

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Classe base para operações CRUD com SQLAlchemy async."""

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object com modelo SQLAlchemy.
        **Parâmetros**
        * `model`: Classe do modelo SQLAlchemy
        """
        self.model = model

    async def get(
            self,
            db: AsyncSession,
            id: Any,
            *,
            load_relations: Optional[List[str]] = None
    ) -> Optional[ModelType]:
        """Buscar um registro por ID."""
        query = select(self.model).where(self.model.id == id)

        if load_relations:
            # Agora carrega apenas os relacionamentos pedidos
            for relation_name in load_relations:
                if hasattr(self.model, relation_name):
                    query = query.options(selectinload(getattr(self.model, relation_name)))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_count(
            self,
            db: AsyncSession,
            *,
            filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Retorna apenas a contagem total de objetos, com filtros."""
        count_query = select(func.count(self.model.id))

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:

                    # --- CORREÇÃO DO BUG AQUI ---
                    # A variável deve ser 'count_query', não 'query'
                    if isinstance(value, str):
                        count_query = count_query.where(getattr(self.model, field).ilike(f"%{value}%"))
                    elif isinstance(value, enum.Enum):
                        count_query = count_query.where(getattr(self.model, field) == value.value)
                    else:
                        count_query = count_query.where(getattr(self.model, field) == value)

        count_result = await db.execute(count_query)
        total = count_result.scalar_one()
        return total

    async def get_multi(
            self,
            db: AsyncSession,
            *,
            skip: int = 0,
            limit: int = 100,
            filters: Optional[Dict[str, Any]] = None,
            # --- CORREÇÃO DA ASSINATURA AQUI ---
            load_relations: Optional[List[str]] = None
    ) -> tuple[List[ModelType], int]:
        """
        Buscar múltiplos registros com paginação e filtros.
        Retorna: (registros, total_count)
        """
        query = select(self.model)
        count_query = select(func.count(self.model.id))

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    if isinstance(value, str):
                        query = query.where(getattr(self.model, field).ilike(f"%{value}%"))
                        count_query = count_query.where(getattr(self.model, field).ilike(f"%{value}%"))
                    elif isinstance(value, enum.Enum):
                        query = query.where(getattr(self.model, field) == value.value)
                        count_query = count_query.where(getattr(self.model, field) == value.value)
                    else:
                        query = query.where(getattr(self.model, field) == value)
                        count_query = count_query.where(getattr(self.model, field) == value)

        if load_relations:
            for relation_name in load_relations:
                if hasattr(self.model, relation_name):
                    query = query.options(selectinload(getattr(self.model, relation_name)))

        query = query.offset(skip).limit(limit).order_by(self.model.id)

        result = await db.execute(query)
        count_result = await db.execute(count_query)

        items = result.scalars().all()
        total = count_result.scalar_one()

        return list(items), total

    async def create(
            self,
            db: AsyncSession,
            *,
            obj_in: CreateSchemaType
    ) -> ModelType:
        """Criar um novo registro."""
        obj_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in.dict()
        db_obj = self.model(**obj_data)

        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)

        return db_obj

    async def update(
            self,
            db: AsyncSession,
            *,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Atualizar um registro existente."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, 'model_dump') else obj_in.dict(
                exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        await db.flush()
        await db.refresh(db_obj)

        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[ModelType]:
        """Remover um registro por ID."""
        db_obj = await self.get(db, id=id)
        if db_obj:
            await db.delete(db_obj)
            await db.flush()
        return db_obj

    async def exists(self, db: AsyncSession, *, id: int) -> bool:
        """Verificar se um registro existe."""
        query = select(self.model.id).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None