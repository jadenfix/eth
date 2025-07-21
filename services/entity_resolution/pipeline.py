"""
Entity Resolution Pipeline using Vertex AI.

Matches and resolves blockchain addresses to known entities,
enriching the data with semantic identity information.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

import structlog
from google.cloud import aiplatform
from google.cloud import bigquery
from google.cloud import pubsub_v1
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@dataclass
class EntityCandidate:
    """Potential entity match candidate."""
    entity_id: str
    name: str
    address: Optional[str]
    labels: List[str]
    confidence_score: float
    match_reasons: List[str]


@dataclass
class EntityResolution:
    """Entity resolution result."""
    input_address: str
    resolved_entity_id: Optional[str]
    confidence_score: float
    candidates: List[EntityCandidate]
    resolution_method: str
    timestamp: datetime


class EntityMatcher:
    """ML-based entity matching engine."""
    
    def __init__(self):
        self.bigquery_client = bigquery.Client()
        self.publisher = pubsub_v1.PublisherClient()
        self.logger = logger.bind(service="entity-matcher")
        
        # Load known entities
        self.known_entities = self._load_known_entities()
        self.address_vectorizer = TfidfVectorizer()
        self.label_vectorizer = TfidfVectorizer()
        
        # Initialize Vertex AI
        aiplatform.init(
            project=os.getenv('GOOGLE_CLOUD_PROJECT'),
            location=os.getenv('VERTEX_AI_REGION', 'us-central1')
        )
        
    def _load_known_entities(self) -> pd.DataFrame:
        """Load known entities from BigQuery."""
        try:
            query = """
            SELECT 
                entity_id,
                name,
                address,
                labels,
                properties,
                risk_score
            FROM `{project}.onchain_data.entities`
            WHERE address IS NOT NULL
            """.format(project=os.getenv('GOOGLE_CLOUD_PROJECT'))
            
            return self.bigquery_client.query(query).to_dataframe()
            
        except Exception as e:
            self.logger.error("Error loading known entities", error=str(e))
            return pd.DataFrame()
    
    def resolve_address(self, address: str, context: Dict[str, Any] = None) -> EntityResolution:
        """Resolve an address to a known entity."""
        context = context or {}
        
        try:
            # Step 1: Direct address lookup
            direct_match = self._direct_address_lookup(address)
            if direct_match and direct_match.confidence_score > 0.9:
                return EntityResolution(
                    input_address=address,
                    resolved_entity_id=direct_match.entity_id,
                    confidence_score=direct_match.confidence_score,
                    candidates=[direct_match],
                    resolution_method="direct_lookup",
                    timestamp=datetime.utcnow()
                )
            
            # Step 2: Behavioral similarity matching
            behavioral_candidates = self._behavioral_similarity_matching(address, context)
            
            # Step 3: Network analysis matching
            network_candidates = self._network_analysis_matching(address, context)
            
            # Combine and rank candidates
            all_candidates = []
            if direct_match:
                all_candidates.append(direct_match)
            all_candidates.extend(behavioral_candidates)
            all_candidates.extend(network_candidates)
            
            # Remove duplicates and sort by confidence
            unique_candidates = self._deduplicate_candidates(all_candidates)
            unique_candidates.sort(key=lambda x: x.confidence_score, reverse=True)
            
            # Select best match if confidence is high enough
            best_match = unique_candidates[0] if unique_candidates else None
            resolved_entity_id = None
            resolution_method = "no_match"
            
            if best_match and best_match.confidence_score > 0.7:
                resolved_entity_id = best_match.entity_id
                resolution_method = "ml_matching"
            
            return EntityResolution(
                input_address=address,
                resolved_entity_id=resolved_entity_id,
                confidence_score=best_match.confidence_score if best_match else 0.0,
                candidates=unique_candidates[:5],  # Top 5 candidates
                resolution_method=resolution_method,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error("Error resolving address", address=address, error=str(e))
            return EntityResolution(
                input_address=address,
                resolved_entity_id=None,
                confidence_score=0.0,
                candidates=[],
                resolution_method="error",
                timestamp=datetime.utcnow()
            )
    
    def _direct_address_lookup(self, address: str) -> Optional[EntityCandidate]:
        """Direct lookup in known entities."""
        matches = self.known_entities[
            self.known_entities['address'].str.lower() == address.lower()
        ]
        
        if len(matches) > 0:
            entity = matches.iloc[0]
            return EntityCandidate(
                entity_id=entity['entity_id'],
                name=entity['name'],
                address=entity['address'],
                labels=entity['labels'] if entity['labels'] else [],
                confidence_score=1.0,
                match_reasons=['direct_address_match']
            )
        
        return None
    
    def _behavioral_similarity_matching(self, address: str, context: Dict[str, Any]) -> List[EntityCandidate]:
        """Match based on behavioral patterns."""
        candidates = []
        
        try:
            # Get transaction patterns for the address
            tx_patterns = self._get_transaction_patterns(address)
            if not tx_patterns:
                return candidates
            
            # Compare with known entity patterns
            for _, entity in self.known_entities.iterrows():
                entity_patterns = self._get_transaction_patterns(entity['address'])
                if not entity_patterns:
                    continue
                
                similarity_score = self._calculate_behavioral_similarity(tx_patterns, entity_patterns)
                
                if similarity_score > 0.5:
                    candidates.append(EntityCandidate(
                        entity_id=entity['entity_id'],
                        name=entity['name'],
                        address=entity['address'],
                        labels=entity['labels'] if entity['labels'] else [],
                        confidence_score=similarity_score * 0.8,  # Reduce confidence for behavioral match
                        match_reasons=[f'behavioral_similarity_{similarity_score:.2f}']
                    ))
            
        except Exception as e:
            self.logger.error("Error in behavioral matching", error=str(e))
        
        return candidates
    
    def _network_analysis_matching(self, address: str, context: Dict[str, Any]) -> List[EntityCandidate]:
        """Match based on network connections."""
        candidates = []
        
        try:
            # Get addresses that frequently interact with the input address
            connected_addresses = self._get_connected_addresses(address)
            
            # Find known entities among connected addresses
            for connected_addr in connected_addresses[:10]:  # Top 10 connections
                direct_match = self._direct_address_lookup(connected_addr['address'])
                if direct_match:
                    # Create candidate based on network connection
                    confidence = min(0.6, connected_addr['interaction_count'] / 100.0)
                    
                    candidates.append(EntityCandidate(
                        entity_id=f"network_inferred_{len(candidates)}",
                        name=f"Connected to {direct_match.name}",
                        address=address,
                        labels=['network_inferred'] + direct_match.labels,
                        confidence_score=confidence,
                        match_reasons=[f'connected_to_{direct_match.entity_id}']
                    ))
            
        except Exception as e:
            self.logger.error("Error in network matching", error=str(e))
        
        return candidates
    
    def _get_transaction_patterns(self, address: str) -> Optional[Dict[str, Any]]:
        """Get transaction patterns for an address."""
        try:
            query = """
            SELECT 
                COUNT(*) as tx_count,
                AVG(value_usd) as avg_value,
                STDDEV(value_usd) as stddev_value,
                COUNT(DISTINCT DATE(timestamp)) as active_days,
                ARRAY_AGG(DISTINCT event_type) as event_types
            FROM `{project}.onchain_data.curated_events`
            WHERE from_address = @address OR to_address = @address
            AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
            """.format(project=os.getenv('GOOGLE_CLOUD_PROJECT'))
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("address", "STRING", address)
                ]
            )
            
            result = self.bigquery_client.query(query, job_config=job_config).to_dataframe()
            
            if len(result) > 0:
                return result.iloc[0].to_dict()
            
        except Exception as e:
            self.logger.error("Error getting transaction patterns", address=address, error=str(e))
        
        return None
    
    def _get_connected_addresses(self, address: str) -> List[Dict[str, Any]]:
        """Get addresses frequently connected to the input address."""
        try:
            query = """
            WITH connections AS (
                SELECT 
                    CASE 
                        WHEN from_address = @address THEN to_address
                        ELSE from_address
                    END as connected_address,
                    COUNT(*) as interaction_count,
                    SUM(value_usd) as total_value
                FROM `{project}.onchain_data.curated_events`
                WHERE (from_address = @address OR to_address = @address)
                AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
                GROUP BY connected_address
                HAVING connected_address != @address
                ORDER BY interaction_count DESC
                LIMIT 20
            )
            SELECT * FROM connections
            """.format(project=os.getenv('GOOGLE_CLOUD_PROJECT'))
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("address", "STRING", address)
                ]
            )
            
            result = self.bigquery_client.query(query, job_config=job_config).to_dataframe()
            return result.to_dict('records')
            
        except Exception as e:
            self.logger.error("Error getting connected addresses", address=address, error=str(e))
            return []
    
    def _calculate_behavioral_similarity(self, patterns1: Dict[str, Any], patterns2: Dict[str, Any]) -> float:
        """Calculate behavioral similarity between two address patterns."""
        try:
            # Normalize numerical features
            features1 = [
                patterns1.get('tx_count', 0),
                patterns1.get('avg_value', 0),
                patterns1.get('active_days', 0)
            ]
            
            features2 = [
                patterns2.get('tx_count', 0),
                patterns2.get('avg_value', 0),
                patterns2.get('active_days', 0)
            ]
            
            # Calculate cosine similarity
            if sum(features1) == 0 or sum(features2) == 0:
                return 0.0
            
            similarity = cosine_similarity([features1], [features2])[0][0]
            return max(0.0, similarity)
            
        except Exception as e:
            self.logger.error("Error calculating similarity", error=str(e))
            return 0.0
    
    def _deduplicate_candidates(self, candidates: List[EntityCandidate]) -> List[EntityCandidate]:
        """Remove duplicate candidates."""
        seen_entities = set()
        unique_candidates = []
        
        for candidate in candidates:
            if candidate.entity_id not in seen_entities:
                seen_entities.add(candidate.entity_id)
                unique_candidates.append(candidate)
        
        return unique_candidates
    
    def batch_resolve_addresses(self, addresses: List[str]) -> List[EntityResolution]:
        """Resolve multiple addresses in batch."""
        results = []
        
        for address in addresses:
            resolution = self.resolve_address(address)
            results.append(resolution)
            
            # Update BigQuery with resolution results
            self._store_resolution(resolution)
        
        return results
    
    def _store_resolution(self, resolution: EntityResolution):
        """Store entity resolution results in BigQuery."""
        try:
            table_id = f"{os.getenv('GOOGLE_CLOUD_PROJECT')}.onchain_data.entity_resolutions"
            
            rows_to_insert = [{
                'input_address': resolution.input_address,
                'resolved_entity_id': resolution.resolved_entity_id,
                'confidence_score': resolution.confidence_score,
                'resolution_method': resolution.resolution_method,
                'timestamp': resolution.timestamp.isoformat(),
                'candidates': json.dumps([
                    {
                        'entity_id': c.entity_id,
                        'confidence_score': c.confidence_score,
                        'match_reasons': c.match_reasons
                    } for c in resolution.candidates[:3]  # Top 3 candidates
                ])
            }]
            
            errors = self.bigquery_client.insert_rows_json(table_id, rows_to_insert)
            
            if errors:
                self.logger.error("Error storing resolution", errors=errors)
            else:
                self.logger.info("Stored entity resolution", address=resolution.input_address)
                
        except Exception as e:
            self.logger.error("Error storing resolution", error=str(e))


def main():
    """Main pipeline entry point."""
    matcher = EntityMatcher()
    
    # Example usage
    test_address = "0x742d35cc6634c0532925a3b8bc9c4b8b0532925a"
    resolution = matcher.resolve_address(test_address)
    
    print(f"Resolution for {test_address}:")
    print(f"Resolved Entity: {resolution.resolved_entity_id}")
    print(f"Confidence: {resolution.confidence_score}")
    print(f"Method: {resolution.resolution_method}")
    print(f"Candidates: {len(resolution.candidates)}")


if __name__ == "__main__":
    main()
