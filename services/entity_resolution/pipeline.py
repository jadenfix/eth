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
        structlog.processors.JSONRenderer(),
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
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("VERTEX_AI_REGION", "us-central1"),
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
            """.format(project=os.getenv("GOOGLE_CLOUD_PROJECT"))

            return self.bigquery_client.query(query).to_dataframe()

        except Exception as e:
            self.logger.error("Error loading known entities", error=str(e))
            return pd.DataFrame()

    def resolve_address(
        self, address: str, context: Dict[str, Any] = None
    ) -> EntityResolution:
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
                    timestamp=datetime.utcnow(),
                )

            # Step 2: Behavioral similarity matching
            behavioral_candidates = self._behavioral_similarity_matching(
                address, context
            )

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
                timestamp=datetime.utcnow(),
            )

        except Exception as e:
            self.logger.error("Error resolving address", address=address, error=str(e))
            return EntityResolution(
                input_address=address,
                resolved_entity_id=None,
                confidence_score=0.0,
                candidates=[],
                resolution_method="error",
                timestamp=datetime.utcnow(),
            )

    def _direct_address_lookup(self, address: str) -> Optional[EntityCandidate]:
        """Direct lookup in known entities."""
        matches = self.known_entities[
            self.known_entities["address"].str.lower() == address.lower()
        ]

        if len(matches) > 0:
            entity = matches.iloc[0]
            return EntityCandidate(
                entity_id=entity["entity_id"],
                name=entity["name"],
                address=entity["address"],
                labels=entity["labels"] if entity["labels"] else [],
                confidence_score=1.0,
                match_reasons=["direct_address_match"],
            )

        return None

    def _behavioral_similarity_matching(
        self, address: str, context: Dict[str, Any]
    ) -> List[EntityCandidate]:
        """Match based on behavioral patterns."""
        candidates = []

        try:
            # Get transaction patterns for the address
            tx_patterns = self._get_transaction_patterns(address)
            if not tx_patterns:
                return candidates

            # Compare with known entity patterns
            for _, entity in self.known_entities.iterrows():
                entity_patterns = self._get_transaction_patterns(entity["address"])
                if not entity_patterns:
                    continue

                similarity_score = self._calculate_behavioral_similarity(
                    tx_patterns, entity_patterns
                )

                if similarity_score > 0.5:
                    candidates.append(
                        EntityCandidate(
                            entity_id=entity["entity_id"],
                            name=entity["name"],
                            address=entity["address"],
                            labels=entity["labels"] if entity["labels"] else [],
                            confidence_score=similarity_score
                            * 0.8,  # Reduce confidence for behavioral match
                            match_reasons=[
                                f"behavioral_similarity_{similarity_score:.2f}"
                            ],
                        )
                    )

        except Exception as e:
            self.logger.error("Error in behavioral matching", error=str(e))

        return candidates

    def _network_analysis_matching(
        self, address: str, context: Dict[str, Any]
    ) -> List[EntityCandidate]:
        """Match based on network connections."""
        candidates = []

        try:
            # Get addresses that frequently interact with the input address
            connected_addresses = self._get_connected_addresses(address)

            # Find known entities among connected addresses
            for connected_addr in connected_addresses[:10]:  # Top 10 connections
                direct_match = self._direct_address_lookup(connected_addr["address"])
                if direct_match:
                    # Create candidate based on network connection
                    confidence = min(0.6, connected_addr["interaction_count"] / 100.0)

                    candidates.append(
                        EntityCandidate(
                            entity_id=f"network_inferred_{len(candidates)}",
                            name=f"Connected to {direct_match.name}",
                            address=address,
                            labels=["network_inferred"] + direct_match.labels,
                            confidence_score=confidence,
                            match_reasons=[f"connected_to_{direct_match.entity_id}"],
                        )
                    )

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
            """.format(project=os.getenv("GOOGLE_CLOUD_PROJECT"))

            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("address", "STRING", address)
                ]
            )

            result = self.bigquery_client.query(
                query, job_config=job_config
            ).to_dataframe()

            if len(result) > 0:
                return result.iloc[0].to_dict()

        except Exception as e:
            self.logger.error(
                "Error getting transaction patterns", address=address, error=str(e)
            )

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
            """.format(project=os.getenv("GOOGLE_CLOUD_PROJECT"))

            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("address", "STRING", address)
                ]
            )

            result = self.bigquery_client.query(
                query, job_config=job_config
            ).to_dataframe()
            return result.to_dict("records")

        except Exception as e:
            self.logger.error(
                "Error getting connected addresses", address=address, error=str(e)
            )
            return []

    def _calculate_behavioral_similarity(
        self, patterns1: Dict[str, Any], patterns2: Dict[str, Any]
    ) -> float:
        """Calculate behavioral similarity between two address patterns."""
        try:
            # Normalize numerical features
            features1 = [
                patterns1.get("tx_count", 0),
                patterns1.get("avg_value", 0),
                patterns1.get("active_days", 0),
            ]

            features2 = [
                patterns2.get("tx_count", 0),
                patterns2.get("avg_value", 0),
                patterns2.get("active_days", 0),
            ]

            # Calculate cosine similarity
            if sum(features1) == 0 or sum(features2) == 0:
                return 0.0

            similarity = cosine_similarity([features1], [features2])[0][0]
            return max(0.0, similarity)

        except Exception as e:
            self.logger.error("Error calculating similarity", error=str(e))
            return 0.0

    def _deduplicate_candidates(
        self, candidates: List[EntityCandidate]
    ) -> List[EntityCandidate]:
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
            table_id = (
                f"{os.getenv('GOOGLE_CLOUD_PROJECT')}.onchain_data.entity_resolutions"
            )

            rows_to_insert = [
                {
                    "input_address": resolution.input_address,
                    "resolved_entity_id": resolution.resolved_entity_id,
                    "confidence_score": resolution.confidence_score,
                    "resolution_method": resolution.resolution_method,
                    "timestamp": resolution.timestamp.isoformat(),
                    "candidates": json.dumps(
                        [
                            {
                                "entity_id": c.entity_id,
                                "confidence_score": c.confidence_score,
                                "match_reasons": c.match_reasons,
                            }
                            for c in resolution.candidates[:3]  # Top 3 candidates
                        ]
                    ),
                }
            ]

            errors = self.bigquery_client.insert_rows_json(table_id, rows_to_insert)

            if errors:
                self.logger.error("Error storing resolution", errors=errors)
            else:
                self.logger.info(
                    "Stored entity resolution", address=resolution.input_address
                )

        except Exception as e:
            self.logger.error("Error storing resolution", error=str(e))


# Public behavioral-resolution interfaces; no cloud calls occur at import time.
import asyncio
import hashlib
import math
import joblib
from neo4j import GraphDatabase
from datetime import timezone
from services.ingestion.ethereum_ingester import field


class FeatureExtractor:
    def extract_features(self, data):
        tx_count = float(data.get("transaction_count", data.get("tx_count", 0)))
        volume = float(data.get("total_volume_eth", data.get("total_volume", 0)))
        counterparts = float(data.get("unique_counterparts", 0))
        if any(not math.isfinite(x) or x < 0 for x in [tx_count, volume, counterparts]):
            raise ValueError("Behavior statistics must be finite and nonnegative")
        first, last = data.get("first_seen"), data.get("last_seen")
        days = 0
        if first and last:

            def parse(v):
                return (
                    datetime.fromisoformat(v.replace("Z", "+00:00"))
                    if isinstance(v, str)
                    else v
                )

            days = (parse(last) - parse(first)).total_seconds() / 86400
            if days < 0:
                raise ValueError("first_seen must precede last_seen")
        return {
            "tx_frequency": tx_count / days if days else 0.0,
            "avg_tx_value": volume / tx_count if tx_count else 0.0,
            "network_centrality": (
                min(1.0, counterparts / tx_count) if tx_count else 0.0
            ),
            "activity_duration_days": days,
            "transaction_count": tx_count,
            "total_volume_eth": volume,
        }


class ConfidenceScorer:
    def calculate_confidence(self, data):
        weights = {
            "feature_similarity": 0.55,
            "transaction_overlap": 0.25,
            "temporal_correlation": 0.1,
            "gas_pattern_similarity": 0.1,
        }
        result = 0.0
        for name, weight in weights.items():
            value = float(data.get(name, 0))
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{name} must be between0 and1")
            result += value * weight
        return result


class GraphUpdater:
    def __init__(self, driver=None):
        self.driver = driver

    async def update_entity_graph(self, entity_data):
        identity = entity_data.get("entity_id")
        addresses = entity_data.get("addresses")
        confidence = float(entity_data.get("confidence", 0))
        if (
            not identity
            or not isinstance(addresses, list)
            or not addresses
            or not 0 <= confidence <= 1
        ):
            raise ValueError("Invalid entity graph candidate")
        if self.driver is None:
            self.driver = GraphDatabase.driver(
                os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
                auth=(
                    os.getenv("NEO4J_USER", "neo4j"),
                    os.getenv("NEO4J_PASSWORD", ""),
                ),
            )

        def update():
            with self.driver.session() as session:
                return session.run(
                    "MERGE (e:Entity {id:$id}) SET e.type=$type,e.confidence=$confidence,e.addresses=$addresses,e.resolution_method=$method,e.payload=$payload,e.labels=$labels,e.riskScore=$risk WITH e UNWIND $addresses AS address MERGE (a:Address {address:address}) MERGE (e)-[:HAS_ADDRESS]->(a) RETURN e",
                    id=identity,
                    type=entity_data.get("entity_type", "UNKNOWN"),
                    confidence=confidence,
                    method=entity_data.get("resolution_method", "behavioral_candidate"),
                    addresses=addresses,
                    payload=json.dumps(
                        {
                            "id": identity,
                            "type": entity_data.get("entity_type", "UNKNOWN"),
                            "addresses": addresses,
                            "confidence": confidence,
                            "labels": entity_data.get("labels", []),
                            "riskScore": None,
                            "createdAt": datetime.now(timezone.utc).isoformat(),
                            "updatedAt": datetime.now(timezone.utc).isoformat(),
                        },
                        allow_nan=False,
                    ),
                    labels=entity_data.get("labels", []),
                    risk=None,
                ).consume()

        await asyncio.to_thread(update)
        return entity_data

    def close(self):
        if self.driver:
            self.driver.close()


class EntityResolutionPipeline:
    """Generate explicit behavioral candidates from observations or a supplied model.

    A candidate is not a verified identity; model confidence requires a separately
    validated model. Missing data/model/provider failures propagate to the caller.
    """

    def __init__(
        self,
        model=None,
        model_path=None,
        data_provider=None,
        graph_updater=None,
        bigquery_client=None,
    ):
        path = model_path or os.getenv("ENTITY_MODEL_PATH")
        self.model = (
            model if model is not None else (joblib.load(path) if path else None)
        )
        self.data_provider = data_provider
        self.bigquery_client = bigquery_client
        self.graph_updater = graph_updater or GraphUpdater()
        self.extractor = FeatureExtractor()

    def _query_observations(self, addresses):
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project or not __import__("re").fullmatch(r"[A-Za-z0-9_-]+", project):
            raise RuntimeError(
                "A valid GOOGLE_CLOUD_PROJECT or explicit data_provider is required"
            )
        if self.bigquery_client is None:
            raise RuntimeError(
                "Provide observed data or an explicitly authenticated BigQuery client"
            )
        client = self.bigquery_client
        job = client.query(
            f"SELECT from_address AS address,COUNT(*) AS tx_count,SUM(value_eth) AS total_volume,COUNT(DISTINCT to_address) AS unique_counterparts,MIN(timestamp) AS first_seen,MAX(timestamp) AS last_seen FROM `{project}.onchain_data.curated_events` WHERE from_address IN UNNEST(@addresses) GROUP BY address",
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ArrayQueryParameter("addresses", "STRING", addresses)
                ]
            ),
        )
        rows = job.result(timeout=30)
        result = {}
        for row in rows:
            address = field(row, "address")
            if address:
                result[address] = {
                    "tx_count": field(row, "tx_count", 0),
                    "total_volume": field(row, "total_volume", 0),
                    "unique_counterparts": field(row, "unique_counterparts", 0),
                    "first_seen": field(row, "first_seen"),
                    "last_seen": field(row, "last_seen"),
                }
        return result

    async def resolve_entities(self, addresses):
        if (
            not isinstance(addresses, list)
            or not addresses
            or len(addresses) > 1000
            or any(not isinstance(a, str) or not a.strip() for a in addresses)
        ):
            raise ValueError("Provide between1 and1000 nonempty addresses")
        addresses = list(dict.fromkeys(addresses))
        observations = await asyncio.to_thread(
            self.data_provider or self._query_observations, addresses
        )
        if not isinstance(observations, dict) or any(
            address not in observations for address in addresses
        ):
            raise ValueError("Missing behavior observations for requested addresses")
        features = [self.extractor.extract_features(observations[a]) for a in addresses]
        vector = [
            [
                f[name]
                for name in [
                    "tx_frequency",
                    "avg_tx_value",
                    "network_centrality",
                    "activity_duration_days",
                    "transaction_count",
                    "total_volume_eth",
                ]
            ]
            for f in features
        ]
        if self.model is not None:
            predictions = await asyncio.to_thread(self.model.predict, vector)
            scores = [float(value) for value in predictions]
            if not scores or any(
                not math.isfinite(v) or not 0 <= v <= 1 for v in scores
            ):
                raise ValueError(
                    "Model must return finite confidence values between0 and1"
                )
            confidence = sum(scores) / len(scores)
            method = "supplied_model_candidate"
        else:
            # Compare observed count/value ratios. This is an explicit heuristic,
            # not inferred identity or a calibrated ML probability.
            pair = []
            for first in features:
                for second in features:
                    for name in ["transaction_count", "avg_tx_value"]:
                        denominator = max(first[name], second[name])
                        if denominator:
                            pair.append(min(first[name], second[name]) / denominator)
            confidence = min(0.8, sum(pair) / len(pair)) if pair else 0.0
            method = "behavioral_candidate"
        result = {
            "entity_id": "candidate-"
            + hashlib.sha256("|".join(sorted(addresses)).encode()).hexdigest()[:24],
            "addresses": addresses,
            "confidence": confidence,
            "entity_type": "UNKNOWN",
            "resolution_method": method,
            "verified_identity": False,
        }
        await self.graph_updater.update_entity_graph(result)
        return result


class VertexAIPipeline:
    """Submit an actual configured Vertex pipeline; submission is not completion."""

    def __init__(self, template_path=None):
        self.template_path = template_path or os.getenv("VERTEX_PIPELINE_TEMPLATE")

    async def run_entity_resolution_job(self, parameters):
        if not self.template_path:
            raise RuntimeError(
                "VERTEX_PIPELINE_TEMPLATE must name a real pipeline template"
            )
        job = aiplatform.PipelineJob(
            display_name="onchain-entity-resolution",
            template_path=self.template_path,
            parameter_values=parameters,
        )
        await asyncio.to_thread(job.submit)
        return {
            "job_id": str(job.resource_name),
            "status": "SUBMITTED",
            "completion_verified": False,
        }


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
