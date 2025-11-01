from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DebtBase(BaseModel):
    """Esquema base de deuda"""
    name: str = Field(..., min_length=1, max_length=255)
    debt_type: str = Field(..., min_length=1, max_length=50)
    lender: str = Field(..., min_length=1, max_length=255)
    original_amount: float = Field(..., gt=0)
    current_balance: float = Field(..., ge=0)
    interest_rate: float = Field(..., ge=0)
    minimum_payment: float = Field(..., ge=0)
    payment_due_date: Optional[int] = None
    loan_start_date: datetime
    expected_end_date: Optional[datetime] = None
    is_paid_off: bool = False
    paid_off_date: Optional[datetime] = None
    currency: str = "COP"
    collateral: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None

class DebtCreate(DebtBase):
    """Esquema para crear deuda"""
    pass

class DebtUpdate(BaseModel):
    """Esquema para actualizar deuda"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    debt_type: Optional[str] = Field(None, min_length=1, max_length=50)
    lender: Optional[str] = Field(None, min_length=1, max_length=255)
    original_amount: Optional[float] = Field(None, gt=0)
    current_balance: Optional[float] = Field(None, ge=0)
    interest_rate: Optional[float] = Field(None, ge=0)
    minimum_payment: Optional[float] = Field(None, ge=0)
    payment_due_date: Optional[int] = None
    loan_start_date: Optional[datetime] = None
    expected_end_date: Optional[datetime] = None
    is_paid_off: Optional[bool] = None
    paid_off_date: Optional[datetime] = None
    currency: Optional[str] = None
    collateral: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None

class DebtInDBBase(DebtBase):
    """Esquema base de deuda en BD"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Debt(DebtInDBBase):
    """Esquema de deuda completo"""
    pass

class DebtResponse(Debt):
    """Esquema de respuesta de deuda"""
    pass