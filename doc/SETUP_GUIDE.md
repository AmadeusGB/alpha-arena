# Alpha Arena 项目设置指南

## 已完成的配置

### 1. 数据库配置 ✅
- **数据库名**: alpha_arena
- **地址**: localhost:5432
- **用户**: postgres
- **密码**: POSTGRESQL_PASSWORD
- **状态**: 数据库已创建

### 2. 后端配置 ✅
- FastAPI 应用结构完成
- 所有模型和服务已实现
- Alembic 配置完成
- API 路由全部实现

### 3. 前端配置 ✅
- Next.js 14 项目已创建
- TypeScript 配置完成
- API 客户端已实现

## 下一步操作

### 1. 安装后端依赖

```bash
cd backend

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
cd backend

# 方式1：使用脚本
./init_database.sh

# 方式2：手动执行
source venv/bin/activate
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 3. 启动后端服务

```bash
cd backend

# 使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 或使用启动脚本
python run.py
```

访问 http://localhost:8000/docs 查看 API 文档

### 4. 启动前端服务

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:3000

## 环境变量

后端环境变量文件：`backend/.env`

```env
DATABASE_URL=postgresql://postgres:POSTGRESQL_PASSWORD@localhost:5432/alpha_arena
SILICONFLOW_API_KEY=your_api_key
BITGET_API_KEY=your_api_key
BITGET_SECRET_KEY=your_secret_key
BITGET_PASSPHRASE=your_passphrase
```

## 使用 Docker

### 启动所有服务

```bash
docker-compose up -d
```

### 初始化数据库（Docker 环境）

```bash
docker exec -it alpha_arena_backend alembic upgrade head
```

### 查看日志

```bash
docker-compose logs -f
```

## 常见问题

### 1. 数据库连接失败

检查 PostgreSQL 是否运行：
```bash
pg_isready -h localhost -p 5432
```

### 2. 端口冲突

修改 `docker-compose.yml` 中的端口映射

### 3. 导入错误

确保在虚拟环境中运行，并安装所有依赖

## API 端点

启动后端后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## 技术支持

如有问题，请查看：
- `STATUS.md` - 项目进度
- `PROGRESS.md` - 详细进展
- `backend/README.md` - 后端文档
- `DEPLOYMENT.md` - 部署指南
