from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import Optional, TYPE_CHECKING
from datetime import datetime, date
from enum import Enum

from app.core.storage import get_file_url

if TYPE_CHECKING:
    from .membro import MembroSummary
    from .subgrupo import SubgrupoSummary


class TipoPublicacaoEnum(str, Enum):
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
    year: Optional[date] = Field(None, description="Data da publicação (AAAA-MM-DD)")


class PublicacaoCreate(PublicacaoBase):
    """Schema para criação de Publicação."""
    autor_ids: list[int] = Field(default_factory=list, description="IDs dos autores")
    subgrupo_ids: list[int] = Field(default_factory=list, description="IDs dos subgrupos")


class PublicacaoUpdate(BaseModel):
    """Schema para atualização de Publicação."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    type: Optional[TipoPublicacaoEnum] = None
    year: Optional[date] = None
    autor_ids: Optional[list[int]] = None
    subgrupo_ids: Optional[list[int]] = None


class PublicacaoInDB(PublicacaoBase):
    """Schema para Publicação no banco de dados."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    image_path: Optional[str] = None


class Publicacao(BaseModel):
    """Schema público para Publicação com URL de imagem."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    type: TipoPublicacaoEnum
    year: Optional[date]
    created_at: datetime
    updated_at: datetime

    # Path armazenado no banco (não exposto diretamente)
    image_path: Optional[str] = Field(None, exclude=True)

    @computed_field(return_type=Optional[str])
    @property
    def image_url(self) -> Optional[str]:
        """URL para acessar a imagem da publicação."""
        return get_file_url(self.image_path)


class PublicacaoSummary(BaseModel):
    """Schema resumido para Publicação (usado em relacionamentos)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    type: TipoPublicacaoEnum


class PublicacaoWithRelations(Publicacao):
    """Schema para Publicação com relacionamentos."""
    autores: list[MembroSummary] = Field(default_factory=list)
    subgrupos: list[SubgrupoSummary] = Field(default_factory=list)