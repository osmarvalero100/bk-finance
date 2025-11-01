from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Income(Base):
    """Modelo de Ingreso"""
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=False)
    source = Column(String(100), nullable=False)  # salario, freelance, inversiones, etc.
    date = Column(DateTime(timezone=True), nullable=False)
    is_recurring = Column(Boolean, default=False)
    recurring_frequency = Column(String(20))  # daily, weekly, monthly, yearly
    category = Column(String(100))  # primary, secondary, passive, etc.
    tags = Column(Text)  # JSON string para etiquetas
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relación con usuario
    user = relationship("User", back_populates="incomes")