import hashlib
from typing import List, Dict, Any, Tuple
from collections import defaultdict
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
import logging

logger = logging.getLogger(__name__)

class EntityResolver:
    def __init__(self):
        self.address_clusters = defaultdict(list)
        self.entity_counter = 0
    
    def extract_features(self, address: str, transactions: List[Dict]) -> Dict[str, Any]:
        """Extract features from address and its transactions"""
        if not transactions:
            return {
                'address': address,
                'transaction_count': 0,
                'total_value_sent': 0.0,
                'total_value_received': 0.0,
                'unique_contracts': 0,
                'avg_gas_price': 0.0,
                'activity_pattern': '',
                'time_between_txs': []
            }
        
        features = {
            'address': address,
            'transaction_count': len(transactions),
            'total_value_sent': sum(tx.get('value', 0) for tx in transactions),
            'total_value_received': sum(tx.get('value', 0) for tx in transactions if tx.get('to') == address),
            'unique_contracts': len(set(tx.get('to') for tx in transactions if tx.get('input') != '0x')),
            'avg_gas_price': np.mean([tx.get('gasPrice', 0) for tx in transactions]) if transactions else 0.0,
            'activity_pattern': self._extract_activity_pattern(transactions),
            'time_between_txs': self._calculate_time_intervals(transactions)
        }
        return features
    
    def _extract_activity_pattern(self, transactions: List[Dict]) -> str:
        """Extract activity pattern as a string for similarity comparison"""
        if not transactions:
            return ''
        
        patterns = []
        for tx in transactions:
            if tx.get('input') == '0x':
                patterns.append('transfer')
            elif tx.get('to') in ['0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D']:  # Uniswap
                patterns.append('swap')
            else:
                patterns.append('contract')
        return ' '.join(patterns)
    
    def _calculate_time_intervals(self, transactions: List[Dict]) -> List[float]:
        """Calculate time intervals between transactions"""
        if len(transactions) < 2:
            return []
        
        timestamps = sorted([tx.get('timestamp', 0) for tx in transactions])
        intervals = []
        for i in range(1, len(timestamps)):
            intervals.append(timestamps[i] - timestamps[i-1])
        return intervals
    
    def cluster_addresses(self, addresses_data: Dict[str, List[Dict]]) -> Dict[str, List[str]]:
        """Cluster addresses based on behavioral similarity"""
        if not addresses_data:
            return {}
        
        # Extract features for all addresses
        features_list = []
        address_list = []
        
        for address, transactions in addresses_data.items():
            features = self.extract_features(address, transactions)
            features_list.append(features)
            address_list.append(address)
        
        # Create feature matrix for clustering
        feature_matrix = []
        for features in features_list:
            feature_vector = [
                float(features['transaction_count']),
                float(features['total_value_sent']),
                float(features['total_value_received']),
                float(features['unique_contracts']),
                float(features['avg_gas_price'])
            ]
            feature_matrix.append(feature_vector)
        
        # Handle NaN values
        feature_matrix = np.array(feature_matrix)
        
        # Replace infinite values with large finite values
        feature_matrix = np.nan_to_num(feature_matrix, nan=0.0, posinf=1e6, neginf=-1e6)
        
        # Normalize features safely
        feature_means = np.mean(feature_matrix, axis=0)
        feature_stds = np.std(feature_matrix, axis=0)
        
        # Avoid division by zero
        feature_stds = np.where(feature_stds == 0, 1.0, feature_stds)
        
        feature_matrix = (feature_matrix - feature_means) / feature_stds
        
        # Perform clustering
        try:
            clustering = DBSCAN(eps=0.5, min_samples=2).fit(feature_matrix)
            
            # Group addresses by cluster
            clusters = defaultdict(list)
            for address, cluster_id in zip(address_list, clustering.labels_):
                if cluster_id != -1:  # Not noise
                    clusters[f"entity_{cluster_id}"].append(address)
            
            return dict(clusters)
        except Exception as e:
            logger.error(f"Clustering failed: {e}")
            return {}
    
    def calculate_similarity_score(self, addr1_features: Dict, addr2_features: Dict) -> float:
        """Calculate similarity score between two addresses"""
        try:
            # Simple cosine similarity for numerical features
            features1 = np.array([
                float(addr1_features['transaction_count']),
                float(addr1_features['total_value_sent']),
                float(addr1_features['total_value_received']),
                float(addr1_features['unique_contracts']),
                float(addr1_features['avg_gas_price'])
            ])
            
            features2 = np.array([
                float(addr2_features['transaction_count']),
                float(addr2_features['total_value_sent']),
                float(addr2_features['total_value_received']),
                float(addr2_features['unique_contracts']),
                float(addr2_features['avg_gas_price'])
            ])
            
            # Handle NaN values
            features1 = np.nan_to_num(features1, nan=0.0)
            features2 = np.nan_to_num(features2, nan=0.0)
            
            # Normalize
            norm1 = np.linalg.norm(features1)
            norm2 = np.linalg.norm(features2)
            
            if norm1 == 0 or norm2 == 0:
                similarity = 0.0
            else:
                features1 = features1 / norm1
                features2 = features2 / norm2
                similarity = np.dot(features1, features2)
            
            # Add pattern similarity
            pattern_similarity = self._calculate_pattern_similarity(
                addr1_features['activity_pattern'],
                addr2_features['activity_pattern']
            )
            
            return 0.7 * similarity + 0.3 * pattern_similarity
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0
    
    def _calculate_pattern_similarity(self, pattern1: str, pattern2: str) -> float:
        """Calculate similarity between activity patterns"""
        if not pattern1 or not pattern2:
            return 0.0
        
        try:
            vectorizer = TfidfVectorizer()
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