from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class FixedExpense(Base):
    """Modelo de Gasto Fijo"""
    __tablename__ = "fixed_expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=True)
    name = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="COP", nullable=False)
    due_day = Column(Integer, nullable=False)  # Día del mes para pago (1-31)
    frequency = Column(String(50), default="monthly", nullable=False)  # monthly, biweekly, yearly
    reminder_days_before = Column(Integer, default=2, nullable=False)  # Días de anticipación para el aviso por email
    email_reminder_enabled = Column(Boolean, default=True, nullable=False)  # Activar/desactivar recordatorio
    is_active = Column(Boolean, default=True, nullable=False)
    last_reminder_sent_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    user = relationship("User", back_populates="fixed_expenses")
    category = relationship("Category")
    payment_method = relationship("PaymentMethod")
