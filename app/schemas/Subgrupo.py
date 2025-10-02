from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


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


class SubgrupoWithRelations(Subgrupo):
    """Schema para Subgrupo com relacionamentos."""
    from .membro import MembroSummary
    from .publicacao import PublicacaoSummary

    membros: list[MembroSummary] = []
    publicacoes: list[PublicacaoSummary] = []