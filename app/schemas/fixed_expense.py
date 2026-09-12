from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

from app.schemas.category import CategoryResponse
from app.schemas.payment_method import PaymentMethodResponse


class FixedExpenseBase(BaseModel):
    """Esquema base para gasto fijo"""
    name: str = Field(..., min_length=1, max_length=255, description="Nombre del gasto fijo (ej. Alquiler, Internet, Seguro)")
    amount: float = Field(..., gt=0, description="Monto del gasto fijo")
    currency: str = Field(default="COP", max_length=3, description="Código de moneda")
    category_id: int = Field(..., description="ID de la categoría asociada")
    payment_method_id: Optional[int] = Field(None, description="ID del método de pago preferido")
    due_day: int = Field(..., ge=1, le=31, description="Día del mes límite de pago (1-31)")
    frequency: str = Field(default="monthly", max_length=50, description="Frecuencia (monthly, biweekly, yearly)")
    reminder_days_before: int = Field(default=2, ge=0, le=30, description="Días previos al vencimiento para notificar")
    email_reminder_enabled: bool = Field(default=True, description="Indica si debe enviarse recordatorio por email")
    is_active: bool = Field(default=True, description="Estado activo del gasto fijo")
    notes: Optional[str] = Field(None, description="Notas adicionales")


class FixedExpenseCreate(FixedExpenseBase):
    """Esquema para crear gasto fijo"""
    pass


class FixedExpenseUpdate(BaseModel):
    """Esquema para actualizar gasto fijo"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, max_length=3)
    category_id: Optional[int] = None
    payment_method_id: Optional[int] = None
    due_day: Optional[int] = Field(None, ge=1, le=31)
    frequency: Optional[str] = Field(None, max_length=50)
    reminder_days_before: Optional[int] = Field(None, ge=0, le=30)
    email_reminder_enabled: Optional[bool] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class FixedExpenseInDBBase(FixedExpenseBase):
    """Esquema base de BD"""
    id: int
    user_id: int
    last_reminder_sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FixedExpenseResponse(FixedExpenseInDBBase):
    """Esquema de respuesta de gasto fijo con información relacional y calculada"""
    category: Optional[CategoryResponse] = None
    payment_method: Optional[PaymentMethodResponse] = None
    next_due_date: Optional[date] = None
    days_until_due: Optional[int] = None
    is_due_soon: Optional[bool] = None

    class Config:
        from_attributes = True


class FixedExpenseSummary(BaseModel):
    """Resumen estadístico de gastos fijos"""
    total_monthly_amount: float
    total_count: int
    active_count: int
    due_soon_count: int
    reminders_enabled_count: int


class ReminderCheckResult(BaseModel):
    """Resultado de la verificación de recordatorios por email"""
    processed: int
    reminders_sent: int
    details: List[dict]
