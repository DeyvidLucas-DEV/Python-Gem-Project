from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """Schema de resposta de token"""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema de payload do token JWT"""
    sub: Optional[int] = None  # user_id
    exp: Optional[int] = None  # expiration time


class LoginRequest(BaseModel):
    """Schema de requisição de login"""
    username: str
    password: str
