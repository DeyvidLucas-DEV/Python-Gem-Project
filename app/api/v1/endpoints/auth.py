from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, get_current_active_user
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.crud.user import user as user_crud
from app.schemas.auth import Token, LoginRequest
from app.schemas.user import User, UserCreate
from app.models.user import User as UserModel

router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Registrar um novo usuário
    """
    # Verificar se o email já existe
    user_by_email = await user_crud.get_by_email(db, email=user_in.email)
    if user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )

    # Verificar se o username já existe
    user_by_username = await user_crud.get_by_username(db, username=user_in.username)
    if user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já cadastrado"
        )

    # Criar o usuário
    user_dict = user_in.model_dump()
    password = user_dict.pop("password")
    user_dict["hashed_password"] = get_password_hash(password)

    # Criar no banco
    from app.models.user import User as UserModel
    db_user = UserModel(**user_dict)
    db.add(db_user)
    await db.flush()
    await db.refresh(db_user)
    await db.commit()

    return db_user


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Login de usuário - retorna token JWT
    """
    # Buscar usuário
    user = await user_crud.get_by_username(db, username=login_data.username)

    # Verificar se o usuário existe e a senha está correta
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar se o usuário está ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    # Criar token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Obter informações do usuário atual
    """
    return current_user
