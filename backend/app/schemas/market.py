"""
市场数据相关的 Pydantic Schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MarketPriceBase(BaseModel):
    """市场价格基础模型"""
    symbol: str
    price: float
    volume: Optional[float] = None
    source: str = "bitget"


class MarketPriceCreate(MarketPriceBase):
    """创建市场价格的请求模型"""
    pass


class MarketPriceResponse(MarketPriceBase):
    """市场价格响应模型"""
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


class MarketPriceList(BaseModel):
    """市场价格列表响应"""
    items: list[MarketPriceResponse]
    total: int

