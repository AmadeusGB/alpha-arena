import os
import json
from typing import Dict, Any
from .llm_base import LLMAdapter

class SiliconAdapter(LLMAdapter):
    """SiliconFlow API 适配器"""

    def __init__(self, api_key: str = None, model: str = None):
        """
        初始化 SiliconFlow 适配器
        
        Args:
            api_key: API密钥
            model: 模型名称，如 'deepseek-ai/DeepSeek-R1-0528-Qwen3-8B'
        """
        # 从环境变量获取配置
        self.api_key = api_key or os.getenv('SILICONFLOW_API_KEY', '')
        self.base_url = os.getenv('SILICONFLOW_BASE_URL', 'https://api.siliconflow.cn/v1')
        self.model = model or os.getenv('SILICONFLOW_MODEL', 'deepseek-ai/DeepSeek-R1-0528-Qwen3-8B')
        
        if not self.api_key:
            raise ValueError("SILICONFLOW_API_KEY 环境变量未设置")
        
        super().__init__(self.api_key)
        
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """初始化 OpenAI 客户端"""
        try:
            from openai import OpenAI
            
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            # 不进行测试请求，只在实际调用时验证
            # 这可以避免不必要的API调用和费用
            
        except Exception as e:
            print(f"❌ SiliconFlow 初始化失败: {e}")
            raise

    def call(self, prompt: str, **kwargs) -> str:
        """
        调用 SiliconFlow API
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数
            
        Returns:
            API 响应文本
        """
        try:
            # 构建请求消息
            messages = [
                {"role": "system", "content": "你是一个专业的量化交易分析师，严格按照JSON格式返回交易决策。"},
                {"role": "user", "content": prompt}
            ]
            
            # 调用 API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=200,
                temperature=0.1,
                timeout=30
            )
            
            # 提取响应文本
            content = response.choices[0].message.content
            return content.strip()
            
        except Exception as e:
            print(f"❌ SiliconFlow API 调用失败: {e}")
            raise

    def get_model_name(self) -> str:
        """获取模型名称"""
        # 从模型ID提取简短名称
        if 'qwen' in self.model.lower():
            return f"Qwen3 (SiliconFlow)"
        elif 'deepseek' in self.model.lower():
            return f"DeepSeek (SiliconFlow)"
        elif 'kimi' in self.model.lower():
            return f"Kimi (SiliconFlow)"
        elif 'doubao' in self.model.lower():
            return f"Doubao (SiliconFlow)"
        return f"{self.model} (SiliconFlow)"

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "name": self.get_model_name(),
            "provider": "SiliconFlow",
            "model": self.model,
            "base_url": self.base_url
        }