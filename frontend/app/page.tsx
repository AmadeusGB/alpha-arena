'use client';

import { useEffect, useState } from 'react';
import { marketApi, portfolioApi, decisionApi } from '../lib/api';
import { MarketPrice, ModelPortfolio } from '../types';

export default function Home() {
  const [prices, setPrices] = useState<Record<string, number>>({});
  const [portfolios, setPortfolios] = useState<ModelPortfolio[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // 每30秒刷新
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // 获取最新价格
      const pricesRes = await marketApi.getLatestPrices();
      setPrices(pricesRes.data);
      
      // 获取投资组合状态
      const portfoliosRes = await portfolioApi.getPortfolios();
      setPortfolios(portfoliosRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const symbols = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'BNBUSDT', 'SOLUSDT'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-50 to-zinc-100 dark:from-zinc-900 dark:to-black">
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-zinc-900 dark:text-zinc-50 mb-2">
            📊 实时仪表盘
          </h1>
          <p className="text-zinc-600 dark:text-zinc-400">
            实时市场数据和模型表现
          </p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-xl text-zinc-600 dark:text-zinc-400">加载中...</div>
          </div>
        ) : (
          <>
            {/* 市场价格卡片 */}
            <div className="mb-8">
              <h2 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50 mb-4">
                实时市场
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                {symbols.map((symbol) => (
                  <div
                    key={symbol}
                    className="bg-white dark:bg-zinc-800 rounded-lg p-6 shadow-sm border border-zinc-200 dark:border-zinc-700"
                  >
                    <div className="text-sm text-zinc-600 dark:text-zinc-400 mb-2">
                      {symbol}
                    </div>
                    <div className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">
                      ${prices[symbol]?.toFixed(4) || '--'}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 投资组合概览 */}
            <div>
              <h2 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50 mb-4">
                模型表现
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {portfolios.map((portfolio) => (
                  <div
                    key={portfolio.model_name}
                    className="bg-white dark:bg-zinc-800 rounded-lg p-6 shadow-sm border border-zinc-200 dark:border-zinc-700"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
                        {portfolio.model_name}
                      </h3>
                      <div
                        className={`px-3 py-1 rounded-full text-sm ${
                          portfolio.total_pnl >= 0
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                            : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        }`}
                      >
                        {portfolio.is_active === 'active' ? '运行中' : '已暂停'}
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-zinc-600 dark:text-zinc-400">总资产</span>
                        <span className="font-semibold text-zinc-900 dark:text-zinc-50">
                          ${portfolio.total_value.toFixed(2)}
                        </span>
                      </div>
                      
                      <div className="flex justify-between">
                        <span className="text-zinc-600 dark:text-zinc-400">总盈亏</span>
                        <span
                          className={`font-semibold ${
                            portfolio.total_pnl >= 0
                              ? 'text-green-600 dark:text-green-400'
                              : 'text-red-600 dark:text-red-400'
                          }`}
                        >
                          ${portfolio.total_pnl >= 0 ? '+' : ''}
                          {portfolio.total_pnl.toFixed(2)}
                        </span>
                      </div>
                      
                      <div className="flex justify-between">
                        <span className="text-zinc-600 dark:text-zinc-400">收益率</span>
                        <span
                          className={`font-semibold ${
                            portfolio.total_return >= 0
                              ? 'text-green-600 dark:text-green-400'
                              : 'text-red-600 dark:text-red-400'
                          }`}
                        >
                          {portfolio.total_return >= 0 ? '+' : ''}
                          {portfolio.total_return.toFixed(2)}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {portfolios.length === 0 && (
              <div className="mt-8 text-center py-12 bg-white dark:bg-zinc-800 rounded-lg border border-zinc-200 dark:border-zinc-700">
                <p className="text-zinc-600 dark:text-zinc-400">
                  暂无模型数据，请确保后端服务正在运行
                </p>
                <p className="text-sm text-zinc-500 dark:text-zinc-500 mt-2">
                  访问: http://localhost:8000/docs 查看 API 文档
                </p>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
