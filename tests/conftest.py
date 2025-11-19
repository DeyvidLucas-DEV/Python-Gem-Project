import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport

# Importe o 'app' principal e a Base declarativa
from main import app
from app.core.database import Base  # Importe sua Base (de models.base ou similar)
from app.api import deps  # Importe de onde 'get_db_session' está

# Configura um banco de dados SQLite em memória para testes
# 'aiosqlite' é necessário: pip install aiosqlite
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Cria o engine de teste
engine = create_async_engine(TEST_DATABASE_URL)

# Cria uma fábrica de sessões de teste
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture principal do banco de dados.

    - Cria todas as tabelas antes de cada teste.
    - Fornece uma sessão de teste.
    - Limpa (dropa) todas as tabelas após cada teste.
    """
    # Cria as tabelas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Fornece a sessão
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        # Fecha a sessão e limpa o banco
        await session.close()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def test_user(db: AsyncSession):
    """
    Cria um usuário de teste no banco de dados.
    """
    from app.models.user import User
    from app.core.security import get_password_hash

    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
        is_active=True,
        is_superuser=False
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def auth_token(test_user):
    """
    Gera um token JWT válido para o usuário de teste.
    """
    from app.core.security import create_access_token
    from datetime import timedelta

    access_token = create_access_token(
        data={"sub": test_user.id},
        expires_delta=timedelta(minutes=30)
    )
    return access_token


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture do cliente de teste (AsyncClient) SEM autenticação.

    - Substitui a dependência 'get_db_session' pela sessão de teste.
    """

    # Define a função de override da dependência
    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield db

    # Aplica o override no app FastAPI
    app.dependency_overrides[deps.get_db_session] = override_get_db_session

    # Fornece o cliente
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture(scope="function")
async def auth_client(db: AsyncSession, test_user, auth_token) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture do cliente de teste (AsyncClient) COM autenticação.

    - Substitui a dependência 'get_db_session' pela sessão de teste.
    - Substitui a dependência 'get_current_active_user' para retornar o test_user.
    - Inclui o token de autenticação no header de todas as requisições.
    """

    # Define a função de override da dependência de DB
    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield db

    # Define override da autenticação para retornar diretamente o test_user
    async def override_get_current_active_user():
        return test_user

    # Aplica os overrides no app FastAPI
    app.dependency_overrides[deps.get_db_session] = override_get_db_session
    app.dependency_overrides[deps.get_current_active_user] = override_get_current_active_user

    # Fornece o cliente com headers de autenticação
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": f"Bearer {auth_token}"}
    ) as c:
        yield c

    # Limpa os overrides após o teste
    app.dependency_overrides.clear()