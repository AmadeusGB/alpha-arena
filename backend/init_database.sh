#!/bin/bash
# 数据库初始化脚本

echo "=== Alpha Arena 数据库初始化 ==="

# 加载环境变量
export DATABASE_URL=postgresql://postgres:POSTGRESQL_PASSWORD@localhost:5433/alpha_arena

# 创建数据库（如果不存在）
echo "检查数据库..."
PGPASSWORD=POSTGRESQL_PASSWORD psql -h localhost -U postgres -c "CREATE DATABASE alpha_arena;" 2>/dev/null || echo "数据库已存在"

# 生成 Alembic 迁移
echo "生成数据库迁移..."
alembic revision --autogenerate -m "Initial migration"

# 运行迁移
echo "运行数据库迁移..."
alembic upgrade head

echo "=== 数据库初始化完成 ==="

