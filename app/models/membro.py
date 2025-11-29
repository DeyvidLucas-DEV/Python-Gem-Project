from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .subgrupo import Subgrupo
    from .publicacao import Publicacao


class Membro(Base, TimestampMixin):
    """Modelo para membros/pesquisadores."""

    __tablename__ = "membros"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text)
    experiencia: Mapped[Optional[str]] = mapped_column(Text)
    bg_path: Mapped[Optional[str]] = mapped_column(String(500))
    foto_path: Mapped[Optional[str]] = mapped_column(String(500))

    # Campos de contato/redes sociais
    email: Mapped[Optional[str]] = mapped_column(String(255))
    linkedin: Mapped[Optional[str]] = mapped_column(String(500))
    lattes: Mapped[Optional[str]] = mapped_column(String(500))

    # Relacionamentos Many-to-Many
    subgrupos: Mapped[list["Subgrupo"]] = relationship(
        "Subgrupo",
        secondary="membros_subgrupos",
        back_populates="membros",
        lazy="selectin"
    )

    publicacoes: Mapped[list["Publicacao"]] = relationship(
        "Publicacao",
        secondary="publicacao_autores",
        back_populates="autores",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Membro(id={self.id}, nome='{self.nome}')>"