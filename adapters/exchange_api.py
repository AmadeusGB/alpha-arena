#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易所API适配器
支持 Bitget、OKX、Binance
"""

import os
from typing import Dict, List, Optional
from adapters.bitget_api_client import BitgetAPIClient
from adapters.okx_api_client import OKXAPIClient
from adapters.binance_api_client import BinanceAPIClient


class ExchangeAPI:
    """交易所API适配器（支持多交易所）"""
    
    def __init__(self, exchange_name: str = None):
        """
        初始化交易所API
        
        Args:
            exchange_name: 交易所名称 (BITGET/OKX/BINANCE)
        """
        self.exchange_name = exchange_name or os.getenv('DEFAULT_EXCHANGE', 'BITGET').upper()
        self.client = None
        
        try:
            if self.exchange_name == 'BITGET':
                self.client = BitgetAPIClient(
                    api_key=os.getenv('BITGET_API_KEY'),
                    secret_key=os.getenv('BITGET_SECRET_KEY'),
                    passphrase=os.getenv('BITGET_PASSPHRASE')
                )
            elif self.exchange_name == 'OKX':
                self.client = OKXAPIClient(
                    api_key=os.getenv('OKX_API_KEY'),
                    secret_key=os.getenv('OKX_SECRET_KEY'),
                    passphrase=os.getenv('OKX_PASSPHRASE')
                )
            elif self.exchange_name == 'BINANCE':
                self.client = BinanceAPIClient(
                    api_key=os.getenv('BINANCE_API_KEY'),
                    secret_key=os.getenv('BINANCE_SECRET_KEY')
                )
            else:
                raise ValueError(f"不支持的交易所: {self.exchange_name}")
                
            print(f"✅ {self.exchange_name} API客户端初始化成功")
        except Exception as e:
            print(f"❌ {self.exchange_name} API客户端初始化失败: {e}")
            self.client = None
    
    def normalize_symbol(self, symbol: str) -> str:
        """
        标准化交易对符号
        
        Args:
            symbol: 原始交易对符号
            
        Returns:
            标准化后的交易对符号
        """
        if self.exchange_name == 'OKX':
            # OKX 使用 BTC-USDT 格式
            if not '-' in symbol and 'USDT' in symbol:
                base = symbol.replace('USDT', '')
                return f"{base}-USDT"
        elif self.exchange_name == 'BITGET':
            # Bitget 使用 BTCUSDT 格式
            return symbol
        elif self.exchange_name == 'BINANCE':
            # Binance 使用 BTCUSDT 格式
            return symbol
        
        return symbol
    
    def get_latest_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        获取多个代币的最新价格
        
        Args:
            symbols: 代币符号列表，如['BTCUSDT', 'ETHUSDT']
            
        Returns:
            价格字典，格式为{symbol: price}
        """
        if self.client is None:
            print("❌ API客户端未初始化")
            return {symbol: 0.0 for symbol in symbols}
        
        prices = {}
        
        for symbol in symbols:
            try:
                # 标准化交易对符号
                normalized_symbol = self.normalize_symbol(symbol)
                price = self.client.get_current_price(normalized_symbol)
                prices[symbol] = price
                print(f"✅ {self.exchange_name} {symbol}: ${price:.4f}")
            except Exception as e:
                print(f"❌ 获取{symbol}价格失败: {e}")
                prices[symbol] = 0.0
        
        return prices
    
    def get_single_price(self, symbol: str) -> float:
        """
        获取单个代币的价格
        
        Args:
            symbol: 代币符号，如'BTCUSDT'
            
        Returns:
            价格
        """
        if self.client is None:
            return 0.0
        
        try:
            # 标准化交易对符号
            normalized_symbol = self.normalize_symbol(symbol)
            return self.client.get_current_price(normalized_symbol)
        except Exception as e:
            print(f"❌ 获取{symbol}价格失败: {e}")
            return 0.0
    
    def is_available(self) -> bool:
        """检查API是否可用"""
        return self.client is not None
    
    def get_account_info(self) -> Dict:
        """获取账户信息"""
        if self.client is None:
            return {}
        try:
            return self.client.get_account_info()
        except Exception as e:
            print(f"❌ 获取账户信息失败: {e}")
            return {}
    
    def get_positions(self) -> Dict:
        """获取持仓信息"""
        if self.client is None:
            return {}
        try:
            return self.client.get_positions()
        except Exception as e:
            print(f"❌ 获取持仓信息失败: {e}")
            return {}
