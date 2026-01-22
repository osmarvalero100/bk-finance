from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DashboardTransaction(BaseModel):
    """Esquema para una transacción unificada en el dashboard"""
    id: int
    amount: float
    description: str
    date: datetime
    type: str  # 'expense' o 'income'
    category_name: Optional[str] = None

class DashboardSummary(BaseModel):
    """Esquema de respuesta para el dashboard"""
    total_expenses: float
    total_incomes: float
    balance: float
    active_budgets_count: int
    recent_transactions: List[DashboardTransaction]
