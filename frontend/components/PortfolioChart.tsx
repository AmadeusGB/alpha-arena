'use client';

import React, { useEffect, useRef } from 'react';
import { ModelPortfolio } from '../types';

interface PortfolioChartProps {
  portfolios: ModelPortfolio[];
  historyData: any[];
  timeRange: '15m' | '1h' | '3h' | '6h' | '12h' | '1d';
  metric?: 'balance' | 'total_value' | 'position_value';
}

export default function PortfolioChart({ portfolios, historyData, timeRange, metric = 'total_value' }: PortfolioChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstanceRef = useRef<any>(null);
  const echartsRef = useRef<any>(null);

  // 处理数据
  const processedData = React.useMemo(() => {
    if (!historyData || historyData.length === 0) {
      return {
        xAxisData: [],
        series: portfolios.map(() => ({ data: [] }))
      };
    }



    // X轴数据（时间）- 转换为时间戳（毫秒）
    const xAxisData = historyData.map((item: any) => new Date(item.timestamp).getTime());
    console.log('📊 ECharts 数据准备:', {
        historyDataLength: historyData.length,
        portfolios: portfolios.map(p => p.model_name),
        xAxisDataSample: xAxisData.slice(0, 3)
      });
    // 每个模型的序列数据（余额/资产总值/持仓总值）- 使用 [时间戳, 值] 格式
    const series = portfolios.map((portfolio) => {
      const rawPoints = historyData.map((item: any) => {
        const timestamp = new Date(item.timestamp).getTime();
        const modelData = item[`${portfolio.model_name}_detail`];
        let value: number | null = null;
        if (metric === 'balance') value = modelData?.balance;
        else if (metric === 'total_value') value = modelData?.balance + (modelData?.position_value || 0);
        else if (metric === 'position_value') value = modelData?.position_value;
        return [timestamp, typeof value === 'number' ? value : null] as [number, number | null];
      });

      // 过滤无效点并按时间升序排序
      const cleanedPoints = rawPoints
        .filter((pt) => Number.isFinite(pt[0]) && pt[1] !== null && Number.isFinite(pt[1] as number))
        .sort((a, b) => a[0] - b[0]);

      // 诊断日志
      if (cleanedPoints.length === 0) {
        console.warn(`ECharts: 无有效数据可绘制 → 模型=${portfolio.model_name}`, {
          total: rawPoints.length,
          samples: rawPoints.slice(0, 3)
        });
      }

      return {
        name: portfolio.model_name,
        type: 'line',
        data: cleanedPoints,
        smooth: false,
        showSymbol: false,
        lineStyle: {
          width: 2,
          type: 'solid'
        },
        areaStyle: {
          opacity: 0.05
        },
        // 在终点处绘制 “模型-金额” 标签
        endLabel: {
          show: true,
          formatter: (params: any) => {
            const v = Array.isArray(params.value) ? params.value[1] : params.value;
            const intVal = typeof v === 'number' && isFinite(v) ? Math.round(v) : 0;
            return `${params.seriesName}$${intVal}`;
          },
          color: '#374151',
          fontWeight: 'bold',
          padding: [2,6,2,6],
          backgroundColor: 'rgba(255,255,255,0.6)',
          borderRadius: 4,
          align: 'left',
          offset: [8, 0]
        },
        labelLayout: { hideOverlap: true, moveOverlap: 'shiftY' },
        emphasis: {
          focus: 'series'
        }
      };
    });

    return { xAxisData, series };
  }, [historyData, portfolios, metric]);

  // 渲染图表
  useEffect(() => {
    if (!chartRef.current) return;

    // 动态导入 ECharts
    const initChart = async () => {
      if (!echartsRef.current) {
        try {
          const echartsModule = await import('echarts');
          echartsRef.current = echartsModule;
          console.log('ECharts loaded:', echartsRef.current);
        } catch (error) {
          console.error('Failed to load ECharts:', error);
          return;
        }
      }

      if (!chartInstanceRef.current && chartRef.current && echartsRef.current) {
        try {
          chartInstanceRef.current = echartsRef.current.init(chartRef.current);
          console.log('Chart initialized:', chartInstanceRef.current);
        } catch (error) {
          console.error('Failed to initialize chart:', error);
          return;
        }
      }

      if (!chartInstanceRef.current) return;
      const chart = chartInstanceRef.current;

      // 格式化时间轴标签
      const formatTimeLabel = (value: string) => {
        const date = new Date(value);
        
        if (['15m', '1h', '3h'].includes(timeRange)) {
          const hours = String(date.getHours()).padStart(2, '0');
          const minutes = String(date.getMinutes()).padStart(2, '0');
          return `${hours}:${minutes}`;
        }
        
        const month = String(date.getMonth() + 1);
        const day = String(date.getDate());
        const hours = String(date.getHours());
        return `${month}/${day} ${hours}时`;
      };

      // 格式化时间戳显示
      const formatTimestamp = (timestamp: string) => {
        const date = new Date(timestamp);
        return date.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        });
      };

      // 计算动态 Y 轴范围（最小值*0.9 ～ 最大值*1.1）
      const allValues: number[] = [];
      try {
        processedData.series.forEach((s: any) => {
          (s.data || []).forEach((pt: any) => {
            const v = Array.isArray(pt) ? pt[1] : pt;
            if (typeof v === 'number' && isFinite(v)) allValues.push(v);
          });
        });
      } catch {}
      let yMin = 0;
      let yMax = 1;
      if (allValues.length > 0) {
        const minVal = Math.min(...allValues);
        const maxVal = Math.max(...allValues);
        if (isFinite(minVal) && isFinite(maxVal)) {
          if (minVal === maxVal) {
            yMin = minVal * 0.99;
            yMax = maxVal * 1.01;
          } else {
            yMin = minVal * 0.99;
            yMax = maxVal * 1.01;
          }
        }
      }

      // 设置配置
      const option: any = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          label: {
            backgroundColor: '#6a7985'
          }
        },
        formatter: (params: any) => {
          if (!Array.isArray(params)) return '';
          const firstParam = params[0];
          const timestamp = Array.isArray(firstParam.value) ? firstParam.value[0] : firstParam.axisValue;
          let result = formatTimestamp(new Date(timestamp).toISOString()) + '<br/>';
          
          params.forEach((param: any) => {
            const value = Array.isArray(param.value) ? param.value[1] : param.value;
            if (value !== null && value !== undefined) {
              result += `${param.marker} <strong>${param.seriesName}</strong>: $${Number(value).toFixed(2)}<br/>`;
            }
          });
          
          return result;
        }
      },
      legend: {
        data: portfolios.map(p => p.model_name),
        top: 10,
        textStyle: {
          color: '#6b7280'
        }
      },
      grid: {
        left: '3%',
        right: 180,
        bottom: '3%',
        top: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'time',
        boundaryGap: false,
        axisLabel: {
          formatter: (value: number) => {
            const date = new Date(value);
            if (['15m', '1h', '3h'].includes(timeRange)) {
              const hours = String(date.getHours()).padStart(2, '0');
              const minutes = String(date.getMinutes()).padStart(2, '0');
              return `${hours}:${minutes}`;
            }
            const month = String(date.getMonth() + 1);
            const day = String(date.getDate());
            const hours = String(date.getHours());
            return `${month}/${day} ${hours}时`;
          },
          color: '#6b7280'
        },
        axisLine: {
          lineStyle: {
            color: '#e5e7eb'
          }
        },
        splitLine: {
          show: false
        }
      },
      yAxis: {
        type: 'value',
        min: yMin,
        max: yMax,
        axisLabel: {
          formatter: (value: number) => `$${value.toFixed(0)}`,
          color: '#6b7280'
        },
        axisLine: {
          lineStyle: {
            color: '#e5e7eb'
          }
        },
        splitLine: {
          show: true,
          lineStyle: {
            color: '#e5e7eb',
            type: 'dashed'
          }
        },
        splitArea: {
          show: true,
          areaStyle: {
            color: ['rgba(250, 250, 250, 0.05)', 'rgba(200, 200, 200, 0.02)']
          }
        }
      },
      dataZoom: [
        {
          type: 'inside',
          start: 0,
          end: 100
        },
        {
          show: true,
          type: 'slider',
          height: 20,
          bottom: 10
        }
      ],
      series: processedData.series.map((s, idx) => ({
        ...s,
        itemStyle: {
          color: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'][idx % 5]
        },
        lineStyle: {
          color: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'][idx % 5],
          width: 2
        }
      }))
    };

      // 设置配置
      chart.setOption(option, true);

      // 响应式调整
      const handleResize = () => {
        chart.resize();
      };
      window.addEventListener('resize', handleResize);

      return () => {
        window.removeEventListener('resize', handleResize);
      };
    };

    initChart().catch(console.error);
  }, [processedData, timeRange, portfolios]);

  // 清理
  useEffect(() => {
    return () => {
      if (chartInstanceRef.current) {
        chartInstanceRef.current.dispose();
        chartInstanceRef.current = null;
      }
    };
  }, []);

  return (
    <div 
      ref={chartRef} 
      style={{ width: '100%', height: '100%' }}
    />
  );
}

