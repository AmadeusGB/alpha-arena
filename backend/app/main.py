"""
FastAPI 主应用
"""
import os
import atexit
from pathlib import Path
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.config import settings
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
from app.api import market, decisions, portfolios, positions, system

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
app.include_router(market.router, prefix=f"{settings.API_V1_PREFIX}/market", tags=["market"])
app.include_router(decisions.router, prefix=f"{settings.API_V1_PREFIX}/decisions", tags=["decisions"])
app.include_router(portfolios.router, prefix=f"{settings.API_V1_PREFIX}/portfolios", tags=["portfolios"])
app.include_router(positions.router, prefix=f"{settings.API_V1_PREFIX}/positions", tags=["positions"])
app.include_router(system.router, prefix=f"{settings.API_V1_PREFIX}/system", tags=["system"])


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
        print(f"❌ 定时任务执行出错: {e}")
    finally:
        db.close()


# 启动调度器（如果启用）
if settings.SCHEDULER_ENABLED:
    scheduler.add_job(
        run_trading_task,
        trigger=IntervalTrigger(minutes=settings.SCHEDULER_INTERVAL_MINUTES),
        id='trading_task',
        name='定时交易任务',
        replace_existing=True
    )
    scheduler.start()
    print(f"✅ 定时任务调度器已启动 (每 {settings.SCHEDULER_INTERVAL_MINUTES} 分钟执行一次)")
    
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

