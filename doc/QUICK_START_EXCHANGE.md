# 交易所快速开始指南

## 环境配置

### 1. 安装依赖

系统已包含所需的依赖包，无需额外安装。

### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```bash
# 选择默认交易所 (BITGET/OKX/BINANCE)
DEFAULT_EXCHANGE=BITGET

# Bitget API 配置
BITGET_API_KEY=your_bitget_api_key
BITGET_SECRET_KEY=your_bitget_secret_key
BITGET_PASSPHRASE=your_bitget_passphrase

# OKX API 配置
OKX_API_KEY=your_okx_api_key
OKX_SECRET_KEY=your_okx_secret_key
OKX_PASSPHRASE=your_okx_passphrase

# Binance API 配置
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
```

### 3. 创建 API 密钥

#### Bitget

1. 登录 [Bitget 官网](https://www.bitget.com/)
2. 进入"账户管理" → "API 管理"
3. 创建新的 API Key
4. 设置 API 权限（建议：只读/交易，不要勾选提现）
5. 记录 API Key、Secret Key、Passphrase

#### OKX

1. 登录 [OKX 官网](https://www.okx.com/)
2. 进入"个人中心" → "API"
3. 创建 API Key
4. 设置权限（建议：只读/交易）
5. 记录 API Key、Secret Key、Passphrase

#### Binance

1. 登录 [Binance 官网](https://www.binance.com/)
2. 进入"API 管理"
3. 创建新的 API Key
4. 设置权限（建议：只启用现货交易）
5. 记录 API Key、Secret Key

## 使用示例

### 基本用法

```python
from adapters.exchange_api import ExchangeAPI

# 初始化默认交易所
exchange = ExchangeAPI()

# 获取单个价格
price = exchange.get_single_price('BTCUSDT')
print(f"BTC 当前价格: ${price}")

# 批量获取价格
symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
prices = exchange.get_latest_prices(symbols)
for symbol, price in prices.items():
    print(f"{symbol}: ${price:.4f}")
```

### 切换交易所

```python
from adapters.exchange_api import ExchangeAPI

# 使用 Bitget
bitget = ExchangeAPI('BITGET')

# 使用 OKX
okx = ExchangeAPI('OKX')

# 使用 Binance
binance = ExchangeAPI('BINANCE')
```

### 获取账户信息

```python
# 获取账户余额
account_info = exchange.get_account_info()
print(f"账户信息: {account_info}")

# 获取持仓
positions = exchange.get_positions()
print(f"持仓信息: {positions}")
```

### 下单示例

```python
# 买入 BTC 限价单
order = exchange.client.place_order(
    symbol='BTCUSDT',
    side='BUY',
    order_type='LIMIT',
    quantity=0.001,
    price=50000
)
print(f"订单ID: {order.get('orderId')}")

# 卖出 ETH 市价单
order = exchange.client.place_order(
    symbol='ETHUSDT',
    side='SELL',
    order_type='MARKET',
    quantity=0.1
)
print(f"订单ID: {order.get('orderId')}")
```

### 合约交易示例

```python
# 开多仓（10倍杠杆）
order = exchange.client.place_order(
    symbol='BTCUSDT',
    side='BUY',
    position_side='LONG',
    order_type='LIMIT',
    quantity=0.01,
    price=50000,
    leverage=10
)

# 平多仓（市价）
order = exchange.client.place_order(
    symbol='BTCUSDT',
    side='SELL',
    position_side='LONG',
    order_type='MARKET',
    quantity=0.01,
    reduce_only=True
)
```

## 集成到服务

### 在 MarketService 中使用

```python
from app.core.adapters.exchange_api import ExchangeAPI

class MarketService:
    def __init__(self, db: Session, exchange: str = 'BITGET'):
        self.db = db
        self.exchange_api = ExchangeAPI(exchange)
    
    async def get_latest_prices(self):
        """获取最新价格"""
        symbols = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "BNBUSDT", "SOLUSDT"]
        return self.exchange_api.get_latest_prices(symbols)
```

## 常见问题

### 1. API 密钥配置错误

**错误**: `ValueError: 缺少 BITGET_API_KEY 配置`

**解决**: 检查 `.env` 文件中的 API 密钥配置是否正确。

### 2. 签名失败

**错误**: `API 返回错误: 签名不正确`

**解决**: 
- 检查时间戳是否正确
- 确认签名算法实现正确
- 验证密钥是否匹配

### 3. 网络超时

**错误**: `Connection timeout`

**解决**: 
- 检查网络连接
- 可能需要配置代理
- 调整超时时间（当前默认 10 秒）

### 4. 交易对不存在

**错误**: `获取 BTCUSDT 价格失败`

**解决**: 
- 确认交易对名称正确
- 不同交易所的交易对格式不同（OKX 使用 `BTC-USDT`）
- 检查交易对是否在对应交易所上线

### 5. 权限不足

**错误**: `API 返回错误: 权限不足`

**解决**: 
- 检查 API Key 的权限设置
- 确保勾选了"交易"权限
- 某些功能可能需要更高等级的 KYC

## 安全建议

1. **最小权限原则**: 创建 API Key 时只授予必要的权限
2. **白名单 IP**: 如果可能，配置 IP 白名单
3. **定期更换密钥**: 建议每 3-6 个月更换一次 API 密钥
4. **监控使用**: 定期查看 API 使用日志
5. **不要存储明文密钥**: 使用环境变量或密钥管理系统

## 下一步

- 查看 [交易所 API 文档](./EXCHANGE_API.md) 了解详细功能
- 阅读 [交易策略](./TRADING_STRATEGY.md) 学习如何制定策略
- 了解 [风险控制](./RISK_MANAGEMENT.md) 保护资金安全

## 技术栈

- Python 3.x
- Requests (HTTP 请求)
- HMAC-SHA256 (签名算法)
- Base64 (编码)

## 相关文件

- `adapters/exchange_api.py` - 统一适配器
- `adapters/bitget_api_client.py` - Bitget 客户端
- `adapters/okx_api_client.py` - OKX 客户端
- `adapters/binance_api_client.py` - Binance 客户端
- `backend/app/config.py` - 配置文件
