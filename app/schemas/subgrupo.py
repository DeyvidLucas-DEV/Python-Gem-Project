from __future__ import annotations

import base64
from typing import Optional, TYPE_CHECKING
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, computed_field

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
    # No banco, os campos são bytes
    icone_grupo: Optional[bytes] = None
    bg: Optional[bytes] = None


class Subgrupo(BaseModel):
    """
    Schema público para Subgrupo.
    Este schema define explicitamente os campos de saída,
    evitando a herança dos campos de bytes e a necessidade de excluí-los.
    """
    model_config = ConfigDict(from_attributes=True)

    # Campos que queremos na resposta da API
    id: int
    nome_grupo: str
    descricao: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Campos que serão usados para os @computed_field
    # Eles não serão expostos diretamente no JSON final.
    icone_grupo: Optional[bytes] = Field(None, exclude=True)
    bg: Optional[bytes] = Field(None, exclude=True)

    @computed_field(return_type=Optional[str])
    @property
    def icone_grupo_b64(self) -> Optional[str]:
        """Campo computado que retorna o ícone como uma string Base64."""
        if self.icone_grupo:
            return base64.b64encode(self.icone_grupo).decode('utf-8')
        return None

    @computed_field(return_type=Optional[str])
    @property
    def bg_b64(self) -> Optional[str]:
        """Campo computado que retorna o background como uma string Base64."""
        if self.bg:
            return base64.b64encode(self.bg).decode('utf-8')
        return None


class SubgrupoSummary(BaseModel):
    """Schema para um resumo de Subgrupo (usado em relações)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome_grupo: str



class SubgrupoWithRelations(Subgrupo):
    """Schema para Subgrupo com relacionamentos."""
    membros: list[MembroSummary] = Field(default_factory=list)
    publicacoes: list[PublicacaoSummary] = Field(default_factory=list)