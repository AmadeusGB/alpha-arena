#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OKX API 客户端
文档：https://www.okx.com/docs-v5/zh/
"""

import os
import time
import hmac
import hashlib
import base64
import json
import requests
from typing import Dict, Optional
from datetime import datetime


class OKXAPIClient:
    """OKX API 客户端"""
    
    BASE_URL = "https://www.okx.com"
    
    def __init__(self, api_key: str = None, secret_key: str = None, passphrase: str = None, is_sandbox: bool = False):
        """
        初始化 OKX API 客户端
        
        Args:
            api_key: API密钥
            secret_key: 密钥
            passphrase: 口令
            is_sandbox: 是否使用沙盒环境
        """
        self.api_key = api_key or os.getenv('OKX_API_KEY')
        self.secret_key = secret_key or os.getenv('OKX_SECRET_KEY')
        self.passphrase = passphrase or os.getenv('OKX_PASSPHRASE')
        self.is_sandbox = is_sandbox
        
        if self.is_sandbox:
            # OKX 沙盒环境使用单独的域名
            self.BASE_URL = "https://www.okx.com"  # 通过 x-simulated-trading 头标识
        
        if not self.api_key:
            raise ValueError("缺少 OKX_API_KEY 配置")
        if not self.secret_key:
            raise ValueError("缺少 OKX_SECRET_KEY 配置")
        if not self.passphrase:
            raise ValueError("缺少 OKX_PASSPHRASE 配置")
    
    def _generate_signature(self, timestamp: str, method: str, request_path: str, body: str = "") -> str:
        """
        生成签名
        
        Args:
            timestamp: 时间戳（ISO 8601）
            method: HTTP方法
            request_path: 请求路径
            body: 请求体
            
        Returns:
            Base64编码的签名
        """
        message = timestamp + method + request_path + body
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    def _get_headers(self, method: str, request_path: str, body: str = "") -> Dict[str, str]:
        """获取请求头"""
        timestamp = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
        
        signature = self._generate_signature(timestamp, method, request_path, body)
        
        headers = {
            'Content-Type': 'application/json',
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
        }
        
        if self.is_sandbox:
            headers['x-simulated-trading'] = '1'
        
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
        url = f"{self.BASE_URL}{endpoint}"
        
        body = ""
        if params and method.upper() in ['POST', 'PUT']:
            body = json.dumps(params)
        
        headers = self._get_headers(method, endpoint, body)
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            else:
                response = requests.post(url, headers=headers, json=params if params else None, timeout=10)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ OKX API请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"响应内容: {e.response.text}")
            raise
    
    def get_current_price(self, symbol: str) -> float:
        """
        获取当前价格
        
        Args:
            symbol: 交易对符号，如 BTC-USDT
            
        Returns:
            当前价格
        """
        try:
            # OKX 现货端点
            endpoint = "/api/v5/market/ticker"
            params = {"instId": symbol}
            
            response = self._make_request('GET', endpoint, params)
            
            if response.get('code') != '0':
                msg = response.get('msg', '未知错误')
                raise Exception(f"OKX API 返回错误: {msg}")
            
            data = response.get('data', [])
            if data and len(data) > 0:
                ticker_data = data[0]
                last_price = ticker_data.get('last')
                if last_price:
                    return float(last_price)
            
            raise Exception("无法从响应中解析价格")
        except Exception as e:
            print(f"❌ 获取{symbol}价格失败: {e}")
            return 0.0
    
    def get_account_info(self) -> Dict:
        """获取账户信息"""
        endpoint = "/api/v5/account/balance"
        return self._make_request('GET', endpoint)
    
    def place_order(self, symbol: str, side: str, order_type: str, size: float, price: Optional[float] = None) -> Dict:
        """
        下单
        
        Args:
            symbol: 交易对
            side: 方向 (buy/sell)
            order_type: 订单类型 (limit/market)
            size: 数量
            price: 价格（限价单必需）
        """
        endpoint = "/api/v5/trade/order"
        params = {
            "instId": symbol,
            "side": side.upper(),
            "ordType": order_type.upper(),
            "sz": str(size),
        }
        
        if price:
            params["px"] = str(price)
        
        return self._make_request('POST', endpoint, params)
    
    def get_positions(self) -> Dict:
        """获取持仓信息"""
        endpoint = "/api/v5/account/positions"
        return self._make_request('GET', endpoint)
