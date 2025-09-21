from sqlalchemy import (Column,Integer,String,Text,LargeBinary,TIMESTAMP,ForeignKey,Table)
import enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

membros_subgrupos_association = Table(
    'membros_subgrupos', Base.metadata,
    Column('membro_id', Integer, ForeignKey('membros.id'), primary_key=True),
    Column('subgrupo_id', Integer, ForeignKey('subgrupo.id'), primary_key=True)
)

class TipoPublicacaoEnum(enum.Enum):
    materia = 'materia'
    dissertacao = 'dissertacao'
    livro = 'livro'
    tese = 'tese'
    capitulo_livro = 'capitulo_livro'
    policy_brief = 'policy_brief'
    Artigo = 'Artigo'


class Subgrupo(Base):
    __tablename__ = "subgrupo"

    id = Column(Integer, primary_key=True, index=True)
    icone_grupo = Column(LargeBinary)
    nome_grupo = Column(String(255), nullable=False, unique=True)
    descricao = Column(Text)
    bg = Column(LargeBinary)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    membros = relationship(
        "Membro",
        secondary=membros_subgrupos_association,
        back_populates="subgrupos"
    )

class Membro(Base):
    __tablename__ = "membros"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text)
    experiencia = Column(Text)
    bg = Column(LargeBinary)
    foto = Column(LargeBinary)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    subgrupos = relationship(
        "Subgrupo",
        secondary=membros_subgrupos_association,
        back_populates="membros"
    )