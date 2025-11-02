from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PaymentMethodBase(BaseModel):
    """Esquema base de método de pago"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    payment_type: str = Field(..., min_length=1, max_length=50)
    institution: Optional[str] = Field(None, max_length=255)
    account_number: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')  # Hex color validation
    icon: Optional[str] = Field(None, max_length=50)
    is_default: bool = False
    is_active: bool = True

class PaymentMethodCreate(PaymentMethodBase):
    """Esquema para crear método de pago"""
    pass

class PaymentMethodUpdate(BaseModel):
    """Esquema para actualizar método de pago"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    payment_type: Optional[str] = Field(None, min_length=1, max_length=50)
    institution: Optional[str] = Field(None, max_length=255)
    account_number: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(None, max_length=50)
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None

class PaymentMethodInDBBase(PaymentMethodBase):
    """Esquema base de método de pago en BD"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaymentMethod(PaymentMethodInDBBase):
    """Esquema de método de pago completo"""
    pass

class PaymentMethodResponse(PaymentMethod):
    """Esquema de respuesta de método de pago"""
    pass