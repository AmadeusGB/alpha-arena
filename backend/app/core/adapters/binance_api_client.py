#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Binance API 客户端
文档：https://binance-docs.github.io/apidocs/
"""

import os
import time
import hmac
import hashlib
import base64
import json
import requests
from typing import Dict, Optional
from urllib.parse import urlencode


class BinanceAPIClient:
    """Binance API 客户端"""
    
    BASE_URL = "https://api.binance.com"
    
    def __init__(self, api_key: str = None, secret_key: str = None, is_testnet: bool = False):
        """
        初始化 Binance API 客户端
        
        Args:
            api_key: API密钥
            secret_key: 密钥
            is_testnet: 是否使用测试网
        """
        self.api_key = api_key or os.getenv('BINANCE_API_KEY')
        self.secret_key = secret_key or os.getenv('BINANCE_SECRET_KEY')
        self.is_testnet = is_testnet
        
        if self.is_testnet:
            self.BASE_URL = "https://testnet.binance.vision"
        
        if not self.api_key:
            raise ValueError("缺少 BINANCE_API_KEY 配置")
        if not self.secret_key:
            raise ValueError("缺少 BINANCE_SECRET_KEY 配置")
    
    def _generate_signature(self, query_string: str) -> str:
        """
        生成签名
        
        Args:
            query_string: 查询字符串
            
        Returns:
            HMAC SHA256 签名
        """
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            'X-MBX-APIKEY': self.api_key,
        }
    
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
        
        if params is None:
            params = {}
        
        # 添加时间戳
        params['timestamp'] = int(time.time() * 1000)
        
        # 生成签名
        query_string = urlencode(params)
        signature = self._generate_signature(query_string)
        params['signature'] = signature
        
        headers = self._get_headers()
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            else:
                response = requests.post(url, headers=headers, params=params, timeout=10)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Binance API请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"响应内容: {e.response.text}")
            raise
    
    def get_current_price(self, symbol: str) -> float:
        """
        获取当前价格
        
        Args:
            symbol: 交易对符号，如 BTCUSDT
            
        Returns:
            当前价格
        """
        try:
            # Binance 现货端点
            endpoint = "/api/v3/ticker/price"
            params = {"symbol": symbol}
            
            url = f"{self.BASE_URL}{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'price' in data:
                return float(data['price'])
            
            raise Exception("无法从响应中解析价格")
        except Exception as e:
            print(f"❌ 获取{symbol}价格失败: {e}")
            return 0.0
    
    def get_account_info(self) -> Dict:
        """获取账户信息"""
        endpoint = "/api/v3/account"
        return self._make_request('GET', endpoint)
    
    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: Optional[float] = None) -> Dict:
        """
        下单
        
        Args:
            symbol: 交易对
            side: 方向 (BUY/SELL)
            order_type: 订单类型 (LIMIT/MARKET)
            quantity: 数量
            price: 价格（限价单必需）
        """
        endpoint = "/api/v3/order"
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": str(quantity),
        }
        
        if price:
            params["price"] = str(price)
            params["timeInForce"] = "GTC"
        
        return self._make_request('POST', endpoint, params)
    
    def get_positions(self) -> Dict:
        """获取持仓信息（Binance现货无持仓概念，返回账户余额）"""
        return self.get_account_info()
