#!/usr/bin/env python3
"""
初始化默认模型配置
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app.models.model_config import ModelConfig
from app.config import settings


def init_default_models():
    """初始化默认模型配置"""
    db = SessionLocal()
    
    try:
        default_configs = [
            {
                'name': 'qwen3',
                'provider': 'siliconflow',
                'model_id': 'Qwen/Qwen3-32B',
                'api_key': settings.SILICONFLOW_API_KEY,
                'base_url': settings.SILICONFLOW_BASE_URL,
                'is_enabled': True,
            },
            {
                'name': 'deepseek',
                'provider': 'siliconflow',
                'model_id': 'deepseek-ai/DeepSeek-V3.1-Terminus',
                'api_key': settings.SILICONFLOW_API_KEY,
                'base_url': settings.SILICONFLOW_BASE_URL,
                'is_enabled': True,
            },
            {
                'name': 'kimi',
                'provider': 'siliconflow',
                'model_id': 'moonshotai/Kimi-K2-Instruct-0905',
                'api_key': settings.SILICONFLOW_API_KEY,
                'base_url': settings.SILICONFLOW_BASE_URL,
                'is_enabled': True,
            }
        ]
        
        created_count = 0
        for config in default_configs:
            # 检查是否已存在
            existing = db.query(ModelConfig).filter(
                ModelConfig.name == config['name']
            ).first()
            
            if not existing:
                model = ModelConfig(**config)
                db.add(model)
                print(f"✅ 创建默认模型配置: {config['name']}")
                created_count += 1
            else:
                print(f"⚠️ 模型配置已存在: {config['name']}")
        
        db.commit()
        
        if created_count > 0:
            print(f"\n✅ 成功创建 {created_count} 个默认模型配置！")
        else:
            print("\n✅ 所有默认模型配置已存在，无需创建。")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    init_default_models()
