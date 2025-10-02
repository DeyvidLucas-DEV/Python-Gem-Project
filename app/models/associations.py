from sqlalchemy import Table, Column, Integer, ForeignKey, TIMESTAMP, func
from .base import Base

# Tabela de associação Many-to-Many: Membros <-> Subgrupos
membros_subgrupos = Table(
    "membros_subgrupos",
    Base.metadata,
    Column("membro_id", Integer, ForeignKey("membros.id", ondelete="CASCADE"), primary_key=True),
    Column("subgrupo_id", Integer, ForeignKey("subgrupo.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", TIMESTAMP(timezone=True), server_default=func.now()),
    Column("updated_at", TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()),
)

# Tabela de associação Many-to-Many: Publicações <-> Autores (Membros)
publicacao_autores = Table(
    "publicacao_autores",
    Base.metadata,
    Column("publicacao_id", Integer, ForeignKey("publicacao.id", ondelete="CASCADE"), primary_key=True),
    Column("membro_id", Integer, ForeignKey("membros.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", TIMESTAMP(timezone=True), server_default=func.now()),
    Column("updated_at", TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()),
)

# Tabela de associação Many-to-Many: Publicações <-> Subgrupos
publicacao_subgrupos = Table(
    "publicacao_subgrupos",
    Base.metadata,
    Column("publicacao_id", Integer, ForeignKey("publicacao.id", ondelete="CASCADE"), primary_key=True),
    Column("subgrupo_id", Integer, ForeignKey("subgrupo.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", TIMESTAMP(timezone=True), server_default=func.now()),
    Column("updated_at", TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()),
)