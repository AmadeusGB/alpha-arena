'use client';

import { useEffect, useState } from 'react';
import { systemApi } from '../../lib/api';
import { SystemStatus } from '../../types';

export default function SystemPage() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 5000); // 每5秒刷新
    return () => clearInterval(interval);
  }, []);

  const loadStatus = async () => {
    try {
      const res = await systemApi.getStatus();
      setStatus(res.data);
    } catch (error) {
      console.error('Error loading system status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartScheduler = async () => {
    try {
      await systemApi.startScheduler();
      setMessage('✅ 调度器已启动');
      loadStatus();
    } catch (error) {
      setMessage('❌ 启动失败');
      console.error('Error starting scheduler:', error);
    }
  };

  const handleStopScheduler = async () => {
    try {
      await systemApi.stopScheduler();
      setMessage('⏹️ 调度器已停止');
      loadStatus();
    } catch (error) {
      setMessage('❌ 停止失败');
      console.error('Error stopping scheduler:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl text-zinc-600 dark:text-zinc-400">加载中...</div>
      </div>
    );
  }

  return (
    <>
      <h1 >
        定时任务调度和系统状态监控
      </h1>

        {message && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.includes('✅') 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
              : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
          }`}>
            {message}
          </div>
        )}

        {/* 系统状态卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white dark:bg-zinc-800 rounded-lg p-6 shadow-sm border border-zinc-200 dark:border-zinc-700">
            <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 mb-4">
              调度器状态
            </h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-zinc-600 dark:text-zinc-400">运行状态</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  status?.scheduler_running
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                }`}>
                  {status?.scheduler_running ? '运行中' : '已停止'}
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-zinc-600 dark:text-zinc-400">上次执行</span>
                <span className="text-zinc-900 dark:text-zinc-50">
                  {status?.last_run_time || '从未执行'}
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-zinc-600 dark:text-zinc-400">错误计数</span>
                <span className={`font-semibold ${
                  (status?.error_count || 0) > 0
                    ? 'text-red-600 dark:text-red-400'
                    : 'text-green-600 dark:text-green-400'
                }`}>
                  {status?.error_count || 0}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-zinc-800 rounded-lg p-6 shadow-sm border border-zinc-200 dark:border-zinc-700">
            <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 mb-4">
              数据库状态
            </h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-zinc-600 dark:text-zinc-400">连接状态</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  status?.database_connected
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                }`}>
                  {status?.database_connected ? '已连接' : '未连接'}
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-zinc-600 dark:text-zinc-400">最新日志</span>
                <span className="text-sm text-zinc-600 dark:text-zinc-400 truncate">
                  {status?.latest_log || '暂无'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* 控制按钮 */}
        <div className="bg-white dark:bg-zinc-800 rounded-lg p-6 shadow-sm border border-zinc-200 dark:border-zinc-700">
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 mb-4">
            调度器控制
          </h2>
          <div className="flex gap-4">
            <button
              onClick={handleStartScheduler}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              ▶️ 启动调度器
            </button>
            
            <button
              onClick={handleStopScheduler}
              className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
            >
              ⏹️ 停止调度器
            </button>
            
            <button
              onClick={loadStatus}
              className="px-6 py-3 bg-zinc-600 text-white rounded-lg hover:bg-zinc-700 transition-colors font-medium"
            >
              🔄 刷新状态
            </button>
          </div>
        </div>

        {/* 说明 */}
        <div className="mt-6 p-6 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
            ℹ️ 定时任务说明
          </h3>
          <ul className="space-y-2 text-sm text-blue-800 dark:text-blue-200">
            <li>• 定时任务每 5 分钟自动执行一次</li>
            <li>• 获取最新市场价格并保存</li>
            <li>• 调用 AI 模型生成交易决策</li>
            <li>• 模拟执行交易并更新持仓</li>
            <li>• 记录所有操作到数据库</li>
          </ul>
        </div>
        </>
  );
}

