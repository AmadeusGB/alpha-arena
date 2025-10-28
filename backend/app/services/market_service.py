"""
市场数据服务
"""
import asyncio
from datetime import datetime
from typing import Dict, List
from sqlalchemy.orm import Session
from app.models.market import MarketPrice
from app.core.adapters.exchange_api import ExchangeAPI


async def _fetch_single_price(exchange_api: ExchangeAPI, symbol: str) -> tuple[str, float]:
    """并发获取单个代币价格"""
    try:
        price = await asyncio.to_thread(exchange_api.get_single_price, symbol)
        return symbol, price
    except Exception as e:
        print(f"❌ 获取{symbol}价格失败: {e}")
        return symbol, 0.0


class MarketService:
    """市场数据服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.exchange_api = ExchangeAPI()
    
    async def get_latest_prices(self) -> Dict[str, float]:
        """获取最新价格（并发请求）"""
        try:
            symbols = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "BNBUSDT", "SOLUSDT"]
            
            # 创建并发任务
            tasks = [
                _fetch_single_price(self.exchange_api, symbol)
                for symbol in symbols
            ]
            
            # 汇总获取日志
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 整理结果
            prices = {}
            for result in results:
                if isinstance(result, Exception):
                    print(f"❌ 价格获取异常: {result}")
                else:
                    symbol, price = result
                    prices[symbol] = price
            
            return prices
            
        except Exception as e:
            print(f"❌ 获取价格失败: {e}")
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

