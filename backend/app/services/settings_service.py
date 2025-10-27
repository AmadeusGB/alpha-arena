"""
设置服务
"""
from sqlalchemy.orm import Session
from app.models.settings import TradingSettings
from app.schemas.settings import TradingSettingsCreate, TradingSettingsUpdate
from app.config import settings as app_settings


class SettingsService:
    """设置服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_settings(self, name: str = "default") -> TradingSettings:
        """获取设置"""
        settings = self.db.query(TradingSettings).filter(
            TradingSettings.name == name
        ).first()
        
        if not settings:
            # 使用默认配置创建
            settings = self.create_default_settings(name)
        
        return settings
    
    def create_default_settings(self, name: str = "default") -> TradingSettings:
        """创建默认设置"""
        settings = TradingSettings(
            name=name,
            maker_fee=app_settings.TRADING_FEE_MAKER,
            taker_fee=app_settings.TRADING_FEE_TAKER,
            slippage=app_settings.SLIPPAGE_TOLERANCE,
            max_leverage=app_settings.MAX_LEVERAGE,
            allow_short=app_settings.ALLOW_SHORT,
            min_position=app_settings.MIN_POSITION_SIZE,
            max_position=app_settings.MAX_POSITION_SIZE,
            position_unit=app_settings.POSITION_SIZE_UNIT,
            stop_loss_min=app_settings.STOP_LOSS_MIN,
            stop_loss_max=app_settings.STOP_LOSS_MAX,
            take_profit_min=app_settings.TAKE_PROFIT_MIN,
            take_profit_max=app_settings.TAKE_PROFIT_MAX,
            max_position_percent=app_settings.MAX_POSITION_PERCENT,
            max_drawdown=app_settings.MAX_DRAWDOWN_LIMIT,
            min_confidence=app_settings.MIN_CONFIDENCE_THRESHOLD,
            max_open_positions=app_settings.MAX_OPEN_POSITIONS,
            cooldown_minutes=app_settings.COOLDOWN_PERIOD_MINUTES,
            min_trade_amount=app_settings.MIN_TRADE_AMOUNT,
            max_trade_amount=app_settings.MAX_TRADE_AMOUNT,
        )
        self.db.add(settings)
        self.db.commit()
        return settings
    
    def update_settings(self, name: str, settings_update: TradingSettingsUpdate) -> TradingSettings:
        """更新设置"""
        settings = self.get_settings(name)
        
        # 更新所有字段
        for key, value in settings_update.model_dump(exclude_unset=True).items():
            setattr(settings, key, value)
        
        self.db.commit()
        return settings
    
    def reset_to_default(self, name: str = "default") -> TradingSettings:
        """重置为默认设置"""
        settings = self.db.query(TradingSettings).filter(
            TradingSettings.name == name
        ).first()
        
        if settings:
            self.db.delete(settings)
            self.db.commit()
        
        return self.create_default_settings(name)
