from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Esquema base de usuario"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Esquema para crear usuario"""
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    """Esquema para actualizar usuario"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)

class UserInDBBase(UserBase):
    """Esquema base de usuario en BD"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class User(UserInDBBase):
    """Esquema de usuario completo"""
    pass

class UserInDB(UserInDBBase):
    """Esquema de usuario en BD con contraseña hasheada"""
    hashed_password: str