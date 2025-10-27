"""
决策服务
"""
import asyncio
import json
from datetime import datetime
import traceback
from typing import Dict, List
from sqlalchemy.orm import Session
from app.models.decision import Decision, Conversation
from app.core.decision import DecisionMaker
from app.core.adapters.silicon_adapter import SiliconAdapter
from app.core.technical_indicators import calculate_basic_indicators


class DecisionService:
    """决策服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.models = {}
        # 不自动初始化，延迟到首次使用时初始化
        self._model_configs = [
            ('qwen3', 'Qwen/Qwen3-32B'),
            ('deepseek', 'deepseek-ai/DeepSeek-R1'),
            ('kimi', 'moonshotai/Kimi-K2-Instruct-0905')
        ]
    
    def _ensure_models_initialized(self):
        """确保模型已初始化"""
        if not self.models:
            self._initialize_models()
    
    def _initialize_models(self):
        """初始化模型"""
        for model_name, model_id in self._model_configs:
            try:
                adapter = SiliconAdapter(model=model_id)
                decision_maker = DecisionMaker(adapter)
                self.models[model_name] = decision_maker
                print(f"✅ 模型 {model_name} 初始化成功")
            except Exception as e:
                print(f"❌ 模型 {model_name} 初始化失败: {e} {traceback.format_exc()}")
    
    async def make_decision_for_model(self, model_name: str, prices: Dict[str, float], indicators: Dict[str, Dict] = None) -> Dict:
        """为特定模型生成决策"""
        self._ensure_models_initialized()
        
        if model_name not in self.models:
            return {}
        
        decision_maker = self.models[model_name]
        prompt = decision_maker.build_prompt(prices, indicators)
        
        try:
            print(f"🔄 模型 {model_name} 开始生成决策...")
            response = await asyncio.to_thread(decision_maker.llm_adapter.call, prompt)
            print(f"📥 模型 {model_name} 原始响应: {response[:200]}...")  # 只打印前200字符
            
            # 尝试解析 JSON
            try:
                decision_data = json.loads(response)
                print(f"✅ 模型 {model_name} JSON 解析成功")
            except json.JSONDecodeError as je:
                print(f"❌ 模型 {model_name} JSON 解析失败: {je}")
                print(f"完整响应内容: {response}")
                
                # 尝试提取 JSON 部分
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    try:
                        decision_data = json.loads(json_match.group())
                        print(f"✅ 通过正则提取 JSON 成功")
                    except:
                        raise ValueError(f"响应不是有效的 JSON 格式。原始响应: {response[:500]}")
                else:
                    raise ValueError(f"响应中未找到 JSON 数据。原始响应: {response[:500]}")
            
            # 验证必需字段
            if 'action' not in decision_data:
                decision_data['action'] = 'HOLD'
            if 'symbol' not in decision_data:
                decision_data['symbol'] = None
            
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
            print(f"✅ 模型 {model_name} 决策保存成功: {decision_data}")
            
            return decision_data
            
        except json.JSONDecodeError as je:
            self.db.rollback()
            print(f"❌ 模型 {model_name} JSON 解析错误: {je}")
            print(f"错误详情: 位置 {je.pos}, 行 {je.lineno}")
            return {}
        except Exception as e:
            self.db.rollback()
            import traceback
            print(f"❌ 模型 {model_name} 决策失败: {e}")
            print(f"错误堆栈:\n{traceback.format_exc()}")
            return {}
    
    async def make_decisions(self, prices: Dict[str, float], indicators: Dict[str, Dict] = None) -> Dict[str, Dict]:
        """为所有模型生成决策（并发执行）"""
        self._ensure_models_initialized()
        
        # 创建并发任务
        tasks = []
        for model_name in self.models.keys():
            tasks.append(self.make_decision_for_model(model_name, prices, indicators))
        
        # 并发执行所有模型决策
        print(f"🚀 开始并发调用 {len(tasks)} 个模型...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 整理结果
        decisions = {}
        for model_name, result in zip(self.models.keys(), results):
            if isinstance(result, Exception):
                print(f"❌ 模型 {model_name} 执行异常: {result}")
                decisions[model_name] = {}
            else:
                decisions[model_name] = result
        
        print(f"✅ 所有模型决策完成，成功: {sum(1 for v in decisions.values() if v)}/{len(decisions)}")
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
