'use client';

import { useEffect, useState } from 'react';
import { portfolioApi, decisionApi, portfolioApi as positionsApi } from '../../lib/api';
import { ModelPortfolio, Decision, Position } from '../../types';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function ModelsPage() {
  const [portfolios, setPortfolios] = useState<ModelPortfolio[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [portfolioHistory, setPortfolioHistory] = useState<any[]>([]);
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [activeTab, setActiveTab] = useState<'history' | 'chat' | 'positions'>('history');
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalContent, setModalContent] = useState<Decision | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (selectedModel) {
      loadModelDetails(selectedModel);
    }
  }, [selectedModel]);

  const loadData = async () => {
    try {
      const portfoliosRes = await portfolioApi.getPortfolios();
      setPortfolios(portfoliosRes.data);
      
      if (portfoliosRes.data.length > 0) {
        setSelectedModel(portfoliosRes.data[0].model_name);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadModelDetails = async (modelName: string) => {
    try {
      // 加载决策历史
      const decisionsRes = await decisionApi.getDecisions(modelName);
      setDecisions(decisionsRes.data);
      
      // 加载持仓
      const positionsRes = await positionsApi.getPositions(modelName);
      setPositions(positionsRes.data);
      
      // 生成模拟历史数据（实际应该从API获取）
      const history = generateMockHistory(portfolios.find(p => p.model_name === modelName));
      setPortfolioHistory(history);
    } catch (error) {
      console.error('Error loading model details:', error);
    }
  };

  const generateMockHistory = (portfolio: ModelPortfolio | undefined) => {
    if (!portfolio) return [];
    
    const data = [];
    const baseValue = portfolio.total_value;
    const now = new Date();
    
    for (let i = 30; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      const value = baseValue + (Math.random() - 0.5) * 1000;
      data.push({
        date: date.toISOString().split('T')[0],
        value: Math.max(value, baseValue * 0.95),
      });
    }
    
    return data;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl text-zinc-600 dark:text-zinc-400">加载中...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-50 to-zinc-100 dark:from-zinc-900 dark:to-black">
      <div className="container mx-auto px-4 py-8 max-w-[1600px]">
        <div className="mb-6">
          <h1 className="text-4xl font-bold text-zinc-900 dark:text-zinc-50 mb-2">
            🎯 模型对比分析
          </h1>
          <p className="text-zinc-600 dark:text-zinc-400">
            实时跟踪多模型交易表现
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左侧：K线图 */}
          <div className="lg:col-span-2 bg-white dark:bg-zinc-800 rounded-lg p-6 shadow-sm border border-zinc-200 dark:border-zinc-700">
            <h2 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50 mb-4">
              模型净值曲线
            </h2>
            <div className="h-[500px]">
              <MultipleLineChart portfolios={portfolios} />
            </div>
          </div>

          {/* 右侧：模型信息和详情 */}
          <div className="space-y-6">
            {/* 模型选择 */}
            <div className="bg-white dark:bg-zinc-800 rounded-lg p-6 shadow-sm border border-zinc-200 dark:border-zinc-700">
              <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50 mb-4">
                选择模型
              </h2>
              <div className="space-y-2">
                {portfolios.map((portfolio) => (
                  <button
                    key={portfolio.model_name}
                    onClick={() => setSelectedModel(portfolio.model_name)}
                    className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                      selectedModel === portfolio.model_name
                        ? 'bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100'
                        : 'hover:bg-zinc-100 dark:hover:bg-zinc-700 text-zinc-700 dark:text-zinc-300'
                    }`}
                  >
                    <div className="font-medium">{portfolio.model_name}</div>
                    <div className="text-sm text-zinc-600 dark:text-zinc-400">
                      ${portfolio.total_value.toFixed(2)}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* 模型详情 */}
            {selectedModel && (
              <div className="bg-white dark:bg-zinc-800 rounded-lg p-6 shadow-sm border border-zinc-200 dark:border-zinc-700">
                <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50 mb-4">
                  {selectedModel} 详情
                </h2>

                {/* Tabs */}
                <div className="mb-4 border-b border-zinc-200 dark:border-zinc-700">
                  <div className="flex gap-2">
                    {(['history', 'chat', 'positions'] as const).map((tab) => (
                      <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`px-4 py-2 font-medium transition-colors ${
                          activeTab === tab
                            ? 'border-b-2 border-blue-500 text-blue-600 dark:text-blue-400'
                            : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-300'
                        }`}
                      >
                        {tab === 'history' ? '交易历史' : tab === 'chat' ? '聊天记录' : '当前仓位'}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Tab Content */}
                <div className="h-[400px] overflow-y-auto">
                  {activeTab === 'history' && (
                    <div className="space-y-2">
                      {Array.isArray(decisions) && decisions.length === 0 ? (
                        <div className="text-center py-8 text-zinc-600 dark:text-zinc-400">
                          暂无交易历史
                        </div>
                      ) : (
                        Array.isArray(decisions) && decisions.map((decision) => (
                        <div
                          key={decision.id}
                          className="p-3 bg-zinc-50 dark:bg-zinc-900 rounded-lg"
                        >
                          <div className="flex justify-between items-start mb-2">
                            <span className="font-medium text-zinc-900 dark:text-zinc-50">
                              {decision.symbol || 'N/A'}
                            </span>
                            <span
                              className={`px-2 py-1 rounded text-sm font-medium ${
                                decision.action === 'BUY'
                                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                                  : decision.action === 'SELL'
                                  ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                                  : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                              }`}
                            >
                              {decision.action}
                            </span>
                          </div>
                          {decision.reasoning && (
                            <p className="text-sm text-zinc-600 dark:text-zinc-400">
                              {decision.reasoning}
                            </p>
                          )}
                          <div className="text-xs text-zinc-500 dark:text-zinc-500 mt-2">
                            {new Date(decision.timestamp).toLocaleString('zh-CN')}
                          </div>
                        </div>
                        ))
                      )}
                    </div>
                  )}

                  {activeTab === 'chat' && (
                    <div className="space-y-2 text-zinc-600 dark:text-zinc-400">
                      {!Array.isArray(decisions) || decisions.length === 0 ? (
                        <div className="text-center py-8 text-zinc-600 dark:text-zinc-400">
                          暂无聊天记录
                        </div>
                      ) : (
                        Array.isArray(decisions) && decisions.slice(0, 10).map((decision, idx) => (
                        <div 
                          key={idx} 
                          className="p-3 bg-zinc-50 dark:bg-zinc-900 rounded-lg cursor-pointer hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                          onClick={() => {
                            setModalContent(decision);
                            setModalOpen(true);
                          }}
                        >
                          <div className="text-xs mb-1 text-zinc-500">
                            {new Date(decision.timestamp).toLocaleString('zh-CN')}
                          </div>
                          <div className="text-sm">
                            <strong>Prompt:</strong> {decision.prompt?.substring(0, 100)}...
                          </div>
                          <div className="text-sm mt-1">
                            <strong>Response:</strong> {decision.response_raw ? JSON.stringify(decision.response_raw).substring(0, 100) : 'N/A'}...
                          </div>
                          <div className="text-xs text-blue-600 dark:text-blue-400 mt-2">
                            点击查看完整内容 →
                          </div>
                        </div>
                        ))
                      )}
                    </div>
                  )}

                  {activeTab === 'positions' && (
                    <div className="space-y-2">
                      {!Array.isArray(positions) || positions.length === 0 ? (
                        <div className="text-center py-8 text-zinc-600 dark:text-zinc-400">
                          暂无持仓
                        </div>
                      ) : (
                        Array.isArray(positions) && positions.map((position) => (
                          <div
                            key={position.id}
                            className="p-4 bg-zinc-50 dark:bg-zinc-900 rounded-lg"
                          >
                            <div className="flex justify-between items-start mb-2">
                              <span className="font-medium text-zinc-900 dark:text-zinc-50">
                                {position.symbol}
                              </span>
                              <span className="text-sm text-zinc-600 dark:text-zinc-400">
                                {position.quantity}
                              </span>
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-sm">
                              <div>
                                <span className="text-zinc-600 dark:text-zinc-400">入场价</span>
                                <div className="font-medium">
                                  ${position.entry_price.toFixed(4)}
                                </div>
                              </div>
                              <div>
                                <span className="text-zinc-600 dark:text-zinc-400">当前价</span>
                                <div className="font-medium">
                                  ${position.current_price?.toFixed(4) || '--'}
                                </div>
                              </div>
                            </div>
                            <div className="mt-2 text-sm">
                              <span className="text-zinc-600 dark:text-zinc-400">盈亏</span>
                              <span
                                className={`ml-2 font-medium ${
                                  position.pnl >= 0
                                    ? 'text-green-600 dark:text-green-400'
                                    : 'text-red-600 dark:text-red-400'
                                }`}
                              >
                                ${position.pnl.toFixed(2)} ({position.pnl_percent.toFixed(2)}%)
                              </span>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modal */}
      {modalOpen && modalContent && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={() => setModalOpen(false)}
        >
          <div 
            className="bg-white dark:bg-zinc-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="px-6 py-4 border-b border-zinc-200 dark:border-zinc-700 flex justify-between items-center">
              <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
                聊天详情
              </h3>
              <button
                onClick={() => setModalOpen(false)}
                className="text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100"
              >
                ✕
              </button>
            </div>

            {/* Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
              <div className="space-y-6">
                {/* Timestamp */}
                <div className="text-sm text-zinc-500 dark:text-zinc-500">
                  {new Date(modalContent.timestamp).toLocaleString('zh-CN')}
                </div>

                {/* Prompt */}
                <div>
                  <h4 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50 mb-2">
                    Prompt:
                  </h4>
                  <div className="p-4 bg-zinc-50 dark:bg-zinc-900 rounded-lg">
                    <pre className="whitespace-pre-wrap text-sm text-zinc-700 dark:text-zinc-300">
                      {modalContent.prompt || 'N/A'}
                    </pre>
                  </div>
                </div>

                {/* Response */}
                <div>
                  <h4 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50 mb-2">
                    Response:
                  </h4>
                  <div className="p-4 bg-zinc-50 dark:bg-zinc-900 rounded-lg">
                    {modalContent.response_raw ? (
                      <pre className="whitespace-pre-wrap text-sm text-zinc-700 dark:text-zinc-300 overflow-x-auto">
                        {JSON.stringify(modalContent.response_raw, null, 2)}
                      </pre>
                    ) : (
                      <div className="text-sm text-zinc-600 dark:text-zinc-400">N/A</div>
                    )}
                  </div>
                </div>

                {/* Decision Info */}
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <div className="text-sm text-zinc-600 dark:text-zinc-400">Symbol</div>
                    <div className="font-medium text-zinc-900 dark:text-zinc-50">
                      {modalContent.symbol || 'N/A'}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-zinc-600 dark:text-zinc-400">Action</div>
                    <div className="font-medium text-zinc-900 dark:text-zinc-50">
                      {modalContent.action}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-zinc-600 dark:text-zinc-400">Confidence</div>
                    <div className="font-medium text-zinc-900 dark:text-zinc-50">
                      {modalContent.confidence ? `${(modalContent.confidence * 100).toFixed(1)}%` : 'N/A'}
                    </div>
                  </div>
                </div>

                {/* Reasoning */}
                {modalContent.reasoning && (
                  <div>
                    <h4 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50 mb-2">
                      Reasoning:
                    </h4>
                    <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <div className="text-sm text-zinc-700 dark:text-zinc-300">
                        {modalContent.reasoning}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-zinc-200 dark:border-zinc-700 flex justify-end">
              <button
                onClick={() => setModalOpen(false)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// 多线图组件
function MultipleLineChart({ portfolios }: { portfolios: ModelPortfolio[] }) {
  // 生成模拟历史数据
  const generateData = () => {
    const data = [];
    const now = new Date();
    const colors = ['#3b82f6', '#10b981', '#f59e0b'];
    
    for (let i = 30; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      const dayData: any = {
        date: date.toISOString().split('T')[0],
      };
      
      portfolios.forEach((portfolio) => {
        const baseValue = portfolio.total_value;
        const variation = (Math.sin(i / 5) + (Math.random() - 0.5)) * 500;
        dayData[portfolio.model_name] = Number((baseValue + variation).toFixed(2));
      });
      
      data.push(dayData);
    }
    
    return data;
  };

  const data = generateData();
  const colors = ['#3b82f6', '#10b981', '#f59e0b'];

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart
        data={data}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis 
          dataKey="date" 
          stroke="#6b7280"
          tick={{ fill: '#6b7280' }}
          tickFormatter={(value) => {
            const date = new Date(value);
            return `${date.getMonth() + 1}/${date.getDate()}`;
          }}
        />
        <YAxis 
          stroke="#6b7280"
          tick={{ fill: '#6b7280' }}
          tickFormatter={(value) => `$${(value / 1000).toFixed(1)}k`}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
          }}
          formatter={(value: any) => `$${value.toFixed(2)}`}
          labelFormatter={(value) => `日期: ${value}`}
        />
        <Legend />
        {portfolios.map((portfolio, idx) => (
          <Line
            key={portfolio.model_name}
            type="monotone"
            dataKey={portfolio.model_name}
            stroke={colors[idx % colors.length]}
            strokeWidth={2}
            dot={false}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

