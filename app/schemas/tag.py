from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TagBase(BaseModel):
    """Esquema base de etiqueta"""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')  # Hex color validation
    icon: Optional[str] = Field(None, max_length=50)
    is_active: bool = True

class TagCreate(TagBase):
    """Esquema para crear etiqueta"""
    pass

class TagUpdate(BaseModel):
    """Esquema para actualizar etiqueta"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

class TagInDBBase(TagBase):
    """Esquema base de etiqueta en BD"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Tag(TagInDBBase):
    """Esquema de etiqueta completo"""
    pass

class TagResponse(Tag):
    """Esquema de respuesta de etiqueta"""
    pass

class TagWithUsage(Tag):
    """Esquema de etiqueta con información de uso"""
    expense_count: int = 0
    income_count: int = 0