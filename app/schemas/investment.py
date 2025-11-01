from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class InvestmentBase(BaseModel):
    """Esquema base de inversión"""
    name: str = Field(..., min_length=1, max_length=255)
    symbol: Optional[str] = Field(None, max_length=20)
    investment_type: str = Field(..., min_length=1, max_length=50)
    amount_invested: float = Field(..., gt=0)
    current_value: Optional[float] = None
    purchase_date: datetime
    quantity: Optional[float] = None
    purchase_price: Optional[float] = None
    current_price: Optional[float] = None
    broker_platform: Optional[str] = Field(None, max_length=100)
    fees: float = 0
    taxes: float = 0
    dividends_earned: float = 0
    is_active: bool = True
    maturity_date: Optional[datetime] = None
    risk_level: Optional[str] = Field(None, max_length=20)
    sector: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None

class InvestmentCreate(InvestmentBase):
    """Esquema para crear inversión"""
    pass

class InvestmentUpdate(BaseModel):
    """Esquema para actualizar inversión"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    symbol: Optional[str] = Field(None, max_length=20)
    investment_type: Optional[str] = Field(None, min_length=1, max_length=50)
    amount_invested: Optional[float] = Field(None, gt=0)
    current_value: Optional[float] = None
    purchase_date: Optional[datetime] = None
    quantity: Optional[float] = None
    purchase_price: Optional[float] = None
    current_price: Optional[float] = None
    broker_platform: Optional[str] = Field(None, max_length=100)
    fees: Optional[float] = None
    taxes: Optional[float] = None
    dividends_earned: Optional[float] = None
    is_active: Optional[bool] = None
    maturity_date: Optional[datetime] = None
    risk_level: Optional[str] = Field(None, max_length=20)
    sector: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None

class InvestmentInDBBase(InvestmentBase):
    """Esquema base de inversión en BD"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Investment(InvestmentInDBBase):
    """Esquema de inversión completo"""
    pass

class InvestmentResponse(Investment):
    """Esquema de respuesta de inversión"""
    pass