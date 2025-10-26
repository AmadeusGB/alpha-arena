"""
投资组合相关的 Pydantic Schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ModelPortfolioResponse(BaseModel):
    """模型账户响应模型"""
    id: int
    model_name: str
    balance: float
    total_value: float
    daily_pnl: float
    total_pnl: float
    total_return: float
    max_drawdown: float
    is_active: str
    initial_capital: float
    updated_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class PositionResponse(BaseModel):
    """持仓响应模型"""
    id: int
    model_name: str
    symbol: str
    quantity: float
    entry_price: float
    current_price: Optional[float]
    pnl: float
    pnl_percent: float
    status: str
    decision_id: Optional[int]
    opened_at: datetime
    closed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PositionList(BaseModel):
    """持仓列表响应"""
    items: list[PositionResponse]
    total: int


class PerformanceMetrics(BaseModel):
    """绩效指标"""
    model_name: str
    total_return: float
    daily_pnl: float
    sharpe_ratio: float  # 夏普比率
    max_drawdown: float
    win_rate: float  # 胜率
    total_trades: int
    profitable_trades: int


class PortfolioHistory(BaseModel):
    """净值历史"""
    timestamp: datetime
    value: float
    pnl: float

