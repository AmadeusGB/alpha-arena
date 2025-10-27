# Alpha Arena 快速启动指南

## ✅ 已完成的配置

1. **数据库配置完成**
   - 数据库：alpha_arena
   - 连接：localhost:5432
   - 用户：postgres
   - 密码：POSTGRESQL_PASSWORD
   - ✅ 所有表已创建

2. **后端代码完成**
   - ✅ 所有 API 路由实现
   - ✅ 数据库模型定义
   - ✅ 服务层实现

3. **依赖安装完成**
   - ✅ 虚拟环境已创建 (.venv)
   - ✅ 所有 Python 包已安装

## 🚀 启动步骤

### 1. 启动后端服务

```bash
cd backend

# 激活虚拟环境
source ../.venv/bin/activate

# 启动服务
python run.py
```

服务将在 http://localhost:8000 启动

### 2. 测试 API

访问以下地址：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

### 3. 启动前端（可选）

```bash
cd frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:3000 启动

## 📊 数据库表结构

已创建以下表：
- `market_prices` - 市场价格
- `decisions` - AI决策记录
- `conversations` - 对话历史
- `model_portfolios` - 模型账户
- `positions` - 持仓记录
- `trades` - 交易记录
- `system_logs` - 系统日志
- `strategy_configs` - 策略配置

## 🔧 常用命令

### 数据库操作

```bash
# 查看数据库表
PGPASSWORD=POSTGRESQL_PASSWORD psql -h localhost -U postgres -d alpha_arena -c "\dt"

# 备份数据库
PGPASSWORD=POSTGRESQL_PASSWORD pg_dump -h localhost -U postgres alpha_arena > backup.sql

# 查看最新数据
PGPASSWORD=POSTGRESQL_PASSWORD psql -h localhost -U postgres -d alpha_arena -c "SELECT * FROM market_prices ORDER BY timestamp DESC LIMIT 10;"
```

### 数据库迁移

```bash
# 创建新迁移
alembic revision --autogenerate -m "描述信息"

# 应用迁移
alembic upgrade head

# 回退迁移
alembic downgrade -1
```

## 🐛 故障排除

### 后端无法启动

1. 检查环境变量：
```bash
cat backend/.env
```

2. 检查数据库连接：
```bash
PGPASSWORD=POSTGRESQL_PASSWORD psql -h localhost -U postgres -c "SELECT 1;"
```

3. 检查端口占用：
```bash
lsof -i :8000
```

### 数据库连接失败

确保 PostgreSQL 正在运行：
```bash
pg_isready -h localhost -p 5432
```

### Import 错误

激活虚拟环境：
```bash
source .venv/bin/activate
```

## 📝 下一步

1. **开发前端页面** - 创建仪表盘和市场数据页面
2. **集成定时任务** - 配置 APScheduler 自动运行
3. **完善 API** - 添加更多功能和错误处理
4. **前端组件** - 开发可视化组件

## 🔗 相关文档

- `SETUP_GUIDE.md` - 详细设置指南
- `STATUS.md` - 项目进度
- `DEPLOYMENT.md` - 部署指南
- `backend/README.md` - 后端文档

