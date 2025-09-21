from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

class MembroBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    experiencia: Optional[str] = None
    foto: Optional[bytes] = None
    bg: Optional[bytes] = None

class SubgrupoBase(BaseModel):
    nome_grupo: str
    descricao: Optional[str] = None
    icone_grupo: Optional[bytes] = None
    bg: Optional[bytes] = None

class SubgrupoCreate(SubgrupoBase):
    pass

class MembroCreate(MembroBase):
    subgrupo_ids: List[int] = Field(..., min_length=1)

class SubgrupoInMembro(SubgrupoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class MembroInSubgrupo(MembroBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class Membro(MembroBase):
    id: int
    created_at: datetime
    updated_at: datetime
    subgrupos: List[SubgrupoInMembro] = []

    model_config = ConfigDict(from_attributes=True)

class Subgrupo(SubgrupoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    membros: List[MembroInSubgrupo] = []

    model_config = ConfigDict(from_attributes=True)