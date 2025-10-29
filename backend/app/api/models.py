"""
模型配置 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.model_config_service import ModelConfigService
from app.schemas.model_config import (
    ModelConfigCreate, ModelConfigUpdate, ModelConfigResponse,
    ModelTestRequest, ModelTestResponse
)

router = APIRouter()


@router.get("/", response_model=List[ModelConfigResponse])
async def get_all_models(db: Session = Depends(get_db)):
    """获取所有模型配置"""
    service = ModelConfigService(db)
    models = service.get_all_models()
    return models


@router.get("/{model_id}", response_model=ModelConfigResponse)
async def get_model(model_id: int, db: Session = Depends(get_db)):
    """获取单个模型配置"""
    service = ModelConfigService(db)
    model = service.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.post("/", response_model=ModelConfigResponse)
async def create_model(model_data: ModelConfigCreate, db: Session = Depends(get_db)):
    """创建模型配置"""
    service = ModelConfigService(db)
    
    # 检查名称是否已存在
    existing = service.get_model_by_name(model_data.name)
    if existing:
        raise HTTPException(status_code=400, detail="Model name already exists")
    
    try:
        model = service.create_model(model_data)
        return model
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{model_id}", response_model=ModelConfigResponse)
async def update_model(
    model_id: int,
    model_data: ModelConfigUpdate,
    db: Session = Depends(get_db)
):
    """更新模型配置"""
    service = ModelConfigService(db)
    try:
        model = service.update_model(model_id, model_data)
        return model
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{model_id}")
async def delete_model(model_id: int, db: Session = Depends(get_db)):
    """删除模型配置"""
    service = ModelConfigService(db)
    success = service.delete_model(model_id)
    if not success:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"message": "Model deleted successfully"}


@router.post("/{model_id}/enable", response_model=ModelConfigResponse)
async def enable_model(model_id: int, db: Session = Depends(get_db)):
    """启用模型"""
    service = ModelConfigService(db)
    try:
        model = service.enable_model(model_id)
        return model
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{model_id}/disable", response_model=ModelConfigResponse)
async def disable_model(model_id: int, db: Session = Depends(get_db)):
    """禁用模型"""
    service = ModelConfigService(db)
    try:
        model = service.disable_model(model_id)
        return model
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{model_id}/test", response_model=ModelTestResponse)
async def test_model(
    model_id: int,
    test_request: ModelTestRequest,
    db: Session = Depends(get_db)
):
    """测试模型"""
    service = ModelConfigService(db)
    try:
        result = service.test_model(model_id, test_request.test_prompt)
        return ModelTestResponse(
            success=result['success'],
            response=result.get('response'),
            error=result.get('error'),
            response_time=result.get('response_time')
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        return ModelTestResponse(
            success=False,
            error=str(e)
        )
