# 📋 Alpha Arena 变更日志

所有重要的项目变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 新增
- 计划添加更多AI模型支持
- 计划添加定时执行功能
- 计划添加数据库存储

### 变更
- 暂无

### 修复
- 暂无

## [0.1.0] - 2024-01-15

### 新增
- 🚀 **最简化MVP实现**
- 📊 **真实价格获取**：基于Bitget API获取5个代币实时价格
- 🤖 **双AI决策对比**：OpenAI GPT-4 vs Claude-3-Sonnet
- 📈 **决策对比功能**：实时对比两个AI的交易决策
- ⚡ **极简架构**：无数据库、无界面、专注核心逻辑

### 技术特性
- **支持代币**：BTCUSDT, ETHUSDT, XRPUSDT, BNBUSDT, SOLUSDT
- **AI模型**：OpenAI GPT-4, Claude-3-Sonnet
- **价格源**：Bitget交易所实时API
- **输出格式**：JSON格式决策，命令行显示

### 使用方法
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置API密钥
cp env.example .env
# 编辑.env文件，填入API密钥

# 3. 运行程序
python main.py
```

### 环境要求
- Python 3.8+
- OpenAI API密钥
- Anthropic Claude API密钥
- Bitget API访问权限（可选，用于价格获取）

### 已知限制
- 仅支持现货价格获取
- 无账户管理和实际交易功能
- 无历史数据存储
- 无定时执行功能

---

## 版本说明

- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

## 贡献指南

提交变更时请：
1. 更新此CHANGELOG.md文件
2. 更新VERSION.md文件（如果适用）
3. 更新README.md中的版本信息
4. 确保所有测试通过
5. 更新相关文档
