from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.core.database import get_db
from app.models.user import User
from app.models.investment import Investment
from app.schemas.investment import InvestmentCreate, InvestmentUpdate, InvestmentResponse
from app.utils.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=InvestmentResponse, status_code=status.HTTP_201_CREATED)
async def create_investment(
    investment_data: InvestmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Crear nueva inversión"""
    try:
        db_investment = Investment(**investment_data.dict(), user_id=current_user.id)
        db.add(db_investment)
        db.commit()
        db.refresh(db_investment)
        return InvestmentResponse.from_orm(db_investment)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear la inversión: {str(e)}"
        )

@router.get("/", response_model=List[InvestmentResponse])
async def get_investments(
    skip: int = 0,
    limit: int = 100,
    investment_type: str = None,
    is_active: bool = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de inversiones del usuario"""
    try:
        query = db.query(Investment).filter(Investment.user_id == current_user.id)

        if investment_type:
            query = query.filter(Investment.investment_type == investment_type)

        if is_active is not None:
            query = query.filter(Investment.is_active == is_active)

        investments = query.order_by(desc(Investment.purchase_date)).offset(skip).limit(limit).all()
        return [InvestmentResponse.from_orm(investment) for investment in investments]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener las inversiones: {str(e)}"
        )

@router.get("/{investment_id}", response_model=InvestmentResponse)
async def get_investment(
    investment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener inversión por ID"""
    try:
        investment = db.query(Investment).filter(
            and_(Investment.id == investment_id, Investment.user_id == current_user.id)
        ).first()

        if not investment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inversión no encontrada"
            )

        return InvestmentResponse.from_orm(investment)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener la inversión: {str(e)}"
        )

@router.put("/{investment_id}", response_model=InvestmentResponse)
async def update_investment(
    investment_id: int,
    investment_data: InvestmentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar inversión"""
    try:
        investment = db.query(Investment).filter(
            and_(Investment.id == investment_id, Investment.user_id == current_user.id)
        ).first()

        if not investment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inversión no encontrada"
            )

        # Actualizar campos
        for field, value in investment_data.dict(exclude_unset=True).items():
            setattr(investment, field, value)

        db.commit()
        db.refresh(investment)
        return InvestmentResponse.from_orm(investment)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar la inversión: {str(e)}"
        )

@router.delete("/{investment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_investment(
    investment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar inversión"""
    try:
        investment = db.query(Investment).filter(
            and_(Investment.id == investment_id, Investment.user_id == current_user.id)
        ).first()

        if not investment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inversión no encontrada"
            )

        db.delete(investment)
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar la inversión: {str(e)}"
        )

@router.get("/summary/type")
async def get_investments_summary_by_type(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener resumen de inversiones por tipo"""
    try:
        from sqlalchemy import func

        summary = db.query(
            Investment.investment_type,
            func.sum(Investment.amount_invested).label('total_invested'),
            func.sum(Investment.current_value).label('total_current_value'),
            func.count(Investment.id).label('count')
        ).filter(
            and_(Investment.user_id == current_user.id, Investment.is_active == True)
        ).group_by(
            Investment.investment_type
        ).all()

        return [
            {
                "investment_type": item.investment_type,
                "total_invested": float(item.total_invested) if item.total_invested else 0,
                "total_current_value": float(item.total_current_value) if item.total_current_value else 0,
                "count": item.count
            } for item in summary
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener el resumen: {str(e)}"
        )

@router.get("/performance/total")
async def get_total_investment_performance(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener rendimiento total de inversiones"""
    try:
        from sqlalchemy import func

        result = db.query(
            func.sum(Investment.amount_invested).label('total_invested'),
            func.sum(Investment.current_value).label('total_current_value')
        ).filter(
            and_(Investment.user_id == current_user.id, Investment.is_active == True)
        ).first()

        total_invested = float(result.total_invested) if result.total_invested else 0
        total_current_value = float(result.total_current_value) if result.total_current_value else 0

        return {
            "total_invested": total_invested,
            "total_current_value": total_current_value,
            "total_performance": total_current_value - total_invested,
            "performance_percentage": (total_current_value - total_invested) / total_invested * 100 if total_invested > 0 else 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener el rendimiento: {str(e)}"
        )