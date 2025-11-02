from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class IncomeBase(BaseModel):
    """Esquema base de ingreso"""
    amount: float = Field(..., gt=0)
    description: str = Field(..., min_length=1, max_length=255)
    source: str = Field(..., min_length=1, max_length=100)
    date: datetime
    is_recurring: bool = False
    recurring_frequency: Optional[str] = Field(None, max_length=20)
    category_id: Optional[int] = None
    tags: Optional[str] = None
    notes: Optional[str] = None

class IncomeCreate(IncomeBase):
    """Esquema para crear ingreso"""
    pass

class IncomeUpdate(BaseModel):
    """Esquema para actualizar ingreso"""
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    source: Optional[str] = Field(None, min_length=1, max_length=100)
    date: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    recurring_frequency: Optional[str] = Field(None, max_length=20)
    category_id: Optional[int] = None
    tags: Optional[str] = None
    notes: Optional[str] = None

class IncomeInDBBase(IncomeBase):
    """Esquema base de ingreso en BD"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Income(IncomeInDBBase):
    """Esquema de ingreso completo"""
    pass

class IncomeResponse(Income):
    """Esquema de respuesta de ingreso"""
    pass