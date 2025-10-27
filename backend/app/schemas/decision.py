"""
决策相关的 Pydantic Schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class DecisionBase(BaseModel):
    """决策基础模型"""
    model_name: str
    symbol: Optional[str] = None
    action: str  # BUY, SELL, HOLD
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    prompt: Optional[str] = None
    response_raw: Optional[Dict[str, Any]] = None


class DecisionCreate(DecisionBase):
    """创建决策的请求模型"""
    pass


class ConversationResponse(BaseModel):
    """对话响应模型"""
    id: int
    model_name: str
    decision_id: Optional[int]
    prompt: str
    response: str
    tokens_used: Optional[int]
    duration_ms: Optional[int]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class DecisionResponse(DecisionBase):
    """决策响应模型"""
    id: int
    timestamp: datetime
    conversation: Optional[ConversationResponse] = None
    
    class Config:
        from_attributes = True


class DecisionList(BaseModel):
    """决策列表响应"""
    items: list[DecisionResponse]
    total: int

