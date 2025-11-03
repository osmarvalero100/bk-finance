from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.core.database import get_db
from app.models.user import User
from app.models.debt import Debt
from app.schemas.debt import DebtCreate, DebtUpdate, DebtResponse
from app.utils.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=DebtResponse, status_code=status.HTTP_201_CREATED)
async def create_debt(
    debt_data: DebtCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Crear nueva deuda"""
    try:
        db_debt = Debt(**debt_data.dict(), user_id=current_user.id)
        db.add(db_debt)
        db.commit()
        db.refresh(db_debt)
        return DebtResponse.from_orm(db_debt)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear la deuda: {str(e)}"
        )

@router.get("/", response_model=List[DebtResponse])
async def get_debts(
    skip: int = 0,
    limit: int = 100,
    debt_type: str = None,
    lender: str = None,
    is_paid_off: bool = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de deudas del usuario"""
    try:
        query = db.query(Debt).filter(Debt.user_id == current_user.id)

        if debt_type:
            query = query.filter(Debt.debt_type == debt_type)

        if lender:
            query = query.filter(Debt.lender == lender)

        if is_paid_off is not None:
            query = query.filter(Debt.is_paid_off == is_paid_off)

        debts = query.order_by(desc(Debt.loan_start_date)).offset(skip).limit(limit).all()
        return [DebtResponse.from_orm(debt) for debt in debts]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener las deudas: {str(e)}"
        )

@router.get("/{debt_id}", response_model=DebtResponse)
async def get_debt(
    debt_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener deuda por ID"""
    try:
        debt = db.query(Debt).filter(
            and_(Debt.id == debt_id, Debt.user_id == current_user.id)
        ).first()

        if not debt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deuda no encontrada"
            )

        return DebtResponse.from_orm(debt)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener la deuda: {str(e)}"
        )

@router.put("/{debt_id}", response_model=DebtResponse)
async def update_debt(
    debt_id: int,
    debt_data: DebtUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar deuda"""
    try:
        debt = db.query(Debt).filter(
            and_(Debt.id == debt_id, Debt.user_id == current_user.id)
        ).first()

        if not debt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deuda no encontrada"
            )

        # Actualizar campos
        for field, value in debt_data.dict(exclude_unset=True).items():
            setattr(debt, field, value)

        db.commit()
        db.refresh(debt)
        return DebtResponse.from_orm(debt)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar la deuda: {str(e)}"
        )

@router.delete("/{debt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_debt(
    debt_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar deuda"""
    try:
        debt = db.query(Debt).filter(
            and_(Debt.id == debt_id, Debt.user_id == current_user.id)
        ).first()

        if not debt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deuda no encontrada"
            )

        db.delete(debt)
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar la deuda: {str(e)}"
        )

@router.get("/summary/type")
async def get_debts_summary_by_type(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener resumen de deudas por tipo"""
    try:
        from sqlalchemy import func

        summary = db.query(
            Debt.debt_type,
            func.sum(Debt.current_balance).label('total_balance'),
            func.count(Debt.id).label('count')
        ).filter(
            and_(Debt.user_id == current_user.id, Debt.is_paid_off == False)
        ).group_by(
            Debt.debt_type
        ).all()

        return [
            {
                "debt_type": item.debt_type,
                "total_balance": float(item.total_balance) if item.total_balance else 0,
                "count": item.count
            } for item in summary
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener el resumen: {str(e)}"
        )

@router.get("/balance/total")
async def get_total_debt_balance(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener balance total de deudas"""
    try:
        from sqlalchemy import func

        result = db.query(
            func.sum(Debt.current_balance).label('total_debt')
        ).filter(
            and_(Debt.user_id == current_user.id, Debt.is_paid_off == False)
        ).first()

        total_debt = float(result.total_debt) if result.total_debt else 0

        return {
            "total_debt": total_debt,
            "currency": "COP"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener el balance total de deudas: {str(e)}"
        )

@router.put("/{debt_id}/pay-off")
async def mark_debt_as_paid_off(
    debt_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Marcar deuda como pagada"""
    try:
        debt = db.query(Debt).filter(
            and_(Debt.id == debt_id, Debt.user_id == current_user.id)
        ).first()

        if not debt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deuda no encontrada"
            )

        if debt.is_paid_off:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La deuda ya está marcada como pagada"
            )

        from datetime import datetime, UTC
        debt.is_paid_off = True
        debt.paid_off_date = datetime.now(UTC)
        debt.current_balance = 0

        db.commit()
        db.refresh(debt)

        return {
            "message": "Deuda marcada como pagada exitosamente",
            "debt": DebtResponse.from_orm(debt)
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al marcar la deuda como pagada: {str(e)}"
        )