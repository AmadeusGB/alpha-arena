# 🎉 Alpha Arena 完整使用指南

## ✅ 项目已完成

### 核心功能

1. **后端服务** ✅
   - FastAPI + PostgreSQL
   - 9个数据库表
   - RESTful API
   - 定时任务调度器
   - 3个AI模型支持

2. **前端应用** ✅
   - Next.js 14 + TypeScript
   - Tailwind CSS
   - Recharts 图表
   - 3个核心页面

3. **定时交易** ✅
   - 每5分钟自动执行
   - 获取价格 → AI决策 → 模拟交易
   - 完整的日志记录

## 🚀 启动项目

### 1. 启动后端

```bash
cd backend
source ../.venv/bin/activate
python run.py
```

启动后会看到：
```
✅ 定时任务调度器已启动 (每 5 分钟执行一次)
```

### 2. 访问应用

- **仪表盘**: http://localhost:3000
- **模型对比**: http://localhost:3000/models  
- **系统管理**: http://localhost:3000/system
- **API 文档**: http://localhost:8000/docs

## 📊 页面功能

### 1. 仪表盘 (/)

**功能**:
- 实时市场价格显示
- 模型投资组合概览
- 总资产、盈亏、收益率
- 自动刷新（30秒）

**显示内容**:
- BTCUSDT, ETHUSDT, XRPUSDT, BNBUSDT, SOLUSDT 价格
- 每个模型的总资产和盈亏
- 运行状态

### 2. 模型对比 (/models)

**左侧 - K线图**:
- 所有模型的净值曲线对比
- 30天历史数据
- 交互式提示
- 图例显示

**右侧 - 模型详情**:
- 模型选择器（点击切换）
- Tabs:
  - **交易历史**: 决策记录列表
  - **聊天记录**: Prompt 和 Response
  - **当前仓位**: 持仓详情和盈亏

### 3. 系统管理 (/system)

**功能**:
- 调度器状态监控
- 手动控制（启动/停止）
- 错误计数显示
- 数据库连接状态
- 最新日志查看

## ⚙️ 定时任务说明

### 执行流程

1. **获取价格** (00:00)
   - 调用 Bitget API
   - 保存到数据库

2. **AI 决策** (00:05)
   - 为 qwen3, deepseek, kimi 生成决策
   - 保存决策和对话记录

3. **执行交易** (00:10)
   - 根据决策模拟交易
   - 更新持仓和账户

4. **记录日志** (00:15)
   - 记录所有操作

### 配置

在 `backend/.env`:
```env
SCHEDULER_ENABLED=true              # 启用调度器
SCHEDULER_INTERVAL_MINUTES=5        # 间隔（分钟）
INITIAL_CAPITAL=10000.0             # 初始资金
```

### 控制

**启动调度器**:
```bash
curl -X POST http://localhost:8000/api/v1/system/scheduler/start
```

**停止调度器**:
```bash
curl -X POST http://localhost:8000/api/v1/system/scheduler/stop
```

**查看状态**:
```bash
curl http://localhost:8000/api/v1/system/status
```

## 📈 数据流

```
市场价格 (Bitget API)
    ↓
保存到 market_prices 表
    ↓
AI 模型决策 (qwen3, deepseek, kimi)
    ↓
保存到 decisions 和 conversations 表
    ↓
模拟交易执行
    ↓
更新 positions, trades 表
    ↓
更新 model_portfolios 表
    ↓
记录到 system_logs 表
```

## 🎯 关键 API

### 市场数据
- `GET /api/v1/market/prices/latest` - 最新价格
- `GET /api/v1/market/prices/history` - 历史价格
- `POST /api/v1/market/prices/refresh` - 手动刷新

### 决策管理
- `GET /api/v1/decisions` - 决策历史
- `POST /api/v1/decisions/trigger` - 手动触发决策
- `GET /api/v1/decisions/compare` - 决策对比

### 投资组合
- `GET /api/v1/portfolios` - 所有模型账户
- `GET /api/v1/portfolios/{model_name}` - 特定模型
- `GET /api/v1/portfolios/{model_name}/performance` - 绩效

### 系统管理
- `GET /api/v1/system/status` - 系统状态
- `POST /api/v1/system/scheduler/start` - 启动调度器
- `POST /api/v1/system/scheduler/stop` - 停止调度器
- `GET /api/v1/system/logs` - 系统日志

## 🔧 常见问题

### 1. 模型初始化失败

**问题**: SiliconFlow 初始化失败
**解决**: 已修复，确保 API 密钥正确

### 2. 定时任务未运行

**检查**:
```bash
curl http://localhost:8000/api/v1/system/status
```

**解决**: 确保 `SCHEDULER_ENABLED=true`

### 3. 无数据显示

**初始化数据**:
```bash
cd backend
python init_test_data.py
```

### 4. 端口冲突

**修改端口**:
- 后端: 修改 `backend/run.py` 中的端口
- 前端: 修改 `docker-compose.yml`

## 📚 文件结构

```
alpha-arena/
├── backend/
│   ├── app/
│   │   ├── api/              # API 路由
│   │   ├── services/          # 业务逻辑
│   │   ├── models/            # 数据库模型
│   │   ├── schemas/           # Pydantic 模型
│   │   └── core/              # 核心组件
│   ├── .env                   # 环境变量
│   ├── run.py                 # 启动脚本
│   └── requirements.txt       # 依赖
├── frontend/
│   ├── app/                   # Next.js 页面
│   ├── components/            # React 组件
│   ├── lib/                   # API 客户端
│   └── types/                 # TypeScript 类型
└── docker-compose.yml         # Docker 配置
```

## 🎊 项目亮点

1. **完整架构**: 前后端分离，API 驱动
2. **实时数据**: 定时更新，自动执行
3. **多模型对比**: 支持多个 AI 模型
4. **可视化**: 图表展示，直观易懂
5. **可控制**: 手动触发，随时监控
6. **完整记录**: 所有操作都有日志

## 📝 下一步优化

1. WebSocket 实时推送
2. 更多图表类型
3. 数据导出功能
4. 策略回测
5. 风险控制增强

**项目已完成并可以正常使用！** 🎉

