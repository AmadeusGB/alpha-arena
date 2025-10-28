# 交易所 API 对接文档

本文档描述 Alpha Arena 交易系统对接的三大主流交易所（Bitget、OKX、Binance）的功能与实现细节。

## 目录

- [概述](#概述)
- [支持的功能](#支持的功能)
- [交易所特性对比](#交易所特性对比)
- [配置说明](#配置说明)
- [使用方法](#使用方法)
- [功能清单](#功能清单)
- [实现细节](#实现细节)

## 概述

Alpha Arena 交易系统已对接三个主流交易所：

1. **Bitget** - 数字资产交易平台
2. **OKX** - 欧易交易所
3. **Binance** - 币安交易所

系统采用适配器模式，提供统一的接口抽象，屏蔽各交易所的差异，便于后续扩展更多交易所。

## 支持的功能

### 1. 用户认证与权限管理

所有交易所均采用 API Key 认证机制：

- **Bitget**: `ACCESS-KEY`, `ACCESS-SIGN`, `ACCESS-TIMESTAMP`, `ACCESS-PASSPHRASE`
- **OKX**: `OK-ACCESS-KEY`, `OK-ACCESS-SIGN`, `OK-ACCESS-TIMESTAMP`, `OK-ACCESS-PASSPHRASE`
- **Binance**: `X-MBX-APIKEY` + 签名参数

签名算法：
- Bitget/OKX: HMAC-SHA256 + Base64
- Binance: HMAC-SHA256 + Hex

### 2. 获取用户基础信息

```python
# 获取用户KYC状态、权限、账户状态
account_info = exchange_api.get_account_info()
```

返回字段：
- 用户ID/昵称
- KYC等级
- 交易权限（现货/期货/合约）
- 账户状态（正常/禁用）

### 3. 获取账户信息

```python
# 获取资金总览
account = exchange_api.get_account_info()
```

返回字段：
- 总资产
- 可用余额
- 冻结资产
- 各币种明细

### 4. 获取交易账户信息

```python
# 获取现货账户
# 获取合约账户（杠杆、保证金模式、持仓）
positions = exchange_api.get_positions()
```

合约账户特有字段：
- 杠杆倍数
- 保证金模式（全仓/逐仓）
- 持仓明细（开仓价、未实现盈亏、强平价）

### 5. 行情接口

**获取单个交易对最新价：**
```python
price = exchange_api.get_single_price('BTCUSDT')
```

返回数据：
- 最新成交价（last）
- 买一卖一价（bid/ask）
- 24小时高低价
- 交易量

**批量获取行情：**
```python
symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
prices = exchange_api.get_latest_prices(symbols)
```

### 6. 交易接口

#### 6.1 现货交易

**买入（限价）：**
```python
exchange_api.client.place_order(
    symbol='BTCUSDT',
    side='BUY',
    order_type='LIMIT',
    quantity=0.001,
    price=50000
)
```

**卖出（市价）：**
```python
exchange_api.client.place_order(
    symbol='ETHUSDT',
    side='SELL',
    order_type='MARKET',
    quantity=0.1
)
```

#### 6.2 合约交易

**开多仓：**
```python
# 限价开多
exchange_api.client.place_order(
    symbol='BTCUSDT',
    side='BUY',
    position_side='LONG',
    order_type='LIMIT',
    quantity=0.01,
    price=50000,
    leverage=10
)
```

**开空仓：**
```python
exchange_api.client.place_order(
    symbol='BTCUSDT',
    side='SELL',
    position_side='SHORT',
    order_type='MARKET',
    quantity=0.01,
    leverage=10
)
```

**平仓：**
```python
# 市价平仓（reduceOnly=True）
exchange_api.client.place_order(
    symbol='BTCUSDT',
    side='SELL',
    position_side='LONG',
    order_type='MARKET',
    quantity=0.01,
    reduce_only=True
)
```

## 交易所特性对比

| 功能 | Bitget | OKX | Binance |
|------|--------|-----|---------|
| 交易对格式 | BTCUSDT | BTC-USDT | BTCUSDT |
| 认证方式 | ACCESS-KEY | OK-ACCESS-KEY | X-MBX-APIKEY |
| 签名算法 | HMAC-SHA256+Base64 | HMAC-SHA256+Base64 | HMAC-SHA256+Hex |
| 时间戳格式 | 毫秒 | ISO 8601 | 毫秒 |
| 现货交易 | ✅ | ✅ | ✅ |
| 合约交易 | ✅ | ✅ | ✅ |
| 杠杆倍数 | 最高20x | 最高100x | 最高125x |
| 期货合约 | USDT本位 | USDT本位/USD本位 | USDT本位/USD本位 |

## 配置说明

在 `.env` 文件中配置各交易所的 API 密钥：

```bash
# 默认交易所（BITGET/OKX/BINANCE）
DEFAULT_EXCHANGE=BITGET

# Bitget API
BITGET_API_KEY=your_bitget_api_key
BITGET_SECRET_KEY=your_bitget_secret_key
BITGET_PASSPHRASE=your_bitget_passphrase

# OKX API
OKX_API_KEY=your_okx_api_key
OKX_SECRET_KEY=your_okx_secret_key
OKX_PASSPHRASE=your_okx_passphrase

# Binance API
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
```

## 使用方法

### 初始化单个交易所

```python
from adapters.exchange_api import ExchangeAPI

# 使用 Bitget
bitget = ExchangeAPI('BITGET')

# 使用 OKX
okx = ExchangeAPI('OKX')

# 使用 Binance
binance = ExchangeAPI('BINANCE')
```

### 获取价格

```python
# 单个价格
price = exchange_api.get_single_price('BTCUSDT')

# 批量价格
prices = exchange_api.get_latest_prices(['BTCUSDT', 'ETHUSDT'])
```

### 切换默认交易所

通过环境变量 `DEFAULT_EXCHANGE` 设置默认交易所，系统会自动初始化对应的客户端。

## 功能清单

### ✅ 已实现

- [x] 多交易所初始化
- [x] 用户认证（签名机制）
- [x] 获取账户信息
- [x] 获取持仓信息
- [x] 获取最新价格（单个/批量）
- [x] 交易对符号标准化
- [x] 现货买入/卖出
- [x] 合约开多/开空
- [x] 平仓操作
- [x] 错误处理与日志

### 🔄 计划实现

- [ ] 订单查询（单个/历史）
- [ ] 订单撤销（单个/批量）
- [ ] 成交查询
- [ ] K线数据获取
- [ ] 深度订单簿
- [ ] 交易规则查询（精度、最小下单量等）
- [ ] 杠杆设置
- [ ] 止损止盈
- [ ] WebSocket 实时行情
- [ ] 资金划转
- [ ] 持仓模式切换

## 实现细节

### 交易对符号转换

系统自动处理各交易所不同的交易对格式：

- **Bitget/Binance**: `BTCUSDT` → `BTCUSDT`
- **OKX**: `BTCUSDT` → `BTC-USDT`

### 错误处理

所有 API 调用都包含完善的异常处理：

```python
try:
    price = exchange_api.get_single_price('BTCUSDT')
except Exception as e:
    print(f"获取价格失败: {e}")
    return 0.0
```

### 日志输出

系统会输出详细的日志信息，方便调试：

```
✅ BITGET API客户端初始化成功
✅ BITGET BTCUSDT: $68000.1234
❌ 获取ETHUSDT价格失败: Connection timeout
```

### 扩展新交易所

添加新交易所只需：

1. 创建新的 API 客户端类（继承基础接口）
2. 实现签名算法
3. 在 `ExchangeAPI` 中添加初始化逻辑
4. 添加交易对格式转换逻辑

## 注意事项

1. **API 密钥安全**: 不要将 API 密钥提交到代码仓库
2. **权限最小化**: 创建 API Key 时只授予必要的权限
3. **限频控制**: 各交易所都有 API 调用频率限制，需合理控制
4. **测试环境**: 建议先在交易所的沙盒/测试环境测试
5. **网络超时**: 所有请求都设置了 10 秒超时
6. **签名精度**: 时间戳格式和签名算法需严格按照各交易所文档实现

## 相关文档

- [Bitget API 文档](https://www.bitget.com/zh-CN/api-doc/common/signature)
- [OKX API 文档](https://www.okx.com/docs-v5/zh/)
- [Binance API 文档](https://binance-docs.github.io/apidocs/)

## 更新日志

### 2024-12-XX
- 初始版本
- 支持 Bitget、OKX、Binance 三大交易所
- 实现统一的适配器接口
- 支持交易对符号自动转换
