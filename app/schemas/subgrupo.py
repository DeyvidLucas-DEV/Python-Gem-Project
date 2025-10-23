from __future__ import annotations

import base64
from typing import Optional, TYPE_CHECKING
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, computed_field, validator

if TYPE_CHECKING:
    from .membro import MembroSummary
    from .publicacao import PublicacaoSummary


# ============================================================
# BASE
# ============================================================

class SubgrupoBase(BaseModel):
    """Schema base para Subgrupo."""
    nome_grupo: str = Field(..., min_length=1, max_length=255, description="Nome do subgrupo")
    descricao: Optional[str] = Field(None, description="Descrição do subgrupo")
    infografico: Optional[str] = Field(None, description="Infográfico em Base64")


# ============================================================
# CREATE
# ============================================================

class SubgrupoCreate(SubgrupoBase):
    """Schema para criação de Subgrupo, com tratamento do campo Base64."""
    @validator("infografico", pre=True)
    def decode_infografico(cls, v):
        if not v:
            return None
        if isinstance(v, bytes):
            return v
        if isinstance(v, str):
            try:
                if "," in v:
                    v = v.split(",", 1)[1]
                return base64.b64decode(v.encode("utf-8"))
            except Exception:
                # Se não for base64 válido, converte pra bytes (texto puro)
                return v.encode("utf-8")
        return v


# ============================================================
# UPDATE
# ============================================================

class SubgrupoUpdate(BaseModel):
    """Schema para atualização de Subgrupo."""
    nome_grupo: Optional[str] = Field(None, min_length=1, max_length=255)
    descricao: Optional[str] = None


# ============================================================
# INDB
# ============================================================

class SubgrupoInDB(SubgrupoBase):
    """Schema para Subgrupo no banco de dados."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    # Campos binários armazenados no banco
    icone_grupo: Optional[bytes] = None
    bg: Optional[bytes] = None
    infografico: Optional[bytes] = None


# ============================================================
# PÚBLICO / SAÍDA
# ============================================================

class Subgrupo(BaseModel):
    """
    Schema público para Subgrupo.
    Define explicitamente os campos retornados pela API
    e transforma campos binários em Base64.
    """
    model_config = ConfigDict(from_attributes=True)

    # Campos públicos
    id: int
    nome_grupo: str
    descricao: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Campos binários ocultos (não aparecem diretamente no JSON)
    icone_grupo: Optional[bytes] = Field(None, exclude=True)
    bg: Optional[bytes] = Field(None, exclude=True)
    infografico: Optional[bytes] = Field(None, exclude=True)

    # ============================================================
    # CAMPOS COMPUTADOS (BINÁRIOS → BASE64)
    # ============================================================

    @computed_field(return_type=Optional[str])
    @property
    def icone_grupo_b64(self) -> Optional[str]:
        """Campo computado que retorna o ícone como string Base64."""
        if self.icone_grupo:
            return base64.b64encode(self.icone_grupo).decode('utf-8')
        return None

    @computed_field(return_type=Optional[str])
    @property
    def bg_b64(self) -> Optional[str]:
        """Campo computado que retorna o background como string Base64."""
        if self.bg:
            return base64.b64encode(self.bg).decode('utf-8')
        return None

    @computed_field(return_type=Optional[str])
    @property
    def infografico_b64(self) -> Optional[str]:
        """Campo computado que retorna o infográfico como string Base64."""
        if self.infografico:
            return base64.b64encode(self.infografico).decode("utf-8")
        return None


# ============================================================
# SUMMARY
# ============================================================

class SubgrupoSummary(BaseModel):
    """Schema para resumo de Subgrupo (usado em relações)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome_grupo: str


# ============================================================
# RELATIONS
# ============================================================

class SubgrupoWithRelations(Subgrupo):
    """Schema para Subgrupo com relacionamentos."""
    membros: list[MembroSummary] = Field(default_factory=list)
    publicacoes: list[PublicacaoSummary] = Field(default_factory=list)


# ============================================================
# RESPONSE (ORM MODE)
# ============================================================

class SubgrupoResponse(SubgrupoBase):
    """Schema genérico de resposta simples."""
    id: int

    class Config:
        orm_mode = True
