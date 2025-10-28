"""
投资组合 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from app.database import get_db
from app.services.portfolio_service import PortfolioService
from app.schemas.portfolio import ModelPortfolioResponse, PortfolioHistoryResponse
from typing import Optional
from fastapi import Body

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


@router.get("/{model_name}/history")
async def get_portfolio_history(
    model_name: str,
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """获取组合净值历史"""
    from typing import List
    service = PortfolioService(db)
    history = service.get_(model_name, limit=limit)
    return [PortfolioHistoryResponse.model_validate(h) for h in history]


@router.get("/history/all")
async def get_all_portfolio_history(
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """获取所有模型的净值历史"""
    from app.models.portfolio import PortfolioHistory, ModelPortfolio
    from typing import List, Dict
    
    # 获取所有模型
    portfolios = db.query(ModelPortfolio).all()
    
    result = {}
    for portfolio in portfolios:
        history = db.query(PortfolioHistory).filter(
            PortfolioHistory.model_name == portfolio.model_name
        ).order_by(PortfolioHistory.timestamp.desc()).limit(limit).all()
        
        result[portfolio.model_name] = [
            {
                "timestamp": h.timestamp.isoformat(),
                "total_value": h.total_value,
                "balance": h.balance,
                "position_value": h.position_value,
                "pnl": h.pnl,
                "pnl_percent": h.pnl_percent
            } for h in history
        ]
    
    return result


@router.post("/rebuild-history")
async def rebuild_history(
    model_name: Optional[str] = Body(default=None),
    db: Session = Depends(get_db)
):
    """根据交易记录重新校正历史与账户（可选按模型名）。"""
    from app.services.portfolio_service import PortfolioService
    service = PortfolioService(db)
    result = service.rebuild_history(model_name)
    return {"message": "rebuild done", "result": result}


@router.get("/{model_name}/trades/analysis")
async def analyze_trades(
    model_name: str,
    db: Session = Depends(get_db)
):
    """查询数据库并按保证金模型计算指定模型的交易历史，返回详细计算与公式。"""
    service = PortfolioService(db)
    return service.analyze_trades(model_name)



@router.get("/dashboard/all")
async def get_dashboard_all_data(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """获取仪表盘所需的所有数据（全量接口，支持分页）"""
    from app.models.portfolio import ModelPortfolio, PortfolioHistory, Position
    from app.models.decision import Decision, Conversation
    from typing import Dict, List
    from app.services.decision_service import DecisionService
    
    # 1. 获取所有模型账户，并在返回前强制刷新 total_value
    portfolios = db.query(ModelPortfolio).all()
    from app.services.portfolio_service import PortfolioService
    pf_service = PortfolioService(db)
    for p in portfolios:
        try:
            pf_service.update_portfolio_value(p.model_name)
        except Exception:
            pass
    # 重新查询最新账户值
    portfolios = db.query(ModelPortfolio).all()
    portfolio_data = [ModelPortfolioResponse.from_orm(p).dict() for p in portfolios]
    
    # 2. 获取所有模型的净值历史
    history_result = {}
    for portfolio in portfolios:
        history = db.query(PortfolioHistory).filter(
            PortfolioHistory.model_name == portfolio.model_name
        ).order_by(PortfolioHistory.timestamp.desc()).limit(1000).all()
        
        history_result[portfolio.model_name] = [
            {
                "timestamp": h.timestamp.isoformat(),
                "total_value": h.total_value,
                "balance": h.balance,
                "position_value": h.position_value,
                "pnl": h.pnl,
                "pnl_percent": h.pnl_percent
            } for h in history
        ]
    
    # 3. 获取所有模型的持仓
    positions_data = []
    model_names = [p.model_name for p in portfolios]
    all_positions = db.query(Position).filter(Position.model_name.in_(model_names)).all()
    
    from app.schemas.portfolio import PositionResponse
    for pos in all_positions:
        position_dict = PositionResponse.from_orm(pos).dict()
        positions_data.append(position_dict)
    
    # 4. 获取所有模型的决策（支持分页）
    decisions_data = []
    service = DecisionService(db)
    
    # 批量获取决策数据（使用offset和limit实现分页）
    all_decisions = db.query(Decision).order_by(
        Decision.timestamp.desc()
    ).offset(offset).limit(limit).all()
    
    # 批量查询对话记录，避免N+1查询
    decision_ids = [d.id for d in all_decisions]
    conversations = {}
    if decision_ids:
        conversations_list = db.query(Conversation).filter(
            Conversation.decision_id.in_(decision_ids)
        ).all()
        conversations = {c.decision_id: c for c in conversations_list}
    
    # 构建精简版决策数据
    for decision in all_decisions:
        from app.schemas.decision import DecisionListItem
        decision_dict = {
            'id': decision.id,
            'model_name': decision.model_name,
            'symbol': decision.symbol,
            'action': decision.action,
            'confidence': decision.confidence,
            'reasoning': decision.reasoning,
            'timestamp': decision.timestamp,
            'response_raw': decision.response_raw,
            'status': getattr(decision, 'status', None),
            'feedback': getattr(decision, 'feedback', None),
            'conversation': None
        }
        
        # 添加对话记录
        conversation = conversations.get(decision.id)
        if conversation:
            from app.schemas.decision import ConversationResponse
            conversation_dict = ConversationResponse(
                id=conversation.id,
                model_name=conversation.model_name,
                decision_id=conversation.decision_id,
                prompt="",  # 不返回大字段
                response=conversation.response[:100] if conversation.response else "",
                tokens_used=conversation.tokens_used,
                duration_ms=conversation.duration_ms,
                timestamp=conversation.timestamp,
            )
            decision_dict['conversation'] = conversation_dict.dict()
        
        decisions_data.append(DecisionListItem(**decision_dict))

    # 5. 获取所有模型的交易（使用相同的分页 offset/limit）
    from app.models.portfolio import Trade
    trade_rows = db.query(Trade).order_by(Trade.executed_at.desc()).offset(offset).limit(limit).all()
    # 预取决策（用于补充交易原因）
    trade_decision_ids = [t.decision_id for t in trade_rows if t.decision_id]
    trade_decision_map = {}
    if trade_decision_ids:
        from app.models.decision import Decision
        decs = db.query(Decision).filter(Decision.id.in_(trade_decision_ids)).all()
        trade_decision_map = {d.id: d for d in decs}
    trades_data = []
    for t in trade_rows:
        reasoning = None
        if t.decision_id and t.decision_id in trade_decision_map:
            reasoning = trade_decision_map[t.decision_id].reasoning
        trades_data.append({
            'id': t.id,
            'decision_id': t.decision_id,
            'model_name': t.model_name,
            'symbol': t.symbol,
            'side': t.side,
            'action_type': t.action_type,
            'direction': t.direction,
            'leverage': t.leverage,
            'quantity': t.quantity,
            'price': t.price,
            'fee': t.fee,
            'total_amount': t.total_amount,
            'status': t.status,
            'feedback': t.feedback,
            'reasoning': reasoning,
            'executed_at': t.executed_at.isoformat() if t.executed_at else None
        })

    return {
        "portfolios": portfolio_data,
        "histories": history_result,
        "positions": positions_data,
        "decisions": decisions_data,
        "trades": trades_data,
        "total_decisions": len(decisions_data),
        "total_trades": len(trades_data),
        "total_positions": len(positions_data)
    }

