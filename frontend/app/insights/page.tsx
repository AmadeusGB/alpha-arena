'use client';

import React, { useEffect, useMemo, useRef, useState } from 'react';
import { portfolioApi } from '../../lib/api';
import { ModelPortfolio, Position } from '../../types';
import PortfolioChart from '@/components/PortfolioChart';
import { decisionApi } from '../../lib/api';

export default function InsightsPage() {
  const [loading, setLoading] = useState(true);
  const [portfolios, setPortfolios] = useState<ModelPortfolio[]>([]);
  const [historyData, setHistoryData] = useState<any[]>([]);
  const [timeRange, setTimeRange] = useState<'15m' | '1h' | '3h' | '6h' | '12h' | '1d'>('6h');
  const [selected, setSelected] = useState<string>('all');
  const [positions, setPositions] = useState<Position[]>([]);
  const [activeRightTab, setActiveRightTab] = useState<'trades'|'dialogs'|'positions'|'tradesAll'>('trades');
  const [decisionsPaged, setDecisionsPaged] = useState<any[]>([]);
  const [decisionOffset, setDecisionOffset] = useState(0);
  const [hasMoreDecisions, setHasMoreDecisions] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string>('');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const loadingRef = useRef(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogData, setDialogData] = useState<any|null>(null);
  const [dialogLoading, setDialogLoading] = useState(false);
  const [hideHold, setHideHold] = useState(true);
  const [metric, setMetric] = useState<'balance'|'total_value'|'position_value'>('total_value');
  const [trades, setTrades] = useState<any[]>([]);

  // KPI 计算
  const kpis = useMemo(() => {
    const totalValue = portfolios.reduce((s, p) => s + (p.total_value || 0), 0);
    const cash = portfolios.reduce((s, p) => s + (p.balance || 0), 0);
    const positionsValue = Math.max(0, totalValue - cash);
    const dailyPnl = portfolios.reduce((s, p) => s + (p.daily_pnl || 0), 0);
    return { totalValue, cash, positionsValue, dailyPnl };
  }, [portfolios]);

  // 模型资产列表与极值标注
  const modelAssets = useMemo(() => portfolios.map(p => ({ name: p.model_name, value: p.total_value || 0 })), [portfolios]);
  const maxAsset = useMemo(() => modelAssets.length ? Math.max(...modelAssets.map(m => m.value)) : 0, [modelAssets]);
  const minAsset = useMemo(() => modelAssets.length ? Math.min(...modelAssets.map(m => m.value)) : 0, [modelAssets]);

  // 统一格式化为 1 位小数
  const fmt1 = (n: number | null | undefined) => (typeof n === 'number' && isFinite(n)) ? n.toFixed(1) : '--';
  const money1 = (n: number | null | undefined) => `$${fmt1(n)}`;
  const pct1 = (n: number | null | undefined) => (typeof n === 'number' && isFinite(n)) ? `${n.toFixed(1)}%` : '--';

  // 拉取数据并转换为图表所需结构
  const loadData = async () => {
    if (loadingRef.current) return;
    loadingRef.current = true;
    try {
      const res = await portfolioApi.getDashboardAllData(300);
      const data = res.data;
      setPortfolios(data.portfolios || []);

      const histories = data.histories || {};
      setPositions(data.positions || []);
      setTrades((data.trades || []) as any[]);
      const models: string[] = Object.keys(histories);
      const timestamps = new Set<string>();
      models.forEach((m) => (histories[m] || []).forEach((h: any) => timestamps.add(h.timestamp)));
      const sorted = Array.from(timestamps).sort();

      const chartRows: any[] = [];
      sorted.forEach((ts) => {
        const row: any = { timestamp: ts };
        models.forEach((m) => {
          const item = (histories[m] || []).find((h: any) => h.timestamp === ts);
          if (item) {
            row[m] = item.balance; // 只保留余额曲线
            row[`${m}_detail`] = {
              balance: item.balance,
              position_value: item.position_value,
              pnl: item.pnl,
              pnl_percent: item.pnl_percent,
            };
          } else {
            row[m] = null;
            row[`${m}_detail`] = null;
          }
        });
        chartRows.push(row);
      });
      chartRows.reverse();
      setHistoryData(chartRows);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (e) {
      console.error('Failed to load insights data:', e);
    } finally {
      setLoading(false);
      loadingRef.current = false;
    }
  };

  const loadMoreDecisions = async (reset = false) => {
    if (loadingMore || !hasMoreDecisions) return;
    setLoadingMore(true);
    try {
      const offset = reset ? 0 : decisionOffset;
      const res = await decisionApi.getDecisions({ modelName: selected==='all'? undefined : selected, limit: 10, offset });
      const items = (res.data as any)?.items || res.data || [];
      setHasMoreDecisions(items.length >= 10);
      setDecisionsPaged(reset ? items : [...decisionsPaged, ...items]);
      setDecisionOffset(offset + items.length);
    } finally {
      setLoadingMore(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // 删除 /trades 接口后，此处不再单独请求；trades 由 dashboard/all 提供

  // 当切换模型时重置决策分页
  useEffect(() => {
    setDecisionsPaged([]);
    setDecisionOffset(0);
    setHasMoreDecisions(true);
    loadMoreDecisions(true);
  }, [selected]);

  // 自动刷新：交易信息/对话记录/持仓信息，10s 间隔，彼此错开 2s
  useEffect(() => {
    if (!autoRefresh) return;
    const t1 = setInterval(() => {
      // 刷新决策分页与全量仪表数据（含 trades）
      setDecisionsPaged([]);
      setDecisionOffset(0);
      setHasMoreDecisions(true);
      loadMoreDecisions(true);
      loadData();
    }, 10000);
    const t2 = setInterval(() => {
      // 刷新对话/持仓等汇总数据
      loadData();
    }, 12000); // 错开 2s
    return () => { clearInterval(t1); clearInterval(t2); };
  }, [autoRefresh, selected]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-zinc-600 dark:text-zinc-400">加载中...</div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-50 to-zinc-100 dark:from-zinc-900 dark:to-black">
      <div className="container mx-auto px-1 py-1 max-w-[1600px]">
        {/* 主体：图表 + 信息栏 */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-1">
          {/* 左：余额图表 */}
          <div className="lg:col-span-8 bg-white dark:bg-zinc-800 rounded-lg p-6 shadow-sm border border-zinc-200 dark:border-zinc-700">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
              <h2 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">余额变化</h2>
                <select
                  value={metric}
                  onChange={(e)=>setMetric(e.target.value as any)}
                  className="px-2 py-1 text-xs bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-600 rounded-md text-zinc-700 dark:text-zinc-200"
                >
                  <option value="balance">余额</option>
                  <option value="total_value">资产总值</option>
                  <option value="position_value">持仓总值</option>
                </select>
              </div>
              {/* 模型：资产 显示全部模型，标注最高/最低 */}
              <div className="flex gap-1 flex-wrap justify-end">
                {modelAssets.map(m => {
                  const isMax = m.value === maxAsset;
                  const isMin = m.value === minAsset;
                  const badge = isMax ? '▲' : (isMin ? '▼' : '');
                  const cls = isMax ? 'border-green-600 text-green-700' : (isMin ? 'border-red-600 text-red-600' : 'border-zinc-300 dark:border-zinc-600 text-zinc-700 dark:text-zinc-200');
                  return (
                    <span key={m.name} className={`px-2 py-1 text-xs rounded border ${cls}`}>
                      {badge && <span className="mr-1">{badge}</span>}
                      {m.name}: ${m.value.toFixed(2)}
                    </span>
                  );
                })}
              </div>
            </div>
            <div className="h-[520px]">
              <PortfolioChart portfolios={portfolios} historyData={historyData} timeRange={timeRange} metric={metric} />
            </div>
          </div>

          {/* 右：Tabs + 模型卡片/交易/对话 */}
          <div className="lg:col-span-4 space-y-1 max-h-[calc(100vh-120px)] overflow-y-auto">
            <div className="bg-white dark:bg-zinc-800 rounded-lg p-2 shadow-sm border border-zinc-200 dark:border-zinc-700 flex items-center gap-1">
            {/* Tabs + 模型下拉 */}
            <div className="flex items-center gap-1">
                <div className="flex gap-1 overflow-x-auto no-scrollbar">
                    <button
                      onClick={()=>setActiveRightTab('trades')}
                      aria-pressed={activeRightTab==='trades'}
                      className={`px-3 py-2 text-sm rounded-md transition-colors border ${
                        activeRightTab==='trades'
                          ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                          : 'bg-white dark:bg-zinc-700 text-zinc-700 dark:text-zinc-200 border-zinc-300 dark:border-zinc-600 hover:bg-zinc-100 dark:hover:bg-zinc-600'
                      }`}
                    >交易信息</button>
                    <button
                      onClick={()=>setActiveRightTab('tradesAll')}
                      aria-pressed={activeRightTab==='tradesAll'}
                      className={`px-3 py-2 text-sm rounded-md transition-colors border ${
                        activeRightTab==='tradesAll'
                          ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                          : 'bg-white dark:bg-zinc-700 text-zinc-700 dark:text-zinc-200 border-zinc-300 dark:border-zinc-600 hover:bg-zinc-100 dark:hover:bg-zinc-600'
                      }`}
                    >全部交易</button>
                    <button
                      onClick={()=>setActiveRightTab('dialogs')}
                      aria-pressed={activeRightTab==='dialogs'}
                      className={`px-3 py-2 text-sm rounded-md transition-colors border ${
                        activeRightTab==='dialogs'
                          ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                          : 'bg-white dark:bg-zinc-700 text-zinc-700 dark:text-zinc-200 border-zinc-300 dark:border-zinc-600 hover:bg-zinc-100 dark:hover:bg-zinc-600'
                      }`}
                    >对话记录</button>
                    <button
                      onClick={()=>setActiveRightTab('positions')}
                      aria-pressed={activeRightTab==='positions'}
                      className={`px-3 py-2 text-sm rounded-md transition-colors border ${
                        activeRightTab==='positions'
                          ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                          : 'bg-white dark:bg-zinc-700 text-zinc-700 dark:text-zinc-200 border-zinc-300 dark:border-zinc-600 hover:bg-zinc-100 dark:hover:bg-zinc-600'
                      }`}
                    >持仓信息</button>
                </div>
                <select
                value={selected}
                onChange={(e)=>setSelected(e.target.value)}
                className="px-3 py-2 text-sm bg-white dark:bg-zinc-700 border border-zinc-300 dark:border-zinc-600 rounded-md text-zinc-700 dark:text-zinc-200"
              >
                <option value="all">全部模型</option>
                {portfolios.map((p)=> (
                  <option key={p.model_name} value={p.model_name}>{p.model_name}</option>
                ))}
              </select>
                {/* 忽略 HOLD 开关 */}
                <label className="ml-auto flex items-center gap-1 text-xs text-zinc-600 dark:text-zinc-300">
                  <input type="checkbox" checked={hideHold} onChange={(e)=>setHideHold(e.target.checked)} />
                  忽略 HOLD
                </label>
            </div>
            </div>

            {activeRightTab==='trades' && (
              <div className="bg-white dark:bg-zinc-800 rounded-lg p-2 shadow-sm border border-zinc-200 dark:border-zinc-700">
                <div className="text-sm text-zinc-500 mb-3">最近交易（滚动加载）</div>
                <div className="space-y-2 max-h-[420px] overflow-y-auto" onScroll={(e)=>{
                  const el = e.currentTarget;
                  if (el.scrollHeight - el.scrollTop - el.clientHeight < 60) {
                    loadMoreDecisions();
                  }
                }}>
                  {trades.length>0 && trades.map((t)=> (
                    <div key={t.id} className="p-3 rounded-md border border-zinc-200 dark:border-zinc-700">
                      <div className="flex items-center justify-between">
                        <div className="text-sm font-medium">{t.model_name} · {t.symbol || '—'}</div>
                        <div className={`text-sm ${t.side==='BUY'?'text-green-600':'text-red-600'}`}>{t.side}</div>
                      </div>
                      <div className="flex items-center gap-2 text-xs mt-1">
                        <span className="text-zinc-500">{t.executed_at? new Date(t.executed_at).toLocaleString():''}</span>
                        <span className={`px-2 py-0.5 rounded text-white ${t.status==='completed'?'bg-green-600':(t.status==='failed'?'bg-red-600':'bg-zinc-500')}`}>{t.status||'unknown'}</span>
                        {t.feedback && <span className="text-red-600">{t.feedback}</span>}
                      </div>
                      <div className="text-xs text-zinc-600 dark:text-zinc-300 mt-1">
                        杠杆：{t.leverage??'—'} ｜ 方向：{(t.direction||'').toUpperCase()} ｜ 金额：${t.total_amount?.toFixed?.(2) || t.total_amount}
                      </div>
                      <div className="text-xs text-zinc-500">交易原因：{t.reasoning || '—'}</div>
                    </div>
                  ))}
                  {(trades.length===0 && (hideHold ? decisionsPaged.filter((d:any)=>d.action!=='HOLD') : decisionsPaged).length===0) ? (
                    <div className="text-center py-8 text-zinc-500">暂无数据</div>
                  ) : (hideHold ? decisionsPaged.filter((d:any)=>d.action!=='HOLD') : decisionsPaged).map((d)=> (
                    <div key={d.id} className="p-3 rounded-md border border-zinc-200 dark:border-zinc-700 cursor-pointer" onClick={async()=>{
                      try{
                        setDialogLoading(true);
                        setDialogOpen(true);
                        const res = await decisionApi.getDecisionConversation(d.id);
                        setDialogData(res.data);
                      }catch(e){
                        setDialogData({error: String(e)});
                      }finally{
                        setDialogLoading(false);
                      }
                    }}>
                      <div className="flex items-center justify-between">
                        <div className="text-sm font-medium tag">{d.model_name}</div> 
                        <div className={`text-sm ${d.action==='BUY'?'text-green-600':'text-red-600'}`}>{d.action}</div>
                      </div>
                      <div className="text-xs text-zinc-500 mt-1">{new Date(d.timestamp).toLocaleString()}</div>
                      {/* 交易关键信息 */}
                      {(() => {
                        const trade = d?.response_raw?.trade || null;
                        const leverage = trade?.leverage ?? '--';
                        const direction = trade?.direction || (d.action==='BUY' ? 'LONG' : (d.action==='SELL' ? 'SHORT' : '--'));
                        const qty = typeof trade?.quantity === 'number' ? trade.quantity : null;
                        const entry = typeof trade?.entry_price === 'number' ? trade.entry_price : null;
                        const amount = (qty!==null && entry!==null) ? qty*entry : (typeof d?.response_raw?.total_amount === 'number' ? d.response_raw.total_amount : null);
                        const reason = d?.reasoning || d?.response_raw?.rationale || '--';
                        return (
                          <div className="mt-2 text-xs text-zinc-600 dark:text-zinc-300">
                            <div className="mb-1">
                              标的物：<span className="font-medium">{d.symbol || '—'}</span>
                              <span className="mx-2">｜</span>
                              杠杆率：<span className="font-medium">{leverage}</span>
                              <span className="mx-2">｜</span>
                              {direction ? direction.toUpperCase() : '--'}
                              <span className="mx-2">｜</span>
                              交易金额：<span className="font-medium">{amount!==null? `$${amount.toFixed(2)}`:'—'}</span>
                            </div>
                            <div className="text-zinc-500">交易原因：{reason}</div>
                          </div>
                        );
                      })()}
                      {/* 点击查看关联对话 */}

                    </div>
                  ))}
                  {loadingMore && <div className="text-center py-2 text-zinc-500">加载中...</div>}
                  {!hasMoreDecisions && decisionsPaged.length>0 && <div className="text-center py-2 text-zinc-500">已无更多</div>}
                </div>
              </div>
            )}

            {activeRightTab==='tradesAll' && (
              <div className="bg-white dark:bg-zinc-800 rounded-lg p-2 shadow-sm border border-zinc-200 dark:border-zinc-700">
                <div className="text-sm text-zinc-500 mb-3">全部交易（来自 /dashboard/all）</div>
                <div className="space-y-2 max-h-[420px] overflow-y-auto">
                  {(trades||[]).length===0 ? (
                    <div className="text-center py-8 text-zinc-500">暂无交易</div>
                  ) : (trades||[]).map((t:any)=> (
                    <div key={`all-${t.id}`} className="p-3 rounded-md border border-zinc-200 dark:border-zinc-700">
                      <div className="flex items-center justify-between">
                        <div className="text-sm font-medium">{t.model_name} · {t.symbol || '—'}</div>
                        <div className={`text-sm ${t.side==='BUY'?'text-green-600':'text-red-600'}`}>{t.side}</div>
                      </div>
                      <div className="flex items-center gap-2 text-xs mt-1">
                        <span className="text-zinc-500">{t.executed_at? new Date(t.executed_at).toLocaleString():''}</span>
                        <span className={`px-2 py-0.5 rounded text-white ${t.status==='completed'?'bg-green-600':(t.status==='failed'?'bg-red-600':'bg-zinc-500')}`}>{t.status||'unknown'}</span>
                        {t.feedback && <span className="text-red-600">{t.feedback}</span>}
                      </div>
                      <div className="text-xs text-zinc-600 dark:text-zinc-300 mt-1">
                        杠杆：{t.leverage??'—'} ｜ 方向：{(t.direction||'').toUpperCase()} ｜ 金额：${t.total_amount?.toFixed?.(2) || t.total_amount}
                      </div>
                      <div className="text-xs text-zinc-500">交易原因：{t.reasoning || '—'}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeRightTab==='dialogs' && (
              <div className="bg-white dark:bg-zinc-800 rounded-lg p-6 shadow-sm border border-zinc-200 dark:border-zinc-700">
                <div className="text-sm text-zinc-500 mb-3">模型对话（来自最近交易）</div>
                <div className="space-y-2 max-h-[420px] overflow-y-auto">
                  {decisionsPaged.flatMap(d=> d.conversation? [d] : []).length===0 ? (
                    <div className="text-center py-8 text-zinc-500">暂无对话</div>
                  ) : decisionsPaged.filter(d=>d.conversation).map((d)=> (
                    <div key={d.id} className="p-3 rounded-md border border-zinc-200 dark:border-zinc-700 cursor-pointer" onClick={async()=>{
                      try{ setDialogLoading(true); setDialogOpen(true);
                        const [conv, dec] = await Promise.all([
                          decisionApi.getDecisionConversation(d.id),
                          decisionApi.getDecision(d.id)
                        ]);
                        setDialogData({ ...conv.data, decision: dec.data });
                      } finally { setDialogLoading(false); }
                    }}>
                      <div className="text-sm font-medium mb-1">{d.model_name} · {d.symbol || 'N/A'} · {new Date(d.timestamp).toLocaleString()}</div>
                      <div className="text-xs text-zinc-500">交易原因：{d.reasoning || d.response_raw?.rationale || '—'}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {activeRightTab =='positions' && (selected==='all'?portfolios:portfolios.filter(p=>p.model_name===selected)).map((pf)=>{
              // 逐仓展示：直接使用 positions（最多显示前 10 条按价值排序）
              const rows = positions
                .filter(pos=>pos.model_name===pf.model_name)
                .map(pos=>{
                  const value = (typeof pos.current_price==='number'? pos.current_price : pos.entry_price) * pos.quantity;
                  const pnl = typeof pos.current_price==='number' ? (pos.current_price - pos.entry_price) * pos.quantity : null;
                  const pnlPct = (typeof pos.current_price==='number' && pos.entry_price) ? ((pos.current_price - pos.entry_price) / pos.entry_price * 100) : null;
                  return {
                    symbol: pos.symbol,
                    side: (pos as any).side || 'long',
                    leverage: (pos as any).leverage || 1,
                    value,
                    closePrice: pos.current_price,
                    pnl,
                    pnlPct
                  };
                })
                .sort((a,b)=> (b.value??0) - (a.value??0))
                .slice(0,10);
              const cashRatio = pf.total_value>0? (pf.balance/pf.total_value*100):0;
              const top1Share = rows.length>0 && pf.total_value>0 ? (rows[0].value/pf.total_value*100) : 0;
              const top3Share = pf.total_value>0 ? rows.slice(0,3).reduce((s,r)=>s+(r.value/pf.total_value*100),0) : 0;
              const cashBandLow = 5, cashBandHigh = 40;
              const cashHint = cashRatio < cashBandLow ? '现金偏低' : (cashRatio > cashBandHigh ? '现金偏高' : '现金合理');
              return (
                <div key={pf.model_name} className="bg-white dark:bg-zinc-800 rounded-lg p-6 shadow-sm border border-zinc-200 dark:border-zinc-700">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-1">
                      <span className="text-base font-semibold text-zinc-900 dark:text-zinc-50">{pf.model_name}</span>
                      <span className="text-xs text-zinc-500">总资产 {money1(pf.total_value)}</span>
                    </div>
                    <div className="w-44">
                      <div className="text-xs text-zinc-500 mb-1">现金 {money1(pf.balance)} ({pct1(cashRatio)}) · {cashHint}</div>
                      <div className="h-2 bg-zinc-200 dark:bg-zinc-800 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500" style={{width:`${Math.max(0,Math.min(100,cashRatio))}%`}} />
                      </div>
                    </div>
                  </div>
                  {/* 健康与集中度 */}
                  <div className="grid grid-cols-3 gap-1 mb-3">
                    <div>
                      <div className="text-xs text-zinc-500">最大单一持仓</div>
                      <div className="text-sm font-medium">{pct1(top1Share)}</div>
                    </div>
                    <div>
                      <div className="text-xs text-zinc-500">前3持仓集中度</div>
                      <div className="text-sm font-medium">{pct1(top3Share)}</div>
                    </div>
                    <div>
                      <div className="text-xs text-zinc-500">现金安全带</div>
                      <div className="text-sm font-medium">{cashBandLow}%–{cashBandHigh}%</div>
                    </div>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full text-sm">
                      <thead>
                        <tr className="text-left text-zinc-600 dark:text-zinc-400">
                          <th className="py-2 pr-4">方向</th>
                          <th className="py-2 pr-4">资产名</th>
                          <th className="py-2 pr-4">杠杆</th>
                          <th className="py-2 pr-4">价值</th>
                          <th className="py-2 pr-4">未实现盈亏</th>
                          <th className="py-2 pr-0">平仓价格</th>
                        </tr>
                      </thead>
                      <tbody>
                        {rows.length===0? (
                          <tr><td colSpan={6} className="py-6 text-center text-zinc-500">无持仓</td></tr>
                        ):(
                          rows.map(r=>{
                            const posUp = (r.pnl??0)>=0;
                            return (
                              <tr key={`${r.symbol}-${r.value}`} className="border-t border-zinc-200 dark:border-zinc-800">
                                <td className="py-2 pr-4">{(r.side||'long').toLowerCase()==='short'?'空':'多'}</td>
                                <td className="py-2 pr-4">{r.symbol}</td>
                                <td className="py-2 pr-4">{r.leverage}x</td>
                                <td className="py-2 pr-4">{r.value!==null? money1(r.value):'--'}</td>
                                <td className={`py-2 pr-4 ${posUp?'text-green-600':'text-red-600'}`}>{r.pnl!==null? `${money1(r.pnl)} (${pct1(r.pnlPct as number)})`:'--'}</td>
                                <td className="py-2 pr-0">{r.closePrice!==null && r.closePrice!==undefined? money1(r.closePrice):'--'}</td>
                              </tr>
                            )
                          })
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              )
            })}
            
          </div>
        </div>

        {/* 底部标注 */}
        <div className="mt-6 text-xs text-zinc-500 dark:text-zinc-400">
          数据延迟与来源说明 · 刷新策略：SWR/无感刷新 · 时区：本地
        </div>
      {/* 对话详情 Modal */}
      {dialogOpen && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={()=>setDialogOpen(false)}>
          <div className="bg-white dark:bg-zinc-900 rounded-lg shadow-xl w-[min(900px,90vw)] max-h-[80vh] overflow-auto" onClick={(e)=>e.stopPropagation()}>
            <div className="p-4 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between">
              <div className="text-base font-semibold text-zinc-900 dark:text-zinc-50">对话详情</div>
              <button className="px-2 py-1 text-sm bg-zinc-200 dark:bg-zinc-800 rounded" onClick={()=>setDialogOpen(false)}>关闭</button>
            </div>
            <div className="p-4 text-sm">
              {dialogLoading ? (
                <div className="py-12 text-center text-zinc-500">加载中...</div>
              ) : dialogData && !dialogData.error ? (
                <div className="space-y-3">
                  <div className="text-zinc-500">时间：{new Date(dialogData.timestamp).toLocaleString()}</div>
                  {dialogData.decision && (
                    <>
                      <div className="text-zinc-500">模型：{dialogData.decision.model_name} · 资产：{dialogData.decision.symbol || '—'}</div>
                      <div className="text-zinc-500">交易原因：{dialogData.decision.reasoning || '—'}</div>
                      {dialogData.decision.analysis && (
                        <div className="bg-zinc-50 dark:bg-zinc-800 rounded p-3">
                          <div className="text-xs text-zinc-500 mb-1">当前分析</div>
                          <pre className="whitespace-pre-wrap break-words text-zinc-800 dark:text-zinc-200">{dialogData.decision.analysis}</pre>
                        </div>
                      )}
                    </>
                  )}
                  <div className="bg-zinc-50 dark:bg-zinc-800 rounded p-3">
                    <div className="text-xs text-zinc-500 mb-1">输入 Prompt</div>
                    <pre className="whitespace-pre-wrap break-words text-zinc-800 dark:text-zinc-200">{dialogData.prompt || '—'}</pre>
                  </div>
                  <div className="bg-zinc-50 dark:bg-zinc-800 rounded p-3">
                    <div className="text-xs text-zinc-500 mb-1">输出 Response</div>
                    <pre className="whitespace-pre-wrap break-words text-zinc-800 dark:text-zinc-200">{dialogData.response || '—'}</pre>
                  </div>
                  <div className="grid grid-cols-3 gap-1 text-xs text-zinc-500">
                    <div>Tokens: {dialogData.tokens_used ?? '--'}</div>
                    <div>耗时: {dialogData.duration_ms ? `${dialogData.duration_ms} ms` : '--'}</div>
                    <div>模型: {dialogData.model_name}</div>
                  </div>
                </div>
              ) : (
                <div className="py-12 text-center text-red-500">{dialogData?.error || '加载失败'}</div>
              )}
            </div>
        </div>
        </div>
      )}
      </div>
    </div>
  );
}


