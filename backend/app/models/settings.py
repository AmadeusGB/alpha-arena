"""
系统设置模型
"""
from sqlalchemy import Column, String, Float, Boolean, Integer, JSON, DateTime
from sqlalchemy.sql import func
from app.database import Base


class TradingSettings(Base):
    """交易设置表"""
    __tablename__ = "trading_settings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, default="default")
    
    # 交易费用
    maker_fee = Column(Float, default=0.0002)
    taker_fee = Column(Float, default=0.0004)
    slippage = Column(Float, default=0.0001)
    
    # 策略配置
    max_leverage = Column(Integer, default=1)
    allow_short = Column(Boolean, default=False)
    min_position = Column(Float, default=0.001)
    max_position = Column(Float, default=0.2)
    position_unit = Column(Float, default=0.01)
    
    # 风险控制
    stop_loss_min = Column(Float, default=0.01)
    stop_loss_max = Column(Float, default=0.10)
    take_profit_min = Column(Float, default=0.01)
    take_profit_max = Column(Float, default=0.20)
    max_position_percent = Column(Float, default=0.8)
    max_drawdown = Column(Float, default=0.20)
    
    # 其他
    min_confidence = Column(Float, default=0.3)
    max_open_positions = Column(Integer, default=3)
    cooldown_minutes = Column(Integer, default=5)
    min_trade_amount = Column(Float, default=10.0)
    max_trade_amount = Column(Float, default=10000.0)
    
    params = Column(JSON, default={})  # 额外配置
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<TradingSettings(name={self.name})>"
