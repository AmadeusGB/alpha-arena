export interface MarketPrice {
  id: number;
  symbol: string;
  price: number;
  volume?: number;
  source: string;
  timestamp: string;
}

export interface Decision {
  id: number;
  model_name: string;
  symbol?: string;
  action: 'BUY' | 'SELL' | 'HOLD';
  confidence?: number;
  reasoning?: string;
  prompt?: string;
  response_raw?: any;
  timestamp: string;
}

export interface ModelPortfolio {
  id: number;
  model_name: string;
  balance: number;
  total_value: number;
  daily_pnl: number;
  total_pnl: number;
  total_return: number;
  max_drawdown: number;
  is_active: string;
  initial_capital: number;
  updated_at: string;
  created_at: string;
}

export interface Position {
  id: number;
  model_name: string;
  symbol: string;
  quantity: number;
  entry_price: number;
  current_price?: number;
  pnl: number;
  pnl_percent: number;
  status: 'open' | 'closed';
  decision_id?: number;
  opened_at: string;
  closed_at?: string;
}

export interface SystemStatus {
  scheduler_running: boolean;
  last_run_time: string | null;
  error_count: number;
  latest_log: string | null;
  database_connected: boolean;
}

export interface PerformanceMetrics {
  model_name: string;
  total_return: number;
  daily_pnl: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  total_trades: number;
  profitable_trades: number;
}

