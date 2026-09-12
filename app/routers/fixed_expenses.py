from datetime import datetime, date, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.models.user import User
from app.models.fixed_expense import FixedExpense
from app.models.expense import Expense
from app.models.category import Category
from app.models.payment_method import PaymentMethod
from app.schemas.fixed_expense import (
    FixedExpenseCreate,
    FixedExpenseUpdate,
    FixedExpenseResponse,
    FixedExpenseSummary,
    ReminderCheckResult
)
from app.schemas.expense import ExpenseResponse
from app.utils.auth import get_current_active_user
from app.services.email_service import (
    calculate_next_due_date_and_days,
    send_fixed_expense_reminder,
    check_and_send_due_reminders
)

router = APIRouter()


def populate_calculated_fields(fe: FixedExpense) -> FixedExpenseResponse:
    """Calcula la próxima fecha de vencimiento y días restantes para la respuesta."""
    today = date.today()
    next_due_date, days_until_due = calculate_next_due_date_and_days(fe.due_day, today)
    is_due_soon = 0 <= days_until_due <= fe.reminder_days_before

    resp = FixedExpenseResponse.model_validate(fe)
    resp.next_due_date = next_due_date
    resp.days_until_due = days_until_due
    resp.is_due_soon = is_due_soon
    return resp


@router.get("/summary", response_model=FixedExpenseSummary)
async def get_fixed_expenses_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener resumen general de gastos fijos para el usuario autenticado"""
    try:
        items = (
            db.query(FixedExpense)
            .filter(FixedExpense.user_id == current_user.id)
            .all()
        )

        today = date.today()
        total_count = len(items)
        active_count = 0
        total_monthly = 0.0
        due_soon_count = 0
        reminders_enabled_count = 0

        for item in items:
            if item.is_active:
                active_count += 1
                total_monthly += item.amount
                if item.email_reminder_enabled:
                    reminders_enabled_count += 1

                _, days = calculate_next_due_date_and_days(item.due_day, today)
                if 0 <= days <= item.reminder_days_before:
                    due_soon_count += 1

        return FixedExpenseSummary(
            total_monthly_amount=round(total_monthly, 2),
            total_count=total_count,
            active_count=active_count,
            due_soon_count=due_soon_count,
            reminders_enabled_count=reminders_enabled_count
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener resumen de gastos fijos: {str(e)}"
        )


@router.get("/", response_model=List[FixedExpenseResponse])
async def get_fixed_expenses(
    is_active: Optional[bool] = None,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Listar todos los gastos fijos del usuario con filtros opcionales"""
    try:
        query = (
            db.query(FixedExpense)
            .options(
                joinedload(FixedExpense.category),
                joinedload(FixedExpense.payment_method)
            )
            .filter(FixedExpense.user_id == current_user.id)
        )

        if is_active is not None:
            query = query.filter(FixedExpense.is_active == is_active)

        if category_id is not None:
            query = query.filter(FixedExpense.category_id == category_id)

        if search:
            query = query.filter(
                or_(
                    FixedExpense.name.ilike(f"%{search}%"),
                    FixedExpense.notes.ilike(f"%{search}%")
                )
            )

        items = query.order_by(FixedExpense.due_day.asc()).all()
        return [populate_calculated_fields(item) for item in items]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al listar gastos fijos: {str(e)}"
        )


@router.post("/", response_model=FixedExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_fixed_expense(
    data: FixedExpenseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Registrar un nuevo gasto fijo"""
    try:
        # Validar categoría
        category = db.query(Category).filter(
            and_(Category.id == data.category_id, Category.user_id == current_user.id)
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )

        if category.category_type != "expense":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La categoría debe ser de tipo 'expense'"
            )

        # Validar método de pago si se proporciona
        if data.payment_method_id:
            pm = db.query(PaymentMethod).filter(
                and_(PaymentMethod.id == data.payment_method_id, PaymentMethod.user_id == current_user.id)
            ).first()
            if not pm:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Método de pago no encontrado"
                )

        new_fe = FixedExpense(
            **data.model_dump(),
            user_id=current_user.id
        )
        db.add(new_fe)
        db.commit()
        db.refresh(new_fe)
        db.refresh(new_fe, ['category', 'payment_method'])

        return populate_calculated_fields(new_fe)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear gasto fijo: {str(e)}"
        )


@router.get("/{id}", response_model=FixedExpenseResponse)
async def get_fixed_expense(
    id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener detalle de un gasto fijo específico"""
    fe = (
        db.query(FixedExpense)
        .options(
            joinedload(FixedExpense.category),
            joinedload(FixedExpense.payment_method)
        )
        .filter(and_(FixedExpense.id == id, FixedExpense.user_id == current_user.id))
        .first()
    )

    if not fe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gasto fijo no encontrado"
        )

    return populate_calculated_fields(fe)


@router.put("/{id}", response_model=FixedExpenseResponse)
async def update_fixed_expense(
    id: int,
    data: FixedExpenseUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar un gasto fijo existente"""
    try:
        fe = (
            db.query(FixedExpense)
            .filter(and_(FixedExpense.id == id, FixedExpense.user_id == current_user.id))
            .first()
        )

        if not fe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gasto fijo no encontrado"
            )

        update_dict = data.model_dump(exclude_unset=True)

        # Si se actualiza la categoría
        if "category_id" in update_dict and update_dict["category_id"] is not None:
            category = db.query(Category).filter(
                and_(Category.id == update_dict["category_id"], Category.user_id == current_user.id)
            ).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoría no encontrada"
                )
            if category.category_type != "expense":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La categoría debe ser de tipo 'expense'"
                )

        # Si se actualiza el método de pago
        if "payment_method_id" in update_dict and update_dict["payment_method_id"] is not None:
            pm = db.query(PaymentMethod).filter(
                and_(PaymentMethod.id == update_dict["payment_method_id"], PaymentMethod.user_id == current_user.id)
            ).first()
            if not pm:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Método de pago no encontrado"
                )

        for key, value in update_dict.items():
            setattr(fe, key, value)

        db.commit()
        db.refresh(fe)
        db.refresh(fe, ['category', 'payment_method'])
        return populate_calculated_fields(fe)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar gasto fijo: {str(e)}"
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fixed_expense(
    id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar un gasto fijo"""
    try:
        fe = (
            db.query(FixedExpense)
            .filter(and_(FixedExpense.id == id, FixedExpense.user_id == current_user.id))
            .first()
        )

        if not fe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gasto fijo no encontrado"
            )

        db.delete(fe)
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar gasto fijo: {str(e)}"
        )


@router.post("/{id}/pay", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def pay_fixed_expense(
    id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Registra el pago de un gasto fijo creando automáticamente una entrada
    en la tabla de gastos (Expense) del usuario.
    """
    try:
        fe = (
            db.query(FixedExpense)
            .filter(and_(FixedExpense.id == id, FixedExpense.user_id == current_user.id))
            .first()
        )

        if not fe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gasto fijo no encontrado"
            )

        now = datetime.now(timezone.utc)
        expense = Expense(
            user_id=current_user.id,
            category_id=fe.category_id,
            payment_method_id=fe.payment_method_id,
            amount=fe.amount,
            description=f"Pago: {fe.name}",
            date=now,
            is_recurring=True,
            recurring_frequency=fe.frequency,
            notes=f"Registrado automáticamente desde gasto fijo (Día {fe.due_day})"
        )

        db.add(expense)
        db.commit()
        db.refresh(expense)
        db.refresh(expense, ['category', 'payment_method', 'tags'])

        return ExpenseResponse.model_validate(expense)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al registrar el pago del gasto fijo: {str(e)}"
        )


@router.post("/{id}/send-test-reminder")
async def send_test_reminder(
    id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Envía un correo de prueba de recordatorio inmediatamente al email del usuario.
    """
    fe = (
        db.query(FixedExpense)
        .options(
            joinedload(FixedExpense.category),
            joinedload(FixedExpense.payment_method)
        )
        .filter(and_(FixedExpense.id == id, FixedExpense.user_id == current_user.id))
        .first()
    )

    if not fe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gasto fijo no encontrado"
        )

    today = date.today()
    next_due_date, days_until_due = calculate_next_due_date_and_days(fe.due_day, today)

    success = send_fixed_expense_reminder(
        user=current_user,
        fixed_expense=fe,
        days_left=days_until_due,
        due_date=next_due_date,
        is_test=True
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo enviar el correo de prueba. Revisa la configuración de SMTP."
        )

    return {
        "success": True,
        "message": f"Correo de recordatorio enviado exitosamente a {current_user.email}",
        "recipient": current_user.email,
        "days_left": days_until_due,
        "due_date": next_due_date.isoformat()
    }


@router.post("/check-reminders", response_model=ReminderCheckResult)
async def check_pending_reminders(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Ejecuta la revisión de gastos fijos próximos a vencer y envía
    los correos de recordatorio correspondientes que no se hayan enviado aún.
    """
    try:
        result = check_and_send_due_reminders(db, user_id=current_user.id)
        return ReminderCheckResult(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al verificar recordatorios: {str(e)}"
        )
