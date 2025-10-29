#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI适配器
调用OpenAI GPT模型进行交易决策
"""

import os
from typing import Dict, Any
from .llm_base import LLMAdapter

try:
    import openai
except ImportError:
    print("❌ 请安装openai: pip install openai")
    openai = None


class OpenAIAdapter(LLMAdapter):
    """OpenAI适配器"""
    
    def __init__(self, api_key: str = None):
        """
        初始化OpenAI适配器
        
        Args:
            api_key: OpenAI API密钥，如果为None则从环境变量获取
        """
        if api_key is None:
            api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            raise ValueError("OpenAI API密钥未设置，请设置OPENAI_API_KEY环境变量")
        
        super().__init__(api_key)
        
        # 初始化OpenAI客户端
        if openai:
            openai.api_key = self.api_key
        else:
            raise ImportError("OpenAI库未安装")
    
    def call(self, prompt: str) -> str:
        """
        调用OpenAI API
        
        Args:
            prompt: 输入提示词
            
        Returns:
            OpenAI响应文本
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一个专业的量化交易分析师，请根据市场数据给出交易决策。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ OpenAI API调用失败: {e}")
            return '{"symbol": null, "action": "HOLD", "confidence": 0.0, "rationale": "API调用失败"}'
    
    def get_model_name(self) -> str:
        """获取模型名称"""
        return "GPT-4"
