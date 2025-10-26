#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alpha Arena MVP - 主程序
最简化的AI交易决策对比系统
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量（支持 .env 和 env 文件）
load_dotenv('.env')
if not os.getenv('BITGET_API_KEY'):
    load_dotenv('env')  # 如果没有 .env，尝试加载 env 文件

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.market import MarketData
from core.decision import DecisionMaker
from adapters.silicon_adapter import SiliconAdapter

def main():
    """主函数"""
    print("🚀 Alpha Arena - 最简化MVP")
    print("=" * 50)
    print(f"📅 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 初始化市场数据管理器
        print("📊 初始化市场数据管理器...")
        market_data = MarketData()
        
        if not market_data.is_api_available():
            print("❌ 交易所API不可用，请检查配置")
            return
        
        # 获取实时价格
        print("💰 获取实时价格...")
        prices = market_data.get_current_prices()
        
        print("\n📈 当前市场价格:")
        print(market_data.format_prices_for_display(prices))
        
        # 检查是否有有效价格
        valid_prices = {k: v for k, v in prices.items() if v > 0}
        if not valid_prices:
            print("❌ 没有获取到有效价格，请检查网络连接")
            return
        
        # 初始化LLM适配器
        print("\n🤖 初始化AI模型...")
        
        # 定义多个 SiliconFlow 模型
        # 模型格式：provider/model-name
        # 可在 https://siliconflow.cn 查看可用模型列表
        # 如需修改模型，请在此处添加或修改模型配置
        silicon_models = [
            ('qwen3', 'Qwen/Qwen3-32B'),  # Qwen3 模型
            ('deepseek', 'deepseek-ai/DeepSeek-R1'),  # DeepSeek 模型
            ('kimi', 'moonshotai/Kimi-K2-Instruct-0905')  # Kimi 模型
        ]
        
        silicon_decision_makers = {}
        for model_name, model_id in silicon_models:
            try:
                adapter = SiliconAdapter(model=model_id)
                decision_maker = DecisionMaker(adapter)
                silicon_decision_makers[model_name] = decision_maker
                print(f"✅ {model_name} ({adapter.get_model_name()}) 初始化成功")
            except Exception as e:
                print(f"❌ {model_name}初始化失败: {e}")
                silicon_decision_makers[model_name] = None
        
        # 检查是否有可用的模型
        available_models = sum([
            1 for dm in silicon_decision_makers.values() if dm is not None
        ])
        
        if available_models == 0:
            print("❌ 没有可用的AI模型，请检查SiliconFlow API密钥配置")
            return
        
        # 获取AI决策
        print("\n🧠 获取AI交易决策...")
        
        decisions = {}
        
        # SiliconFlow 模型决策（多个模型）
        for model_name, decision_maker in silicon_decision_makers.items():
            if decision_maker:
                print(f"\n🤖 {model_name.upper()}决策:")
                try:
                    decision = decision_maker.get_decision(prices)
                    decisions[model_name] = decision
                    print(decision_maker.format_decision_for_display(decision))
                except Exception as e:
                    print(f"❌ {model_name}决策获取失败: {e}")
        
        # 决策对比
        if len(decisions) >= 1:
            print("\n📊 决策对比:")
            print("-" * 50)
            
            for model_name, decision in decisions.items():
                symbol = decision.get('symbol', 'None')
                action = decision.get('action', 'HOLD')
                confidence = decision.get('confidence', 0)
                print(f"   {model_name:15} {action:6} {symbol:10} (信心: {confidence}%)")
            
            # 统计一致性
            print("\n📈 一致性分析:")
            symbols = [d.get('symbol') for d in decisions.values() if d.get('symbol')]
            actions = [d.get('action') for d in decisions.values() if d.get('action')]
            
            unique_symbols = set(filter(None, symbols))
            unique_actions = set(filter(None, actions))
            
            if len(unique_symbols) == 1 and len(unique_actions) == 1:
                print(f"   🎯 所有模型达成一致: {unique_actions.pop()} {unique_symbols.pop()}")
            else:
                print(f"   ⚡ 模型意见分歧")
                print(f"      - 推荐代币: {list(unique_symbols) if unique_symbols else 'None'}")
                print(f"      - 推荐操作: {list(unique_actions) if unique_actions else 'None'}")
        
        print("\n✅ 运行完成！")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断程序")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
