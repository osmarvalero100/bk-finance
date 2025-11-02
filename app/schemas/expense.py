from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ExpenseBase(BaseModel):
    """Esquema base de gasto"""
    amount: float = Field(..., gt=0)
    description: str = Field(..., min_length=1, max_length=255)
    category_id: int
    date: datetime
    payment_method_id: Optional[int] = None
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
    category_id: Optional[int] = None
    date: Optional[datetime] = None
    payment_method_id: Optional[int] = None
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

# Import here to avoid circular imports
try:
    from app.schemas.category import CategoryResponse
    from app.schemas.payment_method import PaymentMethodResponse
except ImportError:
    # Handle circular imports during schema loading
    CategoryResponse = None
    PaymentMethodResponse = None