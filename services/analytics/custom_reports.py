import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import csv
from io import StringIO
import plotly.graph_objects as go
import logging

logger = logging.getLogger(__name__)

@dataclass
class ReportTemplate:
    template_id: str
    name: str
    description: str
    metrics: List[str]
    visualizations: List[str]
    schedule: Optional[str] = None  # cron expression
    recipients: List[str] = None

@dataclass
class CustomReport:
    report_id: str
    template_id: str
    generated_at: datetime
    time_range: str
    data: Dict[str, Any]
    visualizations: List[Dict[str, Any]]
    export_formats: List[str]
    metadata: Dict[str, Any]

class CustomReportingEngine:
    def __init__(self):
        self.templates = {}
        self.report_history = []
        
    async def create_report_template(self, template: ReportTemplate) -> str:
        """Create a new report template"""
        self.templates[template.template_id] = template
        logger.info(f"Created report template: {template.template_id}")
        return template.template_id
    
    async def generate_custom_report(self, template_id: str, time_range: str = '24h', 
                                   custom_filters: Dict[str, Any] = None) -> CustomReport:
        """Generate a custom report based on template"""
        try:
            logger.info(f"Generating custom report for template: {template_id}")
            
            template = self.templates.get(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            # Fetch data based on template metrics
            data = await self._fetch_report_data(template.metrics, time_range, custom_filters)
            
            # Generate visualizations
            visualizations = await self._generate_visualizations(template.visualizations, data)
            
            # Create report
            report = CustomReport(
                report_id=f"report_{datetime.now().timestamp()}",
                template_id=template_id,
                generated_at=datetime.now(),
                time_range=time_range,
                data=data,
                visualizations=visualizations,
                export_formats=['json', 'csv', 'pdf'],
                metadata={
                    'template_name': template.name,
                    'custom_filters': custom_filters or {},
                    'metrics_included': template.metrics
                }
            )
            
            # Store in history
            self.report_history.append(report)
            
            logger.info(f"Generated custom report: {report.report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating custom report: {e}")
            raise
    
    async def export_report(self, report: CustomReport, format: str = 'json') -> str:
        """Export report in specified format"""
        try:
            if format == 'json':
                return await self._export_json(report)
            elif format == 'csv':
                return await self._export_csv(report)
            elif format == 'pdf':
                return await self._export_pdf(report)
            else:
                raise ValueError(f"Unsupported format: {format}")
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            raise
    
    async def _fetch_report_data(self, metrics: List[str], time_range: str, 
                                custom_filters: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data for report metrics"""
        data = {}
        
        # Fetch blockchain data
        blockchain_data = await self._fetch_blockchain_data(time_range, custom_filters)
        
        # Calculate metrics
        for metric in metrics:
            if metric == 'transaction_volume':
                data[metric] = float(blockchain_data['transaction_count'].sum())
            elif metric == 'average_gas_price':
                data[metric] = float(blockchain_data['gas_price'].mean())
            elif metric == 'total_value_transferred':
                data[metric] = float(blockchain_data['total_value'].sum())
            elif metric == 'unique_addresses':
                data[metric] = int(blockchain_data['unique_addresses'].nunique())
            elif metric == 'failed_transaction_rate':
                data[metric] = float(blockchain_data['failed_transactions'].sum() / blockchain_data['transaction_count'].sum())
            elif metric == 'mev_opportunities':
                data[metric] = float(blockchain_data['mev_opportunities'].sum())
            elif metric == 'suspicious_activity':
                data[metric] = float(blockchain_data['suspicious_activity'].sum())
            elif metric == 'large_transfers':
                data[metric] = float(blockchain_data['large_transfers'].sum())
        
        # Add time series data
        data['time_series'] = blockchain_data.to_dict('records')
        
        logger.info(f"Fetched data for {len(metrics)} metrics")
        return data
    
    async def _fetch_blockchain_data(self, time_range: str, custom_filters: Dict[str, Any]) -> pd.DataFrame:
        """Fetch blockchain data with filters"""
        # In real implementation, this would fetch from BigQuery with filters
        # Generate mock data
        
        end_time = datetime.now()
        if time_range == '24h':
            start_time = end_time - timedelta(hours=24)
            periods = 1440  # 1 minute intervals
        elif time_range == '7d':
            start_time = end_time - timedelta(days=7)
            periods = 1008  # 10 minute intervals
        elif time_range == '30d':
            start_time = end_time - timedelta(days=30)
            periods = 720   # 1 hour intervals
        else:
            start_time = end_time - timedelta(hours=24)
            periods = 1440
        
        timestamps = pd.date_range(start=start_time, end=end_time, periods=periods)
        
        data = pd.DataFrame({
            'timestamp': timestamps,
            'block_number': range(18500000, 18500000 + periods),
            'transaction_count': np.random.poisson(150, periods).astype(float),
            'gas_price': np.random.exponential(30, periods).astype(float),
            'total_value': np.random.lognormal(10, 1, periods).astype(float),
            'unique_addresses': np.random.poisson(1000, periods).astype(float),
            'failed_transactions': np.random.binomial(150, 0.05, periods).astype(float),
            'mev_opportunities': np.random.poisson(5, periods).astype(float),
            'large_transfers': np.random.poisson(10, periods).astype(float),
            'suspicious_activity': np.random.poisson(2, periods).astype(float)
        })
        
        # Apply custom filters
        if custom_filters:
            if 'min_gas_price' in custom_filters:
                data = data[data['gas_price'] >= custom_filters['min_gas_price']]
            if 'max_gas_price' in custom_filters:
                data = data[data['gas_price'] <= custom_filters['max_gas_price']]
            if 'min_transaction_count' in custom_filters:
                data = data[data['transaction_count'] >= custom_filters['min_transaction_count']]
        
        logger.info(f"Fetched {len(data)} blockchain data points")
        return data
    
    async def _generate_visualizations(self, visualization_types: List[str], 
                                     data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate visualizations based on types"""
        visualizations = []
        
        for viz_type in visualization_types:
            if viz_type == 'transaction_volume_chart':
                chart = await self._create_transaction_volume_chart(data)
                visualizations.append(chart)
            elif viz_type == 'gas_price_analysis':
                chart = await self._create_gas_price_chart(data)
                visualizations.append(chart)
            elif viz_type == 'risk_heatmap':
                chart = await self._create_risk_heatmap(data)
                visualizations.append(chart)
            elif viz_type == 'mev_timeline':
                chart = await self._create_mev_timeline(data)
                visualizations.append(chart)
        
        logger.info(f"Generated {len(visualizations)} visualizations")
        return visualizations
    
    async def _create_transaction_volume_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create transaction volume chart"""
        time_series = pd.DataFrame(data['time_series'])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=time_series['timestamp'],
            y=time_series['transaction_count'],
            mode='lines',
            name='Transaction Count',
            line=dict(color='blue')
        ))
        
        fig.update_layout(
            title="Transaction Volume Over Time",
            xaxis_title="Time",
            yaxis_title="Transaction Count",
            height=400
        )
        
        return {
            'type': 'transaction_volume',
            'chart': fig.to_json(),
            'title': 'Transaction Volume Over Time'
        }
    
    async def _create_gas_price_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create gas price analysis chart"""
        time_series = pd.DataFrame(data['time_series'])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=time_series['timestamp'],
            y=time_series['gas_price'],
            mode='lines',
            name='Gas Price',
            line=dict(color='orange')
        ))
        
        # Add moving average
        ma_24 = time_series['gas_price'].rolling(window=24).mean()
        fig.add_trace(go.Scatter(
            x=time_series['timestamp'],
            y=ma_24,
            mode='lines',
            name='24-period MA',
            line=dict(color='red', dash='dash')
        ))
        
        fig.update_layout(
            title="Gas Price Analysis",
            xaxis_title="Time",
            yaxis_title="Gas Price (gwei)",
            height=400
        )
        
        return {
            'type': 'gas_price_analysis',
            'chart': fig.to_json(),
            'title': 'Gas Price Analysis'
        }
    
    async def _create_risk_heatmap(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create risk correlation heatmap"""
        time_series = pd.DataFrame(data['time_series'])
        
        # Calculate risk metrics
        risk_data = pd.DataFrame({
            'transaction_risk': time_series['transaction_count'] / time_series['transaction_count'].max(),
            'gas_risk': time_series['gas_price'] / time_series['gas_price'].max(),
            'failure_risk': time_series['failed_transactions'] / time_series['transaction_count'],
            'mev_risk': time_series['mev_opportunities'] / time_series['mev_opportunities'].max(),
            'suspicious_risk': time_series['suspicious_activity'] / time_series['suspicious_activity'].max()
        })
        
        correlation_matrix = risk_data.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale='RdBu',
            zmid=0
        ))
        
        fig.update_layout(
            title="Risk Metrics Correlation Heatmap",
            height=400
        )
        
        return {
            'type': 'risk_heatmap',
            'chart': fig.to_json(),
            'title': 'Risk Metrics Correlation Heatmap'
        }
    
    async def _create_mev_timeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create MEV timeline chart"""
        time_series = pd.DataFrame(data['time_series'])
        
        # Filter for periods with MEV activity
        mev_data = time_series[time_series['mev_opportunities'] > 0]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=mev_data['timestamp'],
            y=mev_data['mev_opportunities'],
            mode='markers',
            name='MEV Opportunities',
            marker=dict(
                size=mev_data['mev_opportunities'] * 2,
                color=mev_data['mev_opportunities'],
                colorscale='Viridis',
                showscale=True
            )
        ))
        
        fig.update_layout(
            title="MEV Opportunities Timeline",
            xaxis_title="Time",
            yaxis_title="MEV Opportunities",
            height=400
        )
        
        return {
            'type': 'mev_timeline',
            'chart': fig.to_json(),
            'title': 'MEV Opportunities Timeline'
        }
    
    async def _export_json(self, report: CustomReport) -> str:
        """Export report as JSON"""
        # Convert time series data to handle timestamps
        data_copy = report.data.copy()
        if 'time_series' in data_copy:
            time_series = pd.DataFrame(data_copy['time_series'])
            # Convert timestamps to strings
            if 'timestamp' in time_series.columns:
                time_series['timestamp'] = time_series['timestamp'].astype(str)
            data_copy['time_series'] = time_series.to_dict('records')
        
        export_data = {
            'report_id': report.report_id,
            'template_id': report.template_id,
            'generated_at': report.generated_at.isoformat(),
            'time_range': report.time_range,
            'data': data_copy,
            'metadata': report.metadata
        }
        
        return json.dumps(export_data, indent=2)
    
    async def _export_csv(self, report: CustomReport) -> str:
        """Export report data as CSV"""
        # Convert time series data to CSV
        time_series = pd.DataFrame(report.data['time_series'])
        
        # Convert timestamps to strings
        if 'timestamp' in time_series.columns:
            time_series['timestamp'] = time_series['timestamp'].astype(str)
        
        csv_buffer = StringIO()
        time_series.to_csv(csv_buffer, index=False)
        
        return csv_buffer.getvalue()
    
    async def _export_pdf(self, report: CustomReport) -> str:
        """Export report as PDF"""
        # In real implementation, this would use a PDF library
        # For now, return a placeholder
        return f"PDF export for report {report.report_id} would be generated here" 