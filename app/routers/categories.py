from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.core.database import get_db
from app.models.user import User
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithSubcategories
from app.utils.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Crear nueva categoría"""
    try:
        # Preparar los datos, convirtiendo parent_id 0 a None
        category_dict = category_data.dict()
        if category_dict.get('parent_id') == 0:
            category_dict['parent_id'] = None

        # Verificar que la categoría padre existe y pertenece al usuario si se especifica
        if category_dict.get('parent_id'):
            parent = db.query(Category).filter(
                and_(Category.id == category_dict['parent_id'], Category.user_id == current_user.id)
            ).first()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoría padre no encontrada"
                )
            # Verificar que el tipo coincida
            if parent.category_type != category_data.category_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El tipo de categoría debe coincidir con la categoría padre"
                )

        db_category = Category(**category_dict, user_id=current_user.id, is_default=False)
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return CategoryResponse.from_orm(db_category)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear la categoría: {str(e)}"
        )

@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    category_type: str = None,
    include_subcategories: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de categorías del usuario"""
    try:
        query = db.query(Category).filter(Category.user_id == current_user.id)

        if category_type:
            query = query.filter(Category.category_type == category_type)

        if include_subcategories:
            # Obtener solo categorías padre (sin parent_id)
            query = query.filter(Category.parent_id.is_(None))

        categories = query.order_by(Category.category_type, Category.name).all()

        if include_subcategories:
            # Cargar subcategorías recursivamente
            result = []
            for category in categories:
                category_dict = CategoryWithSubcategories.from_orm(category)
                category_dict.subcategories = _get_subcategories_recursive(category.id, db, current_user.id)
                result.append(category_dict)
            return result

        return [CategoryResponse.from_orm(category) for category in categories]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener las categorías: {str(e)}"
        )

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener categoría por ID"""
    try:
        category = db.query(Category).filter(
            and_(Category.id == category_id, Category.user_id == current_user.id)
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )

        return CategoryResponse.from_orm(category)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener la categoría: {str(e)}"
        )

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar categoría"""
    try:
        category = db.query(Category).filter(
            and_(Category.id == category_id, Category.user_id == current_user.id)
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )

        # No permitir actualizar categorías por defecto
        if category.is_default:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pueden modificar las categorías por defecto del sistema"
            )

        # Verificar categoría padre si se actualiza
        if category_data.parent_id is not None:
            parent_id = category_data.parent_id if category_data.parent_id != 0 else None
            if parent_id:
                parent = db.query(Category).filter(
                    and_(Category.id == parent_id, Category.user_id == current_user.id)
                ).first()
                if not parent:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Categoría padre no encontrada"
                    )
                # Verificar que el tipo coincida
                new_type = category_data.category_type or category.category_type
                if parent.category_type != new_type:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El tipo de categoría debe coincidir con la categoría padre"
                    )

        # Actualizar campos
        update_dict = category_data.dict(exclude_unset=True)
        if 'parent_id' in update_dict and update_dict['parent_id'] == 0:
            update_dict['parent_id'] = None

        for field, value in update_dict.items():
            setattr(category, field, value)

        db.commit()
        db.refresh(category)
        return CategoryResponse.from_orm(category)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar la categoría: {str(e)}"
        )

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar categoría"""
    try:
        category = db.query(Category).filter(
            and_(Category.id == category_id, Category.user_id == current_user.id)
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )

        # No permitir eliminar categorías por defecto
        if category.is_default:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pueden eliminar las categorías por defecto del sistema"
            )

        # Verificar si tiene subcategorías
        subcategories = db.query(Category).filter(Category.parent_id == category_id).all()
        if subcategories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar una categoría que tiene subcategorías. Elimine las subcategorías primero."
            )

        # Verificar si está siendo usada en transacciones
        from app.models.expense import Expense
        from app.models.income import Income

        expenses_count = db.query(Expense).filter(Expense.category_id == category_id).count()
        incomes_count = db.query(Income).filter(Income.category_id == category_id).count()

        if expenses_count > 0 or incomes_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar una categoría que está siendo utilizada en transacciones"
            )

        db.delete(category)
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar la categoría: {str(e)}"
        )

def _get_subcategories_recursive(parent_id: int, db: Session, user_id: int) -> List[CategoryWithSubcategories]:
    """Función auxiliar para obtener subcategorías recursivamente"""
    subcategories = db.query(Category).filter(
        and_(Category.parent_id == parent_id, Category.user_id == user_id)
    ).order_by(Category.name).all()

    result = []
    for subcat in subcategories:
        subcat_dict = CategoryWithSubcategories.from_orm(subcat)
        subcat_dict.subcategories = _get_subcategories_recursive(subcat.id, db, user_id)
        result.append(subcat_dict)

    return result