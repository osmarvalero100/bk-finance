from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Category(Base):
    """Modelo de Categoría"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    color = Column(String(7))  # Hex color code, e.g., #FF5733
    icon = Column(String(50))  # Icon identifier
    is_default = Column(Boolean, default=False)  # System default categories
    category_type = Column(String(20), nullable=False)  # 'expense' or 'income'
    parent_id = Column(Integer, ForeignKey("categories.id"))  # For subcategories
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    user = relationship("User", back_populates="categories")
    parent = relationship("Category", remote_side=[id], back_populates="subcategories")
    subcategories = relationship("Category", back_populates="parent")

    # Relaciones con transacciones
    expenses = relationship("Expense", back_populates="category")
    incomes = relationship("Income", back_populates="category")