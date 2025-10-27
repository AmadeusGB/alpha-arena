"""
投资组合服务
"""
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from app.models.portfolio import ModelPortfolio, Position, Trade, PortfolioHistory


class PortfolioService:
    """投资组合服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_portfolio(self, model_name: str) -> ModelPortfolio:
        """获取模型账户"""
        portfolio = self.db.query(ModelPortfolio).filter(
            ModelPortfolio.model_name == model_name
        ).first()
        
        if not portfolio:
            # 创建新账户
            portfolio = ModelPortfolio(
                model_name=model_name,
                balance=10000.0,
                total_value=10000.0,
                initial_capital=10000.0
            )
            self.db.add(portfolio)
            self.db.commit()
        
        return portfolio
    
    def update_portfolio_value(self, model_name: str):
        """更新账户总价值"""
        portfolio = self.get_portfolio(model_name)
        
        # 计算持仓市值
        positions = self.db.query(Position).filter(
            Position.model_name == model_name,
            Position.status == "open"
        ).all()
        
        position_value = sum(pos.current_price * pos.quantity for pos in positions if pos.current_price)
        
        # 更新总资产
        portfolio.total_value = portfolio.balance + position_value
        portfolio.total_pnl = portfolio.total_value - portfolio.initial_capital
        portfolio.total_return = (portfolio.total_value / portfolio.initial_capital - 1) * 100
        
        # 更新今日盈亏
        # TODO: 计算今日盈亏
        portfolio.updated_at = datetime.now()
        
        self.db.commit()
    
    def get_positions(self, model_name: str, status: str = "open") -> List[Position]:
        """获取持仓"""
        query = self.db.query(Position).filter(
            Position.model_name == model_name
        )
        
        if status:
            query = query.filter(Position.status == status)
        
        return query.all()
    
    def simulate_trade(
        self,
        model_name: str,
        symbol: str,
        action: str,
        price: float,
        quantity: float
    ) -> Trade:
        """模拟交易"""
        portfolio = self.get_portfolio(model_name)
        
        if action == "BUY":
            # 买入
            cost = price * quantity
            fee = cost * 0.0005  # 0.05% 手续费
            
            if portfolio.balance < (cost + fee):
                raise ValueError("余额不足")
            
            # 更新余额
            portfolio.balance -= (cost + fee)
            
            # 创建持仓
            position = Position(
                model_name=model_name,
                symbol=symbol,
                quantity=quantity,
                entry_price=price,
                current_price=price
            )
            self.db.add(position)
            
        elif action == "SELL":
            # 卖出
            positions = self.db.query(Position).filter(
                Position.model_name == model_name,
                Position.symbol == symbol,
                Position.status == "open"
            ).all()
            
            if not positions:
                raise ValueError("没有持仓")
            
            # 取第一个持仓
            position = positions[0]
            
            revenue = price * quantity
            fee = revenue * 0.0005
            
            # 更新余额
            portfolio.balance += (revenue - fee)
            
            # 更新持仓状态
            position.status = "closed"
            position.closed_at = datetime.now()
            position.pnl = (price - position.entry_price) * quantity
            position.pnl_percent = ((price - position.entry_price) / position.entry_price) * 100
        
        # 记录交易
        trade = Trade(
            model_name=model_name,
            symbol=symbol,
            side=action,
            quantity=quantity,
            price=price,
            fee=fee,
            total_amount=price * quantity
        )
        self.db.add(trade)
        
        # 更新账户价值
        self.update_portfolio_value(model_name)
        
        self.db.commit()
        return trade
    
    def save_portfolio_history(self, model_name: str):
        """保存组合净值历史记录"""
        portfolio = self.get_portfolio(model_name)
        
        # 计算持仓市值
        positions = self.db.query(Position).filter(
            Position.model_name == model_name,
            Position.status == "open"
        ).all()
        
        position_value = sum(pos.current_price * pos.quantity for pos in positions if pos.current_price)
        
        # 创建历史记录
        history = PortfolioHistory(
            model_name=model_name,
            timestamp=datetime.now(),
            total_value=portfolio.total_value,
            balance=portfolio.balance,
            position_value=position_value,
            pnl=portfolio.total_pnl,
            pnl_percent=portfolio.total_return
        )
        
        self.db.add(history)
        self.db.commit()
        
        return history
    
    def get_portfolio_history(self, model_name: str, limit: int = 1000) -> List[PortfolioHistory]:
        """获取组合净值历史"""
        return self.db.query(PortfolioHistory).filter(
            PortfolioHistory.model_name == model_name
        ).order_by(PortfolioHistory.timestamp.desc()).limit(limit).all()

