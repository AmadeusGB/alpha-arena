"""
设置 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.settings_service import SettingsService
from app.schemas.settings import TradingSettingsResponse, TradingSettingsUpdate
from app.config import settings

router = APIRouter()


@router.get("/trading", response_model=TradingSettingsResponse)
async def get_trading_settings(
    name: str = "default",
    db: Session = Depends(get_db)
):
    """获取交易设置"""
    service = SettingsService(db)
    settings_obj = service.get_settings(name)
    return settings_obj


@router.put("/trading", response_model=TradingSettingsResponse)
async def update_trading_settings(
    settings_update: TradingSettingsUpdate,
    name: str = "default",
    db: Session = Depends(get_db)
):
    """更新交易设置"""
    service = SettingsService(db)
    updated_settings = service.update_settings(name, settings_update)
    return updated_settings


@router.post("/trading/reset", response_model=TradingSettingsResponse)
async def reset_trading_settings(
    name: str = "default",
    db: Session = Depends(get_db)
):
    """重置交易设置"""
    service = SettingsService(db)
    reset_settings = service.reset_to_default(name)
    return reset_settings


@router.get("/system")
async def get_system_settings():
    """获取系统设置"""
    return {
        "scheduler_enabled": settings.SCHEDULER_ENABLED,
        "scheduler_interval_minutes": settings.SCHEDULER_INTERVAL_MINUTES,
        "initial_capital": settings.INITIAL_CAPITAL,
        "trading_pairs": settings.TRADING_PAIRS,
    }
