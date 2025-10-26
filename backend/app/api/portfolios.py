"""
投资组合 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.portfolio_service import PortfolioService
from app.schemas.portfolio import ModelPortfolioResponse

router = APIRouter()


@router.get("")
async def get_portfolios(db: Session = Depends(get_db)):
    """获取所有模型账户"""
    from app.models.portfolio import ModelPortfolio
    portfolios = db.query(ModelPortfolio).all()
    return [ModelPortfolioResponse.from_orm(p) for p in portfolios]


@router.get("/{model_name}")
async def get_portfolio(
    model_name: str,
    db: Session = Depends(get_db)
):
    """获取特定模型账户"""
    service = PortfolioService(db)
    portfolio = service.get_portfolio(model_name)
    return ModelPortfolioResponse.from_orm(portfolio)


@router.get("/{model_name}/positions")
async def get_positions(
    model_name: str,
    status: str = None,
    db: Session = Depends(get_db)
):
    """获取模型持仓"""
    service = PortfolioService(db)
    positions = service.get_positions(model_name, status=status)
    return [p.__dict__ for p in positions]


@router.get("/{model_name}/performance")
async def get_performance(
    model_name: str,
    db: Session = Depends(get_db)
):
    """获取绩效指标"""
    service = PortfolioService(db)
    portfolio = service.get_portfolio(model_name)
    service.update_portfolio_value(model_name)
    
    # 计算绩效指标（简化版本）
    from app.models.portfolio import Trade
    trades = db.query(Trade).filter(
        Trade.model_name == model_name,
        Trade.status == "completed"
    ).all()
    
    total_trades = len(trades)
    profitable_trades = sum(1 for t in trades if t.side == "SELL" and t.pnl > 0)
    win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
    
    return {
        "model_name": model_name,
        "total_return": portfolio.total_return,
        "daily_pnl": portfolio.daily_pnl,
        "max_drawdown": portfolio.max_drawdown,
        "win_rate": win_rate,
        "total_trades": total_trades,
        "profitable_trades": profitable_trades
    }

