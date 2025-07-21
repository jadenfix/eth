import React, { useState, useEffect } from 'react';
import { NextPage } from 'next';
import Head from 'next/head';
import { createTimeSeriesChart, BLOCKCHAIN_CHART_CONFIGS } from '../../../services/visualization/timeseries_canvas/chart';

const CanvasPage: NextPage = () => {
  const [activeChart, setActiveChart] = useState('transactionVolume');
  const [timeRange, setTimeRange] = useState('24h');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Initialize the chart when component mounts
    const initializeChart = async () => {
      try {
        const config = {
          ...BLOCKCHAIN_CHART_CONFIGS[activeChart as keyof typeof BLOCKCHAIN_CHART_CONFIGS],
          container: 'time-series-chart'
        };

        // Create the chart
        const chart = createTimeSeriesChart(config);

        // Fetch and load sample data
        await loadChartData(chart, config.metrics, timeRange);
        
        setIsLoading(false);
      } catch (error) {
        console.error('Error initializing chart:', error);
        setIsLoading(false);
      }
    };

    initializeChart();

    return () => {
      // Cleanup chart when component unmounts
      const container = document.getElementById('time-series-chart');
      if (container && container.hasChildNodes()) {
        container.innerHTML = '';
      }
    };
  }, [activeChart, timeRange]);

  const loadChartData = async (chart: any, metrics: string[], range: string) => {
    // Fetch data from metrics API
    try {
      const response = await fetch(`/api/metrics/timeseries`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          metrics,
          timeRange: range,
          granularity: getGranularity(range)
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        // Update chart with fetched data
        metrics.forEach(metric => {
          if (data[metric]) {
            const dataPoints = data[metric].map((point: any) => ({
              timestamp: new Date(point.timestamp),
              value: point.value,
              metric: metric,
              metadata: point.metadata
            }));
            
            chart.updateData(metric, dataPoints);
          }
        });
      }
    } catch (error) {
      console.error('Error loading chart data:', error);
      
      // Load sample data for demo
      loadSampleData(chart, metrics);
    }
  };

  const loadSampleData = (chart: any, metrics: string[]) => {
    const now = new Date();
    const dataPoints = 100;
    
    metrics.forEach(metric => {
      const sampleData = [];
      
      for (let i = 0; i < dataPoints; i++) {
        const timestamp = new Date(now.getTime() - (dataPoints - i) * 60 * 1000); // 1 minute intervals
        let value = 0;
        
        switch (metric) {
          case 'tx_count':
            value = Math.floor(Math.random() * 1000) + 500;
            break;
          case 'tx_volume_eth':
            value = Math.random() * 10000 + 1000;
            break;
          case 'gas_price_gwei':
            value = Math.random() * 100 + 20;
            break;
          case 'gas_used':
            value = Math.random() * 15000000 + 10000000;
            break;
          case 'mev_extracted':
            value = Math.random() * 50 + 10;
            break;
          case 'sandwich_attacks':
            value = Math.floor(Math.random() * 20);
            break;
          case 'arbitrage_volume':
            value = Math.random() * 1000 + 100;
            break;
          default:
            value = Math.random() * 100;
        }
        
        sampleData.push({
          timestamp,
          value,
          metric,
          metadata: { source: 'sample' }
        });
      }
      
      chart.updateData(metric, sampleData);
    });
  };

  const getGranularity = (range: string): string => {
    switch (range) {
      case '1h': return '1m';
      case '6h': return '5m';
      case '24h': return '1h';
      case '7d': return '6h';
      case '30d': return '1d';
      default: return '1h';
    }
  };

  const chartConfigs = [
    { key: 'transactionVolume', name: 'Transaction Volume', icon: '📊' },
    { key: 'gasMetrics', name: 'Gas Metrics', icon: '⛽' },
    { key: 'mevMetrics', name: 'MEV Metrics', icon: '🎯' }
  ];

  const timeRanges = [
    { key: '1h', name: '1 Hour' },
    { key: '6h', name: '6 Hours' },
    { key: '24h', name: '24 Hours' },
    { key: '7d', name: '7 Days' },
    { key: '30d', name: '30 Days' }
  ];

  return (
    <>
      <Head>
        <title>Time Series Canvas - Onchain Command Center</title>
        <meta name="description" content="Real-time blockchain metrics and analytics" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white shadow-sm border-b">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Time Series Canvas</h1>
                <p className="text-gray-600 mt-1">
                  Real-time blockchain metrics and performance analytics
                </p>
              </div>
              
              <div className="flex items-center space-x-4">
                <select
                  value={timeRange}
                  onChange={(e) => setTimeRange(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {timeRanges.map(range => (
                    <option key={range.key} value={range.key}>{range.name}</option>
                  ))}
                </select>
                
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-gray-600">Live</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Chart Type Selector */}
        <div className="bg-white border-b">
          <div className="px-6 py-3">
            <div className="flex space-x-1">
              {chartConfigs.map(config => (
                <button
                  key={config.key}
                  onClick={() => setActiveChart(config.key)}
                  className={`px-4 py-2 rounded-md text-sm font-medium flex items-center space-x-2 ${
                    activeChart === config.key
                      ? 'bg-blue-100 text-blue-700 border-blue-200'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <span>{config.icon}</span>
                  <span>{config.name}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Main Chart Container */}
        <div className="flex-1 p-6">
          {isLoading ? (
            <div className="bg-white rounded-lg shadow-sm border h-96 flex items-center justify-center">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                <p className="mt-4 text-gray-600">Loading chart data...</p>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-sm border">
              {/* Chart Container */}
              <div id="time-series-chart" className="w-full h-96 p-4"></div>
              
              {/* Chart Controls */}
              <div className="border-t bg-gray-50 px-4 py-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <span>Chart: {chartConfigs.find(c => c.key === activeChart)?.name}</span>
                    <span>Range: {timeRanges.find(r => r.key === timeRange)?.name}</span>
                    <span>Updates: Real-time</span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => {
                        // Export chart data
                        const container = document.getElementById('time-series-chart');
                        if (container) {
                          // This would trigger the chart's built-in export functionality
                          console.log('Export chart data');
                        }
                      }}
                      className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
                    >
                      Export
                    </button>
                    
                    <button
                      onClick={() => window.location.reload()}
                      className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Refresh
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Metrics Summary */}
        <div className="bg-white border-t px-6 py-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">--</div>
              <div className="text-xs text-gray-600">Current TPS</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">--</div>
              <div className="text-xs text-gray-600">Gas Price (Gwei)</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">--</div>
              <div className="text-xs text-gray-600">MEV Extracted</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">--</div>
              <div className="text-xs text-gray-600">Network Load</div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default CanvasPage;
