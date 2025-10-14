from __future__ import annotations

# Import Field from pydantic, not field from dataclasses
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, TYPE_CHECKING
from datetime import datetime

# Use TYPE_CHECKING to avoid circular imports at runtime
if TYPE_CHECKING:
    from .membro import MembroSummary
    from .publicacao import PublicacaoSummary


class SubgrupoBase(BaseModel):
    """Schema base para Subgrupo."""
    nome_grupo: str = Field(..., min_length=1, max_length=255, description="Nome do subgrupo")
    descricao: Optional[str] = Field(None, description="Descrição do subgrupo")


class SubgrupoCreate(SubgrupoBase):
    """Schema para criação de Subgrupo."""
    pass


class SubgrupoUpdate(BaseModel):
    """Schema para atualização de Subgrupo."""
    nome_grupo: Optional[str] = Field(None, min_length=1, max_length=255)
    descricao: Optional[str] = None


class SubgrupoInDB(SubgrupoBase):
    """Schema para Subgrupo no banco de dados."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class Subgrupo(SubgrupoInDB):
    """Schema público para Subgrupo."""
    pass


class SubgrupoSummary(BaseModel):
    """Schema para um resumo de Subgrupo (usado em relações)."""
    # Changed to be more consistent with other Summary schemas
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome_grupo: str


class SubgrupoWithRelations(Subgrupo):
    """Schema para Subgrupo com relacionamentos."""
    # Use pydantic.Field with default_factory
    membros: list[MembroSummary] = Field(default_factory=list)
    publicacoes: list[PublicacaoSummary] = Field(default_factory=list)