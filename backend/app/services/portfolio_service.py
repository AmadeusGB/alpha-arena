"""
投资组合服务
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.config import settings as app_settings
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
                balance=app_settings.INITIAL_CAPITAL,
                total_value=app_settings.INITIAL_CAPITAL,
                initial_capital=app_settings.INITIAL_CAPITAL
            )
            self.db.add(portfolio)
            self.db.commit()
        
        return portfolio
    
    def update_portfolio_value(self, model_name: str):
        """更新账户总价值（保证金模型：总资产 = 现金 + Σ(保证金 + 未实现盈亏)）"""
        portfolio = self.get_portfolio(model_name)

        positions = self.db.query(Position).filter(
            Position.model_name == model_name,
            Position.status == "open"
        ).all()

        def unrealized(pos: Position) -> float:
            if pos.current_price is None:
                return 0.0
            if (pos.side or 'long') == 'short':
                return (pos.entry_price - pos.current_price) * pos.quantity
            return (pos.current_price - pos.entry_price) * pos.quantity

        position_value = sum((pos.margin or 0.0) + unrealized(pos) for pos in positions)

        portfolio.total_value = (portfolio.balance or 0.0) + position_value
        initial = portfolio.initial_capital or 0.0
        portfolio.total_pnl = portfolio.total_value - initial
        portfolio.total_return = ((portfolio.total_value / initial - 1) * 100) if initial else 0.0
        portfolio.updated_at = datetime.now(timezone.utc)

        self.db.commit()
    
    def get_positions(self, model_name: str, status: str = "open") -> List[Position]:
        """获取持仓"""
        query = self.db.query(Position).filter(
            Position.model_name == model_name
        )
        
        if status:
            query = query.filter(Position.status == status)
        
        return query.all()

    def update_positions_prices(
        self,
        prices: Dict[str, float],
        model_name: Optional[str] = None,
    ) -> None:
        """根据最新行情更新持仓 current_price 以及 pnl/pnl_percent。
        如果提供 model_name，则仅更新该模型；否则更新所有 open 持仓。
        """
        query = self.db.query(Position).filter(Position.status == "open")
        if model_name:
            query = query.filter(Position.model_name == model_name)
        positions = query.all()

        updated_models: set[str] = set()
        for pos in positions:
            price = prices.get(pos.symbol)
            if price and price > 0:
                pos.current_price = price
                # 多空分别计算未实现盈亏
                if (pos.side or 'long') == 'short':
                    pos.pnl = (pos.entry_price - price) * pos.quantity
                    base = pos.entry_price if pos.entry_price else 0.0
                    pos.pnl_percent = ((pos.entry_price - price) / base * 100) if base else 0.0
                else:
                    pos.pnl = (price - pos.entry_price) * pos.quantity
                    base = pos.entry_price if pos.entry_price else 0.0
                    pos.pnl_percent = ((price - pos.entry_price) / base * 100) if base else 0.0
                updated_models.add(pos.model_name)

        # 刷新各模型总资产
        for m in updated_models:
            self.update_portfolio_value(m)

        self.db.commit()

    # ===== 校验相关工具函数 =====
    def _compute_equity_margin_model(self, model_name: str) -> float:
        """计算当前权益（现金 + Σ保证金）。"""
        portfolio = self.get_portfolio(model_name)
        positions = self.db.query(Position).filter(
            Position.model_name == model_name,
            Position.status == "open"
        ).all()
        margin_sum = sum((p.margin or 0.0) for p in positions)
        return (portfolio.balance or 0.0) + margin_sum

    def _validate_open_trade(
        self,
        *,
        model_name: str,
        symbol: str,
        side: str,  # 'long' | 'short'
        notional: float,
        margin_required: float,
        fee: float,
        leverage_eff: float,
    ) -> None:
        """严格匹配 TradingSettings 的风控限制，拒绝不合规交易。"""
        from app.services.settings_service import SettingsService
        settings_service = SettingsService(self.db)
        ts = settings_service.get_settings()
        portfolio = self.get_portfolio(model_name)

        # 做空权限
        if side == 'short' and not (ts.allow_short if ts and ts.allow_short is not None else False):
            raise ValueError("做空被禁用: allow_short=false")

        # 杠杆上限
        if ts and ts.max_leverage and leverage_eff > ts.max_leverage:
            raise ValueError(f"超出最大杠杆限制: {leverage_eff} > {ts.max_leverage}")

        # 名义金额上下限
        if ts and ts.min_trade_amount and notional < ts.min_trade_amount:
            raise ValueError(f"名义金额低于最小限制: {notional:.4f} < {ts.min_trade_amount}")
        if ts and ts.max_trade_amount and notional > ts.max_trade_amount:
            raise ValueError(f"名义金额超过最大限制: {notional:.4f} > {ts.max_trade_amount}")

        # 最大持仓数
        if ts and ts.max_open_positions:
            open_count = self.db.query(Position).filter(
                Position.model_name == model_name,
                Position.status == 'open'
            ).count()
            if open_count >= ts.max_open_positions:
                raise ValueError("超过最大持仓数限制")

        # 冷却期
        if ts and ts.cooldown_minutes and ts.cooldown_minutes > 0:
            last_trade = self.db.query(Trade).filter(Trade.model_name == model_name).order_by(Trade.executed_at.desc()).first()
            if last_trade and last_trade.executed_at:
                last_exec = last_trade.executed_at
                if last_exec.tzinfo is None:
                    last_exec = last_exec.replace(tzinfo=timezone.utc)
                now_ts = datetime.now(timezone.utc)
                if now_ts - last_exec < timedelta(minutes=ts.cooldown_minutes):
                    raise ValueError("冷却期未结束，暂不可下单")

        # 最大持仓比例（分母=权益=现金+Σ保证金）
        equity = self._compute_equity_margin_model(model_name)
        if ts and ts.max_position_percent and equity > 0:
            if (margin_required / equity) > ts.max_position_percent:
                raise ValueError("超过最大持仓比例限制")

        # 现金充足性
        if (portfolio.balance or 0.0) < (margin_required + fee):
            raise ValueError("余额不足")
    
    def simulate_trade(
        self,
        model_name: str,
        symbol: str,
        action: str,
        price: float,
        quantity: float,
        *,
        direction: Optional[str] = None,
        leverage: Optional[float] = None,
        decision_id: Optional[int] = None
    ) -> Trade:
        """模拟交易"""
        portfolio = self.get_portfolio(model_name)
        
        if action == "BUY":
            existing = self.db.query(Position).filter(
                Position.model_name == model_name,
                Position.symbol == symbol,
                Position.status == "open"
            ).first()

            if existing and (existing.side or 'long') == 'short':
                # 平空（支持部分平仓）
                close_qty = min(quantity, existing.quantity)
                notional = price * close_qty
                fee = notional * 0.0005
                # 盈亏基于平仓数量
                pnl = (existing.entry_price - price) * close_qty
                # 按比例释放保证金
                release_margin = (existing.margin or 0.0) * (close_qty / existing.quantity)
                refund = release_margin + pnl - fee
                portfolio.balance += refund

                # 更新持仓
                remaining_qty = existing.quantity - close_qty
                remaining_margin = (existing.margin or 0.0) - release_margin
                if remaining_qty <= 1e-12:
                    existing.status = "closed"
                    existing.closed_at = datetime.now(timezone.utc)
                    existing.pnl = (existing.pnl or 0.0) + pnl
                    base = existing.entry_price if existing.entry_price else 0.0
                    existing.pnl_percent = (existing.pnl / (base * (existing.quantity or 1)) * 100) if (base and existing.quantity) else 0.0
                else:
                    existing.quantity = remaining_qty
                    existing.margin = remaining_margin
                    # 累计已实现不存入持仓，保持未实现为0；已实现 pnl 不再写入持仓直到完全平仓
                action_type = 'CLOSE'
            else:
                # 开多（保证金模式）- 现金校验与仓位比例控制
                notional = price * quantity
                fee = notional * 0.0005
                # 读取风控设置
                from app.services.settings_service import SettingsService
                settings_service = SettingsService(self.db)
                ts = settings_service.get_settings()
                leverage_eff = leverage or 1.0
                margin_required = notional / leverage_eff
                # 统一风控校验
                self._validate_open_trade(
                    model_name=model_name,
                    symbol=symbol,
                    side='long',
                    notional=notional,
                    margin_required=margin_required,
                    fee=fee,
                    leverage_eff=leverage_eff,
                )
                portfolio.balance -= (margin_required + fee)

                position = Position(
                    model_name=model_name,
                    symbol=symbol,
                    quantity=quantity,
                    entry_price=price,
                    current_price=price,
                    side='long',
                    leverage=leverage_eff,
                    margin=margin_required,
                    decision_id=None
                )
                self.db.add(position)
                action_type = 'OPEN_LONG'
            
        elif action == "SELL":
            # 卖出：可能是开空，或平多
            position = self.db.query(Position).filter(
                Position.model_name == model_name,
                Position.symbol == symbol,
                Position.status == "open"
            ).first()

            if position is None and (isinstance(direction, str) and direction.lower() == 'short'):
                # 开空（保证金模式）：冻结保证金
                notional = price * quantity
                fee = notional * 0.0005
                from app.services.settings_service import SettingsService
                settings_service = SettingsService(self.db)
                ts = settings_service.get_settings()
                leverage_eff = leverage or 1.0
                margin_required = notional / leverage_eff
                # 统一风控校验
                self._validate_open_trade(
                    model_name=model_name,
                    symbol=symbol,
                    side='short',
                    notional=notional,
                    margin_required=margin_required,
                    fee=fee,
                    leverage_eff=leverage_eff,
                )
                portfolio.balance -= (margin_required + fee)

                new_pos = Position(
                    model_name=model_name,
                    symbol=symbol,
                    quantity=quantity,
                    entry_price=price,
                    current_price=price,
                    side='short',
                    leverage=leverage_eff,
                    margin=margin_required,
                    decision_id=None
                )
                self.db.add(new_pos)
                action_type = 'OPEN_SHORT'
            else:
                # 平仓：根据实际方向分别处理，支持部分平仓
                if position is None:
                    raise ValueError("没有持仓")
                close_qty = min(quantity, position.quantity)
                notional = price * close_qty
                fee = notional * 0.0005
                if (position.side or 'long') == 'short':
                    pnl = (position.entry_price - price) * close_qty
                else:
                    pnl = (price - position.entry_price) * close_qty
                release_margin = (position.margin or 0.0) * (close_qty / position.quantity)
                refund = release_margin + pnl - fee
                portfolio.balance += refund

                remaining_qty = position.quantity - close_qty
                remaining_margin = (position.margin or 0.0) - release_margin
                if remaining_qty <= 1e-12:
                    position.status = "closed"
                    position.closed_at = datetime.now(timezone.utc)
                    position.current_price = price
                    position.pnl = (position.pnl or 0.0) + pnl
                    base = position.entry_price if position.entry_price else 0.0
                    position.pnl_percent = (position.pnl / (base * (position.quantity or 1)) * 100) if (base and position.quantity) else 0.0
                else:
                    position.quantity = remaining_qty
                    position.margin = remaining_margin
                    position.current_price = price
                action_type = 'CLOSE'
        
        # 记录交易（默认 completed; 若校验失败抛错不会走到这里）
        trade = Trade(
            model_name=model_name,
            symbol=symbol,
            side=action,
            direction=direction,
            leverage=leverage,
            quantity=quantity,
            price=price,
            fee=fee,
            total_amount=price * quantity,
            action_type=action_type,
            status='completed',
            feedback=None,
            decision_id=decision_id
        )
        self.db.add(trade)
        
        # 更新账户价值
        self.update_portfolio_value(model_name)
        
        self.db.commit()
        return trade
    
    def save_portfolio_history(self, model_name: str, timestamp: Optional[datetime] = None):
        """保存组合净值历史记录"""
        portfolio = self.get_portfolio(model_name)
        
        # 计算持仓市值
        positions = self.db.query(Position).filter(
            Position.model_name == model_name,
            Position.status == "open"
        ).all()
        
        # 采用保证金 + 未实现盈亏 作为持仓价值
        def unrealized(pos: Position) -> float:
            if pos.current_price is None:
                return 0.0
            if (pos.side or 'long') == 'short':
                return (pos.entry_price - pos.current_price) * pos.quantity
            return (pos.current_price - pos.entry_price) * pos.quantity

        position_value = sum((pos.margin or 0.0) + unrealized(pos) for pos in positions)
        long_exposure = sum(((pos.margin or 0.0) + unrealized(pos)) for pos in positions if (pos.side or 'long') == 'long')
        short_exposure = sum(((pos.margin or 0.0) + unrealized(pos)) for pos in positions if (pos.side or 'long') == 'short')
        total_quantity = sum(pos.quantity for pos in positions)
        # 加权平均杠杆（以名义敞口权重）
        exposure_sum = sum(((pos.current_price or 0) * pos.quantity) for pos in positions)
        avg_leverage = (sum(((pos.current_price or 0) * pos.quantity) * (pos.leverage or 1.0) for pos in positions) / exposure_sum) if exposure_sum > 0 else 1.0
        
        # 创建历史记录
        history = PortfolioHistory(
            model_name=model_name,
            timestamp=timestamp or datetime.now(timezone.utc),
            total_value=portfolio.total_value,
            balance=portfolio.balance,
            position_value=position_value,
            long_exposure=long_exposure,
            short_exposure=short_exposure,
            total_quantity=total_quantity,
            avg_leverage=avg_leverage,
            pnl=portfolio.total_pnl,
            pnl_percent=portfolio.total_return
        )
        
        self.db.add(history)
        self.db.commit()
        
        return history

    def rebuild_history(self, model_name: Optional[str] = None) -> dict:
        """根据交易记录重放并校正持仓、账户与净值历史。
        - 按模型重置账户为初始资金
        - 清空 positions 与 portfolio_history
        - 按时间顺序重放 trades，采用保证金结算逻辑
        - 在每笔交易时间点写入历史
        """
        from app.models.portfolio import Trade, Position, ModelPortfolio

        models_to_process = []
        if model_name:
            models_to_process = [model_name]
        else:
            # 以有账户或有交易的模型为准
            model_names = set(m.model_name for m in self.db.query(ModelPortfolio).all())
            trade_models = set(t.model_name for t in self.db.query(Trade).all())
            models_to_process = list(model_names.union(trade_models))

        result = {m: {"trades": 0, "histories": 0} for m in models_to_process}

        for m in models_to_process:
            # 重置账户
            portfolio = self.get_portfolio(m)
            initial = portfolio.initial_capital or 10000.0
            portfolio.balance = initial
            portfolio.total_value = initial
            portfolio.total_pnl = 0.0
            portfolio.total_return = 0.0

            # 清空持仓与历史
            self.db.query(Position).filter(Position.model_name == m).delete(synchronize_session=False)
            self.db.query(PortfolioHistory).filter(PortfolioHistory.model_name == m).delete(synchronize_session=False)
            self.db.commit()

            # 获取交易并按时间排序
            trades = self.db.query(Trade).filter(Trade.model_name == m).order_by(Trade.executed_at.asc()).all()
            for t in trades:
                # 将交易应用到账户（不新增交易记录）
                self._apply_trade_replay(m, t)
                # 以该交易时间点写入历史
                self.save_portfolio_history(m, t.executed_at or datetime.now())
                result[m]["trades"] += 1
                result[m]["histories"] += 1

            # 最终快照
            self.save_portfolio_history(m)
            result[m]["histories"] += 1

        self.db.commit()
        return result

    def _apply_trade_replay(self, model_name: str, t) -> None:
        """重放一笔交易（不写入 Trade），沿用保证金结算逻辑。"""
        from app.models.portfolio import Position
        portfolio = self.get_portfolio(model_name)

        action = t.side
        price = t.price
        quantity = t.quantity
        direction = (t.direction or '').lower() if isinstance(t.direction, str) else None
        leverage = t.leverage or 1.0

        if action == "BUY":
            position = self.db.query(Position).filter(
                Position.model_name == model_name,
                Position.symbol == t.symbol,
                Position.status == "open"
            ).first()

            if position and (position.side or 'long') == 'short':
                # 平空
                notional = price * quantity
                fee = notional * 0.0005
                pnl = (position.entry_price - price) * quantity
                refund = (position.margin or 0.0) + pnl - fee
                portfolio.balance += refund
                position.status = "closed"
                position.closed_at = t.executed_at or datetime.now(timezone.utc)
                position.current_price = price
                position.pnl = pnl
            else:
                # 开多
                notional = price * quantity
                fee = notional * 0.0005
                margin_required = notional / leverage
                portfolio.balance -= (margin_required + fee)
                new_pos = Position(
                    model_name=model_name,
                    symbol=t.symbol,
                    quantity=quantity,
                    entry_price=price,
                    current_price=price,
                    side='long',
                    leverage=leverage,
                    margin=margin_required,
                    opened_at=t.executed_at or datetime.now(timezone.utc)
                )
                self.db.add(new_pos)

        elif action == "SELL":
            position = self.db.query(Position).filter(
                Position.model_name == model_name,
                Position.symbol == t.symbol,
                Position.status == "open"
            ).first()
            if position is None and direction == 'short':
                # 开空
                notional = price * quantity
                fee = notional * 0.0005
                margin_required = notional / leverage
                portfolio.balance -= (margin_required + fee)
                new_pos = Position(
                    model_name=model_name,
                    symbol=t.symbol,
                    quantity=quantity,
                    entry_price=price,
                    current_price=price,
                    side='short',
                    leverage=leverage,
                    margin=margin_required,
                    opened_at=t.executed_at or datetime.now()
                )
                self.db.add(new_pos)
            else:
                # 平多或平空（重放时也支持部分平仓）
                if position is None:
                    return
                close_qty = min(t.quantity or 0.0, position.quantity)
                notional = price * close_qty
                fee = notional * 0.0005
                if (position.side or 'long') == 'short':
                    pnl = (position.entry_price - price) * close_qty
                else:
                    pnl = (price - position.entry_price) * close_qty
                release_margin = (position.margin or 0.0) * (close_qty / position.quantity)
                refund = release_margin + pnl - fee
                portfolio.balance += refund

                remaining_qty = position.quantity - close_qty
                remaining_margin = (position.margin or 0.0) - release_margin
                if remaining_qty <= 1e-12:
                    position.status = "closed"
                    position.closed_at = t.executed_at or datetime.now()
                    position.current_price = price
                    position.pnl = (position.pnl or 0.0) + pnl
                else:
                    position.quantity = remaining_qty
                    position.margin = remaining_margin
                    position.current_price = price

        # 更新账户总资产
        self.update_portfolio_value(model_name)

    def analyze_trades(self, model_name: str) -> dict:
        """对指定模型的交易历史进行计算与解释（只读分析，不修改数据库）。
        输出字段遵循当前保证金结算逻辑，包含每笔交易的名义金额、保证金、手续费、实收/支现金以及累计权益。
        """
        from app.models.portfolio import Trade
        from app.services.settings_service import SettingsService

        # 手续费率采用系统设置的 taker_fee，若为空则回退 0.0005
        settings = SettingsService(self.db).get_settings()
        fee_rate = settings.taker_fee if settings and settings.taker_fee is not None else 0.0005

        # 初始资金
        portfolio = self.get_portfolio(model_name)
        initial = portfolio.initial_capital or 10000.0

        # 读取交易
        trades = self.db.query(Trade).filter(Trade.model_name == model_name).order_by(Trade.executed_at.asc()).all()

        # 运行时状态
        cash = initial
        open_positions = {}  # key: symbol -> {side, entry_price, qty, leverage, margin}
        items = []
        total_fees = 0.0
        realized_pnl = 0.0

        def unrealized_sum() -> float:
            # 分析阶段无行情流入，使用开仓价作为当前价，未实现盈亏视为 0
            # 这样权益变化只受手续费与已实现盈亏影响
            return sum(p.get('margin', 0.0) for p in open_positions.values())

        for t in trades:
            notional = (t.price or 0.0) * (t.quantity or 0.0)
            fee = notional * fee_rate
            total_fees += fee
            leverage_eff = t.leverage or 1.0
            margin = notional / leverage_eff if leverage_eff else notional
            entry_price = t.price or 0.0
            qty = t.quantity or 0.0

            record = {
                'time': (t.executed_at.isoformat() if t.executed_at else None),
                'symbol': t.symbol,
                'action': t.side,
                'action_type': t.action_type,
                'direction': t.direction,
                'price': t.price,
                'quantity': t.quantity,
                'leverage': leverage_eff,
                'notional': notional,
                'fee': fee
            }

            if t.action_type in ('OPEN_LONG', 'OPEN_SHORT'):
                # 冻结保证金与手续费，现金减少
                cash -= (margin + fee)
                open_positions[t.symbol] = {
                    'side': 'short' if t.action_type == 'OPEN_SHORT' else 'long',
                    'entry_price': entry_price,
                    'qty': qty,
                    'leverage': leverage_eff,
                    'margin': margin
                }
                record['cash_delta'] = -(margin + fee)
                record['pnl'] = 0.0
            else:
                # 平仓
                pos = open_positions.get(t.symbol)
                if pos:
                    if pos['side'] == 'short':
                        pnl = (pos['entry_price'] - entry_price) * qty
                    else:
                        pnl = (entry_price - pos['entry_price']) * qty
                    refund = pos.get('margin', 0.0) + pnl - fee
                    cash += refund
                    realized_pnl += pnl
                    # 移除持仓（假定全量平仓）
                    del open_positions[t.symbol]
                    record['cash_delta'] = refund
                    record['pnl'] = pnl
                else:
                    # 无匹配持仓，标记异常
                    record['cash_delta'] = 0.0
                    record['pnl'] = 0.0
                    record['warning'] = 'no_matching_position'

            equity = cash + unrealized_sum()
            record['cash_after'] = cash
            record['equity_after'] = equity
            items.append(record)

        result = {
            'model_name': model_name,
            'initial_capital': initial,
            'fee_rate': fee_rate,
            'formulas': [
                'notional = price * quantity',
                'fee = notional * fee_rate',
                'margin = notional / leverage',
                'close_long: pnl = (sell_price - entry_price) * quantity',
                'close_short: pnl = (entry_price - buy_price) * quantity',
                'cash_after_open = cash_before - (margin + fee)',
                'cash_after_close = cash_before + (margin + pnl - fee)',
                'equity = cash + Σ(margin + unrealized_pnl); 在分析阶段 unrealized_pnl 取 0，equity 仅受手续费与已实现盈亏影响'
            ],
            'summary': {
                'num_trades': len(trades),
                'total_fees': total_fees,
                'realized_pnl': realized_pnl,
                'final_cash': cash,
                'final_equity': cash + unrealized_sum()
            },
            'items': items
        }

        return result
    
    def get_portfolio_history(self, model_name: str, limit: int = 1000) -> List[PortfolioHistory]:
        """获取组合净值历史"""
        return self.db.query(PortfolioHistory).filter(
            PortfolioHistory.model_name == model_name
        ).order_by(PortfolioHistory.timestamp.desc()).limit(limit).all()

