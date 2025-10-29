"""
设置 Schema
"""
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class TradingSettingsBase(BaseModel):
    """交易设置基础模型"""
    maker_fee: float = 0.0002
    taker_fee: float = 0.0004
    slippage: float = 0.0001
    max_leverage: int = 1
    allow_short: bool = False
    min_position: float = 0.001
    max_position: float = 0.2
    position_unit: float = 0.01
    stop_loss_min: float = 0.01
    stop_loss_max: float = 0.10
    take_profit_min: float = 0.01
    take_profit_max: float = 0.20
    max_position_percent: float = 0.8
    max_drawdown: float = 0.20
    min_confidence: float = 0.3
    max_open_positions: int = 3
    cooldown_minutes: int = 5
    min_trade_amount: float = 10.0
    max_trade_amount: float = 10000.0
    params: Optional[Dict] = {}


class TradingSettingsCreate(TradingSettingsBase):
    """创建设置"""
    name: str = "default"


class TradingSettingsUpdate(TradingSettingsBase):
    """更新设置"""
    pass


class TradingSettingsResponse(TradingSettingsBase):
    """设置响应"""
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
