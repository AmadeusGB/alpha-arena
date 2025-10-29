"""
任务调度服务
"""
import asyncio
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.services.market_service import MarketService
from app.services.decision_service import DecisionService
from app.services.portfolio_service import PortfolioService
from app.models.portfolio import SystemLog
from app.models.portfolio import Trade
from app.models.market import MarketPrice
from app.core.technical_indicators import calculate_basic_indicators


class SchedulerService:
    """任务调度服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.is_running = False
        self.is_saving_history = False
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
            
            # 1.5 计算技术指标
            indicators = {}
            symbols = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'BNBUSDT', 'SOLUSDT']
            for symbol in symbols:
                # 获取历史价格数据
                historical_prices = self.db.query(MarketPrice).filter(
                    MarketPrice.symbol == symbol
                ).order_by(MarketPrice.timestamp.desc()).limit(50).all()
                
                if historical_prices:
                    # 提取价格列表（从旧到新）
                    price_list = [p.price for p in reversed(historical_prices)]
                    # 计算指标
                    indicators[symbol] = calculate_basic_indicators(price_list)
            
            # 2. 获取交易设置
            from app.services.settings_service import SettingsService
            settings_service = SettingsService(self.db)
            trading_settings = settings_service.get_settings()
            trading_settings_dict = {
                'max_position_percent': trading_settings.max_position_percent,
                'stop_loss_min': trading_settings.stop_loss_min,
                'stop_loss_max': trading_settings.stop_loss_max,
                'take_profit_min': trading_settings.take_profit_min,
                'take_profit_max': trading_settings.take_profit_max,
                'min_confidence': trading_settings.min_confidence,
                'max_open_positions': trading_settings.max_open_positions,
                'max_drawdown': trading_settings.max_drawdown
            } if trading_settings else None
            
            # 3. 使用最新价格刷新所有未平仓持仓的 current_price / pnl
            from app.models.portfolio import Position
            from app.models.model_config import ModelConfig
            portfolio_service = PortfolioService(self.db)
            try:
                portfolio_service.update_positions_prices(prices)
            except Exception as e:
                self.log_message("ERROR", f"更新持仓现价失败: {str(e)}")
            
            # 从数据库获取所有启用的模型
            enabled_models = self.db.query(ModelConfig).filter(
                ModelConfig.is_enabled == True,
                ModelConfig.is_active == True
            ).all()
            
            model_positions = {}
            for model_config in enabled_models:
                model_name = model_config.name
                positions = portfolio_service.get_positions(model_name, status='open')
                model_positions[model_name] = [
                    {
                        'symbol': p.symbol,
                        'quantity': p.quantity,
                        'entry_price': p.entry_price,
                        'current_price': p.current_price or p.entry_price,
                        'pnl': p.pnl,
                        'pnl_percent': p.pnl_percent
                    }
                    for p in positions
                ]
            
            # 4. 为每个模型生成决策
            decision_service = DecisionService(self.db)
            decisions = await decision_service.make_decisions(
                prices, 
                indicators,
                trading_settings_dict,
                model_positions
            )
            
            # 5. 根据决策更新持仓（简化版本，实际需要更复杂的逻辑）
            for model_name, decision_data in decisions.items():
                if decision_data and decision_data.get('action') != 'HOLD' or (isinstance(decision_data.get('trades'), list) and len(decision_data.get('trades'))>0):
                    decision_id = decision_data.get('decision_id')
                    # 组装要执行的操作列表（兼容单笔trade与多笔trades）
                    ops = []
                    if isinstance(decision_data.get('trades'), list) and len(decision_data.get('trades'))>0:
                        for it in decision_data['trades']:
                            if not isinstance(it, dict):
                                continue
                            if not it.get('symbol') or not it.get('action'):
                                continue
                            ops.append(it)
                    else:
                        symbol = decision_data.get('symbol')
                        action = decision_data.get('action')
                        trade = decision_data.get('trade') if isinstance(decision_data.get('trade'), dict) else None
                        if symbol and action and trade:
                            ops.append({
                                'symbol': symbol,
                                'action': action,
                                'quantity': trade.get('quantity'),
                                'leverage': trade.get('leverage'),
                                'direction': trade.get('direction'),
                                'entry_price': trade.get('entry_price')
                            })
                    
                    for op in ops:
                        symbol = op.get('symbol')
                        action = op.get('action')
                        if not symbol or symbol not in prices:
                            continue
                        try:
                            price = op.get('entry_price') if isinstance(op.get('entry_price'), (int, float)) else prices[symbol]
                            quantity = op.get('quantity') if isinstance(op.get('quantity'), (int, float)) else 0.1
                            direction = op.get('direction')
                            leverage = op.get('leverage')

                            portfolio_service.simulate_trade(
                                model_name=model_name,
                                symbol=symbol,
                                action=action,
                                price=price,
                                quantity=quantity,
                                direction=direction,
                                leverage=leverage,
                                decision_id=decision_id
                            )
                            # 成功：将关联决策标记为 completed
                            try:
                                from app.models.decision import Decision
                                if decision_id:
                                    d = self.db.query(Decision).filter(Decision.id==decision_id).first()
                                else:
                                    d = self.db.query(Decision).filter(Decision.model_name==model_name).order_by(Decision.timestamp.desc()).first()
                                if d:
                                    d.status = 'completed'
                                    d.feedback = None
                                    self.db.commit()
                            except Exception:
                                self.db.rollback()
                        except Exception as e:
                            self.log_message("ERROR", f"模型 {model_name} 交易失败: {str(e)}")
                            # 将失败写入 Trade，供前端展示
                            try:
                                failed_trade = Trade(
                                    model_name=model_name,
                                    symbol=symbol,
                                    side=action,
                                    direction=op.get('direction'),
                                    leverage=op.get('leverage'),
                                    quantity=op.get('quantity') if isinstance(op.get('quantity'), (int, float)) else 0.0,
                                    price=op.get('entry_price') if isinstance(op.get('entry_price'), (int, float)) else 0.0,
                                    fee=0.0,
                                    total_amount=((price or 0.0) * (quantity or 0.0)) if isinstance(price, (int, float)) and isinstance(quantity, (int, float)) else 0.0,
                                    decision_id=decision_id,
                                    status='failed',
                                    feedback=str(e)
                                )
                                self.db.add(failed_trade)
                                self.db.commit()
                                # 同时将最新决策标记为 failed
                                try:
                                    from app.models.decision import Decision
                                    if decision_id:
                                        d = self.db.query(Decision).filter(Decision.id==decision_id).first()
                                    else:
                                        d = self.db.query(Decision).filter(Decision.model_name==model_name).order_by(Decision.timestamp.desc()).first()
                                    if d:
                                        d.status = 'failed'
                                        d.feedback = str(e)
                                        self.db.commit()
                                except Exception:
                                    self.db.rollback()
                            except Exception:
                                self.db.rollback()
            
            self.last_run_time = datetime.now(timezone.utc)
            self.error_count = 0
            self.log_message("INFO", "定时任务执行成功")
            
        except Exception as e:
            self.error_count += 1
            self.log_message("ERROR", f"定时任务执行失败: {str(e)}")
        finally:
            self.is_running = False
    
    async def run_save_history_task(self):
        """执行保存净值历史任务"""
        if self.is_saving_history:
            return
        
        self.is_saving_history = True
        self.log_message("INFO", "开始保存净值历史")
        
        try:
            portfolio_service = PortfolioService(self.db)
            
            # 获取所有模型
            from app.models.portfolio import ModelPortfolio
            models = self.db.query(ModelPortfolio).filter(ModelPortfolio.is_active == 'active').all()
            
            for model in models:
                try:
                    portfolio_service.save_portfolio_history(model.model_name)
                except Exception as e:
                    self.log_message("ERROR", f"模型 {model.model_name} 保存历史失败: {str(e)}")
            
            self.log_message("INFO", "净值历史保存完成")
            
        except Exception as e:
            self.log_message("ERROR", f"保存净值历史失败: {str(e)}")
        finally:
            self.is_saving_history = False

