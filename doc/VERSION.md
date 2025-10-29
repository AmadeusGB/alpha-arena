# 📊 Alpha Arena 版本信息

## 当前版本：v0.1.0 (MVP)

**发布日期**：2024-01-15  
**版本类型**：最小可行产品 (MVP)  
**状态**：开发中

---

## 🎯 版本目标

本版本的目标是验证核心概念：
- AI模型能否基于真实市场价格给出合理交易决策
- 不同AI模型的决策差异和一致性
- 端到端的价格获取到决策输出流程

---

## ✨ 核心功能

### 📊 市场数据
- **价格源**：Bitget交易所实时API
- **支持代币**：5个主流加密货币
  - BTCUSDT (比特币)
  - ETHUSDT (以太坊)
  - XRPUSDT (瑞波币)
  - BNBUSDT (币安币)
  - SOLUSDT (索拉纳)

### 🤖 AI决策引擎
- **OpenAI GPT-4**：强大的语言理解和推理能力
- **Claude-3-Sonnet**：Anthropic的先进AI模型
- **决策格式**：结构化JSON输出
- **决策类型**：BUY/SELL/HOLD + 信心度 + 理由

### 📈 对比分析
- **实时对比**：同时获取两个AI的决策
- **一致性检查**：分析决策是否一致
- **信心度对比**：比较决策信心水平

---

## 🚀 快速开始

### 1. 环境准备
```bash
# Python版本要求
python --version  # 需要 3.8+

# 克隆项目
git clone https://github.com/AmadeusGB/alpha-arena.git
cd alpha-arena
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置API密钥
```bash
# 复制环境变量模板
cp env.example .env

# 编辑.env文件，填入你的API密钥
# OPENAI_API_KEY=your_openai_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 4. 运行程序
```bash
python main.py
```

---

## 📋 使用示例

### 预期输出
```
🚀 Alpha Arena - 最简化MVP
==================================================
📅 运行时间: 2024-01-15 14:30:25

📊 初始化市场数据管理器...
✅ Bitget API客户端初始化成功
💰 获取实时价格...
✅ BTCUSDT: $45123.4500
✅ ETHUSDT: $3198.7600
✅ XRPUSDT: $0.5234
✅ BNBUSDT: $312.4500
✅ SOLUSDT: $98.7600

📈 当前市场价格:
   BTCUSDT: $45123.4500
   ETHUSDT: $3198.7600
   XRPUSDT: $0.5234
   BNBUSDT: $312.4500
   SOLUSDT: $98.7600

🤖 初始化AI模型...
✅ OpenAI (GPT-4) 初始化成功
✅ Claude (Claude-3-Sonnet) 初始化成功

🧠 获取AI交易决策...

🤖 OpenAI决策:
   决策: BUY BTCUSDT
   信心: 0.85
   理由: BTC价格回调，技术指标显示超卖

🤖 Claude决策:
   决策: HOLD
   信心: 0.65
   理由: 市场波动较大，建议观望

📊 决策对比:
------------------------------
   OpenAI: BUY BTCUSDT
   Claude: HOLD
   ⚡ 两个AI意见分歧

✅ 运行完成！
```

---

## 🔧 技术架构

### 项目结构
```
alpha-arena/
├── core/                   # 核心业务逻辑
│   ├── market.py          # 市场数据管理
│   └── decision.py        # 决策引擎
├── adapters/              # 外部接口适配器
│   ├── llm_base.py        # LLM基类
│   ├── openai_adapter.py  # OpenAI适配器
│   ├── claude_adapter.py  # Claude适配器
│   └── exchange_api.py    # 交易所API适配器
├── main.py                # 主程序入口
├── requirements.txt       # 依赖包列表
└── env.example           # 环境变量模板
```

### 技术栈
- **语言**：Python 3.8+
- **AI模型**：OpenAI GPT-4, Claude-3-Sonnet
- **价格源**：Bitget API
- **依赖管理**：pip + requirements.txt
- **配置管理**：python-dotenv

---

## ⚠️ 已知限制

### 功能限制
- ❌ 无实际交易功能（仅决策对比）
- ❌ 无账户管理
- ❌ 无历史数据存储
- ❌ 无定时执行
- ❌ 无风险控制

### 技术限制
- 🔄 依赖外部API（网络连接要求）
- 🔑 需要有效的API密钥
- 📊 仅支持现货价格
- 🎯 决策格式固定（JSON）

---

## 🛠️ 故障排除

### 常见问题

#### 1. API密钥错误
```
❌ OpenAI API密钥未设置，请设置OPENAI_API_KEY环境变量
```
**解决方案**：检查.env文件中的API密钥是否正确

#### 2. 网络连接问题
```
❌ 获取BTCUSDT价格失败: 网络请求失败
```
**解决方案**：检查网络连接，确认可以访问Bitget API

#### 3. 依赖包缺失
```
❌ 请安装openai: pip install openai
```
**解决方案**：运行 `pip install -r requirements.txt`

### 调试模式
```bash
# 启用详细日志
export DEBUG=1
python main.py
```

---

## 📈 性能指标

### 响应时间
- **价格获取**：< 2秒（5个代币）
- **AI决策**：< 10秒（每个模型）
- **总运行时间**：< 30秒

### 成功率
- **价格获取成功率**：> 95%
- **AI决策成功率**：> 90%
- **整体运行成功率**：> 85%

---

## 🔮 下个版本计划

### v0.2.0 (计划中)
- 🕐 **定时执行**：5分钟周期自动运行
- 💾 **数据存储**：SQLite数据库存储历史决策
- 📊 **简单Dashboard**：Streamlit可视化界面
- 🛡️ **基础风控**：决策验证和过滤

### v0.3.0 (规划中)
- 🏦 **账户管理**：模拟交易账户
- 📈 **更多代币**：支持10+个代币
- 🤖 **更多AI模型**：集成更多LLM
- 📊 **性能分析**：决策准确率统计

---

## 📞 支持与反馈

- **问题报告**：[GitHub Issues](https://github.com/AmadeusGB/alpha-arena/issues)
- **功能建议**：[GitHub Discussions](https://github.com/AmadeusGB/alpha-arena/discussions)
- **文档更新**：欢迎提交PR改进文档

---

**注意**：本版本为MVP阶段，仅供概念验证使用，不构成投资建议。
