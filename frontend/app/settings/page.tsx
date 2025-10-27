'use client';

import { useEffect, useState } from 'react';
import { settingsApi, modelsApi } from '../../lib/api';

interface TradingSettings {
  id: number;
  name: string;
  maker_fee: number;
  taker_fee: number;
  slippage: number;
  max_leverage: number;
  allow_short: boolean;
  min_position: number;
  max_position: number;
  position_unit: number;
  stop_loss_min: number;
  stop_loss_max: number;
  take_profit_min: number;
  take_profit_max: number;
  max_position_percent: number;
  max_drawdown: number;
  min_confidence: number;
  max_open_positions: number;
  cooldown_minutes: number;
  min_trade_amount: number;
  max_trade_amount: number;
}

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<'trading' | 'models'>('trading');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState<TradingSettings | null>(null);
  const [message, setMessage] = useState('');
  
  // 模型管理相关状态
  const [models, setModels] = useState<any[]>([]);
  const [modelsLoading, setModelsLoading] = useState(true);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editModel, setEditModel] = useState<any | null>(null);
  const [testingModel, setTestingModel] = useState<number | null>(null);
  const [testResult, setTestResult] = useState<any | null>(null);
  const [testModalOpen, setTestModalOpen] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  useEffect(() => {
    if (activeTab === 'models') {
      loadModels();
    }
  }, [activeTab]);

  const loadSettings = async () => {
    try {
      const res = await settingsApi.getTradingSettings();
      setSettings(res.data);
    } catch (error) {
      console.error('Error loading settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!settings) return;
    
    setSaving(true);
    try {
      await settingsApi.updateTradingSettings('default', settings);
      setMessage('✅ 设置已保存');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('❌ 保存失败');
      console.error('Error saving settings:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    if (!confirm('确定要重置为默认设置吗？')) return;
    
    try {
      const res = await settingsApi.resetTradingSettings();
      setSettings(res.data);
      setMessage('✅ 已重置为默认设置');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('❌ 重置失败');
      console.error('Error resetting settings:', error);
    }
  };

  const updateField = (field: keyof TradingSettings, value: any) => {
    if (!settings) return;
    setSettings({ ...settings, [field]: value });
  };

  // 模型管理相关函数
  const loadModels = async () => {
    try {
      setModelsLoading(true);
      const res = await modelsApi.getModels();
      setModels(res.data);
    } catch (error) {
      console.error('Error loading models:', error);
    } finally {
      setModelsLoading(false);
    }
  };

  const handleEnableModel = async (modelId: number, enabled: boolean) => {
    try {
      if (enabled) {
        await modelsApi.enableModel(modelId);
      } else {
        await modelsApi.disableModel(modelId);
      }
      await loadModels();
      setMessage(`✅ 模型已${enabled ? '启用' : '禁用'}`);
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Error toggling model:', error);
      setMessage('❌ 操作失败');
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const handleDeleteModel = async (modelId: number) => {
    if (!confirm('确定要删除此模型吗？')) return;
    
    try {
      await modelsApi.deleteModel(modelId);
      await loadModels();
      setMessage('✅ 模型已删除');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Error deleting model:', error);
      setMessage('❌ 删除失败');
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const handleSaveModel = async () => {
    if (!editModel) return;
    
    try {
      if (editModel.id) {
        // 更新模型
        await modelsApi.updateModel(editModel.id, editModel);
        setMessage('✅ 模型已更新');
      } else {
        // 创建模型
        await modelsApi.createModel(editModel);
        setMessage('✅ 模型已创建');
      }
      setEditModalOpen(false);
      setEditModel(null);
      await loadModels();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Error saving model:', error);
      setMessage('❌ 保存失败');
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const handleTestModel = async (modelId: number) => {
    setTestingModel(modelId);
    setTestResult(null);
    
    try {
      const res = await modelsApi.testModel(modelId);
      setTestResult(res.data);
      setTestModalOpen(true);
    } catch (error: any) {
      setTestResult({
        success: false,
        error: error.message || '测试失败'
      });
      setTestModalOpen(true);
    } finally {
      setTestingModel(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl text-zinc-600 dark:text-zinc-400">加载中...</div>
      </div>
    );
  }

  if (!settings) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-50 to-zinc-100 dark:from-zinc-900 dark:to-black">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-zinc-900 dark:text-zinc-50 mb-2">
            ⚙️ 系统设置
          </h1>
          <p className="text-zinc-600 dark:text-zinc-400">
            交易参数和风险控制配置
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-6 border-b border-zinc-200 dark:border-zinc-700">
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('trading')}
              className={`px-4 py-2 font-medium transition-colors ${
                activeTab === 'trading'
                  ? 'border-b-2 border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-300'
              }`}
            >
              💰 交易设置
            </button>
            <button
              onClick={() => setActiveTab('models')}
              className={`px-4 py-2 font-medium transition-colors ${
                activeTab === 'models'
                  ? 'border-b-2 border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-300'
              }`}
            >
              🤖 模型管理
            </button>
          </div>
        </div>

        {message && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.includes('✅') 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
              : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
          }`}>
            {message}
          </div>
        )}

    {/* 交易设置 Tab */}
    {activeTab === 'trading' && (
      <>
        {/* 交易费用 */}
        <div className="bg-white dark:bg-zinc-800 rounded-lg p-6 shadow-sm border border-zinc-200 dark:border-zinc-700 mb-6">
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 mb-4">
            💰 交易费用
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                Maker 费率 (%)
              </label>
              <input
                type="number"
                step="0.0001"
                value={settings.maker_fee * 100}
                onChange={(e) => updateField('maker_fee', parseFloat(e.target.value) / 100)}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                Taker 费率 (%)
              </label>
              <input
                type="number"
                step="0.0001"
                value={settings.taker_fee * 100}
                onChange={(e) => updateField('taker_fee', parseFloat(e.target.value) / 100)}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                滑点 (%)
              </label>
              <input
                type="number"
                step="0.0001"
                value={settings.slippage * 100}
                onChange={(e) => updateField('slippage', parseFloat(e.target.value) / 100)}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-50"
              />
            </div>
          </div>
        </div>

        {/* 策略配置 */}
        <div className="bg-white dark:bg-zinc-800 rounded-lg p-6 shadow-sm border border-zinc-200 dark:border-zinc-700 mb-6">
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 mb-4">
            📊 策略配置
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                最大杠杆
              </label>
              <input
                type="number"
                value={settings.max_leverage}
                onChange={(e) => updateField('max_leverage', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                允许做空
              </label>
              <select
                value={settings.allow_short ? 'true' : 'false'}
                onChange={(e) => updateField('allow_short', e.target.value === 'true')}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-50"
              >
                <option value="false">否</option>
                <option value="true">是</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                最大持仓比例
              </label>
              <input
                type="number"
                step="0.01"
                value={settings.max_position}
                onChange={(e) => updateField('max_position', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-50"
              />
            </div>
          </div>
        </div>

        {/* 风险控制 */}
        <div className="bg-white dark:bg-zinc-800 rounded-lg p-6 shadow-sm border border-zinc-200 dark:border-zinc-700 mb-6">
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 mb-4">
            🛡️ 风险控制
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                止损最小 (%)
              </label>
              <input
                type="number"
                step="0.01"
                value={settings.stop_loss_min * 100}
                onChange={(e) => updateField('stop_loss_min', parseFloat(e.target.value) / 100)}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                止损最大 (%)
              </label>
              <input
                type="number"
                step="0.01"
                value={settings.stop_loss_max * 100}
                onChange={(e) => updateField('stop_loss_max', parseFloat(e.target.value) / 100)}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                止盈最小 (%)
              </label>
              <input
                type="number"
                step="0.01"
                value={settings.take_profit_min * 100}
                onChange={(e) => updateField('take_profit_min', parseFloat(e.target.value) / 100)}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                止盈最大 (%)
              </label>
              <input
                type="number"
                step="0.01"
                value={settings.take_profit_max * 100}
                onChange={(e) => updateField('take_profit_max', parseFloat(e.target.value) / 100)}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-50"
              />
            </div>
          </div>
        </div>

        {/* 其他设置 */}
        <div className="bg-white dark:bg-zinc-800 rounded-lg p-6 shadow-sm border border-zinc-200 dark:border-zinc-700 mb-6">
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 mb-4">
            ⚡ 其他设置
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                最小信心阈值
              </label>
              <input
                type="number"
                step="0.1"
                value={settings.min_confidence}
                onChange={(e) => updateField('min_confidence', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                最大持仓数
              </label>
              <input
                type="number"
                value={settings.max_open_positions}
                onChange={(e) => updateField('max_open_positions', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                冷却期 (分钟)
              </label>
              <input
                type="number"
                value={settings.cooldown_minutes}
                onChange={(e) => updateField('cooldown_minutes', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-50"
              />
            </div>
          </div>
        </div>

        {/* 操作按钮 */}
        <div className="flex gap-4">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50"
          >
            {saving ? '保存中...' : '💾 保存设置'}
          </button>
          
          <button
            onClick={handleReset}
            className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
          >
            🔄 重置为默认
          </button>
        </div>
      </>
    )}

    {/* 模型管理 Tab */}
    {activeTab === 'models' && (
      <>
        {/* 模型列表 */}
        <div className="bg-white dark:bg-zinc-800 rounded-lg p-6 shadow-sm border border-zinc-200 dark:border-zinc-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
              AI 模型配置
            </h2>
            <button
              onClick={() => {
                setEditModel({
                  name: '',
                  provider: 'siliconflow',
                  model_id: '',
                  api_key: '',
                  base_url: 'https://api.siliconflow.cn/v1',
                  is_enabled: true
                });
                setEditModalOpen(true);
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              + 添加模型
            </button>
          </div>

          {modelsLoading ? (
            <div className="text-center py-8 text-zinc-600 dark:text-zinc-400">
              加载中...
            </div>
          ) : models.length === 0 ? (
            <div className="text-center py-8 text-zinc-600 dark:text-zinc-400">
              暂无模型配置，点击"添加模型"创建
            </div>
          ) : (
            <div className="space-y-3">
              {models.map((model) => (
                <div
                  key={model.id}
                  className="flex items-center justify-between p-4 border border-zinc-200 dark:border-zinc-700 rounded-lg hover:bg-zinc-50 dark:hover:bg-zinc-700 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-zinc-900 dark:text-zinc-50">
                        {model.name}
                      </h3>
                      <span
                        className={`px-2 py-1 rounded text-xs ${
                          model.is_enabled
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                            : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                        }`}
                      >
                        {model.is_enabled ? '已启用' : '已禁用'}
                      </span>
                    </div>
                    <p className="text-sm text-zinc-600 dark:text-zinc-400">
                      {model.provider} - {model.model_id}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleTestModel(model.id)}
                      disabled={testingModel === model.id}
                      className="px-3 py-1 bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200 rounded text-sm hover:bg-purple-200 dark:hover:bg-purple-800 transition-colors disabled:opacity-50"
                    >
                      {testingModel === model.id ? '测试中...' : '测试'}
                    </button>
                    <button
                      onClick={() => {
                        setEditModel(model);
                        setEditModalOpen(true);
                      }}
                      className="px-3 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded text-sm hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
                    >
                      编辑
                    </button>
                    <button
                      onClick={() => handleEnableModel(model.id, !model.is_enabled)}
                      className={`px-3 py-1 rounded text-sm transition-colors ${
                        model.is_enabled
                          ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 hover:bg-yellow-200 dark:hover:bg-yellow-800'
                          : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 hover:bg-green-200 dark:hover:bg-green-800'
                      }`}
                    >
                      {model.is_enabled ? '禁用' : '启用'}
                    </button>
                    <button
                      onClick={() => handleDeleteModel(model.id)}
                      className="px-3 py-1 bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded text-sm hover:bg-red-200 dark:hover:bg-red-800 transition-colors"
                    >
                      删除
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </>
    )}

    {/* 编辑模型 Modal */}
    {editModalOpen && editModel && (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-zinc-800 rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50 mb-4">
            {editModel.id ? '编辑模型' : '添加模型'}
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                模型名称 *
              </label>
              <input
                type="text"
                value={editModel.name}
                onChange={(e) => setEditModel({ ...editModel, name: e.target.value })}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-50"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                提供商 *
              </label>
              <select
                value={editModel.provider}
                onChange={(e) => setEditModel({ ...editModel, provider: e.target.value })}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-50"
              >
                <option value="siliconflow">SiliconFlow</option>
                <option value="openai">OpenAI</option>
                <option value="claude">Claude</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                模型ID *
              </label>
              <input
                type="text"
                value={editModel.model_id}
                onChange={(e) => setEditModel({ ...editModel, model_id: e.target.value })}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-50"
                placeholder="例如: Qwen/Qwen3-32B"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                API Key
              </label>
              <input
                type="password"
                value={editModel.api_key || ''}
                onChange={(e) => setEditModel({ ...editModel, api_key: e.target.value })}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-50"
                placeholder="留空使用全局配置"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                Base URL
              </label>
              <input
                type="text"
                value={editModel.base_url || ''}
                onChange={(e) => setEditModel({ ...editModel, base_url: e.target.value })}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-50"
                placeholder="例如: https://api.siliconflow.cn/v1"
              />
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_enabled"
                checked={editModel.is_enabled}
                onChange={(e) => setEditModel({ ...editModel, is_enabled: e.target.checked })}
                className="h-4 w-4 text-blue-600 border-zinc-300 rounded"
              />
              <label htmlFor="is_enabled" className="ml-2 text-sm text-zinc-700 dark:text-zinc-300">
                启用此模型
              </label>
            </div>
          </div>
          
          <div className="flex gap-4 mt-6">
            <button
              onClick={handleSaveModel}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              保存
            </button>
            <button
              onClick={() => {
                setEditModalOpen(false);
                setEditModel(null);
              }}
              className="flex-1 px-4 py-2 bg-gray-200 dark:bg-zinc-700 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-zinc-600 transition-colors"
            >
              取消
            </button>
          </div>
        </div>
      </div>
    )}

    {/* 测试结果 Modal */}
    {testModalOpen && testResult && (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-zinc-800 rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50 mb-4">
            模型测试结果
          </h2>
          
          <div className="space-y-4">
            {/* 测试状态 */}
            <div className="p-4 rounded-lg bg-zinc-50 dark:bg-zinc-700">
              <div className="flex items-center gap-2 mb-2">
                <span className={`text-lg ${testResult.success ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                  {testResult.success ? '✅' : '❌'}
                </span>
                <span className="font-semibold text-zinc-900 dark:text-zinc-50">
                  {testResult.success ? '测试成功' : '测试失败'}
                </span>
              </div>
              
              {testResult.response_time && (
                <div className="text-sm text-zinc-600 dark:text-zinc-400">
                  响应时间: {(testResult.response_time * 1000).toFixed(0)}ms
                </div>
              )}
            </div>

            {/* 响应内容 */}
            {testResult.response && (
              <div>
                <h3 className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                  模型响应:
                </h3>
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <pre className="text-sm text-zinc-800 dark:text-zinc-200 whitespace-pre-wrap overflow-x-auto">
                    {typeof testResult.response === 'string' 
                      ? testResult.response 
                      : JSON.stringify(testResult.response, null, 2)}
                  </pre>
                </div>
              </div>
            )}

            {/* 错误信息 */}
            {testResult.error && (
              <div>
                <h3 className="text-sm font-semibold text-red-700 dark:text-red-400 mb-2">
                  错误信息:
                </h3>
                <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                  <p className="text-sm text-red-800 dark:text-red-300">
                    {testResult.error}
                  </p>
                </div>
              </div>
            )}
          </div>
          
          <div className="flex gap-4 mt-6">
            <button
              onClick={() => {
                setTestModalOpen(false);
                setTestResult(null);
              }}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              关闭
            </button>
          </div>
        </div>
      </div>
    )}
      </div>
    </div>
  );
}
