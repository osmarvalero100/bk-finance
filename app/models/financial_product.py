from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class FinancialProduct(Base):
    """Modelo de Producto Financiero"""
    __tablename__ = "financial_products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    product_type = Column(String(50), nullable=False)  # savings_account, checking_account, credit_card, loan, mortgage, etc.
    institution = Column(String(255), nullable=False)  # banco, financiera, etc.
    account_number = Column(String(100))
    balance = Column(Float, default=0)
    interest_rate = Column(Float)
    minimum_balance = Column(Float, default=0)
    monthly_fee = Column(Float, default=0)
    credit_limit = Column(Float)  # Para tarjetas de crédito
    available_credit = Column(Float)  # Para tarjetas de crédito
    payment_due_date = Column(Integer)  # día del mes para pago
    minimum_payment = Column(Float)
    is_active = Column(Boolean, default=True)
    opening_date = Column(DateTime(timezone=True))
    maturity_date = Column(DateTime(timezone=True))  # Para CDs, bonos, etc.
    currency = Column(String(3), default="COP")
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relación con usuario
    user = relationship("User", back_populates="financial_products")