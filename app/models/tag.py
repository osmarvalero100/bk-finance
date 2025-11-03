from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Tag(Base):
    """Modelo de Etiqueta"""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    color = Column(String(7))  # Hex color code
    icon = Column(String(50))  # Icon identifier
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones many-to-many
    expenses = relationship("Expense", secondary="expense_tags", back_populates="tags")
    incomes = relationship("Income", secondary="income_tags", back_populates="tags")

    # Relación con usuario
    user = relationship("User", back_populates="tags")

# Tablas de asociación many-to-many
class ExpenseTag(Base):
    """Tabla de asociación entre gastos y etiquetas"""
    __tablename__ = "expense_tags"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class IncomeTag(Base):
    """Tabla de asociación entre ingresos y etiquetas"""
    __tablename__ = "income_tags"

    id = Column(Integer, primary_key=True, index=True)
    income_id = Column(Integer, ForeignKey("incomes.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())