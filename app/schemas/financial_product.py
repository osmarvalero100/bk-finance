from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FinancialProductBase(BaseModel):
    """Esquema base de producto financiero"""
    name: str = Field(..., min_length=1, max_length=255)
    product_type: str = Field(..., min_length=1, max_length=50)
    institution: str = Field(..., min_length=1, max_length=255)
    account_number: Optional[str] = Field(None, max_length=100)
    balance: float = 0
    interest_rate: Optional[float] = None
    minimum_balance: float = 0
    monthly_fee: float = 0
    credit_limit: Optional[float] = None
    available_credit: Optional[float] = None
    payment_due_date: Optional[int] = None
    minimum_payment: Optional[float] = None
    is_active: bool = True
    opening_date: Optional[datetime] = None
    maturity_date: Optional[datetime] = None
    currency: str = "COP"
    notes: Optional[str] = None

class FinancialProductCreate(FinancialProductBase):
    """Esquema para crear producto financiero"""
    pass

class FinancialProductUpdate(BaseModel):
    """Esquema para actualizar producto financiero"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    product_type: Optional[str] = Field(None, min_length=1, max_length=50)
    institution: Optional[str] = Field(None, min_length=1, max_length=255)
    account_number: Optional[str] = Field(None, max_length=100)
    balance: Optional[float] = None
    interest_rate: Optional[float] = None
    minimum_balance: Optional[float] = None
    monthly_fee: Optional[float] = None
    credit_limit: Optional[float] = None
    available_credit: Optional[float] = None
    payment_due_date: Optional[int] = None
    minimum_payment: Optional[float] = None
    is_active: Optional[bool] = None
    opening_date: Optional[datetime] = None
    maturity_date: Optional[datetime] = None
    currency: Optional[str] = None
    notes: Optional[str] = None

class FinancialProductInDBBase(FinancialProductBase):
    """Esquema base de producto financiero en BD"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FinancialProduct(FinancialProductInDBBase):
    """Esquema de producto financiero completo"""
    pass

class FinancialProductResponse(FinancialProduct):
    """Esquema de respuesta de producto financiero"""
    pass