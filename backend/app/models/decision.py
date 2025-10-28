"""
决策记录模型
"""
from sqlalchemy import Column, String, Float, DateTime, BigInteger, JSON, Text
from sqlalchemy.sql import func
from app.database import Base


class Decision(Base):
    """AI决策记录表"""
    __tablename__ = "decisions"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    model_name = Column(String(50), nullable=False, index=True)
    symbol = Column(String(20), nullable=True)
    action = Column(String(10), nullable=False)  # BUY, SELL, HOLD
    confidence = Column(Float)  # 0.0-1.0
    reasoning = Column(Text)  # 决策理由
    analysis = Column(Text)  # 模型分析（持仓/行情/计划/风险）
    prompt = Column(Text)  # 完整 prompt
    response_raw = Column(JSON)  # LLM 原始响应
    status = Column(String(20), default="pending")  # 交易状态：pending/completed/failed
    feedback = Column(Text)  # 失败或交易反馈信息
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return f"<Decision(model={self.model_name}, symbol={self.symbol}, action={self.action})>"


class Conversation(Base):
    """对话记录表"""
    __tablename__ = "conversations"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    model_name = Column(String(50), nullable=False, index=True)
    decision_id = Column(BigInteger, nullable=True, index=True)  # 关联的决策ID
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    tokens_used = Column(BigInteger)
    duration_ms = Column(BigInteger)  # 响应耗时（毫秒）
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Conversation(model={self.model_name}, tokens={self.tokens_used})>"

