from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.core.database import get_db
from app.models.user import User
from app.models.payment_method import PaymentMethod
from app.schemas.payment_method import PaymentMethodCreate, PaymentMethodUpdate, PaymentMethodResponse
from app.utils.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_method(
    payment_method_data: PaymentMethodCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Crear nuevo método de pago"""
    try:
        db_payment_method = PaymentMethod(**payment_method_data.dict(), user_id=current_user.id)
        db.add(db_payment_method)
        db.commit()
        db.refresh(db_payment_method)
        return PaymentMethodResponse.from_orm(db_payment_method)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear el método de pago: {str(e)}"
        )

@router.get("/", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    payment_type: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de métodos de pago del usuario"""
    try:
        query = db.query(PaymentMethod).filter(
            and_(PaymentMethod.user_id == current_user.id, PaymentMethod.is_active == True)
        )

        if payment_type:
            query = query.filter(PaymentMethod.payment_type == payment_type)

        payment_methods = query.order_by(PaymentMethod.name).all()
        return [PaymentMethodResponse.from_orm(pm) for pm in payment_methods]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener los métodos de pago: {str(e)}"
        )

@router.get("/{payment_method_id}", response_model=PaymentMethodResponse)
async def get_payment_method(
    payment_method_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener método de pago por ID"""
    try:
        payment_method = db.query(PaymentMethod).filter(
            and_(PaymentMethod.id == payment_method_id, PaymentMethod.user_id == current_user.id)
        ).first()

        if not payment_method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Método de pago no encontrado"
            )

        return PaymentMethodResponse.from_orm(payment_method)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener el método de pago: {str(e)}"
        )

@router.put("/{payment_method_id}", response_model=PaymentMethodResponse)
async def update_payment_method(
    payment_method_id: int,
    payment_method_data: PaymentMethodUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar método de pago"""
    try:
        payment_method = db.query(PaymentMethod).filter(
            and_(PaymentMethod.id == payment_method_id, PaymentMethod.user_id == current_user.id)
        ).first()

        if not payment_method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Método de pago no encontrado"
            )

        # Actualizar campos
        for field, value in payment_method_data.dict(exclude_unset=True).items():
            setattr(payment_method, field, value)

        db.commit()
        db.refresh(payment_method)
        return PaymentMethodResponse.from_orm(payment_method)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar el método de pago: {str(e)}"
        )

@router.delete("/{payment_method_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment_method(
    payment_method_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar método de pago"""
    try:
        payment_method = db.query(PaymentMethod).filter(
            and_(PaymentMethod.id == payment_method_id, PaymentMethod.user_id == current_user.id)
        ).first()

        if not payment_method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Método de pago no encontrado"
            )

        # Verificar si está siendo usado en gastos
        from app.models.expense import Expense
        expenses_count = db.query(Expense).filter(Expense.payment_method_id == payment_method_id).count()

        if expenses_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar un método de pago que está siendo utilizado en gastos"
            )

        # Soft delete - marcar como inactivo en lugar de eliminar
        payment_method.is_active = False
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar el método de pago: {str(e)}"
        )