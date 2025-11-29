from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import Optional, TYPE_CHECKING
from datetime import datetime

from app.core.storage import get_file_url

if TYPE_CHECKING:
    from .subgrupo import SubgrupoSummary
    from .publicacao import PublicacaoSummary


class MembroBase(BaseModel):
    """Schema base para Membro."""
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do membro")
    descricao: Optional[str] = Field(None, description="Descrição do membro")
    experiencia: Optional[str] = Field(None, description="Experiência do membro")
    email: Optional[str] = Field(None, max_length=255, description="E-mail do membro")
    linkedin: Optional[str] = Field(None, max_length=500, description="URL do LinkedIn")
    lattes: Optional[str] = Field(None, max_length=500, description="URL do Currículo Lattes")


class MembroCreate(MembroBase):
    """Schema para criação de Membro."""
    pass


class MembroUpdate(BaseModel):
    """Schema para atualização de Membro."""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    descricao: Optional[str] = None
    experiencia: Optional[str] = None
    email: Optional[str] = Field(None, max_length=255)
    linkedin: Optional[str] = Field(None, max_length=500)
    lattes: Optional[str] = Field(None, max_length=500)


class MembroInDB(MembroBase):
    """Schema para Membro no banco de dados."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    foto_path: Optional[str] = None
    bg_path: Optional[str] = None


class Membro(BaseModel):
    """Schema público para Membro com URLs de imagens."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    descricao: Optional[str]
    experiencia: Optional[str]
    email: Optional[str] = None
    linkedin: Optional[str] = None
    lattes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Paths armazenados no banco (não expostos diretamente)
    foto_path: Optional[str] = Field(None, exclude=True)
    bg_path: Optional[str] = Field(None, exclude=True)

    @computed_field(return_type=Optional[str])
    @property
    def foto_url(self) -> Optional[str]:
        """URL para acessar a foto do membro."""
        return get_file_url(self.foto_path)

    @computed_field(return_type=Optional[str])
    @property
    def bg_url(self) -> Optional[str]:
        """URL para acessar o background do membro."""
        return get_file_url(self.bg_path)


class MembroSummary(BaseModel):
    """Schema para um resumo de Membro (usado em relações)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str


class MembroWithRelations(Membro):
    """Schema para Membro com relacionamentos."""
    # Use pydantic.Field with default_factory
    subgrupos: list[SubgrupoSummary] = Field(default_factory=list)
    publicacoes: list[PublicacaoSummary] = Field(default_factory=list)