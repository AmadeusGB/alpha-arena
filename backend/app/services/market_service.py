"""
市场数据服务
"""
import asyncio
from datetime import datetime
from typing import Dict, List
from sqlalchemy.orm import Session
from app.models.market import MarketPrice
from app.core.adapters.exchange_api import ExchangeAPI


class MarketService:
    """市场数据服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.exchange_api = ExchangeAPI()
    
    async def get_latest_prices(self) -> Dict[str, float]:
        """获取最新价格"""
        try:
            prices = await asyncio.to_thread(
                self.exchange_api.get_latest_prices,
                ["BTCUSDT", "ETHUSDT", "XRPUSDT", "BNBUSDT", "SOLUSDT"]
            )
            return prices
        except Exception as e:
            print(f"获取价格失败: {e}")
            return {}
    
    async def fetch_and_save_prices(self) -> Dict[str, float]:
        """获取并保存价格到数据库"""
        prices = await self.get_latest_prices()
        
        for symbol, price in prices.items():
            market_price = MarketPrice(
                symbol=symbol,
                price=price,
                timestamp=datetime.now()
            )
            self.db.add(market_price)
        
        try:
            self.db.commit()
            print(f"成功保存 {len(prices)} 个价格数据")
        except Exception as e:
            self.db.rollback()
            print(f"保存价格失败: {e}")
        
        return prices
    
    def get_price_history(
        self,
        symbol: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
        limit: int = 100
    ) -> List[MarketPrice]:
        """获取历史价格"""
        query = self.db.query(MarketPrice)
        
        if symbol:
            query = query.filter(MarketPrice.symbol == symbol)
        
        if start_time:
            query = query.filter(MarketPrice.timestamp >= start_time)
        
        if end_time:
            query = query.filter(MarketPrice.timestamp <= end_time)
        
        return query.order_by(MarketPrice.timestamp.desc()).limit(limit).all()

