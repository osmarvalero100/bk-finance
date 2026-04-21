from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.models.expense import Expense
from app.models.income import Income
from app.models.budget import Budget
from app.models.category import Category
from app.schemas.dashboard import DashboardSummary, DashboardTransaction
from app.utils.auth import get_current_active_user

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """
    Obtener resumen del dashboard para el usuario actual.
    Incluye gastos totales, ingresos totales, balance, presupuestos activos
    y las últimas 10 transacciones.
    """
    try:
        # 1. Calcular gastos totales
        total_expenses = (
            db.query(func.sum(Expense.amount))
            .filter(Expense.user_id == current_user.id)
            .scalar()
            or 0.0
        )

        # 2. Calcular ingresos totales
        total_incomes = (
            db.query(func.sum(Income.amount))
            .filter(Income.user_id == current_user.id)
            .scalar()
            or 0.0
        )

        # 3. Calcular balance
        balance = total_incomes - total_expenses

        # 4. Contar presupuestos activos
        active_budgets_count = (
            db.query(func.count(Budget.id))
            .filter(Budget.user_id == current_user.id, Budget.is_active == True)
            .scalar()
            or 0
        )

        # 5. Obtener las últimas 10 transacciones (mezcladas)
        # Obtenemos los últimos 10 gastos
        recent_expenses = (
            db.query(Expense)
            .options(joinedload(Expense.category))
            .filter(Expense.user_id == current_user.id)
            .order_by(desc(Expense.date))
            .limit(10)
            .all()
        )

        # Obtenemos los últimos 10 ingresos
        recent_incomes = (
            db.query(Income)
            .filter(Income.user_id == current_user.id)
            .order_by(desc(Income.date))
            .limit(10)
            .all()
        )

        # Unificamos y ordenamos
        transactions = []
        for e in recent_expenses:
            transactions.append(
                DashboardTransaction(
                    id=e.id,
                    amount=float(e.amount),
                    description=e.description,
                    date=e.date,
                    type="expense",
                    category_name=e.category.name if e.category else None,
                )
            )

        for i in recent_incomes:
            transactions.append(
                DashboardTransaction(
                    id=i.id,
                    amount=float(i.amount),
                    description=i.description,
                    date=i.date,
                    type="income",
                    category_name=None,
                )
            )

        # Ordenar por fecha descendente y tomar las 10 mejores
        transactions.sort(key=lambda x: x.date, reverse=True)
        recent_transactions = transactions[:10]

        return DashboardSummary(
            total_expenses=float(total_expenses),
            total_incomes=float(total_incomes),
            balance=float(balance),
            active_budgets_count=active_budgets_count,
            recent_transactions=recent_transactions,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al generar el resumen del dashboard: {str(e)}",
        )
