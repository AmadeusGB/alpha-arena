"""
决策服务
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, List
from sqlalchemy.orm import Session
from app.models.decision import Decision, Conversation
from app.core.decision import DecisionMaker
from app.core.adapters.silicon_adapter import SiliconAdapter


class DecisionService:
    """决策服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.models = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """初始化模型"""
        model_configs = [
            ('qwen3', 'Qwen/Qwen3-32B'),
            ('deepseek', 'deepseek-ai/DeepSeek-R1'),
            ('kimi', 'moonshotai/Kimi-K2-Instruct-0905')
        ]
        
        for model_name, model_id in model_configs:
            try:
                adapter = SiliconAdapter(model=model_id)
                decision_maker = DecisionMaker(adapter)
                self.models[model_name] = decision_maker
            except Exception as e:
                print(f"模型 {model_name} 初始化失败: {e}")
    
    async def make_decision_for_model(self, model_name: str, prices: Dict[str, float]) -> Dict:
        """为特定模型生成决策"""
        if model_name not in self.models:
            return {}
        
        decision_maker = self.models[model_name]
        prompt = decision_maker.build_prompt(prices)
        
        try:
            response = await asyncio.to_thread(decision_maker.llm_adapter.call, prompt)
            decision_data = json.loads(response)
            
            # 保存决策
            decision = Decision(
                model_name=model_name,
                symbol=decision_data.get('symbol'),
                action=decision_data.get('action', 'HOLD'),
                confidence=decision_data.get('confidence'),
                reasoning=decision_data.get('reasoning'),
                prompt=prompt,
                response_raw=decision_data
            )
            self.db.add(decision)
            
            # 保存对话记录
            conversation = Conversation(
                model_name=model_name,
                prompt=prompt,
                response=response
            )
            self.db.add(conversation)
            
            self.db.commit()
            
            return decision_data
            
        except Exception as e:
            self.db.rollback()
            print(f"模型 {model_name} 决策失败: {e}")
            return {}
    
    async def make_decisions(self, prices: Dict[str, float]) -> Dict[str, Dict]:
        """为所有模型生成决策"""
        decisions = {}
        
        for model_name in self.models.keys():
            decision = await self.make_decision_for_model(model_name, prices)
            decisions[model_name] = decision
        
        return decisions
    
    def get_decision_history(
        self,
        model_name: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Decision]:
        """获取决策历史"""
        query = self.db.query(Decision)
        
        if model_name:
            query = query.filter(Decision.model_name == model_name)
        
        return query.order_by(Decision.timestamp.desc()).limit(limit).offset(offset).all()
    
    def get_conversation_history(
        self,
        model_name: str = None,
        limit: int = 100
    ) -> List[Conversation]:
        """获取对话历史"""
        query = self.db.query(Conversation)
        
        if model_name:
            query = query.filter(Conversation.model_name == model_name)
        
        return query.order_by(Conversation.timestamp.desc()).limit(limit).all()


import asyncio

