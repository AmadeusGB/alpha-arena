"""
市场价格数据模型
"""
from sqlalchemy import Column, String, Float, DateTime, BigInteger
from sqlalchemy.sql import func
from app.database import Base


class MarketPrice(Base):
    """市场价格表"""
    __tablename__ = "market_prices"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    volume = Column(Float)
    source = Column(String(50), default="bitget")
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return f"<MarketPrice(symbol={self.symbol}, price={self.price})>"

