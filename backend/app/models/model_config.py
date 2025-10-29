"""
模型配置模型
"""
from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class ModelConfig(Base):
    """模型配置表"""
    __tablename__ = "model_configs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)  # 模型名称
    
    # API 配置
    provider = Column(String(50), nullable=False, default='siliconflow')  # 提供商: siliconflow, openai, anthropic
    model_id = Column(String(100), nullable=False)  # 模型ID: Qwen/Qwen3-32B
    api_key = Column(String(255), nullable=True)  # API密钥（加密存储）
    base_url = Column(String(255), nullable=True)  # API地址
    
    # 模型参数
    max_tokens = Column(Integer, default=200)
    temperature = Column(Float, default=0.1)
    timeout = Column(Integer, default=30)  # 超时时间（秒）
    
    # 状态
    is_enabled = Column(Boolean, default=True)  # 是否启用
    is_active = Column(Boolean, default=True)  # 是否活跃
    
    # 测试信息
    last_test_at = Column(DateTime(timezone=True), nullable=True)
    last_test_result = Column(Boolean, default=False)  # 最后测试结果
    test_error = Column(String(500), nullable=True)  # 测试错误信息
    
    # 统计信息
    total_calls = Column(Integer, default=0)  # 总调用次数
    success_calls = Column(Integer, default=0)  # 成功调用次数
    fail_calls = Column(Integer, default=0)  # 失败调用次数
    avg_response_time = Column(Float, default=0.0)  # 平均响应时间（秒）
    
    # 其他配置
    params = Column(JSON, default={})  # 额外参数

    # 交易参数
    trade_symbol = Column(String(50), nullable=True)  # 交易标的，例如 BTCUSDT
    trade_quantity = Column(Float, nullable=True, default=0.0)  # 交易数量
    leverage = Column(Integer, nullable=True, default=1)  # 杠杆率
    trade_side = Column(String(10), nullable=True)  # LONG/SHORT
    close_price_upper = Column(Float, nullable=True)  # 平仓上价格（止盈价）
    close_price_lower = Column(Float, nullable=True)  # 平仓下价格（止损价）
    
    # 时间戳
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ModelConfig(name={self.name}, provider={self.provider}, model_id={self.model_id})>"
