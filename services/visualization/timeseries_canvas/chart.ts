/**
 * Time-Series Canvas - High-performance blockchain metrics visualization
 * Plotly.js and D3.js based charts for transaction volumes, prices, and analytics
 */

import * as d3 from 'd3';
import Plotly from 'plotly.js-dist';

interface TimeSeriesDataPoint {
  timestamp: Date;
  value: number;
  metric: string;
  metadata?: Record<string, any>;
}

interface TimeSeriesConfig {
  container: string;
  title: string;
  metrics: string[];
  colors?: string[];
  yAxisLabel?: string;
  showRangeSelector?: boolean;
  showCrosshair?: boolean;
  realtime?: boolean;
}

class TimeSeriesCanvas {
  private container: HTMLElement;
  private config: TimeSeriesConfig;
  private data: Map<string, TimeSeriesDataPoint[]> = new Map();
  private plot: Plotly.PlotlyHTMLElement | null = null;
  private websocket: WebSocket | null = null;

  constructor(config: TimeSeriesConfig) {
    this.config = config;
    this.container = document.getElementById(config.container) as HTMLElement;
    
    if (!this.container) {
      throw new Error(`Container element '${config.container}' not found`);
    }

    this.initialize();
  }

  private initialize(): void {
    // Initialize data maps for each metric
    this.config.metrics.forEach(metric => {
      this.data.set(metric, []);
    });

    this.createPlot();
    
    if (this.config.realtime) {
      this.setupWebSocket();
    }
  }

  private createPlot(): void {
    const traces = this.config.metrics.map((metric, index) => ({
      x: this.data.get(metric)?.map(d => d.timestamp) || [],
      y: this.data.get(metric)?.map(d => d.value) || [],
      type: 'scatter',
      mode: 'lines',
      name: metric,
      line: {
        color: this.config.colors?.[index] || d3.schemeCategory10[index % 10],
        width: 2
      },
      hovertemplate: `<b>${metric}</b><br>` +
                    'Time: %{x}<br>' +
                    'Value: %{y:,.2f}<br>' +
                    '<extra></extra>'
    })) as Plotly.Data[];

    const layout: Partial<Plotly.Layout> = {
      title: {
        text: this.config.title,
        font: { size: 16 }
      },
      xaxis: {
        title: 'Time',
        type: 'date',
        showgrid: true,
        gridcolor: '#f0f0f0',
        ...(this.config.showRangeSelector && {
          rangeselector: {
            buttons: [
              { count: 1, label: '1h', step: 'hour', stepmode: 'backward' },
              { count: 6, label: '6h', step: 'hour', stepmode: 'backward' },
              { count: 24, label: '1d', step: 'hour', stepmode: 'backward' },
              { count: 7, label: '7d', step: 'day', stepmode: 'backward' },
              { step: 'all' }
            ]
          },
          rangeslider: { visible: false }
        })
      },
      yaxis: {
        title: this.config.yAxisLabel || 'Value',
        showgrid: true,
        gridcolor: '#f0f0f0',
        tickformat: ',.2f'
      },
      hovermode: this.config.showCrosshair ? 'x unified' : 'closest',
      showlegend: true,
      legend: {
        orientation: 'h',
        y: -0.2
      },
      margin: { l: 50, r: 50, t: 50, b: 100 },
      plot_bgcolor: 'white',
      paper_bgcolor: 'white'
    };

    const plotConfig: Partial<Plotly.Config> = {
      responsive: true,
      displayModeBar: true,
      modeBarButtonsToAdd: [
        {
          name: 'Download CSV',
          icon: Plotly.Icons.disk,
          click: () => this.downloadData()
        }
      ],
      toImageButtonOptions: {
        format: 'png',
        filename: `${this.config.title.toLowerCase().replace(/\s+/g, '_')}_chart`,
        height: 500,
        width: 1200,
        scale: 2
      }
    };

    Plotly.newPlot(this.container, traces, layout, plotConfig).then(plot => {
      this.plot = plot as Plotly.PlotlyHTMLElement;
      
      // Add event listeners
      this.plot.on('plotly_hover', (data) => {
        if (data.points.length > 0) {
          const point = data.points[0];
          this.onPointHover(point);
        }
      });

      this.plot.on('plotly_click', (data) => {
        if (data.points.length > 0) {
          const point = data.points[0];
          this.onPointClick(point);
        }
      });
    });
  }

  public updateData(metric: string, dataPoints: TimeSeriesDataPoint[]): void {
    if (!this.data.has(metric)) {
      console.warn(`Metric '${metric}' not configured`);
      return;
    }

    this.data.set(metric, dataPoints);
    this.refreshPlot();
  }

  public addDataPoint(metric: string, dataPoint: TimeSeriesDataPoint): void {
    if (!this.data.has(metric)) {
      console.warn(`Metric '${metric}' not configured`);
      return;
    }

    const points = this.data.get(metric)!;
    points.push(dataPoint);

    // Keep only last 1000 points for performance
    if (points.length > 1000) {
      points.shift();
    }

    this.data.set(metric, points);
    
    if (this.config.realtime) {
      this.refreshPlotRealtime(metric);
    }
  }

  private refreshPlot(): void {
    if (!this.plot) return;

    const update = this.config.metrics.reduce((acc, metric) => {
      const points = this.data.get(metric) || [];
      acc.x.push(points.map(d => d.timestamp));
      acc.y.push(points.map(d => d.value));
      return acc;
    }, { x: [] as Date[][], y: [] as number[][] });

    Plotly.restyle(this.plot, update);
  }

  private refreshPlotRealtime(metric: string): void {
    if (!this.plot) return;

    const metricIndex = this.config.metrics.indexOf(metric);
    if (metricIndex === -1) return;

    const points = this.data.get(metric) || [];
    const update = {
      x: [points.map(d => d.timestamp)],
      y: [points.map(d => d.value)]
    };

    Plotly.restyle(this.plot, update, [metricIndex]);
  }

  private setupWebSocket(): void {
    const wsUrl = process.env.NEXT_PUBLIC_WEBSOCKET_ENDPOINT || 'ws://localhost:4000/subscriptions';
    this.websocket = new WebSocket(wsUrl);

    this.websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'timeseries' && this.config.metrics.includes(data.metric)) {
          this.addDataPoint(data.metric, {
            timestamp: new Date(data.timestamp),
            value: data.value,
            metric: data.metric,
            metadata: data.metadata
          });
        }
      } catch (error) {
        console.error('Error processing WebSocket message:', error);
      }
    };

    this.websocket.onopen = () => {
      console.log('WebSocket connected for time-series updates');
      // Subscribe to metrics
      this.websocket?.send(JSON.stringify({
        type: 'subscribe',
        metrics: this.config.metrics
      }));
    };

    this.websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.websocket.onclose = () => {
      console.log('WebSocket disconnected');
      // Attempt to reconnect after 5 seconds
      setTimeout(() => this.setupWebSocket(), 5000);
    };
  }

  private onPointHover(point: any): void {
    // Custom hover behavior - could emit events for external handlers
    console.log('Point hovered:', point);
  }

  private onPointClick(point: any): void {
    // Custom click behavior - could emit events for external handlers
    console.log('Point clicked:', point);
  }

  private downloadData(): void {
    const csvData = this.generateCSV();
    const blob = new Blob([csvData], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${this.config.title.toLowerCase().replace(/\s+/g, '_')}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  private generateCSV(): string {
    const headers = ['timestamp', ...this.config.metrics];
    const rows = [headers.join(',')];

    // Get all unique timestamps
    const allTimestamps = new Set<number>();
    this.config.metrics.forEach(metric => {
      const points = this.data.get(metric) || [];
      points.forEach(point => allTimestamps.add(point.timestamp.getTime()));
    });

    // Sort timestamps
    const sortedTimestamps = Array.from(allTimestamps).sort();

    // Generate rows
    sortedTimestamps.forEach(timestamp => {
      const row = [new Date(timestamp).toISOString()];
      
      this.config.metrics.forEach(metric => {
        const points = this.data.get(metric) || [];
        const point = points.find(p => p.timestamp.getTime() === timestamp);
        row.push(point ? point.value.toString() : '');
      });
      
      rows.push(row.join(','));
    });

    return rows.join('\n');
  }

  public destroy(): void {
    if (this.websocket) {
      this.websocket.close();
    }
    if (this.plot) {
      Plotly.purge(this.container);
    }
  }
}

// Export for use in React components or vanilla JS
export default TimeSeriesCanvas;

// Factory function for easy instantiation
export function createTimeSeriesChart(config: TimeSeriesConfig): TimeSeriesCanvas {
  return new TimeSeriesCanvas(config);
}

// Predefined chart configurations for common blockchain metrics
export const BLOCKCHAIN_CHART_CONFIGS = {
  transactionVolume: {
    title: 'Transaction Volume',
    metrics: ['tx_count', 'tx_volume_eth'],
    colors: ['#3b82f6', '#10b981'],
    yAxisLabel: 'Volume',
    showRangeSelector: true,
    showCrosshair: true,
    realtime: true
  },
  gasMetrics: {
    title: 'Gas Metrics',
    metrics: ['gas_price_gwei', 'gas_used'],
    colors: ['#f59e0b', '#ef4444'],
    yAxisLabel: 'Gas',
    showRangeSelector: true,
    showCrosshair: true,
    realtime: true
  },
  mevMetrics: {
    title: 'MEV Metrics',
    metrics: ['mev_extracted', 'sandwich_attacks', 'arbitrage_volume'],
    colors: ['#8b5cf6', '#ec4899', '#06b6d4'],
    yAxisLabel: 'MEV Value (ETH)',
    showRangeSelector: true,
    showCrosshair: true,
    realtime: true
  }
};
