from __future__ import annotations

# Import Field from pydantic, not field from dataclasses
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, TYPE_CHECKING
from datetime import datetime

# Use TYPE_CHECKING to avoid circular imports at runtime
if TYPE_CHECKING:
    from .subgrupo import SubgrupoSummary
    from .publicacao import PublicacaoSummary


class MembroBase(BaseModel):
    """Schema base para Membro."""
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do membro")
    email: Optional[str] = Field(None, description="Email do membro")
    experiencia: Optional[str] = Field(None, description="Experiência do membro")


class MembroCreate(MembroBase):
    """Schema para criação de Membro."""
    pass


class MembroUpdate(BaseModel):
    """Schema para atualização de Membro."""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = None


class MembroInDB(MembroBase):
    """Schema para Membro no banco de dados."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class Membro(MembroInDB):
    """Schema público para Membro."""
    pass


class MembroSummary(BaseModel):
    """Schema para um resumo de Membro (usado em relações)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    experiencia: Optional[str] = None

class MembroWithRelations(Membro):
    """Schema para Membro com relacionamentos."""
    # Use pydantic.Field with default_factory
    subgrupos: list[SubgrupoSummary] = Field(default_factory=list)
    publicacoes: list[PublicacaoSummary] = Field(default_factory=list)

class MembroSchema(BaseModel):
    id: int
    nome: str
    experiencia: Optional[str] = None

    class Config:
        orm_mode = True