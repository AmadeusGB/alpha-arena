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
    
    def build_prompt(self, market_data: Dict[str, float], indicators: Dict[str, Dict] = None) -> str:
        """
        构建交易决策提示词
        
        Args:
            market_data: 市场数据字典
            indicators: 技术指标字典，格式为 {symbol: {indicators...}}
            
        Returns:
            构建的提示词
        """
        # 构建市场数据部分
        market_info = []
        for symbol in ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'BNBUSDT', 'SOLUSDT']:
            price = market_data.get(symbol, 0)
            if indicators and symbol in indicators:
                ind = indicators[symbol]
                market_info.append(
                    f"{symbol} - current_price: {price:.2f}, "
                    f"ema20: {ind.get('ema20', 0):.2f}, "
                    f"macd: {ind.get('macd', 0):.3f}, "
                    f"rsi: {ind.get('rsi', 50):.2f}"
                )
            else:
                market_info.append(f"{symbol} - current_price: ${price:.4f}")
        
        market_section = "\n".join(market_info)
        
        prompt = f"""
You are a professional quantitative trading analyst. Analyze the current market data and provide a trading decision.

**CURRENT MARKET DATA:**
{market_section}

**TRADING INSTRUCTIONS:**
- Analyze technical indicators (EMA, MACD, RSI)
- Consider price trends and momentum
- Identify the best trading opportunity among available symbols
- Decide whether to BUY, SELL, or HOLD

**OUTPUT REQUIREMENTS:**
Return ONLY a valid JSON object with the following structure:
{{
    "symbol": "BTCUSDT|ETHUSDT|XRPUSDT|BNBUSDT|SOLUSDT|null",
    "action": "BUY|SELL|HOLD",
    "confidence": <number between 0.0 and 1.0>,
    "rationale": "<brief explanation in less than 50 characters>"
}}

**RULES:**
1. symbol: Choose one of BTCUSDT, ETHUSDT, XRPUSDT, BNBUSDT, SOLUSDT, or null for no action
2. action: BUY (open long position), SELL (close position), or HOLD (maintain current state)
3. confidence: Your confidence in this decision (0.0 to 1.0)
4. rationale: Brief reasoning for your decision
5. Return ONLY the JSON object, no additional text or explanation

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
