from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.core.database import get_db
from app.models.user import User
from app.models.financial_product import FinancialProduct
from app.schemas.financial_product import FinancialProductCreate, FinancialProductUpdate, FinancialProductResponse
from app.utils.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=FinancialProductResponse, status_code=status.HTTP_201_CREATED)
async def create_financial_product(
    product_data: FinancialProductCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Crear nuevo producto financiero"""
    try:
        db_product = FinancialProduct(**product_data.dict(), user_id=current_user.id)
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return FinancialProductResponse.from_orm(db_product)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear el producto financiero: {str(e)}"
        )

@router.get("/", response_model=List[FinancialProductResponse])
async def get_financial_products(
    skip: int = 0,
    limit: int = 100,
    product_type: str = None,
    institution: str = None,
    is_active: bool = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de productos financieros del usuario"""
    try:
        query = db.query(FinancialProduct).filter(FinancialProduct.user_id == current_user.id)

        if product_type:
            query = query.filter(FinancialProduct.product_type == product_type)

        if institution:
            query = query.filter(FinancialProduct.institution == institution)

        if is_active is not None:
            query = query.filter(FinancialProduct.is_active == is_active)

        products = query.order_by(desc(FinancialProduct.opening_date)).offset(skip).limit(limit).all()
        return [FinancialProductResponse.from_orm(product) for product in products]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener los productos financieros: {str(e)}"
        )

@router.get("/{product_id}", response_model=FinancialProductResponse)
async def get_financial_product(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener producto financiero por ID"""
    try:
        product = db.query(FinancialProduct).filter(
            and_(FinancialProduct.id == product_id, FinancialProduct.user_id == current_user.id)
        ).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto financiero no encontrado"
            )

        return FinancialProductResponse.from_orm(product)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener el producto financiero: {str(e)}"
        )

@router.put("/{product_id}", response_model=FinancialProductResponse)
async def update_financial_product(
    product_id: int,
    product_data: FinancialProductUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar producto financiero"""
    try:
        product = db.query(FinancialProduct).filter(
            and_(FinancialProduct.id == product_id, FinancialProduct.user_id == current_user.id)
        ).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto financiero no encontrado"
            )

        # Actualizar campos
        for field, value in product_data.dict(exclude_unset=True).items():
            setattr(product, field, value)

        db.commit()
        db.refresh(product)
        return FinancialProductResponse.from_orm(product)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar el producto financiero: {str(e)}"
        )

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_financial_product(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar producto financiero"""
    try:
        product = db.query(FinancialProduct).filter(
            and_(FinancialProduct.id == product_id, FinancialProduct.user_id == current_user.id)
        ).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto financiero no encontrado"
            )

        db.delete(product)
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar el producto financiero: {str(e)}"
        )

@router.get("/summary/type")
async def get_financial_products_summary_by_type(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener resumen de productos financieros por tipo"""
    try:
        from sqlalchemy import func

        summary = db.query(
            FinancialProduct.product_type,
            func.sum(FinancialProduct.balance).label('total_balance'),
            func.count(FinancialProduct.id).label('count')
        ).filter(
            and_(FinancialProduct.user_id == current_user.id, FinancialProduct.is_active == True)
        ).group_by(
            FinancialProduct.product_type
        ).all()

        return [
            {
                "product_type": item.product_type,
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
async def get_total_financial_balance(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener balance total de productos financieros"""
    try:
        from sqlalchemy import func

        result = db.query(
            func.sum(FinancialProduct.balance).label('total_balance')
        ).filter(
            and_(FinancialProduct.user_id == current_user.id, FinancialProduct.is_active == True)
        ).first()

        total_balance = float(result.total_balance) if result.total_balance else 0

        return {
            "total_balance": total_balance,
            "currency": "COP"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener el balance total: {str(e)}"
        )