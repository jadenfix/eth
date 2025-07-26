# Phase 5: Advanced Analytics & Visualization Implementation Guide

## �� **PHASE 5 OVERVIEW**

**Goal:** Build advanced analytics dashboard and real-time visualization capabilities

**Duration:** 2 Weeks (Week 9: Advanced Analytics, Week 10: Real-time Visualizations)

**Prerequisites:** ✅ Phase 1 completed (Authentication, Multi-chain data), ✅ Phase 2 completed (Entity resolution, Graph database), ✅ Phase 3 completed (MEV detection, Risk scoring, Sanctions screening), ✅ Phase 4 completed (Automated actions, Workflow builder)
**Target Status:** �� Advanced analytics dashboard + Real-time visualizations + Custom reporting + Data export capabilities

---

## �� **WEEK 9: ADVANCED ANALYTICS**

### **Day 1-2: Advanced Risk Analytics**

#### **Step 1: Create Advanced Analytics Service**
**File:** `services/analytics/advanced_analytics.py`

```python
import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import json

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
            
            return report
            
        except Exception as e:
            print(f"Error generating risk analytics: {e}")
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
        
        return metrics
    
    async def _detect_anomalies(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomalies in the data"""
        # Prepare features for anomaly detection
        features = data[['transaction_count', 'gas_price', 'total_value', 
                        'unique_addresses', 'failed_transactions']].copy()
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Detect anomalies
        anomaly_labels = self.anomaly_detector.fit_predict(features_scaled)
        
        # Get anomalous points
        anomalous_indices = np.where(anomaly_labels == -1)[0]
        anomalous_data = data.iloc[anomalous_indices]
        
        # Cluster anomalies to identify patterns
        if len(anomalous_data) > 0:
            anomaly_features = self.scaler.transform(anomalous_data[['transaction_count', 'gas_price']])
            clusters = self.clustering_model.fit_predict(anomaly_features)
            anomalous_data = anomalous_data.copy()
            anomalous_data['cluster'] = clusters
        
        return {
            'anomalous_points': anomalous_data,
            'anomaly_count': len(anomalous_data),
            'total_points': len(data),
            'anomaly_percentage': len(anomalous_data) / len(data) * 100
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
```

### **Day 3-4: Predictive Analytics**

#### **Step 1: Create Predictive Analytics Service**
**File:** `services/analytics/predictive_analytics.py`

```python
import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import json

@dataclass
class Prediction:
    metric_name: str
    current_value: float
    predicted_value: float
    confidence_interval: Tuple[float, float]
    prediction_horizon: str
    timestamp: datetime
    model_accuracy: float

@dataclass
class PredictiveReport:
    report_id: str
    generated_at: datetime
    predictions: List[Prediction]
    model_performance: Dict[str, float]
    feature_importance: Dict[str, float]
    alerts: List[str]

class PredictiveAnalytics:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.model_performance = {}
        
    async def generate_predictions(self, horizon: str = '24h') -> PredictiveReport:
        """Generate predictions for various metrics"""
        try:
            # Fetch historical data
            historical_data = await self._fetch_historical_data()
            
            # Prepare features
            features = await self._prepare_features(historical_data)
            
            # Train models for different metrics
            predictions = []
            model_performance = {}
            feature_importance = {}
            
            # Predict transaction volume
            tx_prediction = await self._predict_transaction_volume(features, horizon)
            predictions.append(tx_prediction)
            
            # Predict gas prices
            gas_prediction = await self._predict_gas_prices(features, horizon)
            predictions.append(gas_prediction)
            
            # Predict MEV opportunities
            mev_prediction = await self._predict_mev_opportunities(features, horizon)
            predictions.append(mev_prediction)
            
            # Predict risk scores
            risk_prediction = await self._predict_risk_scores(features, horizon)
            predictions.append(risk_prediction)
            
            # Generate alerts
            alerts = await self._generate_prediction_alerts(predictions)
            
            report = PredictiveReport(
                report_id=f"predictive_{datetime.now().timestamp()}",
                generated_at=datetime.now(),
                predictions=predictions,
                model_performance=model_performance,
                feature_importance=feature_importance,
                alerts=alerts
            )
            
            return report
            
        except Exception as e:
            print(f"Error generating predictions: {e}")
            raise
    
    async def _fetch_historical_data(self) -> pd.DataFrame:
        """Fetch historical data for training"""
        # In real implementation, this would fetch from BigQuery
        # Generate 30 days of historical data
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Generate hourly data points
        timestamps = pd.date_range(start=start_date, end=end_date, freq='H')
        
        data = pd.DataFrame({
            'timestamp': timestamps,
            'hour': timestamps.hour,
            'day_of_week': timestamps.dayofweek,
            'transaction_count': np.random.poisson(150, len(timestamps)),
            'gas_price': np.random.exponential(30, len(timestamps)),
            'total_value': np.random.lognormal(10, 1, len(timestamps)),
            'unique_addresses': np.random.poisson(1000, len(timestamps)),
            'failed_transactions': np.random.binomial(150, 0.05, len(timestamps)),
            'mev_opportunities': np.random.poisson(5, len(timestamps)),
            'large_transfers': np.random.poisson(10, len(timestamps)),
            'suspicious_activity': np.random.poisson(2, len(timestamps))
        })
        
        # Add trends and seasonality
        data['transaction_count'] += np.sin(np.arange(len(timestamps)) * 2 * np.pi / 24) * 20  # Daily cycle
        data['transaction_count'] += np.sin(np.arange(len(timestamps)) * 2 * np.pi / (24 * 7)) * 10  # Weekly cycle
        
        # Add some upward trend
        data['transaction_count'] += np.arange(len(timestamps)) * 0.1
        
        return data
    
    async def _prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for prediction"""
        features = data.copy()
        
        # Create lag features
        for lag in [1, 2, 3, 6, 12, 24]:
            features[f'tx_count_lag_{lag}'] = features['transaction_count'].shift(lag)
            features[f'gas_price_lag_{lag}'] = features['gas_price'].shift(lag)
            features[f'total_value_lag_{lag}'] = features['total_value'].shift(lag)
        
        # Create rolling statistics
        for window in [3, 6, 12, 24]:
            features[f'tx_count_mean_{window}'] = features['transaction_count'].rolling(window).mean()
            features[f'tx_count_std_{window}'] = features['transaction_count'].rolling(window).std()
            features[f'gas_price_mean_{window}'] = features['gas_price'].rolling(window).mean()
            features[f'gas_price_std_{window}'] = features['gas_price'].rolling(window).std()
        
        # Create time-based features
        features['is_weekend'] = (features['day_of_week'] >= 5).astype(int)
        features['is_business_hours'] = ((features['hour'] >= 9) & (features['hour'] <= 17)).astype(int)
        
        # Remove NaN values
        features = features.dropna()
        
        return features
    
    async def _predict_transaction_volume(self, features: pd.DataFrame, horizon: str) -> Prediction:
        """Predict transaction volume"""
        # Prepare target and features
        target = features['transaction_count']
        feature_cols = [col for col in features.columns if col not in ['timestamp', 'transaction_count']]
        X = features[feature_cols]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, target, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Make prediction
        latest_features = X.iloc[-1:].values
        prediction = model.predict(latest_features)[0]
        
        # Calculate confidence interval
        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        confidence_interval = (prediction - 2 * np.sqrt(mse), prediction + 2 * np.sqrt(mse))
        
        # Calculate model accuracy
        accuracy = r2_score(y_test, predictions)
        
        # Store feature importance
        self.feature_importance['transaction_volume'] = dict(zip(feature_cols, model.feature_importances_))
        
        return Prediction(
            metric_name="Transaction Volume",
            current_value=target.iloc[-1],
            predicted_value=prediction,
            confidence_interval=confidence_interval,
            prediction_horizon=horizon,
            timestamp=datetime.now(),
            model_accuracy=accuracy
        )
    
    async def _predict_gas_prices(self, features: pd.DataFrame, horizon: str) -> Prediction:
        """Predict gas prices"""
        # Prepare target and features
        target = features['gas_price']
        feature_cols = [col for col in features.columns if col not in ['timestamp', 'gas_price']]
        X = features[feature_cols]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, target, test_size=0.2, random_state=42)
        
        # Train model
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Make prediction
        latest_features = X.iloc[-1:].values
        prediction = model.predict(latest_features)[0]
        
        # Calculate confidence interval
        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        confidence_interval = (prediction - 2 * np.sqrt(mse), prediction + 2 * np.sqrt(mse))
        
        # Calculate model accuracy
        accuracy = r2_score(y_test, predictions)
        
        # Store feature importance
        self.feature_importance['gas_prices'] = dict(zip(feature_cols, model.feature_importances_))
        
        return Prediction(
            metric_name="Gas Price",
            current_value=target.iloc[-1],
            predicted_value=prediction,
            confidence_interval=confidence_interval,
            prediction_horizon=horizon,
            timestamp=datetime.now(),
            model_accuracy=accuracy
        )
    
    async def _predict_mev_opportunities(self, features: pd.DataFrame, horizon: str) -> Prediction:
        """Predict MEV opportunities"""
        # Prepare target and features
        target = features['mev_opportunities']
        feature_cols = [col for col in features.columns if col not in ['timestamp', 'mev_opportunities']]
        X = features[feature_cols]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, target, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Make prediction
        latest_features = X.iloc[-1:].values
        prediction = model.predict(latest_features)[0]
        
        # Calculate confidence interval
        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        confidence_interval = (prediction - 2 * np.sqrt(mse), prediction + 2 * np.sqrt(mse))
        
        # Calculate model accuracy
        accuracy = r2_score(y_test, predictions)
        
        return Prediction(
            metric_name="MEV Opportunities",
            current_value=target.iloc[-1],
            predicted_value=prediction,
            confidence_interval=confidence_interval,
            prediction_horizon=horizon,
            timestamp=datetime.now(),
            model_accuracy=accuracy
        )
    
    async def _predict_risk_scores(self, features: pd.DataFrame, horizon: str) -> Prediction:
        """Predict overall risk scores"""
        # Calculate risk score as combination of various factors
        risk_score = (
            features['failed_transactions'] / features['transaction_count'] * 0.3 +
            features['suspicious_activity'] / features['transaction_count'] * 0.4 +
            features['mev_opportunities'] / features['transaction_count'] * 0.3
        )
        
        # Prepare target and features
        target = risk_score
        feature_cols = [col for col in features.columns if col not in ['timestamp', 'failed_transactions', 'suspicious_activity', 'mev_opportunities']]
        X = features[feature_cols]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, target, test_size=0.2, random_state=42)
        
        # Train model
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Make prediction
        latest_features = X.iloc[-1:].values
        prediction = model.predict(latest_features)[0]
        
        # Calculate confidence interval
        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        confidence_interval = (prediction - 2 * np.sqrt(mse), prediction + 2 * np.sqrt(mse))
        
        # Calculate model accuracy
        accuracy = r2_score(y_test, predictions)
        
        return Prediction(
            metric_name="Risk Score",
            current_value=target.iloc[-1],
            predicted_value=prediction,
            confidence_interval=confidence_interval,
            prediction_horizon=horizon,
            timestamp=datetime.now(),
            model_accuracy=accuracy
        )
    
    async def _generate_prediction_alerts(self, predictions: List[Prediction]) -> List[str]:
        """Generate alerts based on predictions"""
        alerts = []
        
        for prediction in predictions:
            # Check for significant changes
            change_percentage = abs(prediction.predicted_value - prediction.current_value) / prediction.current_value
            
            if change_percentage > 0.5:  # 50% change
                alerts.append(f"Significant change predicted for {prediction.metric_name}: {change_percentage:.1%}")
            
            # Check for high predicted values
            if prediction.metric_name == "Risk Score" and prediction.predicted_value > 0.7:
                alerts.append(f"High risk predicted: {prediction.predicted_value:.2f}")
            
            elif prediction.metric_name == "Gas Price" and prediction.predicted_value > 100:
                alerts.append(f"High gas prices predicted: {prediction.predicted_value:.2f} gwei")
            
            elif prediction.metric_name == "MEV Opportunities" and prediction.predicted_value > 10:
                alerts.append(f"High MEV activity predicted: {prediction.predicted_value:.1f} opportunities")
        
        return alerts
```

### **Day 5-7: Custom Reporting Engine**

#### **Step 1: Create Custom Reporting Service**
**File:** `services/analytics/custom_reports.py`

```python
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
import plotly.express as px

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
        return template.template_id
    
    async def generate_custom_report(self, template_id: str, time_range: str = '24h', 
                                   custom_filters: Dict[str, Any] = None) -> CustomReport:
        """Generate a custom report based on template"""
        try:
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
            
            return report
            
        except Exception as e:
            print(f"Error generating custom report: {e}")
            raise
    
    async def export_report(self, report: CustomReport, format: str = 'json') -> str:
        """Export report in specified format"""
        if format == 'json':
            return await self._export_json(report)
        elif format == 'csv':
            return await self._export_csv(report)
        elif format == 'pdf':
            return await self._export_pdf(report)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def _fetch_report_data(self, metrics: List[str], time_range: str, 
                                custom_filters: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data for report metrics"""
        data = {}
        
        # Fetch blockchain data
        blockchain_data = await self._fetch_blockchain_data(time_range, custom_filters)
        
        # Calculate metrics
        for metric in metrics:
            if metric == 'transaction_volume':
                data[metric] = blockchain_data['transaction_count'].sum()
            elif metric == 'average_gas_price':
                data[metric] = blockchain_data['gas_price'].mean()
            elif metric == 'total_value_transferred':
                data[metric] = blockchain_data['total_value'].sum()
            elif metric == 'unique_addresses':
                data[metric] = blockchain_data['unique_addresses'].nunique()
            elif metric == 'failed_transaction_rate':
                data[metric] = blockchain_data['failed_transactions'].sum() / blockchain_data['transaction_count'].sum()
            elif metric == 'mev_opportunities':
                data[metric] = blockchain_data['mev_opportunities'].sum()
            elif metric == 'suspicious_activity':
                data[metric] = blockchain_data['suspicious_activity'].sum()
            elif metric == 'large_transfers':
                data[metric] = blockchain_data['large_transfers'].sum()
        
        # Add time series data
        data['time_series'] = blockchain_data.to_dict('records')
        
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
            'transaction_count': np.random.poisson(150, periods),
            'gas_price': np.random.exponential(30, periods),
            'total_value': np.random.lognormal(10, 1, periods),
            'unique_addresses': np.random.poisson(1000, periods),
            'failed_transactions': np.random.binomial(150, 0.05, periods),
            'mev_opportunities': np.random.poisson(5, periods),
            'large_transfers': np.random.poisson(10, periods),
            'suspicious_activity': np.random.poisson(2, periods)
        })
        
        # Apply custom filters
        if custom_filters:
            if 'min_gas_price' in custom_filters:
                data = data[data['gas_price'] >= custom_filters['min_gas_price']]
            if 'max_gas_price' in custom_filters:
                data = data[data['gas_price'] <= custom_filters['max_gas_price']]
            if 'min_transaction_count' in custom_filters:
                data = data[data['transaction_count'] >= custom_filters['min_transaction_count']]
        
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
        export_data = {
            'report_id': report.report_id,
            'template_id': report.template_id,
            'generated_at': report.generated_at.isoformat(),
            'time_range': report.time_range,
            'data': report.data,
            'metadata': report.metadata
        }
        
        return json.dumps(export_data, indent=2)
    
    async def _export_csv(self, report: CustomReport) -> str:
        """Export report data as CSV"""
        # Convert time series data to CSV
        time_series = pd.DataFrame(report.data['time_series'])
        
        csv_buffer = StringIO()
        time_series.to_csv(csv_buffer, index=False)
        
        return csv_buffer.getvalue()
    
    async def _export_pdf(self, report: CustomReport) -> str:
        """Export report as PDF"""
        # In real implementation, this would use a PDF library
        # For now, return a placeholder
        return f"PDF export for report {report.report_id} wou