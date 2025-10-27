"""
配置管理
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # API配置
    API_V1_PREFIX: str = "/api/v1"
    
    # 数据库配置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://arena_user:password@localhost:5432/alpha_arena"
    )
    
    # SiliconFlow API
    SILICONFLOW_API_KEY: str = os.getenv("SILICONFLOW_API_KEY", "")
    SILICONFLOW_BASE_URL: str = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
    
    # Bitget API
    BITGET_API_KEY: str = os.getenv("BITGET_API_KEY", "")
    BITGET_SECRET_KEY: str = os.getenv("BITGET_SECRET_KEY", "")
    BITGET_PASSPHRASE: str = os.getenv("BITGET_PASSPHRASE", "")
    
    # 任务调度配置
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_INTERVAL_MINUTES: int = 1
    
    # 初始资金
    INITIAL_CAPITAL: float = 10000.0
    
    # 支持的交易对
    TRADING_PAIRS: list = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "BNBUSDT", "SOLUSDT"]
    
    # ============= 交易费用配置 =============
    TRADING_FEE_MAKER: float = 0.0002      # Maker 费率 0.02%
    TRADING_FEE_TAKER: float = 0.0004      # Taker 费率 0.04%
    SLIPPAGE_TOLERANCE: float = 0.0001     # 滑点容忍度 0.01%
    
    # ============= 交易策略配置 =============
    MAX_LEVERAGE: int = 1                  # 最大杠杆倍数（1=无杠杆）
    ALLOW_SHORT: bool = False              # 是否允许做空
    MIN_POSITION_SIZE: float = 0.001       # 最小持仓数量
    MAX_POSITION_SIZE: float = 0.2         # 最大仓位比例
    POSITION_SIZE_UNIT: float = 0.01       # 仓位步进
    
    # ============= 风险控制配置 =============
    STOP_LOSS_MIN: float = 0.01            # 止损最小比例 1%
    STOP_LOSS_MAX: float = 0.10            # 止损最大比例 10%
    TAKE_PROFIT_MIN: float = 0.01          # 止盈最小比例 1%
    TAKE_PROFIT_MAX: float = 0.20          # 止盈最大比例 20%
    MAX_POSITION_PERCENT: float = 0.8      # 最大总持仓比例
    MAX_DRAWDOWN_LIMIT: float = 0.20       # 最大回撤限制 20%
    
    # ============= 其他交易配置 =============
    MIN_CONFIDENCE_THRESHOLD: float = 0.3  # 最小信心阈值
    COOLDOWN_PERIOD_MINUTES: int = 5       # 冷却期（分钟）
    MAX_OPEN_POSITIONS: int = 3            # 最大同时持仓数
    ORDER_TIMEOUT_SECONDS: int = 30        # 订单超时时间
    MIN_TRADE_AMOUNT: float = 10.0         # 最小交易金额（USDT）
    MAX_TRADE_AMOUNT: float = 10000.0      # 最大交易金额（USDT）
    
    class Config:
        env_file = ".env"


settings = Settings()

