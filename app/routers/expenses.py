from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc

from app.core.database import get_db
from app.models.user import User
from app.models.expense import Expense
from app.models.category import Category
from app.models.payment_method import PaymentMethod
from app.models.tag import Tag
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
        # Verificar que la categoría existe y pertenece al usuario
        category = db.query(Category).filter(
            and_(Category.id == expense_data.category_id, Category.user_id == current_user.id)
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )

        if category.category_type != "expense":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La categoría seleccionada no es válida para gastos"
            )

        # Verificar método de pago si se especifica
        if expense_data.payment_method_id:
            payment_method = db.query(PaymentMethod).filter(
                and_(PaymentMethod.id == expense_data.payment_method_id, PaymentMethod.user_id == current_user.id)
            ).first()

            if not payment_method:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Método de pago no encontrado"
                )

        # Verificar etiquetas si se especifican
        if expense_data.tag_ids:
            tags = db.query(Tag).filter(
                and_(Tag.id.in_(expense_data.tag_ids), Tag.user_id == current_user.id, Tag.is_active == True)
            ).all()

            if len(tags) != len(expense_data.tag_ids):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Una o más etiquetas no encontradas"
                )

        db_expense = Expense(**expense_data.dict(exclude={'tag_ids'}), user_id=current_user.id)
        db.add(db_expense)

        # Agregar etiquetas si se especifican
        if expense_data.tag_ids:
            tags = db.query(Tag).filter(
                and_(Tag.id.in_(expense_data.tag_ids), Tag.user_id == current_user.id, Tag.is_active == True)
            ).all()
            db_expense.tags.extend(tags)

        db.commit()
        db.refresh(db_expense)
        return ExpenseResponse.model_validate(db_expense)
    except HTTPException:
        raise
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
    category_id: int = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de gastos del usuario"""
    try:
        query = db.query(Expense).options(joinedload(Expense.category), joinedload(Expense.payment_method), joinedload(Expense.tags)).filter(Expense.user_id == current_user.id)

        if category_id:
            query = query.filter(Expense.category_id == category_id)

        expenses = query.order_by(desc(Expense.date)).offset(skip).limit(limit).all()
        return [ExpenseResponse.model_validate(expense) for expense in expenses]
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
        expense = db.query(Expense).options(joinedload(Expense.category), joinedload(Expense.payment_method), joinedload(Expense.tags)).filter(
            and_(Expense.id == expense_id, Expense.user_id == current_user.id)
        ).first()

        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gasto no encontrado"
            )

        return ExpenseResponse.model_validate(expense)
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

        # Verificar categoría si se está actualizando
        if expense_data.category_id is not None:
            category = db.query(Category).filter(
                and_(Category.id == expense_data.category_id, Category.user_id == current_user.id)
            ).first()

            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoría no encontrada"
                )

            if category.category_type != "expense":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La categoría seleccionada no es válida para gastos"
                )

        # Verificar método de pago si se está actualizando
        if expense_data.payment_method_id is not None:
            if expense_data.payment_method_id:
                payment_method = db.query(PaymentMethod).filter(
                    and_(PaymentMethod.id == expense_data.payment_method_id, PaymentMethod.user_id == current_user.id)
                ).first()

                if not payment_method:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Método de pago no encontrado"
                    )

        # Verificar etiquetas si se están actualizando
        if expense_data.tag_ids is not None:
            if expense_data.tag_ids:
                tags = db.query(Tag).filter(
                    and_(Tag.id.in_(expense_data.tag_ids), Tag.user_id == current_user.id, Tag.is_active == True)
                ).all()

                if len(tags) != len(expense_data.tag_ids):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Una o más etiquetas no encontradas"
                    )

        # Actualizar campos
        update_data = expense_data.dict(exclude_unset=True)

        # Manejar etiquetas por separado
        if 'tag_ids' in update_data:
            tag_ids = update_data.pop('tag_ids')
            if tag_ids is not None:
                tags = db.query(Tag).filter(
                    and_(Tag.id.in_(tag_ids), Tag.user_id == current_user.id, Tag.is_active == True)
                ).all()
                expense.tags = tags

        # Actualizar otros campos
        for field, value in update_data.items():
            setattr(expense, field, value)

        db.commit()
        db.refresh(expense)
        return ExpenseResponse.model_validate(expense)
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
            Category.name.label('category_name'),
            Category.id.label('category_id'),
            Category.color,
            Category.icon,
            func.sum(Expense.amount).label('total_amount'),
            func.count(Expense.id).label('count')
        ).join(
            Expense, Category.id == Expense.category_id
        ).filter(
            Category.user_id == current_user.id
        ).group_by(
            Category.id, Category.name, Category.color, Category.icon
        ).all()

        return [
            {
                "category_id": item.category_id,
                "category_name": item.category_name,
                "color": item.color,
                "icon": item.icon,
                "total_amount": float(item.total_amount),
                "count": item.count
            } for item in summary
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener el resumen: {str(e)}"
        )