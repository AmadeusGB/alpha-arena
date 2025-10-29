#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术指标计算模块
"""

import statistics
from typing import List, Dict, Any


def calculate_ema(prices: List[float], period: int = 20) -> float:
    """
    计算指数移动平均线 (EMA)
    
    Args:
        prices: 价格列表
        period: 周期
        
    Returns:
        EMA值
    """
    if len(prices) < period:
        return statistics.mean(prices) if prices else 0.0
    
    # 使用最近的period个数据点
    prices = prices[-period:]
    
    # 简单EMA计算
    multiplier = 2 / (period + 1)
    ema = prices[0]
    
    for price in prices[1:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    
    return ema


def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26) -> Dict[str, float]:
    """
    计算MACD指标
    
    Args:
        prices: 价格列表
        fast: 快速周期
        slow: 慢速周期
        
    Returns:
        MACD字典包含signal和histogram
    """
    if len(prices) < slow:
        return {'macd': 0.0, 'signal': 0.0, 'histogram': 0.0}
    
    # 计算快慢EMA
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    
    macd_line = ema_fast - ema_slow
    
    # 使用9周期EMA作为信号线
    signal = macd_line * 0.2  # 简化处理
    
    histogram = macd_line - signal
    
    return {
        'macd': macd_line,
        'signal': signal,
        'histogram': histogram
    }


def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """
    计算相对强弱指标 (RSI)
    
    Args:
        prices: 价格列表
        period: 周期
        
    Returns:
        RSI值 (0-100)
    """
    if len(prices) < period + 1:
        return 50.0  # 中性值
    
    # 计算价格变化
    changes = []
    for i in range(1, len(prices)):
        changes.append(prices[i] - prices[i - 1])
    
    # 计算平均涨幅和跌幅
    gains = [c if c > 0 else 0 for c in changes[-period:]]
    losses = [-c if c < 0 else 0 for c in changes[-period:]]
    
    avg_gain = statistics.mean(gains) if gains else 0
    avg_loss = statistics.mean(losses) if losses else 0
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_atr(prices: List[float], period: int = 14) -> float:
    """
    计算平均真实波幅 (ATR)
    简化版本，使用价格变化幅度
    
    Args:
        prices: 价格列表
        period: 周期
        
    Returns:
        ATR值
    """
    if len(prices) < period + 1:
        return 0.0
    
    # 计算价格波动范围
    ranges = []
    for i in range(1, len(prices)):
        ranges.append(abs(prices[i] - prices[i - 1]))
    
    recent_ranges = ranges[-period:]
    atr = statistics.mean(recent_ranges)
    
    return atr


def calculate_basic_indicators(prices: List[float]) -> Dict[str, Any]:
    """
    计算基础技术指标
    
    Args:
        prices: 价格列表
        
    Returns:
        指标字典
    """
    if not prices:
        return {
            'ema20': 0.0,
            'macd': 0.0,
            'rsi': 50.0,
            'atr': 0.0,
            'current_price': 0.0
        }
    
    current_price = prices[-1]
    ema20 = calculate_ema(prices, 20)
    macd_result = calculate_macd(prices)
    rsi = calculate_rsi(prices, 14)
    atr = calculate_atr(prices, 14)
    
    return {
        'current_price': current_price,
        'ema20': ema20,
        'macd': macd_result['macd'],
        'macd_signal': macd_result['signal'],
        'macd_histogram': macd_result['histogram'],
        'rsi': rsi,
        'rsi_7': calculate_rsi(prices, 7),
        'rsi_14': rsi,
        'atr': atr,
        'sma20': statistics.mean(prices[-20:]) if len(prices) >= 20 else statistics.mean(prices),
        'sma50': statistics.mean(prices[-50:]) if len(prices) >= 50 else statistics.mean(prices)
    }
