from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Numeric, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Budget(Base):
    """Modelo de Presupuesto"""
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_budgeted = Column(Numeric(10, 2), nullable=False, default=0.00)
    total_spent = Column(Numeric(10, 2), nullable=False, default=0.00)
    currency = Column(String(3), default="COP")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    user = relationship("User", back_populates="budgets")
    budget_items = relationship("BudgetItem", back_populates="budget", cascade="all, delete-orphan")

class BudgetItem(Base):
    """Modelo de Ítem de Presupuesto"""
    __tablename__ = "budget_items"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    budgeted_amount = Column(Numeric(10, 2), nullable=False)
    spent_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    budget = relationship("Budget", back_populates="budget_items")
    category = relationship("Category", back_populates="budget_items")