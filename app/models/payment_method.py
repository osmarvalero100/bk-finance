from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class PaymentMethod(Base):
    """Modelo de Método de Pago"""
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    payment_type = Column(String(50), nullable=False)  # cash, credit_card, debit_card, bank_transfer, digital_wallet, etc.
    institution = Column(String(255))  # banco, financiera, etc.
    account_number = Column(String(100))  # último 4 dígitos o referencia
    color = Column(String(7))  # Hex color code
    icon = Column(String(50))  # Icon identifier
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    user = relationship("User", back_populates="payment_methods")
    expenses = relationship("Expense", back_populates="payment_method")