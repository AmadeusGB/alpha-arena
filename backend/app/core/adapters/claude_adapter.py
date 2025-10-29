#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude适配器
调用Anthropic Claude模型进行交易决策
"""

import os
from typing import Dict, Any
from .llm_base import LLMAdapter

try:
    import anthropic
except ImportError:
    print("❌ 请安装anthropic: pip install anthropic")
    anthropic = None


class ClaudeAdapter(LLMAdapter):
    """Claude适配器"""
    
    def __init__(self, api_key: str = None):
        """
        初始化Claude适配器
        
        Args:
            api_key: Anthropic API密钥，如果为None则从环境变量获取
        """
        if api_key is None:
            api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key:
            raise ValueError("Anthropic API密钥未设置，请设置ANTHROPIC_API_KEY环境变量")
        
        super().__init__(api_key)
        
        # 初始化Anthropic客户端
        if anthropic:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            raise ImportError("Anthropic库未安装")
    
    def call(self, prompt: str) -> str:
        """
        调用Claude API
        
        Args:
            prompt: 输入提示词
            
        Returns:
            Claude响应文本
        """
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                temperature=0.7,
                system="你是一个专业的量化交易分析师，请根据市场数据给出交易决策。",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            print(f"❌ Claude API调用失败: {e}")
            return '{"symbol": null, "action": "HOLD", "confidence": 0.0, "rationale": "API调用失败"}'
    
    def get_model_name(self) -> str:
        """获取模型名称"""
        return "Claude-3-Sonnet"
