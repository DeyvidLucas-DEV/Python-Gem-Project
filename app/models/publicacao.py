from sqlalchemy import String, Text, LargeBinary, Enum, TIMESTAMP, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, date
import enum

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .membro import Membro
    from .subgrupo import Subgrupo


class TipoPublicacaoEnum(str, enum.Enum):
    MATERIA = "materia"
    DISSERTACAO = "dissertacao"
    LIVRO = "livro"
    TESE = "tese"
    CAPITULO_LIVRO = "capitulo_livro"
    POLICY_BRIEF = "policy_brief"
    ARTIGO = "Artigo" # <-- mude para minúsculo


class Publicacao(Base, TimestampMixin):
    """Modelo para publicações acadêmicas."""

    __tablename__ = "publicacao"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    image: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    type: Mapped[TipoPublicacaoEnum] = mapped_column(
        Enum(TipoPublicacaoEnum, name="tipo_publicacao_enum", native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    year: Mapped[Optional[date]] = mapped_column(Date)

    # Relacionamentos Many-to-Many
    autores: Mapped[list["Membro"]] = relationship(
        "Membro",
        secondary="publicacao_autores",
        back_populates="publicacoes",
        lazy="selectin"
    )

    subgrupos: Mapped[list["Subgrupo"]] = relationship(
        "Subgrupo",
        secondary="publicacao_subgrupos",
        back_populates="publicacoes",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Publicacao(id={self.id}, title='{self.title[:50]}...')>"