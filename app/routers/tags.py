from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from app.core.database import get_db
from app.models.user import User
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate, TagResponse, TagWithUsage
from app.utils.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Crear nueva etiqueta"""
    try:
        # Verificar que no exista una etiqueta con el mismo nombre para el usuario
        existing_tag = db.query(Tag).filter(
            and_(Tag.user_id == current_user.id, Tag.name == tag_data.name)
        ).first()

        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una etiqueta con este nombre"
            )

        db_tag = Tag(**tag_data.dict(), user_id=current_user.id)
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        return TagResponse.from_orm(db_tag)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear la etiqueta: {str(e)}"
        )

@router.get("/", response_model=List[TagResponse])
async def get_tags(
    include_usage: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de etiquetas del usuario"""
    try:
        query = db.query(Tag).filter(
            and_(Tag.user_id == current_user.id, Tag.is_active == True)
        )

        tags = query.order_by(Tag.name).all()

        if include_usage:
            # Obtener información de uso para cada etiqueta
            result = []
            for tag in tags:
                # Contar gastos asociados
                expense_count = db.query(func.count(Tag.id)).filter(
                    and_(Tag.id == tag.id, Tag.expenses.any())
                ).scalar()

                # Contar ingresos asociados
                income_count = db.query(func.count(Tag.id)).filter(
                    and_(Tag.id == tag.id, Tag.incomes.any())
                ).scalar()

                tag_dict = TagWithUsage.from_orm(tag)
                tag_dict.expense_count = expense_count or 0
                tag_dict.income_count = income_count or 0
                result.append(tag_dict)

            return result

        return [TagResponse.from_orm(tag) for tag in tags]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener las etiquetas: {str(e)}"
        )

@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener etiqueta por ID"""
    try:
        tag = db.query(Tag).filter(
            and_(Tag.id == tag_id, Tag.user_id == current_user.id)
        ).first()

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Etiqueta no encontrada"
            )

        return TagResponse.from_orm(tag)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener la etiqueta: {str(e)}"
        )

@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar etiqueta"""
    try:
        tag = db.query(Tag).filter(
            and_(Tag.id == tag_id, Tag.user_id == current_user.id)
        ).first()

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Etiqueta no encontrada"
            )

        # Verificar nombre único si se está cambiando
        if tag_data.name and tag_data.name != tag.name:
            existing_tag = db.query(Tag).filter(
                and_(Tag.user_id == current_user.id, Tag.name == tag_data.name, Tag.id != tag_id)
            ).first()

            if existing_tag:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe una etiqueta con este nombre"
                )

        # Actualizar campos
        for field, value in tag_data.dict(exclude_unset=True).items():
            setattr(tag, field, value)

        db.commit()
        db.refresh(tag)
        return TagResponse.from_orm(tag)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar la etiqueta: {str(e)}"
        )

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar etiqueta"""
    try:
        tag = db.query(Tag).filter(
            and_(Tag.id == tag_id, Tag.user_id == current_user.id)
        ).first()

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Etiqueta no encontrada"
            )

        # Verificar si está siendo usada en transacciones
        from app.models.expense import Expense
        from app.models.income import Income

        expenses_count = db.query(Expense).filter(Expense.tags.any(id=tag_id)).count()
        incomes_count = db.query(Income).filter(Income.tags.any(id=tag_id)).count()

        if expenses_count > 0 or incomes_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar una etiqueta que está siendo utilizada en transacciones"
            )

        # Soft delete - marcar como inactivo
        tag.is_active = False
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar la etiqueta: {str(e)}"
        )