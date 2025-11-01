from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.core.database import get_db
from app.models.user import User
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.utils.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Crear nuevo gasto"""
    try:
        db_expense = Expense(**expense_data.dict(), user_id=current_user.id)
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
        return ExpenseResponse.from_orm(db_expense)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear el gasto: {str(e)}"
        )

@router.get("/", response_model=List[ExpenseResponse])
async def get_expenses(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de gastos del usuario"""
    try:
        query = db.query(Expense).filter(Expense.user_id == current_user.id)

        if category:
            query = query.filter(Expense.category == category)

        expenses = query.order_by(desc(Expense.date)).offset(skip).limit(limit).all()
        return [ExpenseResponse.from_orm(expense) for expense in expenses]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener los gastos: {str(e)}"
        )

@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener gasto por ID"""
    try:
        expense = db.query(Expense).filter(
            and_(Expense.id == expense_id, Expense.user_id == current_user.id)
        ).first()

        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gasto no encontrado"
            )

        return ExpenseResponse.from_orm(expense)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener el gasto: {str(e)}"
        )

@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar gasto"""
    try:
        expense = db.query(Expense).filter(
            and_(Expense.id == expense_id, Expense.user_id == current_user.id)
        ).first()

        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gasto no encontrado"
            )

        # Actualizar campos
        for field, value in expense_data.dict(exclude_unset=True).items():
            setattr(expense, field, value)

        db.commit()
        db.refresh(expense)
        return ExpenseResponse.from_orm(expense)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar el gasto: {str(e)}"
        )

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar gasto"""
    try:
        expense = db.query(Expense).filter(
            and_(Expense.id == expense_id, Expense.user_id == current_user.id)
        ).first()

        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gasto no encontrado"
            )

        db.delete(expense)
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar el gasto: {str(e)}"
        )

@router.get("/summary/category")
async def get_expenses_summary_by_category(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener resumen de gastos por categoría"""
    try:
        from sqlalchemy import func

        summary = db.query(
            Expense.category,
            func.sum(Expense.amount).label('total_amount'),
            func.count(Expense.id).label('count')
        ).filter(
            Expense.user_id == current_user.id
        ).group_by(
            Expense.category
        ).all()

        return [
            {
                "category": item.category,
                "total_amount": float(item.total_amount),
                "count": item.count
            } for item in summary
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener el resumen: {str(e)}"
        )