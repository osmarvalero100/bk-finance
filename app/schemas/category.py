from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CategoryBase(BaseModel):
    """Esquema base de categoría"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')  # Hex color validation
    icon: Optional[str] = Field(None, max_length=50)
    category_type: str = Field(..., pattern=r'^(expense|income)$')
    parent_id: Optional[int] = None
    is_active: bool = True

class CategoryCreate(CategoryBase):
    """Esquema para crear categoría"""
    pass

class CategoryUpdate(BaseModel):
    """Esquema para actualizar categoría"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(None, max_length=50)
    category_type: Optional[str] = Field(None, pattern=r'^(expense|income)$')
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None

class CategoryInDBBase(CategoryBase):
    """Esquema base de categoría en BD"""
    id: int
    user_id: int
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Category(CategoryInDBBase):
    """Esquema de categoría completo"""
    pass

class CategoryResponse(Category):
    """Esquema de respuesta de categoría"""
    pass

class CategoryWithSubcategories(Category):
    """Esquema de categoría con subcategorías"""
    subcategories: List['CategoryWithSubcategories'] = []

    class Config:
        from_attributes = True

# Update forward reference
CategoryWithSubcategories.update_forward_refs()