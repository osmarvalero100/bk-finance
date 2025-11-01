from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ExpenseBase(BaseModel):
    """Esquema base de gasto"""
    amount: float = Field(..., gt=0)
    description: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    date: datetime
    payment_method: Optional[str] = Field(None, max_length=50)
    is_recurring: bool = False
    recurring_frequency: Optional[str] = Field(None, max_length=20)
    tags: Optional[str] = None
    notes: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    """Esquema para crear gasto"""
    pass

class ExpenseUpdate(BaseModel):
    """Esquema para actualizar gasto"""
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    date: Optional[datetime] = None
    payment_method: Optional[str] = Field(None, max_length=50)
    is_recurring: Optional[bool] = None
    recurring_frequency: Optional[str] = Field(None, max_length=20)
    tags: Optional[str] = None
    notes: Optional[str] = None

class ExpenseInDBBase(ExpenseBase):
    """Esquema base de gasto en BD"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Expense(ExpenseInDBBase):
    """Esquema de gasto completo"""
    pass

class ExpenseResponse(Expense):
    """Esquema de respuesta de gasto"""
    pass