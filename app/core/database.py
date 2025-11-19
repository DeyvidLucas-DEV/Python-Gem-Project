from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Detectar se é SQLite ou PostgreSQL e configurar engine apropriadamente
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# Configuração do engine baseado no tipo de banco
if is_sqlite:
    # SQLite não suporta pool_size e max_overflow
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False} if "aiosqlite" in settings.DATABASE_URL else {}
    )
else:
    # PostgreSQL com pool de conexões
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

class Base(DeclarativeBase):
    """Base class para todos os modelos SQLAlchemy."""
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency para obter sessão do banco de dados."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            await session.close()