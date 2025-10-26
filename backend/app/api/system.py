"""
系统管理 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.scheduler_service import SchedulerService
from app.config import settings

router = APIRouter()

# 全局调度器服务实例
scheduler_instance = None


def get_scheduler_service(db: Session = Depends(get_db)) -> SchedulerService:
    """获取调度器服务"""
    global scheduler_instance
    if scheduler_instance is None:
        scheduler_instance = SchedulerService(db)
    return scheduler_instance


@router.get("/status")
async def get_system_status(
    db: Session = Depends(get_db),
    scheduler: SchedulerService = Depends(get_scheduler_service)
):
    """获取系统状态"""
    from app.models.portfolio import SystemLog
    
    # 获取最新日志
    latest_log = db.query(SystemLog).order_by(SystemLog.timestamp.desc()).first()
    
    return {
        "scheduler_running": scheduler.is_running,
        "last_run_time": scheduler.last_run_time.isoformat() if scheduler.last_run_time else None,
        "error_count": scheduler.error_count,
        "latest_log": latest_log.message if latest_log else None,
        "database_connected": True
    }


@router.post("/scheduler/start")
async def start_scheduler(
    db: Session = Depends(get_db),
    scheduler: SchedulerService = Depends(get_scheduler_service)
):
    """启动定时任务"""
    import asyncio
    
    if scheduler.is_running:
        return {"message": "调度器已在运行中"}
    
    # 在后台运行一次
    asyncio.create_task(scheduler.run_scheduled_task())
    
    return {"message": "定时任务已启动"}


@router.post("/scheduler/stop")
async def stop_scheduler(
    scheduler: SchedulerService = Depends(get_scheduler_service)
):
    """停止定时任务"""
    scheduler.is_running = False
    return {"message": "定时任务已停止"}


@router.get("/logs")
async def get_logs(
    level: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取系统日志"""
    from app.models.portfolio import SystemLog
    
    query = db.query(SystemLog)
    
    if level:
        query = query.filter(SystemLog.level == level)
    
    logs = query.order_by(SystemLog.timestamp.desc()).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "level": log.level,
            "module": log.module,
            "message": log.message,
            "timestamp": log.timestamp.isoformat()
        }
        for log in logs
    ]

