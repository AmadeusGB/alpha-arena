#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
决策引擎
处理LLM交易决策
"""

import json
from typing import Dict, Any
from app.core.adapters.llm_base import LLMAdapter


class DecisionMaker:
    """交易决策引擎"""
    
    def __init__(self, llm_adapter: LLMAdapter):
        """
        初始化决策引擎
        
        Args:
            llm_adapter: LLM适配器实例
        """
        self.llm_adapter = llm_adapter
        self.model_name = llm_adapter.get_model_name()
    
    def build_prompt(self, market_data: Dict[str, float]) -> str:
        """
        构建交易决策提示词
        
        Args:
            market_data: 市场数据字典
            
        Returns:
            构建的提示词
        """
        prompt = f"""
你是专业的量化交易分析师，请根据当前市场价格给出交易决策。

当前市场价格：
- BTCUSDT: ${market_data.get('BTCUSDT', 0):.4f}
- ETHUSDT: ${market_data.get('ETHUSDT', 0):.4f}
- XRPUSDT: ${market_data.get('XRPUSDT', 0):.4f}
- BNBUSDT: ${market_data.get('BNBUSDT', 0):.4f}
- SOLUSDT: ${market_data.get('SOLUSDT', 0):.4f}

请以JSON格式返回你的交易决策：
{{
    "symbol": "BTCUSDT|ETHUSDT|XRPUSDT|BNBUSDT|SOLUSDT|null",
    "action": "BUY|SELL|HOLD",
    "confidence": 0.0-1.0,
    "rationale": "简短理由（不超过50字）"
}}

注意事项：
1. 只返回JSON，不要其他文字
2. symbol为null表示不选择任何代币
3. action为HOLD表示持有/观望
4. confidence表示决策信心度
5. rationale给出决策理由

JSON:
"""
        return prompt
    
    def get_decision(self, market_data: Dict[str, float]) -> Dict[str, Any]:
        """
        获取交易决策
        
        Args:
            market_data: 市场数据
            
        Returns:
            解析后的决策字典
        """
        prompt = self.build_prompt(market_data)
        
        try:
            response = self.llm_adapter.call(prompt)
            return self.parse_decision(response)
        except Exception as e:
            print(f"❌ {self.model_name}决策获取失败: {e}")
            return self.get_default_decision()
    
    def parse_decision(self, response: str) -> Dict[str, Any]:
        """
        解析LLM响应
        
        Args:
            response: LLM响应文本
            
        Returns:
            解析后的决策字典
        """
        try:
            # 尝试提取JSON
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            
            decision = json.loads(response)
            
            # 验证必要字段
            required_fields = ['symbol', 'action', 'confidence', 'rationale']
            for field in required_fields:
                if field not in decision:
                    print(f"⚠️ 决策缺少字段: {field}")
                    return self.get_default_decision()
            
            # 验证字段值
            if decision['action'] not in ['BUY', 'SELL', 'HOLD']:
                print(f"⚠️ 无效的action: {decision['action']}")
                decision['action'] = 'HOLD'
            
            if not isinstance(decision['confidence'], (int, float)) or not (0 <= decision['confidence'] <= 1):
                print(f"⚠️ 无效的confidence: {decision['confidence']}")
                decision['confidence'] = 0.5
            
            return decision
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"原始响应: {response}")
            return self.get_default_decision()
        except Exception as e:
            print(f"❌ 决策解析失败: {e}")
            return self.get_default_decision()
    
    def get_default_decision(self) -> Dict[str, Any]:
        """获取默认决策"""
        return {
            "symbol": None,
            "action": "HOLD",
            "confidence": 0.0,
            "rationale": "解析失败，默认观望"
        }
    
    def format_decision_for_display(self, decision: Dict[str, Any]) -> str:
        """
        格式化决策用于显示
        
        Args:
            decision: 决策字典
            
        Returns:
            格式化的决策字符串
        """
        symbol = decision.get('symbol', 'None')
        action = decision.get('action', 'HOLD')
        confidence = decision.get('confidence', 0.0)
        rationale = decision.get('rationale', '无理由')
        
        return f"   决策: {action} {symbol}\n   信心: {confidence:.2f}\n   理由: {rationale}"
