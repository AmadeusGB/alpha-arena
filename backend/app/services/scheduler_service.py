"""
任务调度服务
"""
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.market_service import MarketService
from app.services.decision_service import DecisionService
from app.services.portfolio_service import PortfolioService
from app.models.portfolio import SystemLog


class SchedulerService:
    """任务调度服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.is_running = False
        self.last_run_time = None
        self.error_count = 0
    
    def log_message(self, level: str, message: str, details: str = None):
        """记录日志"""
        log_entry = SystemLog(
            level=level,
            module="scheduler",
            message=message,
            details=details
        )
        self.db.add(log_entry)
        self.db.commit()
    
    async def run_scheduled_task(self):
        """执行定时任务"""
        if self.is_running:
            return
        
        self.is_running = True
        self.log_message("INFO", "定时任务开始执行")
        
        try:
            # 1. 获取最新价格并保存
            market_service = MarketService(self.db)
            prices = await market_service.fetch_and_save_prices()
            
            if not prices:
                self.log_message("WARNING", "未能获取价格数据")
                return
            
            # 2. 为每个模型生成决策
            decision_service = DecisionService(self.db)
            decisions = await decision_service.make_decisions(prices)
            
            # 3. 根据决策更新持仓（简化版本，实际需要更复杂的逻辑）
            portfolio_service = PortfolioService(self.db)
            for model_name, decision_data in decisions.items():
                if decision_data and decision_data.get('action') != 'HOLD':
                    symbol = decision_data.get('symbol')
                    action = decision_data.get('action')
                    
                    if symbol and symbol in prices:
                        try:
                            # 简化：每次交易固定数量
                            quantity = 0.1  # 固定交易 0.1 个单位
                            price = prices[symbol]
                            
                            portfolio_service.simulate_trade(
                                model_name=model_name,
                                symbol=symbol,
                                action=action,
                                price=price,
                                quantity=quantity
                            )
                        except Exception as e:
                            self.log_message("ERROR", f"模型 {model_name} 交易失败: {str(e)}")
            
            self.last_run_time = datetime.now()
            self.error_count = 0
            self.log_message("INFO", "定时任务执行成功")
            
        except Exception as e:
            self.error_count += 1
            self.log_message("ERROR", f"定时任务执行失败: {str(e)}")
        finally:
            self.is_running = False

