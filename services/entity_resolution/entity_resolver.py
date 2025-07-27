import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import logging
from typing import List, Dict, Any, Tuple
import re

logger = logging.getLogger(__name__)

class EntityResolver:
    def __init__(self, eps=0.5, min_samples=2):
        self.eps = eps
        self.min_samples = min_samples
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='mean')
        
    def extract_features(self, transactions: List[Dict[str, Any]]) -> List[float]:
        """Extract numerical features from transactions"""
        if not transactions:
            # Return default features for empty transaction list
            return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        try:
            # Initialize features with safe defaults
            total_value_sent = 0.0
            total_value_received = 0.0
            avg_gas_price = 0.0
            total_transactions = len(transactions)
            unique_contracts = set()
            time_intervals = []
            
            for tx in transactions:
                # Safe value extraction
                value = float(tx.get('value', 0))
                if tx.get('from') and tx.get('to'):
                    if tx['from'] == tx.get('address', ''):
                        total_value_sent += value
                    else:
                        total_value_received += value
                
                # Safe gas price extraction
                gas_price = float(tx.get('gasPrice', 0))
                avg_gas_price += gas_price
                
                # Contract interaction detection
                if tx.get('input') and tx['input'] != '0x':
                    unique_contracts.add(tx.get('to', ''))
            
            # Calculate averages safely
            avg_gas_price = avg_gas_price / total_transactions if total_transactions > 0 else 0.0
            
            # Extract time patterns
            time_intervals = self._calculate_time_intervals(transactions)
            
            # Extract activity patterns
            activity_pattern = self._extract_activity_pattern(transactions)
            
            # Create feature vector with explicit float conversion
            features = [
                float(total_value_sent),
                float(total_value_received),
                float(avg_gas_price),
                float(total_transactions),
                float(len(unique_contracts)),
                float(len(time_intervals)),
                float(np.mean(time_intervals) if time_intervals else 0.0),
                float(np.std(time_intervals) if time_intervals else 0.0),
                float(activity_pattern.get('frequency', 0.0)),
                float(activity_pattern.get('regularity', 0.0))
            ]
            
            # Ensure all features are finite numbers
            features = [float(f) if np.isfinite(f) else 0.0 for f in features]
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            # Return safe default features
            return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    
    def _calculate_time_intervals(self, transactions: List[Dict[str, Any]]) -> List[float]:
        """Calculate time intervals between transactions"""
        if not transactions or len(transactions) < 2:
            return []
        
        try:
            timestamps = []
            for tx in transactions:
                timestamp = tx.get('timestamp', 0)
                if timestamp:
                    timestamps.append(float(timestamp))
            
            if len(timestamps) < 2:
                return []
            
            timestamps.sort()
            intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
            return [float(i) for i in intervals if np.isfinite(i)]
            
        except Exception as e:
            logger.error(f"Error calculating time intervals: {e}")
            return []
    
    def _extract_activity_pattern(self, transactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Extract activity pattern features"""
        if not transactions:
            return {'frequency': 0.0, 'regularity': 0.0}
        
        try:
            # Calculate transaction frequency
            total_time = 0
            if len(transactions) > 1:
                timestamps = [float(tx.get('timestamp', 0)) for tx in transactions]
                timestamps.sort()
                total_time = timestamps[-1] - timestamps[0]
            
            frequency = len(transactions) / max(total_time, 1)
            
            # Calculate regularity (standard deviation of intervals)
            intervals = self._calculate_time_intervals(transactions)
            regularity = float(np.std(intervals)) if intervals else 0.0
            
            return {
                'frequency': float(frequency) if np.isfinite(frequency) else 0.0,
                'regularity': float(regularity) if np.isfinite(regularity) else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error extracting activity pattern: {e}")
            return {'frequency': 0.0, 'regularity': 0.0}
    
    def cluster_addresses(self, addresses: List[str], transactions_by_address: Dict[str, List[Dict[str, Any]]]) -> Dict[str, int]:
        """Cluster addresses based on transaction patterns"""
        if len(addresses) < 2:
            return {addr: 0 for addr in addresses}
        
        try:
            # Extract features for each address
            feature_matrix = []
            valid_addresses = []
            
            for addr in addresses:
                transactions = transactions_by_address.get(addr, [])
                features = self.extract_features(transactions)
                
                # Ensure all features are valid numbers
                if all(np.isfinite(f) for f in features):
                    feature_matrix.append(features)
                    valid_addresses.append(addr)
            
            if len(feature_matrix) < 2:
                return {addr: 0 for addr in addresses}
            
            # Convert to numpy array and handle NaN/Inf values
            feature_matrix = np.array(feature_matrix, dtype=float)
            feature_matrix = np.nan_to_num(feature_matrix, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Normalize features safely
            try:
                # Check if we have any variance in the data
                if feature_matrix.shape[1] > 0:
                    std_devs = np.std(feature_matrix, axis=0)
                    # Only normalize if we have non-zero standard deviation
                    if np.any(std_devs > 1e-10):
                        feature_matrix = (feature_matrix - np.mean(feature_matrix, axis=0)) / np.maximum(std_devs, 1e-10)
            except Exception as e:
                logger.warning(f"Normalization failed, using raw features: {e}")
            
            # Apply DBSCAN clustering
            clustering = DBSCAN(eps=self.eps, min_samples=self.min_samples)
            cluster_labels = clustering.fit_predict(feature_matrix)
            
            # Create result mapping
            result = {}
            for i, addr in enumerate(valid_addresses):
                result[addr] = int(cluster_labels[i])
            
            # Add addresses that weren't processed
            for addr in addresses:
                if addr not in result:
                    result[addr] = -1  # Noise points
            
            logger.info(f"Clustering completed: {len(set(cluster_labels))} clusters found")
            return result
            
        except Exception as e:
            logger.error(f"Clustering failed: {e}")
            # Return individual clusters for each address
            return {addr: i for i, addr in enumerate(addresses)}
    
    def calculate_similarity_score(self, address1: str, address2: str, 
                                 transactions_by_address: Dict[str, List[Dict[str, Any]]]) -> float:
        """Calculate similarity score between two addresses"""
        try:
            transactions1 = transactions_by_address.get(address1, [])
            transactions2 = transactions_by_address.get(address2, [])
            
            features1 = self.extract_features(transactions1)
            features2 = self.extract_features(transactions2)
            
            # Ensure features are valid
            features1 = [float(f) if np.isfinite(f) else 0.0 for f in features1]
            features2 = [float(f) if np.isfinite(f) else 0.0 for f in features2]
            
            # Convert to numpy arrays
            features1 = np.array(features1, dtype=float)
            features2 = np.array(features2, dtype=float)
            
            # Handle NaN values
            features1 = np.nan_to_num(features1, nan=0.0)
            features2 = np.nan_to_num(features2, nan=0.0)
            
            # Calculate cosine similarity
            norm1 = np.linalg.norm(features1)
            norm2 = np.linalg.norm(features2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = np.dot(features1, features2) / (norm1 * norm2)
            return float(np.clip(similarity, -1.0, 1.0))
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def _calculate_pattern_similarity(self, pattern1: str, pattern2: str) -> float:
        """Calculate similarity between transaction patterns"""
        try:
            if not pattern1 or not pattern2:
                return 0.0
            
            # Create TF-IDF vectors
            vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3))
            tfidf_matrix = vectorizer.fit_transform([pattern1, pattern2])
            
            # Convert to dense array for similarity calculation
            tfidf_dense = tfidf_matrix.toarray()
            similarity = np.dot(tfidf_dense[0], tfidf_dense[1])
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Pattern similarity calculation failed: {e}")
            return 0.0
    
    def detect_exchange_patterns(self, addresses_data: Dict[str, List[Dict]]) -> List[str]:
        """Detect exchange-like wallet patterns"""
        exchange_addresses = []
        
        for address, transactions in addresses_data.items():
            if len(transactions) < 10:
                continue
            
            # Exchange-like patterns
            high_frequency = len(transactions) > 100  # transactions per day
            low_value = all(tx.get('value', 0) < 0.1 * 1e18 for tx in transactions)  # < 0.1 ETH
            contract_interaction = sum(1 for tx in transactions if tx.get('input') != '0x') / len(transactions) > 0.8
            
            if high_frequency and low_value and contract_interaction:
                exchange_addresses.append(address)
        
        return exchange_addresses
    
    def detect_whale_patterns(self, addresses_data: Dict[str, List[Dict]]) -> List[str]:
        """Detect whale wallet patterns"""
        whale_addresses = []
        whale_threshold = 100 * 1e18  # 100 ETH
        
        for address, transactions in addresses_data.items():
            total_value = sum(tx.get('value', 0) for tx in transactions)
            if total_value > whale_threshold:
                whale_addresses.append(address)
        
        return whale_addresses
    
    def detect_mev_patterns(self, addresses_data: Dict[str, List[Dict]]) -> List[str]:
        """Detect MEV bot patterns"""
        mev_addresses = []
        high_gas_threshold = 200 * 1e9  # 200 gwei
        
        for address, transactions in addresses_data.items():
            high_gas_count = sum(1 for tx in transactions if tx.get('gasPrice', 0) > high_gas_threshold)
            if high_gas_count > len(transactions) * 0.5:  # More than 50% high gas
                mev_addresses.append(address)
        
        return mev_addresses 