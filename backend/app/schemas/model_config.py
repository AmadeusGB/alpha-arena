"""
模型配置 Schema
"""
from pydantic import BaseModel, field_serializer
from typing import Optional, Dict
from datetime import datetime


class ModelConfigBase(BaseModel):
    """模型配置基础模型"""
    name: str
    provider: str = 'siliconflow'
    model_id: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 200
    temperature: float = 0.1
    timeout: int = 30
    is_enabled: bool = True
    params: Optional[Dict] = {}


class ModelConfigCreate(ModelConfigBase):
    """创建模型配置"""
    pass


class ModelConfigUpdate(BaseModel):
    """更新模型配置"""
    name: Optional[str] = None
    provider: Optional[str] = None
    model_id: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    timeout: Optional[int] = None
    is_enabled: Optional[bool] = None
    params: Optional[Dict] = None


class ModelConfigResponse(ModelConfigBase):
    """模型配置响应"""
    id: int
    is_active: bool
    last_test_at: Optional[datetime] = None
    last_test_result: bool = False
    test_error: Optional[str] = None
    total_calls: int = 0
    success_calls: int = 0
    fail_calls: int = 0
    avg_response_time: float = 0.0
    created_at: datetime
    updated_at: datetime
    
    @field_serializer('created_at', 'updated_at', 'last_test_at')
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """将 datetime 序列化为 ISO 格式字符串"""
        return dt.isoformat() if dt else None
    
    class Config:
        from_attributes = True


class ModelTestRequest(BaseModel):
    """模型测试请求"""
    test_prompt: str = "测试提示词，请返回JSON格式：{\"symbol\":\"null\",\"action\":\"HOLD\",\"confidence\":0.5,\"rationale\":\"测试\"}"


class ModelTestResponse(BaseModel):
    """模型测试响应"""
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    response_time: Optional[float] = None
