"""
决策 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.decision_service import DecisionService
from app.schemas.decision import DecisionResponse, DecisionList, DecisionListItem, ConversationResponse

router = APIRouter()


@router.get("")
async def get_decisions(
    model_name: str = None,
    limit: int = 50,  # 减少默认返回数量
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """获取决策历史"""
    from app.models.decision import Conversation
    from app.schemas.decision import DecisionListItem
    
    service = DecisionService(db)
    decisions = service.get_decision_history(
        model_name=model_name,
        limit=limit,
        offset=offset
    )
    
    # 批量查询所有对话记录，避免N+1查询
    decision_ids = [d.id for d in decisions]
    conversations = {}
    if decision_ids:
        conversations_list = db.query(Conversation).filter(
            Conversation.decision_id.in_(decision_ids)
        ).all()
        conversations = {c.decision_id: c for c in conversations_list}
    
    # 构建精简版响应（不包含prompt等大字段）
    decision_responses = []
    for decision in decisions:
        # 创建精简版的决策数据
        decision_data = DecisionListItem(
            id=decision.id,
            model_name=decision.model_name,
            symbol=decision.symbol,
            action=decision.action,
            confidence=decision.confidence,
            reasoning=decision.reasoning,
            timestamp=decision.timestamp,
            response_raw=decision.response_raw,
            status=decision.status,
            feedback=decision.feedback,
            conversation=None
        )
        
        # 从预加载的对话记录中查找
        conversation = conversations.get(decision.id)
        
        if conversation:
            # 创建精简的conversation对象
            conversation_data = ConversationResponse(
                id=conversation.id,
                model_name=conversation.model_name,
                decision_id=conversation.decision_id,
                prompt="",  # 不返回大字段
                response=conversation.response[:100] if conversation.response else "",  # 只返回前100字符
                tokens_used=conversation.tokens_used,
                duration_ms=conversation.duration_ms,
                timestamp=conversation.timestamp,
            )
            decision_data.conversation = conversation_data
        
        decision_responses.append(decision_data)
    
    return DecisionList(
        items=decision_responses,
        total=len(decision_responses)
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


@router.get("/{decision_id}/conversation", response_model=ConversationResponse)
async def get_decision_conversation(
    decision_id: int,
    db: Session = Depends(get_db)
):
    """获取指定决策的对话详情（包含完整 prompt/response）"""
    from app.models.decision import Conversation
    conv = db.query(Conversation).filter(Conversation.decision_id == decision_id).order_by(Conversation.timestamp.desc()).first()
    if not conv:
        raise HTTPException(status_code=404, detail="对话不存在")
    return ConversationResponse.from_orm(conv)


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

