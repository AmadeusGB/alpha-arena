# Alpha Arena Backend

FastAPI 后端服务，提供 AI 交易决策系统的 API 和数据管理。

## 功能特性

- ✅ 市场价格数据获取和持久化
- ✅ 多模型 AI 决策生成
- ✅ 投资组合管理和持仓跟踪
- ✅ 定时任务调度（每5分钟执行一次）
- ✅ RESTful API
- ✅ PostgreSQL 数据库支持

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入配置：

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/alpha_arena
SILICONFLOW_API_KEY=your_api_key
BITGET_API_KEY=your_api_key
BITGET_SECRET_KEY=your_secret_key
BITGET_PASSPHRASE=your_passphrase
```

### 3. 初始化数据库

```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 4. 运行服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要 API 端点

- `GET /api/v1/market/prices/latest` - 最新价格
- `GET /api/v1/decisions` - 决策历史
- `POST /api/v1/decisions/trigger` - 手动触发决策
- `GET /api/v1/portfolios` - 投资组合状态
- `GET /api/v1/positions` - 持仓列表
- `GET /api/v1/system/status` - 系统状态
- `POST /api/v1/system/scheduler/start` - 启动定时任务

## 项目结构

```
backend/
├── app/
│   ├── api/           # API 路由
│   ├── models/        # SQLAlchemy 模型
│   ├── schemas/       # Pydantic 模型
│   ├── services/      # 业务逻辑
│   ├── core/          # 核心组件（适配器）
│   └── main.py        # 应用入口
├── alembic/           # 数据库迁移
└── requirements.txt   # 依赖列表

