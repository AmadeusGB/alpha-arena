#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM适配器基类
定义统一的LLM接口规范
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class LLMAdapter(ABC):
    """LLM适配器基类"""
    
    def __init__(self, api_key: str):
        """
        初始化LLM适配器
        
        Args:
            api_key: API密钥
        """
        self.api_key = api_key
    
    @abstractmethod
    def call(self, prompt: str) -> str:
        """
        调用LLM API
        
        Args:
            prompt: 输入提示词
            
        Returns:
            LLM响应文本
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """
        获取模型名称
        
        Returns:
            模型名称
        """
        pass
