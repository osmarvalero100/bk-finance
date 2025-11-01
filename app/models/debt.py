from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Debt(Base):
    """Modelo de Deuda"""
    __tablename__ = "debts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    debt_type = Column(String(50), nullable=False)  # credit_card, personal_loan, mortgage, student_loan, etc.
    lender = Column(String(255), nullable=False)  # banco, financiera, persona, etc.
    original_amount = Column(Float, nullable=False)
    current_balance = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)
    minimum_payment = Column(Float, nullable=False)
    payment_due_date = Column(Integer)  # día del mes para pago
    loan_start_date = Column(DateTime(timezone=True), nullable=False)
    expected_end_date = Column(DateTime(timezone=True))
    is_paid_off = Column(Boolean, default=False)
    paid_off_date = Column(DateTime(timezone=True))
    currency = Column(String(3), default="COP")
    collateral = Column(String(255))  # garantía si aplica
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relación con usuario
    user = relationship("User", back_populates="debts")