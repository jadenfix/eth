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
import logging

logger = logging.getLogger(__name__)

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
            logger.info(f"Generating predictions for horizon: {horizon}")
            
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
            
            logger.info(f"Generated predictive report: {report.report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
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
            'transaction_count': np.random.poisson(150, len(timestamps)).astype(float),
            'gas_price': np.random.exponential(30, len(timestamps)).astype(float),
            'total_value': np.random.lognormal(10, 1, len(timestamps)).astype(float),
            'unique_addresses': np.random.poisson(1000, len(timestamps)).astype(float),
            'failed_transactions': np.random.binomial(150, 0.05, len(timestamps)).astype(float),
            'mev_opportunities': np.random.poisson(5, len(timestamps)).astype(float),
            'large_transfers': np.random.poisson(10, len(timestamps)).astype(float),
            'suspicious_activity': np.random.poisson(2, len(timestamps)).astype(float)
        })
        
        # Add trends and seasonality
        data['transaction_count'] += np.sin(np.arange(len(timestamps)) * 2 * np.pi / 24) * 20  # Daily cycle
        data['transaction_count'] += np.sin(np.arange(len(timestamps)) * 2 * np.pi / (24 * 7)) * 10  # Weekly cycle
        
        # Add some upward trend
        data['transaction_count'] += np.arange(len(timestamps)) * 0.1
        
        logger.info(f"Fetched {len(data)} historical data points")
        return data
    
    async def _prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for prediction"""
        features = data.copy()
        
        # Ensure required columns exist
        required_columns = ['transaction_count', 'gas_price', 'total_value']
        for col in required_columns:
            if col not in features.columns:
                features[col] = 0  # Default value if column missing
        
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
        if 'day_of_week' in features.columns:
            features['is_weekend'] = (features['day_of_week'] >= 5).astype(int)
        else:
            features['is_weekend'] = 0
            
        if 'hour' in features.columns:
            features['is_business_hours'] = ((features['hour'] >= 9) & (features['hour'] <= 17)).astype(int)
        else:
            features['is_business_hours'] = 0
        
        # Fill NaN values instead of dropping
        features = features.fillna(0)
        
        logger.info(f"Prepared {len(features)} feature rows with {len(features.columns)} features")
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
        self.feature_importance['transaction_volume'] = dict(zip(feature_cols, [float(x) for x in model.feature_importances_]))
        
        logger.info(f"Transaction volume prediction: {prediction:.1f} (accuracy: {accuracy:.3f})")
        
        return Prediction(
            metric_name="Transaction Volume",
            current_value=float(target.iloc[-1]),
            predicted_value=float(prediction),
            confidence_interval=(float(confidence_interval[0]), float(confidence_interval[1])),
            prediction_horizon=horizon,
            timestamp=datetime.now(),
            model_accuracy=float(accuracy)
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
        self.feature_importance['gas_prices'] = dict(zip(feature_cols, [float(x) for x in model.feature_importances_]))
        
        logger.info(f"Gas price prediction: {prediction:.2f} gwei (accuracy: {accuracy:.3f})")
        
        return Prediction(
            metric_name="Gas Price",
            current_value=float(target.iloc[-1]),
            predicted_value=float(prediction),
            confidence_interval=(float(confidence_interval[0]), float(confidence_interval[1])),
            prediction_horizon=horizon,
            timestamp=datetime.now(),
            model_accuracy=float(accuracy)
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
        
        logger.info(f"MEV opportunities prediction: {prediction:.1f} (accuracy: {accuracy:.3f})")
        
        return Prediction(
            metric_name="MEV Opportunities",
            current_value=float(target.iloc[-1]),
            predicted_value=float(prediction),
            confidence_interval=(float(confidence_interval[0]), float(confidence_interval[1])),
            prediction_horizon=horizon,
            timestamp=datetime.now(),
            model_accuracy=float(accuracy)
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
        
        logger.info(f"Risk score prediction: {prediction:.3f} (accuracy: {accuracy:.3f})")
        
        return Prediction(
            metric_name="Risk Score",
            current_value=float(target.iloc[-1]),
            predicted_value=float(prediction),
            confidence_interval=(float(confidence_interval[0]), float(confidence_interval[1])),
            prediction_horizon=horizon,
            timestamp=datetime.now(),
            model_accuracy=float(accuracy)
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
        
        logger.info(f"Generated {len(alerts)} prediction alerts")
        return alerts 