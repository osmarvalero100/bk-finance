from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.core.database import get_db
from app.models.user import User
from app.models.income import Income
from app.schemas.income import IncomeCreate, IncomeUpdate, IncomeResponse
from app.utils.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=IncomeResponse, status_code=status.HTTP_201_CREATED)
async def create_income(
    income_data: IncomeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Crear nuevo ingreso"""
    try:
        db_income = Income(**income_data.dict(), user_id=current_user.id)
        db.add(db_income)
        db.commit()
        db.refresh(db_income)
        return IncomeResponse.from_orm(db_income)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear el ingreso: {str(e)}"
        )

@router.get("/", response_model=List[IncomeResponse])
async def get_incomes(
    skip: int = 0,
    limit: int = 100,
    source: str = None,
    category: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de ingresos del usuario"""
    try:
        query = db.query(Income).filter(Income.user_id == current_user.id)

        if source:
            query = query.filter(Income.source == source)

        if category:
            query = query.filter(Income.category == category)

        incomes = query.order_by(desc(Income.date)).offset(skip).limit(limit).all()
        return [IncomeResponse.from_orm(income) for income in incomes]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener los ingresos: {str(e)}"
        )

@router.get("/{income_id}", response_model=IncomeResponse)
async def get_income(
    income_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener ingreso por ID"""
    try:
        income = db.query(Income).filter(
            and_(Income.id == income_id, Income.user_id == current_user.id)
        ).first()

        if not income:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingreso no encontrado"
            )

        return IncomeResponse.from_orm(income)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener el ingreso: {str(e)}"
        )

@router.put("/{income_id}", response_model=IncomeResponse)
async def update_income(
    income_id: int,
    income_data: IncomeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar ingreso"""
    try:
        income = db.query(Income).filter(
            and_(Income.id == income_id, Income.user_id == current_user.id)
        ).first()

        if not income:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingreso no encontrado"
            )

        # Actualizar campos
        for field, value in income_data.dict(exclude_unset=True).items():
            setattr(income, field, value)

        db.commit()
        db.refresh(income)
        return IncomeResponse.from_orm(income)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar el ingreso: {str(e)}"
        )

@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_income(
    income_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar ingreso"""
    try:
        income = db.query(Income).filter(
            and_(Income.id == income_id, Income.user_id == current_user.id)
        ).first()

        if not income:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingreso no encontrado"
            )

        db.delete(income)
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar el ingreso: {str(e)}"
        )

@router.get("/summary/source")
async def get_incomes_summary_by_source(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener resumen de ingresos por fuente"""
    try:
        from sqlalchemy import func

        summary = db.query(
            Income.source,
            func.sum(Income.amount).label('total_amount'),
            func.count(Income.id).label('count')
        ).filter(
            Income.user_id == current_user.id
        ).group_by(
            Income.source
        ).all()

        return [
            {
                "source": item.source,
                "total_amount": float(item.total_amount),
                "count": item.count
            } for item in summary
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener el resumen: {str(e)}"
        )