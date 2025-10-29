#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
市场数据模块
获取和管理市场数据
"""

from typing import Dict, List
from app.core.adapters.exchange_api import ExchangeAPI


class MarketData:
    """市场数据管理器"""
    
    def __init__(self):
        """初始化市场数据管理器"""
        self.exchange_api = ExchangeAPI()
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'BNBUSDT', 'SOLUSDT']
    
    def get_current_prices(self) -> Dict[str, float]:
        """
        获取当前所有代币的价格
        
        Returns:
            价格字典
        """
        return self.exchange_api.get_latest_prices(self.symbols)
    
    def get_price(self, symbol: str) -> float:
        """
        获取指定代币的价格
        
        Args:
            symbol: 代币符号
            
        Returns:
            价格
        """
        return self.exchange_api.get_single_price(symbol)
    
    def get_symbols(self) -> List[str]:
        """获取支持的代币列表"""
        return self.symbols.copy()
    
    def is_api_available(self) -> bool:
        """检查API是否可用"""
        return self.exchange_api.is_available()
    
    def format_prices_for_display(self, prices: Dict[str, float]) -> str:
        """
        格式化价格用于显示
        
        Args:
            prices: 价格字典
            
        Returns:
            格式化的价格字符串
        """
        lines = []
        for symbol, price in prices.items():
            if price > 0:
                lines.append(f"   {symbol}: ${price:.4f}")
            else:
                lines.append(f"   {symbol}: 获取失败")
        return "\n".join(lines)
