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
    side = Column(String(10), default="long")  # long, short
    leverage = Column(Float, default=1.0)  # 杠杆
    margin = Column(Float, default=0.0)  # 冻结保证金（做空使用）
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
    action_type = Column(String(20), nullable=True)  # OPEN_LONG, OPEN_SHORT, CLOSE
    direction = Column(String(10), nullable=True)  # LONG, SHORT
    leverage = Column(Float, nullable=True)  # 杠杆率
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    fee = Column(Float, default=0.0)  # 手续费
    total_amount = Column(Float, nullable=False)  # 总金额
    close_price_upper = Column(Float, nullable=True)  # 平仓上价格（止盈）
    close_price_lower = Column(Float, nullable=True)  # 平仓下价格（止损）
    status = Column(String(20), default="completed")  # pending, completed, failed
    feedback = Column(String(500), nullable=True)  # 失败或交易反馈信息
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Trade(model={self.model_name}, symbol={self.symbol}, side={self.side})>"


class StrategyConfig(Base):
    """策略配置表"""
    __tablename__ = "strategy_configs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    model_name = Column(String(50), nullable=False, unique=True, index=True)
    max_position_percent = Column(Float, default=0.9)  # 最大持仓比例
    stop_loss_percent = Column(Float, default=0.05)  # 止损比例
    take_profit_percent = Column(Float, default=0.1)  # 止盈比例
    is_active = Column(String(10), default="active")
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


class PortfolioHistory(Base):
    """组合净值历史表"""
    __tablename__ = "portfolio_history"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    model_name = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    total_value = Column(Float, nullable=False)  # 总资产
    balance = Column(Float, nullable=False)  # 现金余额
    position_value = Column(Float, default=0.0)  # 持仓市值
    long_exposure = Column(Float, default=0.0)  # 做多名义敞口
    short_exposure = Column(Float, default=0.0)  # 做空名义敞口
    total_quantity = Column(Float, default=0.0)  # 总数量
    avg_leverage = Column(Float, default=1.0)  # 平均杠杆（名义加权）
    pnl = Column(Float, default=0.0)  # 盈亏
    pnl_percent = Column(Float, default=0.0)  # 盈亏百分比
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<PortfolioHistory(model={self.model_name}, timestamp={self.timestamp}, value={self.total_value})>"

