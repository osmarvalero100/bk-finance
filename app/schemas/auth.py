from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class Token(BaseModel):
    """Esquema de token de acceso"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Esquema de datos del token"""
    username: Optional[str] = None

class UserLogin(BaseModel):
    """Esquema para login de usuario"""
    username: str
    password: str

class UserRegister(BaseModel):
    """Esquema para registro de usuario"""
    email: EmailStr
    username: str
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None