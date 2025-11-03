from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc

from app.core.database import get_db
from app.models.user import User
from app.models.income import Income
from app.models.category import Category
from app.models.tag import Tag
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
        # Verificar categoría si se especifica
        if income_data.category_id:
            category = db.query(Category).filter(
                and_(Category.id == income_data.category_id, Category.user_id == current_user.id)
            ).first()

            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoría no encontrada"
                )

            if category.category_type != "income":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La categoría seleccionada no es válida para ingresos"
                )

        # Verificar etiquetas si se especifican
        if income_data.tag_ids:
            tags = db.query(Tag).filter(
                and_(Tag.id.in_(income_data.tag_ids), Tag.user_id == current_user.id, Tag.is_active == True)
            ).all()

            if len(tags) != len(income_data.tag_ids):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Una o más etiquetas no encontradas"
                )

        db_income = Income(**income_data.dict(exclude={'tag_ids'}), user_id=current_user.id)
        db.add(db_income)

        # Agregar etiquetas si se especifican
        if income_data.tag_ids:
            tags = db.query(Tag).filter(
                and_(Tag.id.in_(income_data.tag_ids), Tag.user_id == current_user.id, Tag.is_active == True)
            ).all()
            db_income.tags.extend(tags)

        db.commit()
        db.refresh(db_income)
        return IncomeResponse.model_validate(db_income)
    except HTTPException:
        raise
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
    category_id: int = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de ingresos del usuario"""
    try:
        query = db.query(Income).options(joinedload(Income.category), joinedload(Income.tags)).filter(Income.user_id == current_user.id)

        if source:
            query = query.filter(Income.source == source)

        if category_id:
            query = query.filter(Income.category_id == category_id)

        incomes = query.order_by(desc(Income.date)).offset(skip).limit(limit).all()
        return [IncomeResponse.model_validate(income) for income in incomes]
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
        income = db.query(Income).options(joinedload(Income.category), joinedload(Income.tags)).filter(
            and_(Income.id == income_id, Income.user_id == current_user.id)
        ).first()

        if not income:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingreso no encontrado"
            )

        return IncomeResponse.model_validate(income)
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

        # Verificar categoría si se está actualizando
        if income_data.category_id is not None:
            if income_data.category_id:
                category = db.query(Category).filter(
                    and_(Category.id == income_data.category_id, Category.user_id == current_user.id)
                ).first()

                if not category:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Categoría no encontrada"
                    )

                if category.category_type != "income":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="La categoría seleccionada no es válida para ingresos"
                    )

        # Verificar etiquetas si se están actualizando
        if income_data.tag_ids is not None:
            if income_data.tag_ids:
                tags = db.query(Tag).filter(
                    and_(Tag.id.in_(income_data.tag_ids), Tag.user_id == current_user.id, Tag.is_active == True)
                ).all()

                if len(tags) != len(income_data.tag_ids):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Una o más etiquetas no encontradas"
                    )

        # Actualizar campos
        update_data = income_data.dict(exclude_unset=True)

        # Manejar etiquetas por separado
        if 'tag_ids' in update_data:
            tag_ids = update_data.pop('tag_ids')
            if tag_ids is not None:
                tags = db.query(Tag).filter(
                    and_(Tag.id.in_(tag_ids), Tag.user_id == current_user.id, Tag.is_active == True)
                ).all()
                income.tags = tags

        # Actualizar otros campos
        for field, value in update_data.items():
            setattr(income, field, value)

        db.commit()
        db.refresh(income)
        return IncomeResponse.model_validate(income)
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

@router.get("/summary/category")
async def get_incomes_summary_by_category(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener resumen de ingresos por categoría"""
    try:
        from sqlalchemy import func

        summary = db.query(
            Category.name.label('category_name'),
            Category.id.label('category_id'),
            Category.color,
            Category.icon,
            func.sum(Income.amount).label('total_amount'),
            func.count(Income.id).label('count')
        ).join(
            Income, Category.id == Income.category_id, isouter=True
        ).filter(
            Income.user_id == current_user.id
        ).group_by(
            Category.id, Category.name, Category.color, Category.icon
        ).all()

        return [
            {
                "category_id": item.category_id,
                "category_name": item.category_name,
                "color": item.color,
                "icon": item.icon,
                "total_amount": float(item.total_amount) if item.total_amount else 0,
                "count": item.count
            } for item in summary
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener el resumen: {str(e)}"
        )