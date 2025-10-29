# Alpha Arena 部署指南

## 前置要求

1. Docker 和 Docker Compose
2. Git
3. API 密钥：
   - SiliconFlow API Key
   - Bitget API Key, Secret Key, Passphrase

## 快速部署

### 1. 克隆项目

```bash
git clone https://github.com/Laurel-rao/alpha-arena.git
cd alpha-arena
```

### 2. 配置环境变量

复制 env.example 为 .env 并填入真实 API 密钥：

```bash
cp env.example .env
```

编辑 `.env` 文件：
```bash
SILICONFLOW_API_KEY=your_siliconflow_api_key
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
BITGET_API_KEY=your_bitget_api_key
BITGET_SECRET_KEY=your_bitget_secret_key
BITGET_PASSPHRASE=your_bitget_passphrase
```

### 3. 启动服务

使用 Docker Compose 一键启动所有服务：

```bash
docker-compose up -d
```

服务将在以下端口启动：
- 后端 API: http://localhost:8000
- 前端界面: http://localhost:3000
- 数据库: localhost:5432

### 4. 初始化数据库

进入后端容器执行数据库迁移：

```bash
docker exec -it alpha_arena_backend alembic upgrade head
```

### 5. 访问应用

- 前端：http://localhost:3000
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## 本地开发

### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export DATABASE_URL="postgresql://arena_user:password@localhost:5432/alpha_arena"

# 运行数据库迁移
alembic upgrade head

# 启动服务
python run.py
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 日志查看

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 停止服务

```bash
docker-compose down
```

## 数据备份

PostgreSQL 数据保存在 Docker volume 中，备份方法：

```bash
# 备份
docker exec alpha_arena_postgres pg_dump -U arena_user alpha_arena > backup.sql

# 恢复
docker exec -i alpha_arena_postgres psql -U arena_user alpha_arena < backup.sql
```

## 故障排除

### 数据库连接失败

检查 PostgreSQL 容器是否正常运行：
```bash
docker-compose ps
docker-compose logs postgres
```

### API 密钥错误

确保 `.env` 文件中的 API 密钥正确，并重启容器：
```bash
docker-compose restart backend
```

### 端口冲突

如果端口被占用，修改 `docker-compose.yml` 中的端口映射。

