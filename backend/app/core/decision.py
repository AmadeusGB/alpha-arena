#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
决策引擎
处理LLM交易决策
"""

import json
from typing import Dict, Any
from app.core.adapters.llm_base import LLMAdapter


class DecisionMaker:
    """交易决策引擎"""
    
    def __init__(self, llm_adapter: LLMAdapter):
        """
        初始化决策引擎
        
        Args:
            llm_adapter: LLM适配器实例
        """
        self.llm_adapter = llm_adapter
        self.model_name = llm_adapter.get_model_name()
    
    def build_prompt(
        self,
        market_data: Dict[str, float],
        indicators: Dict[str, Dict] = None,
        trading_settings: Dict = None,
        current_positions: list = None,
        model_trading_params: Dict = None,
        allowed_symbols: list = None,
        portfolio_info: Dict = None
    ) -> str:
        """
        构建交易决策提示词
        
        Args:
            market_data: 市场数据字典
            indicators: 技术指标字典，格式为 {symbol: {indicators...}}
            trading_settings: 交易设置（包括止损、止盈、最大持仓等）
            current_positions: 当前持仓列表
            
        Returns:
            构建的提示词
        """
        # 允许的交易标的
        default_symbols = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'BNBUSDT', 'SOLUSDT']
        symbols = allowed_symbols if (allowed_symbols and len(allowed_symbols) > 0) else default_symbols

        # 构建市场数据部分
        market_info = []
        for symbol in symbols:
            price = market_data.get(symbol, 0)
            if indicators and symbol in indicators:
                ind = indicators[symbol]
                market_info.append(
                    f"{symbol} - current_price: {price:.2f}, "
                    f"ema20: {ind.get('ema20', 0):.2f}, "
                    f"macd: {ind.get('macd', 0):.3f}, "
                    f"rsi: {ind.get('rsi', 50):.2f}"
                )
            else:
                market_info.append(f"{symbol} - current_price: ${price:.4f}")
        
        market_section = "\n".join(market_info)
        
        # 构建持仓信息
        positions_section = ""
        if current_positions:
            positions_info = []
            for pos in current_positions:
                positions_info.append(
                    f"  - {pos.get('symbol')}: {pos.get('quantity', 0):.4f} @ ${pos.get('entry_price', 0):.2f}, "
                    f"P&L: ${pos.get('pnl', 0):.2f} ({pos.get('pnl_percent', 0):.2f}%)"
                )
            positions_section = "**CURRENT POSITIONS:**\n" + "\n".join(positions_info)
        else:
            positions_section = "**CURRENT POSITIONS:** None"
        
        # 构建交易配置和风险管理策略
        risk_section = ""
        if trading_settings:
            risk_section = f"""
**TRADING CONFIGURATION & RISK MANAGEMENT:**
- Max Position Ratio: {trading_settings.get('max_position_percent', 0.8) * 100:.0f}%
- Stop Loss Range: {trading_settings.get('stop_loss_min', 0.01) * 100:.0f}% - {trading_settings.get('stop_loss_max', 0.10) * 100:.0f}%
- Take Profit Range: {trading_settings.get('take_profit_min', 0.01) * 100:.0f}% - {trading_settings.get('take_profit_max', 0.20) * 100:.0f}%
- Min Confidence Threshold: {trading_settings.get('min_confidence', 0.3) * 100:.0f}%
- Max Open Positions: {trading_settings.get('max_open_positions', 3)}
- Max Drawdown Limit: {trading_settings.get('max_drawdown', 0.2) * 100:.0f}%

**RISK CONTROL STRATEGY:**
1. Always implement stop-loss orders at {trading_settings.get('stop_loss_min', 0.01) * 100:.0f}%-{trading_settings.get('stop_loss_max', 0.10) * 100:.0f}% below entry price
2. Set take-profit targets at {trading_settings.get('take_profit_min', 0.01) * 100:.0f}%-{trading_settings.get('take_profit_max', 0.20) * 100:.0f}% above entry price
3. Do not exceed {trading_settings.get('max_position_percent', 0.8) * 100:.0f}% of total capital in any single position
4. Maintain maximum {trading_settings.get('max_open_positions', 3)} concurrent positions
5. Only take trades with confidence above {trading_settings.get('min_confidence', 0.3) * 100:.0f}%

**PROFIT PROTECTION STRATEGY:**
1. Use trailing stop-loss to protect profits after position reaches 5% gain
2. Scale out of winning positions at 10%, 15%, and 20% profit levels
3. Close positions immediately if market conditions deteriorate significantly
4. Avoid adding to losing positions
"""

        # 账户状态与交易额度限制
        account_section = ""
        if portfolio_info:
            balance = float(portfolio_info.get('balance', 0) or 0)
            total_value = float(portfolio_info.get('total_value', 0) or 0)
            position_value = float(portfolio_info.get('position_value', 0) or 0)
            max_trade_amount = float(portfolio_info.get('max_trade_amount', balance) or balance)
            account_section = f"""
**ACCOUNT STATUS:**
- Available Cash: ${balance:.2f}
- Position Market Value: ${position_value:.2f}
- Total Equity: ${total_value:.2f}
- MAX_TRADE_AMOUNT (hard cap for this decision): ${max_trade_amount:.2f}
"""

        # 模型专属交易参数
        model_params_section = ""
        if model_trading_params:
            model_params_section_lines = [
                "**MODEL TRADING PARAMETERS:**",
                f"- Preferred Symbol: {model_trading_params.get('trade_symbol') or 'None'}",
                f"- Quantity: {model_trading_params.get('trade_quantity') if model_trading_params.get('trade_quantity') is not None else 'None'}",
                f"- Leverage: {model_trading_params.get('leverage') if model_trading_params.get('leverage') is not None else 'None'}x",
                f"- Side: {model_trading_params.get('trade_side') or 'None'} (LONG/SHORT)",
                f"- Close Price Upper (TP): {model_trading_params.get('close_price_upper') if model_trading_params.get('close_price_upper') is not None else 'None'}",
                f"- Close Price Lower (SL): {model_trading_params.get('close_price_lower') if model_trading_params.get('close_price_lower') is not None else 'None'}",
            ]
            model_params_section = "\n".join(model_params_section_lines)
        
        prompt = f"""
You are a professional quantitative trading analyst. Analyze the current market data and provide a trading decision.

**CURRENT MARKET DATA:**
{market_section}

{positions_section}

{risk_section}

{account_section}

{model_params_section}

**TRADING INSTRUCTIONS:**
- Analyze technical indicators (EMA, MACD, RSI)
- Consider price trends and momentum
- Identify the best trading opportunity among available symbols
- Strictly follow the risk control strategy outlined above
- Decide whether to BUY, SELL, or HOLD
  - Terminology (Chinese labels for leveraged trading):
    * BUY with leverage and direction LONG → "开多仓"
    * SELL with direction SHORT and no existing position → "开空仓"
    * SELL that closes an existing LONG or BUY that closes an existing SHORT → "平仓"
    * Non-leveraged opening → "开仓"

**OUTPUT REQUIREMENTS:**
IMPORTANT: You MUST return ONLY a valid JSON object, without any code blocks, markdown formatting, or additional text.

Return your response in this exact format:
{{
    "symbol": "{'|'.join(symbols)}|null",
    "action": "BUY|SELL|HOLD",
    "confidence": <number between 0.0 and 1.0>,
    "rationale": "<brief explanation in less than 50 characters>",
    "analysis": "<current analysis: positions, market, next steps, risk>",
    "trade": {{
        "quantity": <number>,
        "leverage": <integer>,
        "direction": "LONG|SHORT",  
        "entry_price": <number>,
        "close_price_upper": <number|null>,
        "close_price_lower": <number|null>
    }},
    "action_label": "开仓|开多仓|开空仓|平仓|观望"
}}

**STRICT RULES:**
1. symbol: Choose one of {', '.join(symbols)}, or null for no action
2. action: BUY (open long / close short), SELL (open short / close long), or HOLD
   When leverage is used, also set action_label as:
   - 开多仓: BUY with direction LONG and opening a new position
   - 开空仓: SELL with direction SHORT and opening a new position
   - 平仓: Closing an existing position (either side)
   - 开仓: Non-leveraged opening
   - 观望: HOLD
3. confidence: Your confidence in this decision (0.0 to 1.0)
4. rationale: Brief reasoning for your decision
5. analysis: Provide a concise paragraph including (positions analysis, market analysis, next action plan, risk management strategy)
5. trade: Provide full trade details. If action is HOLD, set trade to null or omit it.
6. DO NOT use markdown code blocks (```json or ```)
7. DO NOT include any explanatory text before or after the JSON
8. Return ONLY the raw JSON object starting with {{ and ending with }}
9. Make sure your response is valid JSON that can be parsed directly
10. IMPORTANT CONSTRAINT: Ensure (quantity * entry_price) <= MAX_TRADE_AMOUNT and <= Available Cash. If your initial plan exceeds this limit, you MUST reduce quantity accordingly.

Response:
"""
        return prompt
    
    def get_decision(self, market_data: Dict[str, float]) -> Dict[str, Any]:
        """
        获取交易决策
        
        Args:
            market_data: 市场数据
            
        Returns:
            解析后的决策字典
        """
        prompt = self.build_prompt(market_data)
        
        try:
            response = self.llm_adapter.call(prompt)
            return self.parse_decision(response)
        except Exception as e:
            print(f"❌ {self.model_name}决策获取失败: {e}")
            return self.get_default_decision()
    
    def parse_decision(self, response: str) -> Dict[str, Any]:
        """
        解析LLM响应
        
        Args:
            response: LLM响应文本
            
        Returns:
            解析后的决策字典
        """
        try:
            # 不再打印原始响应，避免日志噪音
            
            # 清理响应文本
            response = response.strip()
            
            # 移除 markdown 代码块标记
            if response.startswith('```json'):
                response = response[7:].strip()
            elif response.startswith('```'):
                response = response[3:].strip()
            
            if response.endswith('```'):
                response = response[:-3].strip()
            
            # 使用正则表达式提取完整的JSON对象（处理嵌套）
            import re
            
            # 找到第一个 { 的位置
            start_idx = response.find('{')
            if start_idx == -1:
                print(f"⚠️ [{self.model_name}] 未找到JSON开始标记")
                return self.get_default_decision()
            
            # 从第一个 { 开始，计算括号匹配
            brace_count = 0
            end_idx = -1
            
            for i in range(start_idx, len(response)):
                if response[i] == '{':
                    brace_count += 1
                elif response[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i
                        break
            
            if end_idx != -1:
                response = response[start_idx:end_idx + 1]
            
            # 尝试解析JSON
            decision = json.loads(response)
            
            # 验证必要字段
            required_fields = ['symbol', 'action', 'confidence', 'rationale']
            for field in required_fields:
                if field not in decision:
                    print(f"⚠️ [{self.model_name}] 决策缺少字段: {field}")
                    return self.get_default_decision()
            
            # 验证字段值
            if decision['action'] not in ['BUY', 'SELL', 'HOLD']:
                print(f"⚠️ [{self.model_name}] 无效的action: {decision['action']}")
                decision['action'] = 'HOLD'
            
            if not isinstance(decision['confidence'], (int, float)) or not (0 <= decision['confidence'] <= 1):
                print(f"⚠️ [{self.model_name}] 无效的confidence: {decision['confidence']}")
                decision['confidence'] = 0.5
            
            # 保留最小必要信息由上层汇总打印
            return decision
            
        except json.JSONDecodeError as e:
            print(f"❌ [{self.model_name}] JSON 解析失败: {e}")
            
            # 打印原始响应的前后50个字符
            full_response = response if response else "空响应"
            print(f"完整响应内容: {full_response}")
            
            return self.get_default_decision()
        except Exception as e:
            print(f"❌ [{self.model_name}] 决策解析失败: {e}")
            return self.get_default_decision()
    
    def get_default_decision(self) -> Dict[str, Any]:
        """获取默认决策"""
        return {
            "symbol": None,
            "action": "HOLD",
            "confidence": 0.0,
            "rationale": "解析失败，默认观望"
        }
    
    def format_decision_for_display(self, decision: Dict[str, Any]) -> str:
        """
        格式化决策用于显示
        
        Args:
            decision: 决策字典
            
        Returns:
            格式化的决策字符串
        """
        symbol = decision.get('symbol', 'None')
        action = decision.get('action', 'HOLD')
        confidence = decision.get('confidence', 0.0)
        rationale = decision.get('rationale', '无理由')
        
        return f"   决策: {action} {symbol}\n   信心: {confidence:.2f}\n   理由: {rationale}"
