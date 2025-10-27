"""
模型配置服务
"""
import os
import time
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.model_config import ModelConfig
from app.schemas.model_config import ModelConfigCreate, ModelConfigUpdate
from app.core.adapters.silicon_adapter import SiliconAdapter
from app.config import settings as app_settings


class ModelConfigService:
    """模型配置服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_models(self):
        """获取所有模型配置"""
        return self.db.query(ModelConfig).all()
    
    def get_model(self, model_id: int):
        """获取单个模型配置"""
        return self.db.query(ModelConfig).filter(ModelConfig.id == model_id).first()
    
    def get_model_by_name(self, name: str):
        """根据名称获取模型配置"""
        return self.db.query(ModelConfig).filter(ModelConfig.name == name).first()
    
    def create_model(self, model_data: ModelConfigCreate) -> ModelConfig:
        """创建模型配置"""
        # 如果API密钥为空，使用环境变量中的默认密钥
        api_key = model_data.api_key or app_settings.SILICONFLOW_API_KEY
        base_url = model_data.base_url or app_settings.SILICONFLOW_BASE_URL
        
        model = ModelConfig(
            name=model_data.name,
            provider=model_data.provider,
            model_id=model_data.model_id,
            api_key=api_key,
            base_url=base_url,
            max_tokens=model_data.max_tokens,
            temperature=model_data.temperature,
            timeout=model_data.timeout,
            is_enabled=model_data.is_enabled,
            params=model_data.params or {}
        )
        
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model
    
    def update_model(self, model_id: int, model_data: ModelConfigUpdate) -> ModelConfig:
        """更新模型配置"""
        model = self.get_model(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        # 更新字段
        for key, value in model_data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(model, key, value)
        
        self.db.commit()
        return model
    
    def delete_model(self, model_id: int) -> bool:
        """删除模型配置"""
        model = self.get_model(model_id)
        if not model:
            return False
        
        self.db.delete(model)
        self.db.commit()
        return True
    
    def enable_model(self, model_id: int) -> ModelConfig:
        """启用模型"""
        model = self.get_model(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        model.is_enabled = True
        self.db.commit()
        return model
    
    def disable_model(self, model_id: int) -> ModelConfig:
        """禁用模型"""
        model = self.get_model(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        model.is_enabled = False
        self.db.commit()
        return model
    
    def test_model(self, model_id: int, test_prompt: str = None) -> dict:
        """测试模型"""
        model = self.get_model(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        # 准备测试提示词
        if not test_prompt:
            test_prompt = "测试提示词，请返回JSON格式：{\"symbol\":\"null\",\"action\":\"HOLD\",\"confidence\":0.5,\"rationale\":\"测试\"}"
        
        try:
            # 根据provider创建适配器
            if model.provider == 'siliconflow':
                # 设置环境变量
                original_api_key = os.getenv('SILICONFLOW_API_KEY')
                original_base_url = os.getenv('SILICONFLOW_BASE_URL')
                
                os.environ['SILICONFLOW_API_KEY'] = model.api_key
                os.environ['SILICONFLOW_BASE_URL'] = model.base_url
                
                try:
                    adapter = SiliconAdapter(model=model.model_id)
                    
                    # 测试调用
                    start_time = time.time()
                    response = adapter.call(test_prompt)
                    response_time = time.time() - start_time
                    
                    # 更新测试结果
                    model.last_test_at = datetime.now()
                    model.last_test_result = True
                    model.test_error = None
                    model.is_active = True
                    model.success_calls += 1
                    model.total_calls += 1
                    model.avg_response_time = (
                        (model.avg_response_time * (model.total_calls - 1) + response_time) / model.total_calls
                        if model.total_calls > 0 else response_time
                    )
                    self.db.commit()
                    
                    return {
                        'success': True,
                        'response': response,
                        'response_time': response_time
                    }
                    
                except Exception as e:
                    # 更新测试结果
                    model.last_test_at = datetime.now()
                    model.last_test_result = False
                    model.test_error = str(e)
                    model.is_active = False
                    model.fail_calls += 1
                    model.total_calls += 1
                    self.db.commit()
                    
                    return {
                        'success': False,
                        'error': str(e)
                    }
                
                finally:
                    # 恢复原始环境变量
                    if original_api_key:
                        os.environ['SILICONFLOW_API_KEY'] = original_api_key
                    if original_base_url:
                        os.environ['SILICONFLOW_BASE_URL'] = original_base_url
            
            else:
                raise ValueError(f"Unsupported provider: {model.provider}")
                
        except Exception as e:
            model.last_test_at = datetime.now()
            model.last_test_result = False
            model.test_error = str(e)
            model.fail_calls += 1
            model.total_calls += 1
            self.db.commit()
            
            return {
                'success': False,
                'error': str(e)
            }
