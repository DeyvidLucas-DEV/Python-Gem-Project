from sqlalchemy import String, Text, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .membro import Membro
    from .publicacao import Publicacao


class Subgrupo(Base, TimestampMixin):
    """Modelo para subgrupos de pesquisa."""

    __tablename__ = "subgrupo"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome_grupo: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text)
    icone_grupo: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    bg: Mapped[Optional[bytes]] = mapped_column(LargeBinary)

    # Relacionamentos Many-to-Many
    membros: Mapped[list["Membro"]] = relationship(
        "Membro",
        secondary="membros_subgrupos",
        back_populates="subgrupos",
        lazy="selectin"
    )

    publicacoes: Mapped[list["Publicacao"]] = relationship(
        "Publicacao",
        secondary="publicacao_subgrupos",
        back_populates="subgrupos",
        lazy="selectin"
    )

    infografico: Mapped[Optional[bytes]] = mapped_column(LargeBinary)

    def __repr__(self) -> str:
        return f"<Subgrupo(id={self.id}, nome='{self.nome_grupo}')>"