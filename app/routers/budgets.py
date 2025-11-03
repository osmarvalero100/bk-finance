from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, between
from datetime import date

from app.core.database import get_db
from app.models.user import User
from app.models.budget import Budget, BudgetItem
from app.models.category import Category
from app.models.expense import Expense
from app.schemas.budget import (
    BudgetCreate, BudgetUpdate, BudgetResponse,
    BudgetItemCreate, BudgetItemUpdate, BudgetItemResponse,
    BudgetComparison, BudgetSummary
)
from app.utils.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Crear nuevo presupuesto"""
    try:
        # Validar fechas
        if budget_data.start_date >= budget_data.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de inicio debe ser anterior a la fecha de fin"
            )

        # Verificar que las categorías existen y pertenecen al usuario
        if budget_data.budget_items:
            category_ids = [item.category_id for item in budget_data.budget_items]
            categories = db.query(Category).filter(
                and_(Category.id.in_(category_ids), Category.user_id == current_user.id)
            ).all()

            if len(categories) != len(category_ids):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Una o más categorías no encontradas"
                )

            # Verificar que todas las categorías sean de tipo expense
            for category in categories:
                if category.category_type != "expense":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"La categoría '{category.name}' no es válida para presupuestos de gastos"
                    )

        # Crear presupuesto
        db_budget = Budget(
            name=budget_data.name,
            description=budget_data.description,
            start_date=budget_data.start_date,
            end_date=budget_data.end_date,
            currency=budget_data.currency,
            is_active=budget_data.is_active,
            user_id=current_user.id,
            total_budgeted=0.00
        )
        db.add(db_budget)
        db.flush()  # Para obtener el ID del presupuesto

        # Crear ítems del presupuesto
        total_budgeted = 0.00
        for item_data in budget_data.budget_items:
            db_item = BudgetItem(
                category_id=item_data.category_id,
                budgeted_amount=item_data.budgeted_amount,
                notes=item_data.notes,
                budget_id=db_budget.id
            )
            db.add(db_item)
            total_budgeted += float(item_data.budgeted_amount)

        # Actualizar total del presupuesto
        db_budget.total_budgeted = total_budgeted

        db.commit()
        db.refresh(db_budget)

        # Reload budget with joined relationships for proper serialization
        budget_with_items = db.query(Budget).options(joinedload(Budget.budget_items).joinedload(BudgetItem.category)).filter(
            Budget.id == db_budget.id
        ).first()

        # Convert to dict and manually handle category serialization
        budget_dict = budget_with_items.__dict__.copy()
        budget_dict['budget_items'] = []

        for item in budget_with_items.budget_items:
            item_dict = item.__dict__.copy()
            if item.category:
                item_dict['category'] = {
                    'id': item.category.id,
                    'name': item.category.name,
                    'description': item.category.description,
                    'color': item.category.color,
                    'icon': item.category.icon,
                    'category_type': item.category.category_type
                }
            else:
                item_dict['category'] = None
            budget_dict['budget_items'].append(item_dict)

        return BudgetResponse(**budget_dict)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear el presupuesto: {str(e)}"
        )

@router.get("/", response_model=List[BudgetResponse])
async def get_budgets(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de presupuestos del usuario"""
    try:
        query = db.query(Budget).options(joinedload(Budget.budget_items).joinedload(BudgetItem.category)).filter(
            Budget.user_id == current_user.id
        )

        if is_active is not None:
            query = query.filter(Budget.is_active == is_active)

        budgets = query.order_by(Budget.created_at.desc()).offset(skip).limit(limit).all()

        # Manually serialize budgets with proper category handling
        result = []
        for budget in budgets:
            budget_dict = budget.__dict__.copy()
            budget_dict['budget_items'] = []

            for item in budget.budget_items:
                item_dict = item.__dict__.copy()
                if item.category:
                    item_dict['category'] = {
                        'id': item.category.id,
                        'name': item.category.name,
                        'description': item.category.description,
                        'color': item.category.color,
                        'icon': item.category.icon,
                        'category_type': item.category.category_type
                    }
                else:
                    item_dict['category'] = None
                budget_dict['budget_items'].append(item_dict)

            result.append(BudgetResponse(**budget_dict))

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener los presupuestos: {str(e)}"
        )

@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener presupuesto por ID"""
    try:
        budget = db.query(Budget).options(joinedload(Budget.budget_items).joinedload(BudgetItem.category)).filter(
            and_(Budget.id == budget_id, Budget.user_id == current_user.id)
        ).first()

        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Presupuesto no encontrado"
            )

        # Manually serialize budget with proper category handling
        budget_dict = budget.__dict__.copy()
        budget_dict['budget_items'] = []

        for item in budget.budget_items:
            item_dict = item.__dict__.copy()
            if item.category:
                item_dict['category'] = {
                    'id': item.category.id,
                    'name': item.category.name,
                    'description': item.category.description,
                    'color': item.category.color,
                    'icon': item.category.icon,
                    'category_type': item.category.category_type
                }
            else:
                item_dict['category'] = None
            budget_dict['budget_items'].append(item_dict)

        return BudgetResponse(**budget_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener el presupuesto: {str(e)}"
        )

@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar presupuesto"""
    try:
        budget = db.query(Budget).filter(
            and_(Budget.id == budget_id, Budget.user_id == current_user.id)
        ).first()

        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Presupuesto no encontrado"
            )

        # Validar fechas si se están actualizando
        if budget_data.start_date is not None and budget_data.end_date is not None:
            if budget_data.start_date >= budget_data.end_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La fecha de inicio debe ser anterior a la fecha de fin"
                )

        # Actualizar campos
        update_data = budget_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(budget, field, value)

        db.commit()
        db.refresh(budget)
        # Manually serialize budget with proper category handling
        budget_dict = budget.__dict__.copy()
        budget_dict['budget_items'] = []

        for item in budget.budget_items:
            item_dict = item.__dict__.copy()
            if item.category:
                item_dict['category'] = {
                    'id': item.category.id,
                    'name': item.category.name,
                    'description': item.category.description,
                    'color': item.category.color,
                    'icon': item.category.icon,
                    'category_type': item.category.category_type
                }
            else:
                item_dict['category'] = None
            budget_dict['budget_items'].append(item_dict)

        return BudgetResponse(**budget_dict)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar el presupuesto: {str(e)}"
        )

@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar presupuesto"""
    try:
        budget = db.query(Budget).filter(
            and_(Budget.id == budget_id, Budget.user_id == current_user.id)
        ).first()

        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Presupuesto no encontrado"
            )

        db.delete(budget)
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar el presupuesto: {str(e)}"
        )

@router.post("/{budget_id}/items/", response_model=BudgetItemResponse, status_code=status.HTTP_201_CREATED)
async def create_budget_item(
    budget_id: int,
    item_data: BudgetItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Crear ítem de presupuesto"""
    try:
        # Verificar que el presupuesto existe y pertenece al usuario
        budget = db.query(Budget).filter(
            and_(Budget.id == budget_id, Budget.user_id == current_user.id)
        ).first()

        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Presupuesto no encontrado"
            )

        # Verificar que la categoría existe y pertenece al usuario
        category = db.query(Category).filter(
            and_(Category.id == item_data.category_id, Category.user_id == current_user.id)
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )

        if category.category_type != "expense":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La categoría seleccionada no es válida para presupuestos de gastos"
            )

        # Verificar que no existe ya un ítem para esta categoría en el presupuesto
        existing_item = db.query(BudgetItem).filter(
            and_(BudgetItem.budget_id == budget_id, BudgetItem.category_id == item_data.category_id)
        ).first()

        if existing_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un ítem para esta categoría en el presupuesto"
            )

        # Crear ítem
        db_item = BudgetItem(
            category_id=item_data.category_id,
            budgeted_amount=item_data.budgeted_amount,
            notes=item_data.notes,
            budget_id=budget_id
        )
        db.add(db_item)

        # Actualizar total del presupuesto
        from decimal import Decimal
        budget.total_budgeted += Decimal(str(item_data.budgeted_amount))

        db.commit()
        db.refresh(db_item)

        # Reload item with category for proper serialization
        item_with_category = db.query(BudgetItem).options(joinedload(BudgetItem.category)).filter(
            BudgetItem.id == db_item.id
        ).first()

        # Convert to dict and manually handle category serialization
        item_dict = item_with_category.__dict__.copy()
        if item_with_category.category:
            item_dict['category'] = {
                'id': item_with_category.category.id,
                'name': item_with_category.category.name,
                'description': item_with_category.category.description,
                'color': item_with_category.category.color,
                'icon': item_with_category.category.icon,
                'category_type': item_with_category.category.category_type
            }
        else:
            item_dict['category'] = None

        return BudgetItemResponse(**item_dict)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear el ítem del presupuesto: {str(e)}"
        )

@router.put("/{budget_id}/items/{item_id}", response_model=BudgetItemResponse)
async def update_budget_item(
    budget_id: int,
    item_id: int,
    item_data: BudgetItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar ítem de presupuesto"""
    try:
        # Verificar que el presupuesto pertenece al usuario
        budget = db.query(Budget).filter(
            and_(Budget.id == budget_id, Budget.user_id == current_user.id)
        ).first()

        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Presupuesto no encontrado"
            )

        # Obtener el ítem
        item = db.query(BudgetItem).filter(
            and_(BudgetItem.id == item_id, BudgetItem.budget_id == budget_id)
        ).first()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ítem del presupuesto no encontrado"
            )

        # Calcular diferencia para actualizar total del presupuesto
        from decimal import Decimal
        old_amount = float(item.budgeted_amount)
        new_amount = float(item_data.budgeted_amount) if item_data.budgeted_amount is not None else old_amount

        # Actualizar campos
        if item_data.budgeted_amount is not None:
            item.budgeted_amount = item_data.budgeted_amount
        if item_data.notes is not None:
            item.notes = item_data.notes

        # Actualizar total del presupuesto
        budget.total_budgeted += Decimal(str(new_amount - old_amount))

        db.commit()
        db.refresh(item)

        # Reload item with category for proper serialization
        item_with_category = db.query(BudgetItem).options(joinedload(BudgetItem.category)).filter(
            BudgetItem.id == item.id
        ).first()

        # Convert to dict and manually handle category serialization
        item_dict = item_with_category.__dict__.copy()
        if item_with_category.category:
            item_dict['category'] = {
                'id': item_with_category.category.id,
                'name': item_with_category.category.name,
                'description': item_with_category.category.description,
                'color': item_with_category.category.color,
                'icon': item_with_category.category.icon,
                'category_type': item_with_category.category.category_type
            }
        else:
            item_dict['category'] = None

        return BudgetItemResponse(**item_dict)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar el ítem del presupuesto: {str(e)}"
        )

@router.delete("/{budget_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget_item(
    budget_id: int,
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar ítem de presupuesto"""
    try:
        # Verificar que el presupuesto pertenece al usuario
        budget = db.query(Budget).filter(
            and_(Budget.id == budget_id, Budget.user_id == current_user.id)
        ).first()

        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Presupuesto no encontrado"
            )

        # Obtener el ítem
        item = db.query(BudgetItem).filter(
            and_(BudgetItem.id == item_id, BudgetItem.budget_id == budget_id)
        ).first()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ítem del presupuesto no encontrado"
            )

        # Actualizar total del presupuesto
        from decimal import Decimal
        budget.total_budgeted -= Decimal(str(item.budgeted_amount))

        db.delete(item)
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar el ítem del presupuesto: {str(e)}"
        )

@router.get("/{budget_id}/comparison", response_model=BudgetSummary)
async def get_budget_comparison(
    budget_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener comparación del presupuesto vs gastos reales"""
    try:
        # Verificar que el presupuesto pertenece al usuario
        budget = db.query(Budget).filter(
            and_(Budget.id == budget_id, Budget.user_id == current_user.id)
        ).first()

        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Presupuesto no encontrado"
            )

        # Obtener gastos reales por categoría en el período del presupuesto
        spent_amounts = db.query(
            Expense.category_id,
            func.sum(Expense.amount).label('spent')
        ).filter(
            and_(
                Expense.user_id == current_user.id,
                between(Expense.date, budget.start_date, budget.end_date)
            )
        ).group_by(Expense.category_id).all()

        spent_dict = {item.category_id: float(item.spent) for item in spent_amounts}

        # Obtener ítems del presupuesto con información de categorías
        budget_items = db.query(BudgetItem).options(joinedload(BudgetItem.category)).filter(
            BudgetItem.budget_id == budget_id
        ).all()

        comparisons = []
        total_spent = 0.00
        categories_under_budget = 0
        categories_on_budget = 0
        categories_over_budget = 0

        for item in budget_items:
            spent = spent_dict.get(item.category_id, 0.00)
            remaining = float(item.budgeted_amount) - spent
            percentage_used = (spent / float(item.budgeted_amount) * 100) if item.budgeted_amount > 0 else 0

            if spent < float(item.budgeted_amount):
                status = "under_budget"
                categories_under_budget += 1
            elif spent == float(item.budgeted_amount):
                status = "on_budget"
                categories_on_budget += 1
            else:
                status = "over_budget"
                categories_over_budget += 1

            comparisons.append(BudgetComparison(
                budget_id=budget_id,
                budget_name=budget.name,
                category_id=item.category_id,
                category_name=item.category.name,
                budgeted_amount=item.budgeted_amount,
                spent_amount=spent,
                remaining_amount=remaining,
                percentage_used=percentage_used,
                status=status
            ))

            total_spent += spent

        # Actualizar total gastado en el presupuesto
        budget.total_spent = total_spent
        db.commit()

        return BudgetSummary(
            total_budgeted=float(budget.total_budgeted),
            total_spent=total_spent,
            total_remaining=float(budget.total_budgeted) - total_spent,
            percentage_used=(total_spent / float(budget.total_budgeted) * 100) if budget.total_budgeted > 0 else 0,
            categories_under_budget=categories_under_budget,
            categories_on_budget=categories_on_budget,
            categories_over_budget=categories_over_budget,
            comparisons=comparisons
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener la comparación del presupuesto: {str(e)}"
        )