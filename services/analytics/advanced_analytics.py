import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class RiskMetric:
    metric_name: str
    value: float
    threshold: float
    status: str  # 'low', 'medium', 'high', 'critical'
    trend: str   # 'increasing', 'decreasing', 'stable'
    timestamp: datetime

@dataclass
class AnalyticsReport:
    report_id: str
    report_type: str
    generated_at: datetime
    time_range: str
    metrics: List[RiskMetric]
    visualizations: List[Dict[str, Any]]
    insights: List[str]
    recommendations: List[str]

class AdvancedAnalytics:
    def __init__(self):
        self.risk_models = {}
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.clustering_model = DBSCAN(eps=0.5, min_samples=5)
        
    async def generate_risk_analytics(self, time_range: str = '24h') -> AnalyticsReport:
        """Generate comprehensive risk analytics report"""
        try:
            logger.info(f"Generating risk analytics for time range: {time_range}")
            
            # Fetch data for analysis
            data = await self._fetch_analytics_data(time_range)
            
            # Calculate risk metrics
            risk_metrics = await self._calculate_risk_metrics(data)
            
            # Detect anomalies
            anomalies = await self._detect_anomalies(data)
            
            # Generate insights
            insights = await self._generate_insights(data, risk_metrics, anomalies)
            
            # Create recommendations
            recommendations = await self._generate_recommendations(risk_metrics, insights)
            
            # Generate visualizations
            visualizations = await self._create_visualizations(data, risk_metrics, anomalies)
            
            report = AnalyticsReport(
                report_id=f"analytics_{datetime.now().timestamp()}",
                report_type="risk_analytics",
                generated_at=datetime.now(),
                time_range=time_range,
                metrics=risk_metrics,
                visualizations=visualizations,
                insights=insights,
                recommendations=recommendations
            )
            
            logger.info(f"Generated analytics report: {report.report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating risk analytics: {e}")
            raise
    
    async def _fetch_analytics_data(self, time_range: str) -> pd.DataFrame:
        """Fetch data for analytics"""
        # In real implementation, this would fetch from BigQuery/Neo4j
        # For now, generate mock data
        
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
        
        # Generate mock blockchain data
        timestamps = pd.date_range(start=start_time, end=end_time, periods=periods)
        
        data = pd.DataFrame({
            'timestamp': timestamps,
            'block_number': range(18500000, 18500000 + periods),
            'transaction_count': np.random.poisson(150, periods),
            'gas_price': np.random.exponential(30, periods),
            'total_value': np.random.lognormal(10, 1, periods),
            'unique_addresses': np.random.poisson(1000, periods),
            'failed_transactions': np.random.binomial(150, 0.05, periods),
            'mev_opportunities': np.random.poisson(5, periods),
            'large_transfers': np.random.poisson(10, periods),
            'suspicious_activity': np.random.poisson(2, periods)
        })
        
        # Add some trends and patterns
        data['transaction_count'] += np.sin(np.arange(periods) * 2 * np.pi / 1440) * 20  # Daily cycle
        data['gas_price'] += np.random.normal(0, 5, periods)  # Add volatility
        
        logger.info(f"Fetched {len(data)} data points for analytics")
        return data
    
    async def _calculate_risk_metrics(self, data: pd.DataFrame) -> List[RiskMetric]:
        """Calculate various risk metrics"""
        metrics = []
        
        # Transaction volume risk
        avg_transactions = data['transaction_count'].mean()
        transaction_risk = min(avg_transactions / 200, 1.0)  # Normalize to 0-1
        metrics.append(RiskMetric(
            metric_name="Transaction Volume Risk",
            value=transaction_risk,
            threshold=0.8,
            status=self._get_risk_status(transaction_risk),
            trend=self._get_trend(data['transaction_count']),
            timestamp=datetime.now()
        ))
        
        # Gas price volatility risk
        gas_volatility = data['gas_price'].std() / data['gas_price'].mean()
        gas_risk = min(gas_volatility, 1.0)
        metrics.append(RiskMetric(
            metric_name="Gas Price Volatility Risk",
            value=gas_risk,
            threshold=0.5,
            status=self._get_risk_status(gas_risk),
            trend=self._get_trend(data['gas_price']),
            timestamp=datetime.now()
        ))
        
        # Failed transaction rate
        failure_rate = data['failed_transactions'].sum() / data['transaction_count'].sum()
        failure_risk = min(failure_rate * 10, 1.0)  # Scale up for visibility
        metrics.append(RiskMetric(
            metric_name="Transaction Failure Risk",
            value=failure_risk,
            threshold=0.1,
            status=self._get_risk_status(failure_risk),
            trend=self._get_trend(data['failed_transactions']),
            timestamp=datetime.now()
        ))
        
        # MEV activity risk
        mev_risk = min(data['mev_opportunities'].mean() / 10, 1.0)
        metrics.append(RiskMetric(
            metric_name="MEV Activity Risk",
            value=mev_risk,
            threshold=0.7,
            status=self._get_risk_status(mev_risk),
            trend=self._get_trend(data['mev_opportunities']),
            timestamp=datetime.now()
        ))
        
        # Large transfer risk
        large_transfer_risk = min(data['large_transfers'].mean() / 20, 1.0)
        metrics.append(RiskMetric(
            metric_name="Large Transfer Risk",
            value=large_transfer_risk,
            threshold=0.6,
            status=self._get_risk_status(large_transfer_risk),
            trend=self._get_trend(data['large_transfers']),
            timestamp=datetime.now()
        ))
        
        # Suspicious activity risk
        suspicious_risk = min(data['suspicious_activity'].mean() / 5, 1.0)
        metrics.append(RiskMetric(
            metric_name="Suspicious Activity Risk",
            value=suspicious_risk,
            threshold=0.4,
            status=self._get_risk_status(suspicious_risk),
            trend=self._get_trend(data['suspicious_activity']),
            timestamp=datetime.now()
        ))
        
        logger.info(f"Calculated {len(metrics)} risk metrics")
        return metrics
    
    async def _detect_anomalies(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomalies in the data"""
        try:
            # Prepare features for anomaly detection
            feature_columns = ['transaction_count', 'gas_price', 'total_value', 
                             'unique_addresses', 'failed_transactions']
            
            # Ensure all required columns exist
            available_columns = [col for col in feature_columns if col in data.columns]
            if len(available_columns) < 2:
                # Fallback to basic features if not enough columns
                available_columns = ['transaction_count', 'gas_price']
            
            features = data[available_columns].copy()
            
            # Handle missing values
            features = features.fillna(features.mean())
            
            # Create a fresh scaler for this detection to avoid feature mismatch
            temp_scaler = StandardScaler()
            features_scaled = temp_scaler.fit_transform(features)
            
            # Detect anomalies
            anomaly_labels = self.anomaly_detector.fit_predict(features_scaled)
            
            # Get anomalous points
            anomalous_indices = np.where(anomaly_labels == -1)[0]
            anomalous_data = data.iloc[anomalous_indices]
            
            # Cluster anomalies to identify patterns
            if len(anomalous_data) > 0 and len(anomalous_data) > 1:
                try:
                    # Use only basic features for clustering to avoid dimension issues
                    cluster_features = anomalous_data[['transaction_count', 'gas_price']].fillna(0)
                    clusters = self.clustering_model.fit_predict(cluster_features)
                    anomalous_data = anomalous_data.copy()
                    anomalous_data['cluster'] = clusters
                except Exception as e:
                    logger.warning(f"Clustering failed: {e}")
                    anomalous_data['cluster'] = 0
            
            anomaly_result = {
                'anomalous_points': anomalous_data,
                'anomaly_count': len(anomalous_data),
                'total_points': len(data),
                'anomaly_percentage': len(anomalous_data) / len(data) * 100 if len(data) > 0 else 0
            }
            
            logger.info(f"Detected {len(anomalous_data)} anomalies ({anomaly_result['anomaly_percentage']:.1f}%)")
            return anomaly_result
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            # Return empty anomaly result
            return {
                'anomalous_points': pd.DataFrame(),
                'anomaly_count': 0,
                'total_points': len(data),
                'anomaly_percentage': 0.0
            }
    
    async def _generate_insights(self, data: pd.DataFrame, metrics: List[RiskMetric], 
                               anomalies: Dict[str, Any]) -> List[str]:
        """Generate insights from the data"""
        insights = []
        
        # High-level insights
        total_transactions = data['transaction_count'].sum()
        total_value = data['total_value'].sum()
        avg_gas_price = data['gas_price'].mean()
        
        insights.append(f"Processed {total_transactions:,} transactions with total value ${total_value:,.2f}")
        insights.append(f"Average gas price: {avg_gas_price:.2f} gwei")
        
        # Risk insights
        high_risk_metrics = [m for m in metrics if m.status in ['high', 'critical']]
        if high_risk_metrics:
            insights.append(f"Detected {len(high_risk_metrics)} high-risk metrics requiring attention")
        
        # Anomaly insights
        if anomalies['anomaly_count'] > 0:
            insights.append(f"Identified {anomalies['anomaly_count']} anomalous patterns ({anomalies['anomaly_percentage']:.1f}% of data)")
        
        # Trend insights
        increasing_metrics = [m for m in metrics if m.trend == 'increasing']
        if increasing_metrics:
            insights.append(f"{len(increasing_metrics)} risk metrics showing increasing trends")
        
        # MEV insights
        total_mev = data['mev_opportunities'].sum()
        if total_mev > 0:
            insights.append(f"Detected {total_mev} MEV opportunities during the period")
        
        logger.info(f"Generated {len(insights)} insights")
        return insights
    
    async def _generate_recommendations(self, metrics: List[RiskMetric], 
                                      insights: List[str]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check for critical risks
        critical_metrics = [m for m in metrics if m.status == 'critical']
        if critical_metrics:
            recommendations.append("Immediate action required: Review and address critical risk metrics")
        
        # Check for increasing trends
        increasing_metrics = [m for m in metrics if m.trend == 'increasing' and m.status in ['medium', 'high']]
        if increasing_metrics:
            recommendations.append("Monitor increasing risk trends and consider preventive measures")
        
        # Specific recommendations based on metrics
        for metric in metrics:
            if metric.metric_name == "Gas Price Volatility Risk" and metric.status in ['high', 'critical']:
                recommendations.append("Consider implementing gas price monitoring and alerting")
            
            elif metric.metric_name == "Transaction Failure Risk" and metric.status in ['high', 'critical']:
                recommendations.append("Investigate transaction failure patterns and optimize gas settings")
            
            elif metric.metric_name == "MEV Activity Risk" and metric.status in ['high', 'critical']:
                recommendations.append("Review MEV protection strategies and consider anti-sandwich measures")
        
        # General recommendations
        recommendations.append("Continue monitoring all risk metrics and maintain alert thresholds")
        recommendations.append("Review and update risk models based on recent patterns")
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations
    
    async def _create_visualizations(self, data: pd.DataFrame, metrics: List[RiskMetric], 
                                   anomalies: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create visualization charts"""
        visualizations = []
        
        # 1. Risk Metrics Dashboard
        risk_chart = go.Figure()
        
        metric_names = [m.metric_name for m in metrics]
        metric_values = [m.value for m in metrics]
        metric_colors = [self._get_risk_color(m.status) for m in metrics]
        
        risk_chart.add_trace(go.Bar(
            x=metric_names,
            y=metric_values,
            marker_color=metric_colors,
            name='Risk Score'
        ))
        
        risk_chart.update_layout(
            title="Risk Metrics Overview",
            xaxis_title="Risk Metric",
            yaxis_title="Risk Score",
            yaxis_range=[0, 1],
            height=400
        )
        
        visualizations.append({
            'type': 'risk_metrics',
            'chart': risk_chart.to_json(),
            'title': 'Risk Metrics Overview'
        })
        
        # 2. Transaction Volume Over Time
        volume_chart = go.Figure()
        
        volume_chart.add_trace(go.Scatter(
            x=data['timestamp'],
            y=data['transaction_count'],
            mode='lines',
            name='Transaction Count',
            line=dict(color='blue')
        ))
        
        # Add anomaly points
        if len(anomalies['anomalous_points']) > 0:
            volume_chart.add_trace(go.Scatter(
                x=anomalies['anomalous_points']['timestamp'],
                y=anomalies['anomalous_points']['transaction_count'],
                mode='markers',
                name='Anomalies',
                marker=dict(color='red', size=8)
            ))
        
        volume_chart.update_layout(
            title="Transaction Volume Over Time",
            xaxis_title="Time",
            yaxis_title="Transaction Count",
            height=400
        )
        
        visualizations.append({
            'type': 'transaction_volume',
            'chart': volume_chart.to_json(),
            'title': 'Transaction Volume Over Time'
        })
        
        # 3. Gas Price Analysis
        gas_chart = go.Figure()
        
        gas_chart.add_trace(go.Scatter(
            x=data['timestamp'],
            y=data['gas_price'],
            mode='lines',
            name='Gas Price',
            line=dict(color='orange')
        ))
        
        gas_chart.update_layout(
            title="Gas Price Trends",
            xaxis_title="Time",
            yaxis_title="Gas Price (gwei)",
            height=400
        )
        
        visualizations.append({
            'type': 'gas_price',
            'chart': gas_chart.to_json(),
            'title': 'Gas Price Trends'
        })
        
        # 4. Risk Heatmap
        # Create correlation matrix for risk metrics
        risk_data = data[['transaction_count', 'gas_price', 'total_value', 
                         'failed_transactions', 'mev_opportunities', 'suspicious_activity']]
        correlation_matrix = risk_data.corr()
        
        heatmap = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale='RdBu',
            zmid=0
        ))
        
        heatmap.update_layout(
            title="Risk Metrics Correlation Heatmap",
            height=400
        )
        
        visualizations.append({
            'type': 'correlation_heatmap',
            'chart': heatmap.to_json(),
            'title': 'Risk Metrics Correlation Heatmap'
        })
        
        logger.info(f"Created {len(visualizations)} visualizations")
        return visualizations
    
    def _get_risk_status(self, value: float) -> str:
        """Get risk status based on value"""
        if value < 0.3:
            return 'low'
        elif value < 0.6:
            return 'medium'
        elif value < 0.8:
            return 'high'
        else:
            return 'critical'
    
    def _get_trend(self, series: pd.Series) -> str:
        """Determine trend of a time series"""
        if len(series) < 2:
            return 'stable'
        
        # Simple trend detection
        first_half = series[:len(series)//2].mean()
        second_half = series[len(series)//2:].mean()
        
        if second_half > first_half * 1.1:
            return 'increasing'
        elif second_half < first_half * 0.9:
            return 'decreasing'
        else:
            return 'stable'
    
    def _get_risk_color(self, status: str) -> str:
        """Get color for risk status"""
        colors = {
            'low': 'green',
            'medium': 'yellow',
            'high': 'orange',
            'critical': 'red'
        }
        return colors.get(status, 'gray') 