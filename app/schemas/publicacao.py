from __future__ import annotations

# Import Field from pydantic, not field from dataclasses
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from enum import Enum

# Use TYPE_CHECKING to avoid circular imports at runtime
if TYPE_CHECKING:
    from .membro import MembroSummary
    from .subgrupo import SubgrupoSummary


class TipoPublicacaoEnum(str, Enum):
    """Enum para tipos de publicação."""
    MATERIA = "materia"
    DISSERTACAO = "dissertacao"
    LIVRO = "livro"
    TESE = "tese"
    CAPITULO_LIVRO = "capitulo_livro"
    POLICY_BRIEF = "policy_brief"
    ARTIGO = "Artigo"


class PublicacaoBase(BaseModel):
    """Schema base para Publicação."""
    title: str = Field(..., min_length=1, max_length=500, description="Título da publicação")
    description: Optional[str] = Field(None, description="Descrição da publicação")
    type: TipoPublicacaoEnum = Field(..., description="Tipo da publicação")
    year: Optional[datetime] = Field(None, description="Ano da publicação")


class PublicacaoCreate(PublicacaoBase):
    """Schema para criação de Publicação."""
    autor_ids: list[int] = Field(default_factory=list, description="IDs dos autores")
    subgrupo_ids: list[int] = Field(default_factory=list, description="IDs dos subgrupos")


class PublicacaoUpdate(BaseModel):
    """Schema para atualização de Publicação."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    type: Optional[TipoPublicacaoEnum] = None
    year: Optional[datetime] = None
    autor_ids: Optional[list[int]] = None
    subgrupo_ids: Optional[list[int]] = None


class PublicacaoInDB(PublicacaoBase):
    """Schema para Publicação no banco de dados."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class Publicacao(PublicacaoInDB):
    """Schema público para Publicação."""
    pass


class PublicacaoSummary(BaseModel):
    """Schema resumido para Publicação (usado em relacionamentos)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    type: TipoPublicacaoEnum



class PublicacaoWithRelations(Publicacao):
    """Schema para Publicação com relacionamentos."""
    # Use pydantic.Field with default_factory
    autores: list[MembroSummary] = Field(default_factory=list)
    subgrupos: list[SubgrupoSummary] = Field(default_factory=list)