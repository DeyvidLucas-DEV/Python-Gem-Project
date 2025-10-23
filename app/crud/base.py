from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from app.core.database import Base
import base64

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
        load_relations: bool = False
    ) -> Optional[ModelType]:
        """Buscar um registro por ID."""
        query = select(self.model).where(self.model.id == id)

        if load_relations:
            # Carrega relacionamentos automaticamente
            for relationship in self.model.__mapper__.relationships:
                query = query.options(selectinload(getattr(self.model, relationship.key)))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        load_relations: bool = False
    ) -> tuple[List[ModelType], int]:
        """
        Buscar múltiplos registros com paginação e filtros.

        Retorna: (registros, total_count)
        """
        query = select(self.model)
        count_query = select(func.count(self.model.id))

        # Aplicar filtros
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    if isinstance(value, str):
                        # Busca parcial para strings
                        query = query.where(getattr(self.model, field).ilike(f"%{value}%"))
                        count_query = count_query.where(getattr(self.model, field).ilike(f"%{value}%"))
                    else:
                        query = query.where(getattr(self.model, field) == value)
                        count_query = count_query.where(getattr(self.model, field) == value)

        # Carregar relacionamentos se solicitado
        if load_relations:
            for relationship in self.model.__mapper__.relationships:
                query = query.options(selectinload(getattr(self.model, relationship.key)))

        # Aplicar paginação
        query = query.offset(skip).limit(limit).order_by(self.model.id)

        # Executar queries
        result = await db.execute(query)
        count_result = await db.execute(count_query)

        items = result.scalars().all()
        total = count_result.scalar()

        return list(items), total

    async def create(self, db: AsyncSession, *, obj_in):
        """
        Criar um novo registro no banco de dados.
        Converte automaticamente o campo 'infografico' de base64 para bytes, se presente.
        """
        # --- Converte Pydantic pra dict ---
        if hasattr(obj_in, "model_dump"):
            obj_data = obj_in.model_dump()
        elif hasattr(obj_in, "dict"):
            obj_data = obj_in.dict()
        elif isinstance(obj_in, dict):
            obj_data = obj_in
        else:
            raise TypeError(f"Tipo inesperado em create(): {type(obj_in)}")

        # --- FORÇA a conversão de infografico ---
        if "infografico" in obj_data and obj_data["infografico"] is not None:
            value = obj_data["infografico"]
            print("DEBUG antes da conversão:", type(value), value)
            if isinstance(value, str):
                try:
                    obj_data["infografico"] = base64.b64decode(value)
                    print("DEBUG convertido (base64):", type(obj_data["infografico"]))
                except Exception:
                    obj_data["infografico"] = value.encode("utf-8")
                    print("DEBUG convertido (utf-8):", type(obj_data["infografico"]))
            else:
                print("DEBUG já é bytes:", type(value))

        db_obj = self.model(**obj_data)
        print("DEBUG FINAL antes do flush:", type(db_obj.infografico), db_obj.infografico)

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
            update_data = (
                obj_in.model_dump(exclude_unset=True)
                if hasattr(obj_in, 'model_dump')
                else obj_in.dict(exclude_unset=True)
            )

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
