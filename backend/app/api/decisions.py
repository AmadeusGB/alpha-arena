"""
决策 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.decision_service import DecisionService
from app.schemas.decision import DecisionResponse, DecisionList

router = APIRouter()


@router.get("")
async def get_decisions(
    model_name: str = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """获取决策历史"""
    service = DecisionService(db)
    decisions = service.get_decision_history(
        model_name=model_name,
        limit=limit,
        offset=offset
    )
    return DecisionList(
        items=[DecisionResponse.from_orm(d) for d in decisions],
        total=len(decisions)
    )


@router.get("/{decision_id}")
async def get_decision(
    decision_id: int,
    db: Session = Depends(get_db)
):
    """获取决策详情"""
    from app.models.decision import Decision
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="决策不存在")
    return DecisionResponse.from_orm(decision)


@router.post("/trigger")
async def trigger_decisions(db: Session = Depends(get_db)):
    """手动触发决策"""
    from app.models.market import MarketPrice
    from app.core.technical_indicators import calculate_basic_indicators
    from app.services.market_service import MarketService
    
    # 获取最新价格
    market_service = MarketService(db)
    prices = await market_service.get_latest_prices()
    
    if not prices:
        raise HTTPException(status_code=400, detail="无法获取价格数据")
    
    # 计算技术指标
    indicators = {}
    symbols = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'BNBUSDT', 'SOLUSDT']
    for symbol in symbols:
        historical_prices = db.query(MarketPrice).filter(
            MarketPrice.symbol == symbol
        ).order_by(MarketPrice.timestamp.desc()).limit(50).all()
        
        if historical_prices:
            price_list = [p.price for p in reversed(historical_prices)]
            indicators[symbol] = calculate_basic_indicators(price_list)
    
    # 生成决策
    service = DecisionService(db)
    decisions = await service.make_decisions(prices, indicators)
    
    return {"decisions": decisions, "indicators": indicators}


@router.get("/compare")
async def compare_decisions(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """对比不同模型的决策"""
    service = DecisionService(db)
    decisions = service.get_decision_history(limit=limit)
    
    # 按时间分组
    decisions_by_time = {}
    for decision in decisions:
        key = decision.timestamp.isoformat()
        if key not in decisions_by_time:
            decisions_by_time[key] = []
        decisions_by_time[key].append(DecisionResponse.from_orm(decision))
    
    return {"comparisons": decisions_by_time}

