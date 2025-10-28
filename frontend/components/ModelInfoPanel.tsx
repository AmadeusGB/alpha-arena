'use client';

import React, { useMemo, useState } from 'react';
import { Decision, Position, ModelPortfolio } from '../types';

interface ModelInfoPanelProps {
  selectedModel: string;
  portfolios: ModelPortfolio[];
  decisions: Decision[];
  positions: Position[];
  onSelectedModelChange: (model: string) => void;
  onConversationClick: (content: { prompt: string; response: string }) => void;
  scrollContainerRef: React.RefObject<HTMLDivElement>;
  isLoadingMore: boolean;
  hasMoreDecisions: boolean;
  isRefreshing?: boolean;
}

const formatTimestamp = (timestamp: string) => {
  try {
    const date = new Date(timestamp);
    
    if (isNaN(date.getTime())) {
      console.warn('Invalid timestamp:', timestamp);
      return 'Invalid Date';
    }
    
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    return `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`;
  } catch (error) {
    console.error('Error formatting timestamp:', error);
    return 'Invalid Date';
  }
};

export default function ModelInfoPanel({
  selectedModel,
  portfolios,
  decisions,
  positions,
  onSelectedModelChange,
  onConversationClick,
  scrollContainerRef,
  isLoadingMore,
  hasMoreDecisions
}: ModelInfoPanelProps) {
  const [activeTab, setActiveTab] = useState<'history' | 'chat' | 'positions'>('history');
  const [modalOpen, setModalOpen] = useState(false);
  const [modalContent, setModalContent] = useState<Decision | null>(null);
  const [showAllMap, setShowAllMap] = useState<Record<string, boolean>>({});

  // 直接使用后端返回的逐仓 positions，不再做前端合并
  const aggregatedByModel = useMemo(() => {
    const modelNameToPortfolio: Record<string, ModelPortfolio> = Object.fromEntries(
      portfolios.map((p) => [p.model_name, p])
    );

    const modelNames = selectedModel === 'all'
      ? portfolios.map((p) => p.model_name)
      : portfolios.filter((p) => p.model_name === selectedModel).map((p) => p.model_name);

    const result: Array<{
      modelName: string;
      portfolio: ModelPortfolio | undefined;
      rows: Array<{
        symbol: string;
        avgEntryPrice: number; // 实际为 entry_price
        avgCurrentPrice: number | null; // 实际为 current_price
        quantity: number;
        unrealizedPnl: number | null;
        unrealizedPnlPct: number | null;
        portfolioSharePct: number | null;
      }>;
      cashBalance: number;
      cashRatioPct: number | null;
    }> = [];

    for (const modelName of modelNames) {
      const pf = modelNameToPortfolio[modelName];
      const positionsForModel = positions.filter((pos) => pos.model_name === modelName);

      const rows = positionsForModel.map((pos) => {
        const entry = pos.entry_price;
        const cur = typeof pos.current_price === 'number' ? pos.current_price : null;
        const qty = pos.quantity;
        const pnl = cur === null ? null : (cur - entry) * qty;
        const cost = entry * qty;
        const pnlPct = cur === null || cost === 0 ? null : ((cur * qty - cost) / cost) * 100;
        const mv = cur === null ? null : cur * qty;
        const portfolioSharePct = pf && mv !== null && pf.total_value > 0 ? (mv / pf.total_value) * 100 : null;
        return {
          symbol: pos.symbol,
          avgEntryPrice: entry,
          avgCurrentPrice: cur,
          quantity: qty,
          unrealizedPnl: pnl,
          unrealizedPnlPct: pnlPct,
          portfolioSharePct,
        };
      }).sort((a, b) => (b.portfolioSharePct ?? 0) - (a.portfolioSharePct ?? 0));

      const cashBalance = pf?.balance ?? 0;
      const cashRatioPct = pf && pf.total_value > 0 ? (cashBalance / pf.total_value) * 100 : null;

      result.push({
        modelName,
        portfolio: pf,
        rows,
        cashBalance,
        cashRatioPct,
      });
    }

    return result;
  }, [positions, portfolios, selectedModel]);

  return (
    <div className="bg-white dark:bg-zinc-800 rounded-lg p-6 shadow-sm border border-zinc-200 dark:border-zinc-700">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
          持仓详情
        </h2>
        {/* 分段控件（Segmented）替代下拉 */}
        <div className="flex gap-2 overflow-x-auto no-scrollbar">
          <button
            onClick={() => onSelectedModelChange('all')}
            className={`px-3 py-1.5 text-sm rounded-lg border transition-colors ${
              selectedModel === 'all'
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white dark:bg-zinc-700 text-zinc-700 dark:text-zinc-300 border-zinc-300 dark:border-zinc-600'
            }`}
          >全部模型</button>
          {portfolios.map((p) => (
            <button
              key={p.model_name}
              onClick={() => onSelectedModelChange(p.model_name)}
              className={`px-3 py-1.5 text-sm rounded-lg border transition-colors ${
                selectedModel === p.model_name
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white dark:bg-zinc-700 text-zinc-700 dark:text-zinc-300 border-zinc-300 dark:border-zinc-600'
              }`}
            >{p.model_name}</button>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-4 border-b border-zinc-200 dark:border-zinc-700">
        <div className="flex gap-2">
          {(['positions', 'history', 'chat'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 font-medium transition-colors ${
                activeTab === tab
                  ? 'border-b-2 border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-300'
              }`}
            >
              {tab === 'positions' ? '持仓' : tab === 'history' ? '交易历史' : '对话记录'}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="h-[600px] overflow-y-auto" ref={scrollContainerRef}>
        {activeTab === 'history' && (
          <div className="space-y-2">
            {Array.isArray(decisions) && decisions.length === 0 ? (
              <div className="text-center py-8 text-zinc-600 dark:text-zinc-400">
                暂无交易历史
              </div>
            ) : (
              <>
                {Array.isArray(decisions) && decisions.map((decision) => (
                <div
                  key={decision.id}
                  className={`p-3 bg-zinc-50 dark:bg-zinc-900 rounded-lg transition-colors ${
                    decision.conversation ? 'cursor-pointer hover:bg-zinc-100 dark:hover:bg-zinc-800' : ''
                  }`}
                  onClick={() => {
                    if (decision.conversation) {
                      onConversationClick({
                        prompt: decision.conversation.prompt || '',
                        response: decision.conversation.response || ''
                      });
                    }
                  }}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-zinc-900 dark:text-zinc-50">
                        {decision.symbol || 'N/A'}
                      </span>
                      {selectedModel === 'all' && (
                        <span className="px-2 py-0.5 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded text-xs font-medium">
                          {decision.model_name}
                        </span>
                      )}
                    </div>
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
                  {(decision.reasoning || decision.response_raw?.rationale) && (
                    <p className="text-sm text-zinc-600 dark:text-zinc-400">
                      {decision.reasoning || decision.response_raw?.rationale}
                    </p>
                  )}
                  <div className="flex justify-between items-center mt-2">
                    <div className="text-xs text-zinc-500 dark:text-zinc-500">
                      {formatTimestamp(decision.timestamp)}
                    </div>
                    {decision.conversation && (
                      <div className="text-xs text-blue-600 dark:text-blue-400 cursor-pointer">
                        查看对话 →
                      </div>
                    )}
                  </div>
                </div>
                ))}
                {/* 加载更多提示 */}
                {isLoadingMore && (
                  <div className="text-center py-4 text-zinc-600 dark:text-zinc-400">
                    🔄 加载更多...
                  </div>
                )}
                {!hasMoreDecisions && decisions.length > 0 && (
                  <div className="text-center py-4 text-zinc-600 dark:text-zinc-400">
                    ✅ 已加载全部数据
                  </div>
                )}
              </>
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
                <div className="flex items-center justify-between mb-1">
                  <div className="text-xs text-zinc-500">
                    {formatTimestamp(decision.timestamp)}
                  </div>
                  {selectedModel === 'all' && (
                    <span className="px-2 py-0.5 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded text-xs font-medium">
                      {decision.model_name}
                    </span>
                  )}
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
          <div className="overflow-x-auto snap-x snap-mandatory flex gap-4 pr-2">
            {aggregatedByModel.length === 0 ? (
              <div className="text-center py-8 text-zinc-600 dark:text-zinc-400 w-full">暂无持仓</div>
            ) : (
              aggregatedByModel.map(({ modelName, portfolio, rows, cashBalance, cashRatioPct }) => {
                const showAll = !!showAllMap[modelName];
                const visibleRows = showAll ? rows : rows.slice(0, 5);
                const hiddenCount = Math.max(0, rows.length - visibleRows.length);
                return (
                <div key={modelName} className="bg-zinc-50 dark:bg-zinc-900 rounded-lg p-4 border border-zinc-200 dark:border-zinc-700 snap-start shrink-0 w-[760px]">
                  {/* 模型卡片头部 */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-base font-semibold text-zinc-900 dark:text-zinc-50">{modelName}</span>
                      {portfolio && (
                        <span className="text-xs text-zinc-500">总资产 ${portfolio.total_value.toFixed(2)}</span>
                      )}
                    </div>
                    {portfolio && (
                      <div className="flex items-center gap-3">
                        {/* 同步指示 */}
                        <div className="flex items-center gap-1 text-xs text-zinc-500">
                          <span className={`inline-block w-2 h-2 rounded-full ${isRefreshing ? 'bg-blue-500 animate-pulse' : 'bg-green-500'}`}></span>
                          <span>{isRefreshing ? '同步中' : '已同步'}</span>
                        </div>
                        {/* 现金占比进度条 */}
                        <div className="w-44">
                          <div className="text-xs text-zinc-500 mb-1">现金余额 ${cashBalance.toFixed(2)} {typeof cashRatioPct === 'number' ? `(${cashRatioPct.toFixed(2)}%)` : ''}</div>
                          <div className="h-2 bg-zinc-200 dark:bg-zinc-800 rounded-full overflow-hidden">
                            <div className="h-full bg-blue-500" style={{ width: `${Math.max(0, Math.min(100, cashRatioPct || 0))}%` }} />
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* 持仓表格 */}
                  <div className="overflow-x-auto">
                    <table className="min-w-full text-sm">
                      <thead>
                        <tr className="text-left text-zinc-600 dark:text-zinc-400">
                          <th className="py-2 pr-4">模型</th>
                          <th className="py-2 pr-4">资产</th>
                          <th className="py-2 pr-4">购买价</th>
                          <th className="py-2 pr-4">当前价</th>
                          <th className="py-2 pr-4">数量</th>
                          <th className="py-2 pr-4">未实现盈亏</th>
                          <th className="py-2 pr-4">盈亏%</th>
                          <th className="py-2 pr-0">占总资产%</th>
                        </tr>
                      </thead>
                      <tbody>
                        {visibleRows.length === 0 ? (
                          <tr>
                            <td colSpan={8} className="py-6 text-center text-zinc-500">无持仓</td>
                          </tr>
                        ) : (
                          visibleRows.map((r) => {
                            const pnlPositive = (r.unrealizedPnl ?? 0) >= 0;
                            return (
                              <tr key={r.symbol} className="border-t border-zinc-200 dark:border-zinc-800">
                                <td className="py-2 pr-4 text-zinc-900 dark:text-zinc-50">{modelName}</td>
                                <td className="py-2 pr-4">{r.symbol}</td>
                                <td className="py-2 pr-4">${r.avgEntryPrice.toFixed(4)}</td>
                                <td className="py-2 pr-4">{r.avgCurrentPrice !== null ? `$${r.avgCurrentPrice.toFixed(4)}` : '--'}</td>
                                <td className="py-2 pr-4">{r.quantity}</td>
                                <td className={`py-2 pr-4 font-medium ${pnlPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>{r.unrealizedPnl !== null ? `$${r.unrealizedPnl.toFixed(2)}` : '--'}</td>
                                <td className={`py-2 pr-4 ${pnlPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>{r.unrealizedPnlPct !== null ? `${r.unrealizedPnlPct.toFixed(2)}%` : '--'}</td>
                                <td className="py-2 pr-0">{r.portfolioSharePct !== null ? `${r.portfolioSharePct.toFixed(2)}%` : '--'}</td>
                              </tr>
                            );
                          })
                        )}
                        {hiddenCount > 0 && (
                          <tr>
                            <td colSpan={8} className="py-2">
                              <button
                                onClick={() => setShowAllMap({ ...showAllMap, [modelName]: !showAll })}
                                className="text-blue-600 dark:text-blue-400 text-sm hover:underline"
                              >{showAll ? '收起' : `展开更多（${hiddenCount}）`}</button>
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              )})
            )}
          </div>
        )}
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

            <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
              <div className="space-y-6">
                <div className="text-sm text-zinc-500 dark:text-zinc-500">
                  {formatTimestamp(modalContent.timestamp)}
                </div>

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

