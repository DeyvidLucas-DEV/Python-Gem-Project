from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class MembroBase(BaseModel):
    """Schema base para Membro."""
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do membro")
    descricao: Optional[str] = Field(None, description="Descrição do membro")
    experiencia: Optional[str] = Field(None, description="Experiência do membro")


class MembroCreate(MembroBase):
    """Schema para criação de Membro."""
    pass


class MembroUpdate(BaseModel):
    """Schema para atualização de Membro."""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    descricao: Optional[str] = None
    experiencia: Optional[str] = None


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
    """Schema resumido para Membro (usado em relacionamentos)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str


class MembroWithRelations(Membro):
    """Schema para Membro com relacionamentos."""
    from .Subgrupo import SubgrupoSummary
    from .publicacao import PublicacaoSummary

    subgrupos: list[SubgrupoSummary] = []
    publicacoes: list[PublicacaoSummary] = []


class SubgrupoSummary(BaseModel):
    """Schema resumido para Subgrupo (usado em relacionamentos)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome_grupo: str