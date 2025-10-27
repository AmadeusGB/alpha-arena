"""
FastAPI 主应用
"""
import os
import atexit
from pathlib import Path
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.config import settings as app_settings
from app.database import SessionLocal
from app.services.scheduler_service import SchedulerService

# 确保加载环境变量
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)
# 同时也从当前目录加载
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import get_db
from app.api import market, decisions, portfolios, positions, system, settings as settings_api, models

app = FastAPI(
    title="Alpha Arena API",
    description="AI 交易决策系统 API",
    version="0.1.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(market.router, prefix=f"{app_settings.API_V1_PREFIX}/market", tags=["market"])
app.include_router(decisions.router, prefix=f"{app_settings.API_V1_PREFIX}/decisions", tags=["decisions"])
app.include_router(portfolios.router, prefix=f"{app_settings.API_V1_PREFIX}/portfolios", tags=["portfolios"])
app.include_router(positions.router, prefix=f"{app_settings.API_V1_PREFIX}/positions", tags=["positions"])
app.include_router(system.router, prefix=f"{app_settings.API_V1_PREFIX}/system", tags=["system"])
app.include_router(settings_api.router, prefix=f"{app_settings.API_V1_PREFIX}/settings", tags=["settings"])
app.include_router(models.router, prefix=f"{app_settings.API_V1_PREFIX}/models", tags=["models"])


# 定时任务调度器
scheduler = BackgroundScheduler()

def run_trading_task():
    """执行交易任务"""
    db = SessionLocal()
    try:
        service = SchedulerService(db)
        import asyncio
        asyncio.run(service.run_scheduled_task())
    except Exception as e:
        print(f"❌ 交易任务执行出错: {e}")
    finally:
        db.close()


def run_save_history_task():
    """执行保存净值历史任务"""
    db = SessionLocal()
    try:
        service = SchedulerService(db)
        import asyncio
        asyncio.run(service.run_save_history_task())
    except Exception as e:
        print(f"❌ 保存历史任务执行出错: {e}")
    finally:
        db.close()


# 启动调度器（如果启用）
if app_settings.SCHEDULER_ENABLED:
    # 任务1: 交易决策任务 - 每30秒执行一次
    import datetime
    scheduler.add_job(
        run_trading_task,
        trigger=IntervalTrigger(seconds=30),
        id='trading_task',
        name='交易决策任务',
        replace_existing=True
    )
    
    # 任务2: 保存净值历史任务 - 每30秒执行一次
    scheduler.add_job(
        run_save_history_task,
        trigger=IntervalTrigger(seconds=60),
        id='save_history_task',
        name='保存净值历史任务',
        replace_existing=True
    )
    
    scheduler.start()
    print(f"✅ 定时任务调度器已启动:")
    print(f"   - 交易决策任务: 每 30 秒执行一次")
    print(f"   - 保存净值历史任务: 每 30 秒执行一次")
    
    # 注册关闭钩子
    atexit.register(lambda: scheduler.shutdown())


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的处理"""
    if scheduler.running:
        scheduler.shutdown()


@app.get("/")
async def root():
    """根路径"""
    return {"message": "Alpha Arena API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

