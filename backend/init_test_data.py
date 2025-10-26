#!/usr/bin/env python3
"""
初始化测试数据
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal, engine, Base
from app.models.portfolio import ModelPortfolio, StrategyConfig
from datetime import datetime

def init_test_data():
    """初始化测试数据"""
    # 创建表
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 创建模型账户
        models = ['qwen3', 'deepseek', 'kimi']
        
        for model_name in models:
            # 检查是否已存在
            existing = db.query(ModelPortfolio).filter(
                ModelPortfolio.model_name == model_name
            ).first()
            
            if not existing:
                portfolio = ModelPortfolio(
                    model_name=model_name,
                    balance=10000.0,
                    total_value=10000.0,
                    initial_capital=10000.0,
                    daily_pnl=0.0,
                    total_pnl=0.0,
                    total_return=0.0,
                    max_drawdown=0.0,
                    is_active='active'
                )
                db.add(portfolio)
                print(f"✅ 创建模型账户: {model_name}")
                
                # 创建策略配置
                strategy = StrategyConfig(
                    model_name=model_name,
                    params='{}',
                    is_active='active',
                    max_position_size=0.2,
                    stop_loss_percent=0.05
                )
                db.add(strategy)
                print(f"✅ 创建策略配置: {model_name}")
        
        db.commit()
        print("\n✅ 测试数据初始化完成！")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_test_data()

