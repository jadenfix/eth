import numpy as np
from typing import Dict, List, Any, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
import logging

logger = logging.getLogger(__name__)

class RiskScorer:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.feature_names = [
            'transaction_count',
            'total_volume_eth',
            'avg_transaction_value',
            'max_transaction_value',
            'gas_price_volatility',
            'contract_interaction_ratio',
            'unique_counterparties',
            'mev_activity_score',
            'whale_movement_score',
            'sanctions_risk_score',
            'age_days',
            'balance_volatility'
        ]
        self.model_path = 'models/risk_scorer.pkl'
        self.scaler_path = 'models/risk_scaler.pkl'
        
        # Load pre-trained model if exists
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model and scaler"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            try:
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                logger.info("Loaded pre-trained risk scoring model")
            except Exception as e:
                logger.warning(f"Could not load pre-trained model: {e}")
    
    def extract_risk_features(self, address: str, address_data: Dict[str, Any]) -> List[float]:
        """Extract risk features for an address"""
        features = []
        
        # Transaction-based features
        features.append(address_data.get('transaction_count', 0))
        features.append(address_data.get('total_volume_eth', 0))
        features.append(address_data.get('avg_transaction_value', 0))
        features.append(address_data.get('max_transaction_value', 0))
        
        # Gas price volatility
        gas_prices = address_data.get('gas_prices', [])
        if gas_prices:
            features.append(np.std(gas_prices))
        else:
            features.append(0)
        
        # Contract interaction ratio
        total_txs = address_data.get('transaction_count', 1)
        contract_txs = address_data.get('contract_interactions', 0)
        features.append(contract_txs / total_txs if total_txs > 0 else 0)
        
        # Unique counterparties
        features.append(address_data.get('unique_counterparties', 0))
        
        # MEV activity score
        features.append(address_data.get('mev_activity_score', 0))
        
        # Whale movement score
        features.append(address_data.get('whale_movement_score', 0))
        
        # Sanctions risk score
        features.append(address_data.get('sanctions_risk_score', 0))
        
        # Age in days
        features.append(address_data.get('age_days', 0))
        
        # Balance volatility
        balance_history = address_data.get('balance_history', [])
        if balance_history:
            features.append(np.std(balance_history))
        else:
            features.append(0)
        
        return features
    
    def calculate_risk_score(self, address: str, address_data: Dict[str, Any]) -> float:
        """Calculate risk score for an address"""
        try:
            features = self.extract_risk_features(address, address_data)
            
            # Normalize features
            features_scaled = self.scaler.transform([features])
            
            # Predict risk score
            risk_score = self.model.predict(features_scaled)[0]
            
            # Ensure score is between 0 and 1
            return max(0.0, min(1.0, risk_score))
        except Exception as e:
            logger.error(f"Error calculating risk score for {address}: {e}")
            # Return default risk score if model fails
            return 0.5
    
    def train_model(self, training_data: List[Dict[str, Any]]):
        """Train the risk scoring model"""
        try:
            X = []
            y = []
            
            for data_point in training_data:
                features = self.extract_risk_features(data_point['address'], data_point['address_data'])
                X.append(features)
                y.append(data_point['risk_score'])
            
            X = np.array(X)
            y = np.array(y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            logger.info(f"Model trained - MSE: {mse:.4f}, R²: {r2:.4f}")
            
            # Save model
            self._save_model()
            
            return {'mse': mse, 'r2': r2}
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {'mse': 0, 'r2': 0}
    
    def _save_model(self):
        """Save trained model and scaler"""
        try:
            os.makedirs('models', exist_ok=True)
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            logger.info("Model saved successfully")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from the model"""
        try:
            importance = self.model.feature_importances_
            return dict(zip(self.feature_names, importance))
        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return {}
    
    def explain_risk_score(self, address: str, address_data: Dict[str, Any]) -> Dict[str, Any]:
        """Explain the risk score for an address"""
        try:
            features = self.extract_risk_features(address, address_data)
            feature_importance = self.get_feature_importance()
            
            # Calculate contribution of each feature
            contributions = {}
            for i, feature_name in enumerate(self.feature_names):
                importance = feature_importance.get(feature_name, 0)
                value = features[i]
                contributions[feature_name] = {
                    'value': value,
                    'importance': importance,
                    'contribution': value * importance
                }
            
            # Sort by contribution
            sorted_contributions = sorted(
                contributions.items(), 
                key=lambda x: abs(x[1]['contribution']), 
                reverse=True
            )
            
            return {
                'address': address,
                'risk_score': self.calculate_risk_score(address, address_data),
                'feature_contributions': dict(sorted_contributions[:5]),  # Top 5 features
                'risk_factors': self._identify_risk_factors(contributions)
            }
        except Exception as e:
            logger.error(f"Error explaining risk score: {e}")
            return {
                'address': address,
                'risk_score': 0.5,
                'feature_contributions': {},
                'risk_factors': ['Model error']
            }
    
    def _identify_risk_factors(self, contributions: Dict[str, Dict[str, float]]) -> List[str]:
        """Identify main risk factors"""
        risk_factors = []
        
        for feature_name, data in contributions.items():
            if abs(data['contribution']) > 0.1:  # Significant contribution
                if data['contribution'] > 0:
                    risk_factors.append(f"High {feature_name.replace('_', ' ')}")
                else:
                    risk_factors.append(f"Low {feature_name.replace('_', ' ')}")
        
        return risk_factors[:3]  # Top 3 risk factors
    
    def generate_sample_training_data(self) -> List[Dict[str, Any]]:
        """Generate sample training data for model training"""
        sample_data = []
        
        # Generate various risk profiles
        risk_profiles = [
            # Low risk - normal user
            {
                'address': '0x1234567890123456789012345678901234567890',
                'address_data': {
                    'transaction_count': 50,
                    'total_volume_eth': 10,
                    'avg_transaction_value': 0.2,
                    'max_transaction_value': 2,
                    'gas_prices': [20, 25, 30, 22, 28],
                    'contract_interactions': 5,
                    'unique_counterparties': 8,
                    'mev_activity_score': 0,
                    'whale_movement_score': 0,
                    'sanctions_risk_score': 0,
                    'age_days': 365,
                    'balance_history': [1, 1.2, 0.8, 1.1, 0.9]
                },
                'risk_score': 0.1
            },
            # Medium risk - active trader
            {
                'address': '0x2345678901234567890123456789012345678901',
                'address_data': {
                    'transaction_count': 200,
                    'total_volume_eth': 100,
                    'avg_transaction_value': 0.5,
                    'max_transaction_value': 10,
                    'gas_prices': [50, 80, 120, 90, 150],
                    'contract_interactions': 80,
                    'unique_counterparties': 25,
                    'mev_activity_score': 0.3,
                    'whale_movement_score': 0.2,
                    'sanctions_risk_score': 0,
                    'age_days': 180,
                    'balance_history': [5, 8, 3, 12, 6]
                },
                'risk_score': 0.5
            },
            # High risk - MEV bot
            {
                'address': '0x3456789012345678901234567890123456789012',
                'address_data': {
                    'transaction_count': 1000,
                    'total_volume_eth': 1000,
                    'avg_transaction_value': 1,
                    'max_transaction_value': 50,
                    'gas_prices': [200, 300, 500, 400, 600],
                    'contract_interactions': 900,
                    'unique_counterparties': 100,
                    'mev_activity_score': 0.9,
                    'whale_movement_score': 0.8,
                    'sanctions_risk_score': 0.1,
                    'age_days': 90,
                    'balance_history': [20, 50, 10, 80, 30]
                },
                'risk_score': 0.9
            }
        ]
        
        # Add more variations
        for i in range(10):
            base_profile = risk_profiles[i % 3].copy()
            base_profile['address'] = f"0x{i:040x}"
            base_profile['address_data'] = base_profile['address_data'].copy()
            
            # Add some variation
            base_profile['address_data']['transaction_count'] += np.random.randint(-10, 10)
            base_profile['address_data']['total_volume_eth'] += np.random.uniform(-5, 5)
            base_profile['risk_score'] += np.random.uniform(-0.1, 0.1)
            base_profile['risk_score'] = max(0, min(1, base_profile['risk_score']))
            
            sample_data.append(base_profile)
        
        return sample_data
    
    def initialize_with_sample_data(self):
        """Initialize the model with sample training data"""
        logger.info("Initializing risk scorer with sample data...")
        sample_data = self.generate_sample_training_data()
        self.train_model(sample_data)
        logger.info("Risk scorer initialized successfully") 