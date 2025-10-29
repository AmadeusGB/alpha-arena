#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bitget API 客户端
基于官方文档实现：https://www.bitget.com/zh-CN/api-doc/common/signature
"""

import os
import time
import hmac
import hashlib
import base64
import traceback
import requests
from typing import Dict, Optional
from dotenv import load_dotenv

# 加载 .env 文件（从 backend 目录）
env_path = os.path.join(os.path.dirname(__file__), '../../../../.env')
load_dotenv(env_path)
# 同时尝试从当前目录加载
load_dotenv()


class BitgetAPIClient:
    """Bitget API 客户端，实现官方签名机制"""
    
    BASE_URL = "https://api.bitget.com"
    
    def __init__(self, api_key: str = None, secret_key: str = None, passphrase: str = None):
        """
        初始化 Bitget API 客户端
        
        Args:
            api_key: API密钥 (ACCESS-KEY)
            secret_key: 密钥 (Secret Key)
            passphrase: 口令 (ACCESS-PASSPHRASE)
        """
        self.api_key = api_key or os.getenv('BITGET_API_KEY')
        self.secret_key = secret_key or os.getenv('BITGET_SECRET_KEY')
        self.passphrase = passphrase or os.getenv('BITGET_PASSPHRASE')
        
        if not self.api_key:
            raise ValueError("缺少 BITGET_API_KEY 配置")
        if not self.secret_key:
            raise ValueError("缺少 BITGET_SECRET_KEY 配置")
        if not self.passphrase:
            raise ValueError("缺少 BITGET_PASSPHRASE 配置")
    
    def _generate_signature(self, timestamp: str, method: str, request_path: str, 
                          query_string: str = "", body: str = "") -> str:
        """
        生成签名
        
        Args:
            timestamp: 时间戳（毫秒）
            method: HTTP方法
            request_path: 请求路径
            query_string: 查询字符串
            body: 请求体
            
        Returns:
            Base64编码的签名
        """
        # 构建待签名字符串
        if query_string:
            message = f"{timestamp}{method}{request_path}?{query_string}{body}"
        else:
            message = f"{timestamp}{method}{request_path}{body}"
        
        # HMAC SHA256 加密
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        # Base64 编码
        signature_base64 = base64.b64encode(signature).decode('utf-8')
        
        return signature_base64
    
    def _get_headers(self, method: str, request_path: str, 
                     query_string: str = "", body: str = "") -> Dict[str, str]:
        """
        获取请求头
        
        Args:
            method: HTTP方法
            request_path: 请求路径
            query_string: 查询字符串
            body: 请求体
            
        Returns:
            请求头字典
        """
        # 获取时间戳（毫秒）
        timestamp = str(int(time.time() * 1000))
        
        # 生成签名
        signature = self._generate_signature(timestamp, method, request_path, query_string, body)
        
        # 构建请求头
        headers = {
            'Content-Type': 'application/json',
            'ACCESS-KEY': self.api_key,
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': timestamp,
            'ACCESS-PASSPHRASE': self.passphrase,
            'locale': 'zh-CN'
        }
        
        return headers
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None) -> Dict:
        """
        发起API请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            params: 请求参数
            
        Returns:
            响应数据
        """
        # 构建URL
        url = f"{self.BASE_URL}{endpoint}"
        
        # 处理参数
        query_string = ""
        body = ""
        
        if params:
            if method.upper() == 'GET':
                # GET请求参数放在URL中
                query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            else:
                # POST请求参数在body中
                import json
                body = json.dumps(params)
        
        # 获取请求头
        headers = self._get_headers(method, endpoint, query_string, body)
        
        # 发起请求
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            else:
                response = requests.post(url, headers=headers, json=params if params else None)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API请求失败: {e}")
            if hasattr(e.response, 'text'):
                print(f"响应内容: {e.response.text}")
            raise
    
    def get_current_price(self, symbol: str) -> float:
        """
        获取当前价格（使用公共端点，无需签名）
        
        Args:
            symbol: 交易对符号，如 BTCUSDT
            
        Returns:
            当前价格
        """
        # Bitget 合约市场的 symbol 需要后缀 _UMCBL 表示 USDT 本位永续合约
        # 但如果用户提供的是 BTCUSDT，我们需要转换为 BTCUSDT_UMCBL
        mix_symbol = symbol
        if not symbol.endswith('_UMCBL') and not symbol.endswith('_CMCBL'):
            mix_symbol = f"{symbol}_UMCBL"
        
        # 优先尝试现货端点（更简单且稳定）
        # try:
        #     price = self._get_spot_price(symbol)
        #     if price > 0:
        #         return price
        # except Exception as e:
        #     print(f"⚠️ 现货端点失败: {e}")
        
        # 如果现货失败，尝试合约端点
        try:
            return self._get_mix_price(mix_symbol, symbol)
        except Exception as e:
            print(f"❌ 所有端点失败: {e}")
            return 0.0
    
    def _get_spot_price(self, symbol: str) -> float:
        """
        使用现货端点获取价格
        
        Args:
            symbol: 交易对符号，如 BTCUSDT
            
        Returns:
            价格
        """
        url = f"{self.BASE_URL}/api/spot/v1/market/ticker"
        params = {"symbol": symbol}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 检查API返回码
        if data.get('code') != '00000':
            msg = data.get('msg', '未知错误')
            raise Exception(f"API 返回错误: {msg}")
        
        # 解析价格数据
        if 'data' in data:
            ticker_data = data['data']
            # 尝试多种可能的字段
            for field in ['close', 'last', 'price', 'markPrice']:
                if field in ticker_data:
                    try:
                        return float(ticker_data[field])
                    except (ValueError, TypeError):
                        continue
        
        raise Exception("无法从响应中解析价格")
    
    def _get_mix_price(self, mix_symbol: str, original_symbol: str) -> float:
        """
        使用合约端点获取价格
        
        Args:
            mix_symbol: 合约交易对符号，如 BTCUSDT_UMCBL
            original_symbol: 原始交易对符号，如 BTCUSDT
            
        Returns:
            价格
        """
        url = f"{self.BASE_URL}/api/mix/v1/market/ticker"
        params = {
            "symbol": mix_symbol,
            "productType": "USDT-FUTURES"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        # 打印调试信息
        if response.status_code != 200:
            print(f"⚠️ 合约端点错误 (状态码: {response.status_code})")
            print(f"请求: {mix_symbol} (原始: {original_symbol})")
            print(f"URL: {response.url}")
            print(f"响应: {response.text}")
        
        response.raise_for_status()
        data = response.json()
        
        if data.get('code') != '00000':
            raise Exception(f"API 返回错误: {data.get('msg')}")
        
        if 'data' in data:
            ticker_data = data['data']
            if 'last' in ticker_data:
                return float(ticker_data['last'])
            elif 'price' in ticker_data:
                return float(ticker_data['price'])
            elif 'markPrice' in ticker_data:
                return float(ticker_data['markPrice'])
        
        return 0.0