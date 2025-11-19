from .membro import (
    MembroBase,
    MembroCreate,
    MembroUpdate,
    MembroInDB,
    Membro,
    MembroSummary,
    MembroWithRelations,
)
from .publicacao import (
    TipoPublicacaoEnum,
    PublicacaoBase,
    PublicacaoCreate,
    PublicacaoUpdate,
    PublicacaoInDB,
    Publicacao,
    PublicacaoSummary,
    PublicacaoWithRelations,
)
from .subgrupo import (
    SubgrupoBase,
    SubgrupoCreate,
    SubgrupoUpdate,
    SubgrupoInDB,
    Subgrupo,
    SubgrupoSummary,
    SubgrupoWithRelations,
)
from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    User,
    UserInDB,
)
from .auth import (
    Token,
    TokenPayload,
    LoginRequest,
)

__all__ = [
    # Membro
    "MembroBase",
    "MembroCreate",
    "MembroUpdate",
    "MembroInDB",
    "Membro",
    "MembroSummary",
    "MembroWithRelations",
    # Publicação
    "TipoPublicacaoEnum",
    "PublicacaoBase",
    "PublicacaoCreate",
    "PublicacaoUpdate",
    "PublicacaoInDB",
    "Publicacao",
    "PublicacaoSummary",
    "PublicacaoWithRelations",
    # Subgrupo
    "SubgrupoBase",
    "SubgrupoCreate",
    "SubgrupoUpdate",
    "SubgrupoInDB",
    "Subgrupo",
    "SubgrupoSummary",
    "SubgrupoWithRelations",
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "User",
    "UserInDB",
    # Auth
    "Token",
    "TokenPayload",
    "LoginRequest",
]

MembroWithRelations.model_rebuild()
PublicacaoWithRelations.model_rebuild()
SubgrupoWithRelations.model_rebuild()