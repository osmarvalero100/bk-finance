from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class BudgetItemBase(BaseModel):
    """Esquema base de ítem de presupuesto"""
    category_id: int
    budgeted_amount: Decimal = Field(..., gt=0)
    notes: Optional[str] = None

class BudgetItemCreate(BudgetItemBase):
    """Esquema para crear ítem de presupuesto"""
    pass

class BudgetItemUpdate(BaseModel):
    """Esquema para actualizar ítem de presupuesto"""
    budgeted_amount: Optional[Decimal] = Field(None, gt=0)
    notes: Optional[str] = None

class BudgetItemInDBBase(BudgetItemBase):
    """Esquema base de ítem de presupuesto en BD"""
    id: int
    budget_id: int
    spent_amount: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class BudgetItem(BudgetItemInDBBase):
    """Esquema de ítem de presupuesto completo"""
    pass

class BudgetItemResponse(BudgetItem):
    """Esquema de respuesta de ítem de presupuesto"""
    category: Optional[dict] = None  # Información básica de la categoría

    model_config = {"from_attributes": True}

    def __init__(self, **data):
        # Extract the ORM object if present
        obj = data.pop('_obj', None)
        super().__init__(**data)

        # Handle category serialization
        if obj and hasattr(obj, 'category') and obj.category:
            self.category = {
                'id': obj.category.id,
                'name': obj.category.name,
                'description': obj.category.description,
                'color': obj.category.color,
                'icon': obj.category.icon,
                'category_type': obj.category.category_type
            }
        else:
            self.category = None

class BudgetBase(BaseModel):
    """Esquema base de presupuesto"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    start_date: date
    end_date: date
    currency: str = Field("COP", min_length=3, max_length=3)
    is_active: bool = True

class BudgetCreate(BudgetBase):
    """Esquema para crear presupuesto"""
    budget_items: List[BudgetItemCreate] = []

class BudgetUpdate(BaseModel):
    """Esquema para actualizar presupuesto"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    is_active: Optional[bool] = None

class BudgetInDBBase(BudgetBase):
    """Esquema base de presupuesto en BD"""
    id: int
    user_id: int
    total_budgeted: Decimal
    total_spent: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class Budget(BudgetInDBBase):
    """Esquema de presupuesto completo"""
    pass

class BudgetResponse(Budget):
    """Esquema de respuesta de presupuesto"""
    budget_items: List[BudgetItemResponse] = []

class BudgetComparison(BaseModel):
    """Esquema para comparación de presupuesto vs gastos reales"""
    budget_id: int
    budget_name: str
    category_id: int
    category_name: str
    budgeted_amount: Decimal
    spent_amount: Decimal
    remaining_amount: Decimal
    percentage_used: Decimal
    status: str  # 'under_budget', 'on_budget', 'over_budget'

class BudgetSummary(BaseModel):
    """Esquema para resumen de presupuesto"""
    total_budgeted: Decimal
    total_spent: Decimal
    total_remaining: Decimal
    percentage_used: Decimal
    categories_under_budget: int
    categories_on_budget: int
    categories_over_budget: int
    comparisons: List[BudgetComparison]