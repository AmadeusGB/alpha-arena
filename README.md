# 🧠 Alpha Arena

> 一个让 AI 模型在真实市场中进行实盘交易与对抗的实验平台。  
> "让智能体在不确定性中生存，并最终学会盈利。"

[![Version](https://img.shields.io/badge/version-v0.1.0--MVP-blue.svg)](VERSION.md)
[![Status](https://img.shields.io/badge/status-开发中-yellow.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](backend/requirements.txt)
[![Next.js](https://img.shields.io/badge/next.js-14+-black.svg)](frontend/package.json)

---

## 📘 项目简介

**Alpha Arena** 是一个以真实市场为测试场的 AI 智能体交易实验平台。  
每个模型（如 GPT-4、Claude、DeepSeek、Qwen、Kimi 等）都会获得相同的实时市场数据与初始资金，独立决策、执行交易，并实时比较收益、回撤和风险控制能力。

### 🎯 核心功能

1. **实时市场数据**：从 Bitget 交易所获取 BTCUSDT、ETHUSDT 等代币的实时价格
2. **多模型决策**：支持多个 AI 模型（SiliconFlow 适配的 Qwen、DeepSeek、Kimi 等）同时生成交易决策
3. **独立投资组合**：每个模型拥有独立的资金账户和持仓
4. **实时监控**：可视化仪表盘显示市场数据、模型表现和系统状态
5. **定时调度**：每 5 分钟自动执行一次交易决策流程

---

## 🏗️ 项目架构

```
alpha-arena/
├── backend/                    # 后端服务
│   ├── app/                   # 应用主代码
│   │   ├── api/              # API 路由
│   │   │   ├── decisions.py  # 决策 API
│   │   │   ├── market.py     # 市场数据 API
│   │   │   ├── portfolios.py # 投资组合 API
│   │   │   ├── positions.py  # 持仓 API
│   │   │   └── system.py     # 系统管理 API
│   │   ├── core/             # 核心业务逻辑
│   │   │   ├── adapters/     # 适配器
│   │   │   │   ├── silicon_adapter.py  # SiliconFlow 适配
│   │   │   │   ├── exchange_api.py     # 交易所 API
│   │   │   │   └── llm_base.py         # LLM 基类
│   │   │   ├── decision.py   # 决策生成
│   │   │   └── market.py     # 市场数据处理
│   │   ├── models/           # 数据库模型
│   │   ├── schemas/          # Pydantic 模式
│   │   ├── services/         # 业务服务
│   │   │   ├── decision_service.py    # 决策服务
│   │   │   ├── market_service.py      # 市场服务
│   │   │   ├── portfolio_service.py   # 投资组合服务
│   │   │   └── scheduler_service.py   # 调度器服务
│   │   ├── config.py         # 配置管理
│   │   ├── database.py       # 数据库连接
│   │   └── main.py           # FastAPI 应用入口
│   ├── alembic/              # 数据库迁移
│   ├── Dockerfile            # Docker 镜像
│   ├── requirements.txt      # Python 依赖
│   └── init_database.sh      # 数据库初始化脚本
├── frontend/                  # 前端服务
│   ├── app/                  # Next.js 应用
│   │   ├── page.tsx         # 首页（市场与模型表现）
│   │   ├── models/          # 模型页面
│   │   └── system/          # 系统管理页面
│   ├── components/           # React 组件
│   ├── lib/                  # 工具库
│   │   └── api.ts           # API 客户端
│   ├── types/                # TypeScript 类型
│   ├── package.json         # 依赖管理
│   └── next.config.js       # Next.js 配置
├── docker-compose.yml        # Docker Compose 配置
├── env.example              # 环境变量示例
└── README.md                # 项目说明
```

### 📋 服务职责

| 模块 | 说明 |
|------|------|
| **Market Service** | 从 Bitget API 获取实时价格数据 |
| **Decision Service** | 调用多个 LLM 模型生成交易决策 |
| **Portfolio Service** | 管理每个模型的资金账户和持仓 |
| **Scheduler Service** | 定时执行交易决策流程 |
| **Position Service** | 处理开仓、平仓等操作 |
| **Frontend Dashboard** | 实时监控市场数据、模型表现和系统状态 |

---

## ⚙️ 技术栈

### 后端
- **Python 3.9+**
- **FastAPI** - 高性能 Web 框架
- **SQLAlchemy** - ORM
- **Alembic** - 数据库迁移
- **APScheduler** - 定时任务
- **PostgreSQL** - 数据库
- **OpenAI SDK** - LLM 调用

### 前端
- **Next.js 14** - React 框架
- **TypeScript** - 类型安全
- **Tailwind CSS** - 样式框架
- **React Hooks** - 状态管理

### 基础设施
- **Docker** - 容器化
- **Bitget API** - 加密货币交易所
- **SiliconFlow** - LLM 服务（支持 Qwen、DeepSeek、Kimi 等）

---

## 🚀 快速开始

### 前置要求

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 数据库

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/yourusername/alpha-arena.git
cd alpha-arena
```

#### 2. 配置环境变量

```bash
cp env.example .env
```

编辑 `.env` 文件，填入必要的 API 密钥：

```env
# 数据库配置
DATABASE_URL=postgresql://postgres:POSTGRESQL_PASSWORD@localhost:5433/alpha_arena

# SiliconFlow API
SILICONFLOW_API_KEY=your_siliconflow_api_key
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1

# Bitget API（可选）
BITGET_API_KEY=your_bitget_api_key
BITGET_SECRET_KEY=your_bitget_secret_key
BITGET_PASSPHRASE=your_bitget_passphrase
```

#### 3. 启动数据库

```bash
docker-compose up -d postgres
```

#### 4. 初始化数据库

```bash
cd backend
source ../.venv/bin/activate  # 如果有虚拟环境
export DATABASE_URL=postgresql://postgres:POSTGRESQL_PASSWORD@localhost:5433/alpha_arena
alembic upgrade head
```

或者使用自动化脚本：

```bash
bash init_database.sh
```

#### 5. 启动后端服务

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端将在 http://localhost:8000 运行

#### 6. 启动前端服务

```bash
cd frontend
npm install
npm run dev
```

前端将在 http://localhost:3000 运行

### Docker 部署（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 📊 核心功能

### 1. 实时市场数据

- 获取 BTCUSDT、ETHUSDT、XRPUSDT、BNBUSDT、SOLUSDT 的实时价格
- 自动定时刷新（每 30 秒）
- 历史价格数据存储

### 2. 多模型决策

当前支持的模型：
- **Qwen3** (Qwen/Qwen3-32B)
- **DeepSeek** (deepseek-ai/DeepSeek-R1)
- **Kimi** (moonshotai/Kimi-K2-Instruct-0905)

每个模型独立生成交易决策，对比表现差异。

### 3. 投资组合管理

- 每个模型拥有独立的资金账户（初始 10,000 USDT）
- 实时计算总资产、盈亏、收益率
- 跟踪最大回撤、Sharpe 比率等指标

### 4. 定时调度

- 每 5 分钟自动执行一次
- 自动获取市场数据
- 调用所有模型生成决策
- 更新持仓和账户状态

### 5. 实时监控

- **市场页面**：显示实时价格和模型表现
- **模型页面**：详细的模型决策历史
- **系统管理页面**：调度器控制和系统状态

---

## 🔧 配置说明

### 后端配置

编辑 `backend/app/config.py`：

```python
# API配置
API_V1_PREFIX: str = "/api/v1"

# 任务调度配置
SCHEDULER_ENABLED: bool = True
SCHEDULER_INTERVAL_MINUTES: int = 5

# 初始资金
INITIAL_CAPITAL: float = 10000.0

# 支持的交易对
TRADING_PAIRS: list = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "BNBUSDT", "SOLUSDT"]
```

### 前端配置

编辑 `frontend/next.config.js`：

```javascript
env: {
  NEXT_PUBLIC_API_URL: 'http://localhost:8000/api/v1',
}
```

---

## 📡 API 文档

启动后端服务后，访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要 API 端点

#### 市场数据
- `GET /api/v1/market/prices/latest` - 获取最新价格
- `GET /api/v1/market/prices/history` - 获取历史价格

#### 投资组合
- `GET /api/v1/portfolios` - 获取所有投资组合
- `GET /api/v1/portfolios/{model_name}` - 获取特定模型组合

#### 决策
- `GET /api/v1/decisions` - 获取决策历史
- `GET /api/v1/decisions/{decision_id}` - 获取决策详情

#### 持仓
- `GET /api/v1/positions` - 获取所有持仓
- `GET /api/v1/positions?model_name={name}` - 获取特定模型持仓

#### 系统管理
- `GET /api/v1/system/status` - 获取系统状态
- `POST /api/v1/system/scheduler/start` - 启动调度器
- `POST /api/v1/system/scheduler/stop` - 停止调度器

---

## 🛡️ 安全与合规

- **只读 API**：Bitget API 使用只读权限
- **隔离账户**：每个模型独立资金账户
- **安全配置**：敏感信息通过环境变量管理
- **日志审计**：完整的操作日志记录

---

## 🔮 未来规划

### 短期（1-2 个月）
- [ ] 支持更多交易所（OKX、Binance）
- [ ] 添加更多交易策略
- [ ] 完善风控系统
- [ ] 性能优化

### 中期（3-6 个月）
- [ ] 支持杠杆和做空
- [ ] 回测功能
- [ ] 策略回放
- [ ] 实时告警

### 长期（6+ 个月）
- [ ] AI 策略自动优化
- [ ] 多时间框架分析
- [ ] 社群治理
- [ ] 商业化

---

## 📄 许可

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📮 联系方式

- **GitHub**: https://github.com/yourusername/alpha-arena
- **邮箱**: your.email@example.com

---

**Happy Trading! 📈**
