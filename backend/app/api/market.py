"""
市场数据 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.market_service import MarketService
from app.schemas.market import MarketPriceResponse, MarketPriceList

router = APIRouter()


@router.get("/prices/latest")
async def get_latest_prices(db: Session = Depends(get_db)):
    """获取最新价格"""
    service = MarketService(db)
    prices = await service.get_latest_prices()
    return prices


@router.get("/prices/history")
async def get_price_history(
    symbol: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取历史价格"""
    service = MarketService(db)
    prices = service.get_price_history(symbol=symbol, limit=limit)
    return [MarketPriceResponse.from_orm(p) for p in prices]


@router.post("/prices/refresh")
async def refresh_prices(db: Session = Depends(get_db)):
    """手动刷新价格"""
    service = MarketService(db)
    prices = await service.fetch_and_save_prices()
    return prices


@router.get("/symbols")
async def get_symbols():
    """获取支持的交易对"""
    return {
        "symbols": ["BTCUSDT", "ETHUSDT", "XRPUSDT", "BNBUSDT", "SOLUSDT"]
    }

