"""
持仓 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.portfolio_service import PortfolioService
from app.schemas.portfolio import PositionResponse, PositionList

router = APIRouter()


@router.get("")
async def get_positions(
    model_name: str = None,
    status: str = "open",
    db: Session = Depends(get_db)
):
    """获取当前持仓"""
    service = PortfolioService(db)
    
    if model_name:
        positions = service.get_positions(model_name, status=status)
    else:
        # 获取所有模型的持仓
        from app.models.portfolio import Position
        query = db.query(Position)
        if status:
            query = query.filter(Position.status == status)
        positions = query.all()
    
    return PositionList(
        items=[PositionResponse.from_orm(p) for p in positions],
        total=len(positions)
    )


@router.get("/history")
async def get_position_history(
    model_name: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取历史持仓"""
    from app.models.portfolio import Position
    query = db.query(Position)
    
    if model_name:
        query = query.filter(Position.model_name == model_name)
    
    positions = query.filter(Position.status == "closed").order_by(
        Position.closed_at.desc()
    ).limit(limit).all()
    
    return [PositionResponse.from_orm(p) for p in positions]

