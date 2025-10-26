"""
投资组合相关模型
"""
from sqlalchemy import Column, String, Float, DateTime, BigInteger, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class ModelPortfolio(Base):
    """模型账户状态表"""
    __tablename__ = "model_portfolios"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    model_name = Column(String(50), nullable=False, unique=True, index=True)
    balance = Column(Float, default=10000.0)  # 现金余额
    total_value = Column(Float, default=10000.0)  # 总资产（现金+持仓市值）
    daily_pnl = Column(Float, default=0.0)  # 今日盈亏
    total_pnl = Column(Float, default=0.0)  # 总盈亏
    total_return = Column(Float, default=0.0)  # 总收益率
    max_drawdown = Column(Float, default=0.0)  # 最大回撤
    is_active = Column(String(10), default="active")  # active, paused
    initial_capital = Column(Float, default=10000.0)  # 初始资金
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ModelPortfolio(model={self.model_name}, total_value={self.total_value})>"


class Position(Base):
    """持仓记录表"""
    __tablename__ = "positions"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    model_name = Column(String(50), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    quantity = Column(Float, nullable=False)  # 持仓数量
    entry_price = Column(Float, nullable=False)  # 入场价格
    current_price = Column(Float)  # 当前价格
    pnl = Column(Float, default=0.0)  # 盈亏
    pnl_percent = Column(Float, default=0.0)  # 盈亏百分比
    status = Column(String(10), default="open")  # open, closed
    decision_id = Column(BigInteger, nullable=True, index=True)  # 关联的决策ID
    opened_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Position(model={self.model_name}, symbol={self.symbol})>"


class Trade(Base):
    """交易执行记录表"""
    __tablename__ = "trades"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    decision_id = Column(BigInteger, nullable=True, index=True)
    model_name = Column(String(50), nullable=False, index=True)
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)  # BUY, SELL
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    fee = Column(Float, default=0.0)  # 手续费
    total_amount = Column(Float, nullable=False)  # 总金额
    status = Column(String(20), default="completed")  # pending, completed, failed
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Trade(model={self.model_name}, symbol={self.symbol}, side={self.side})>"


class StrategyConfig(Base):
    """策略配置表"""
    __tablename__ = "strategy_configs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    model_name = Column(String(50), nullable=False, unique=True, index=True)
    params = Column(String)  # JSON格式的策略参数
    is_active = Column(String(10), default="active")
    max_position_size = Column(Float, default=0.2)  # 最大仓位比例
    stop_loss_percent = Column(Float, default=0.05)  # 止损比例
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<StrategyConfig(model={self.model_name}, is_active={self.is_active})>"


class SystemLog(Base):
    """系统日志表"""
    __tablename__ = "system_logs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    level = Column(String(10), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR
    module = Column(String(50), nullable=True)
    message = Column(String(500), nullable=False)
    details = Column(String)  # JSON格式的详细信息
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<SystemLog(level={self.level}, message={self.message})>"

