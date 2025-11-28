from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, computed_field

from app.core.storage import get_file_url

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
    icone_grupo_path: Optional[str] = None
    bg_path: Optional[str] = None


class Subgrupo(BaseModel):
    """
    Schema público para Subgrupo.
    Retorna URLs para as imagens ao invés de dados binários.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome_grupo: str
    descricao: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Paths armazenados no banco (não expostos diretamente)
    icone_grupo_path: Optional[str] = Field(None, exclude=True)
    bg_path: Optional[str] = Field(None, exclude=True)

    @computed_field(return_type=Optional[str])
    @property
    def icone_grupo_url(self) -> Optional[str]:
        """URL para acessar o ícone do subgrupo."""
        return get_file_url(self.icone_grupo_path)

    @computed_field(return_type=Optional[str])
    @property
    def bg_url(self) -> Optional[str]:
        """URL para acessar o background do subgrupo."""
        return get_file_url(self.bg_path)


class SubgrupoSummary(BaseModel):
    """Schema para um resumo de Subgrupo (usado em relações)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome_grupo: str



class SubgrupoWithRelations(Subgrupo):
    """Schema para Subgrupo com relacionamentos."""
    membros: list[MembroSummary] = Field(default_factory=list)
    publicacoes: list[PublicacaoSummary] = Field(default_factory=list)