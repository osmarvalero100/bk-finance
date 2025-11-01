from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Investment(Base):
    """Modelo de Inversión"""
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    symbol = Column(String(20))  # Para acciones, cripto, etc.
    investment_type = Column(String(50), nullable=False)  # stocks, crypto, bonds, real_estate, etc.
    amount_invested = Column(Float, nullable=False)
    current_value = Column(Float)
    purchase_date = Column(DateTime(timezone=True), nullable=False)
    quantity = Column(Float)  # Para acciones, cripto, etc.
    purchase_price = Column(Float)
    current_price = Column(Float)
    broker_platform = Column(String(100))
    fees = Column(Float, default=0)
    taxes = Column(Float, default=0)
    dividends_earned = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    maturity_date = Column(DateTime(timezone=True))  # Para bonos, CDs, etc.
    risk_level = Column(String(20))  # low, medium, high
    sector = Column(String(100))  # tecnología, salud, finanzas, etc.
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relación con usuario
    user = relationship("User", back_populates="investments")