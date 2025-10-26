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
    SCHEDULER_INTERVAL_MINUTES: int = 5
    
    # 初始资金
    INITIAL_CAPITAL: float = 10000.0
    
    # 支持的交易对
    TRADING_PAIRS: list = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "BNBUSDT", "SOLUSDT"]
    
    class Config:
        env_file = ".env"


settings = Settings()

