"""
Environment utilities for E2E tests.
Handles environment detection and service toggles.
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class EnvironmentManager:
    """Manages environment detection and service configuration for tests."""
    
    def __init__(self):
        self.env_file_path = Path("/Users/jadenfix/eth/.env")
        self._load_env_file()
    
    def _load_env_file(self):
        """Load environment variables from .env file."""
        if self.env_file_path.exists():
            with open(self.env_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
            logger.info(f"Loaded environment from {self.env_file_path}")
    
    def get_required_env_vars(self) -> Dict[str, str]:
        """Get all required environment variables."""
        required_vars = {
            # GCP
            'GOOGLE_CLOUD_PROJECT': os.getenv('GOOGLE_CLOUD_PROJECT'),
            'GOOGLE_APPLICATION_CREDENTIALS': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            
            # BigQuery
            'BIGQUERY_DATASET': os.getenv('BIGQUERY_DATASET'),
            'BIGQUERY_TABLE_RAW': os.getenv('BIGQUERY_TABLE_RAW'),
            'BIGQUERY_TABLE_CURATED': os.getenv('BIGQUERY_TABLE_CURATED'),
            
            # Pub/Sub
            'PUBSUB_TOPIC_RAW': os.getenv('PUBSUB_TOPIC_RAW'),
            'PUBSUB_TOPIC_SIGNALS': os.getenv('PUBSUB_TOPIC_SIGNALS'),
            
            # Neo4j
            'NEO4J_URI': os.getenv('NEO4J_URI'),
            'NEO4J_USER': os.getenv('NEO4J_USER'),
            'NEO4J_PASSWORD': os.getenv('NEO4J_PASSWORD'),
            
            # Vertex AI
            'VERTEX_AI_REGION': os.getenv('VERTEX_AI_REGION'),
            'VERTEX_AI_ENDPOINT': os.getenv('VERTEX_AI_ENDPOINT'),
            'VERTEX_AI_MODEL_NAME': os.getenv('VERTEX_AI_MODEL_NAME'),
            
            # ElevenLabs
            'ELEVENLABS_API_KEY': os.getenv('ELEVENLABS_API_KEY'),
            'ELEVENLABS_VOICE_ID': os.getenv('ELEVENLABS_VOICE_ID'),
            
            # Slack
            'SLACK_BOT_TOKEN': os.getenv('SLACK_BOT_TOKEN'),
            'SLACK_APP_TOKEN': os.getenv('SLACK_APP_TOKEN'),
            'SLACK_SIGNING_SECRET': os.getenv('SLACK_SIGNING_SECRET'),
            
            # Stripe
            'STRIPE_SECRET_KEY': os.getenv('STRIPE_SECRET_KEY'),
            'STRIPE_WEBHOOK_SECRET': os.getenv('STRIPE_WEBHOOK_SECRET'),
            
            # Dagster
            'DAGSTER_CLOUD_API_TOKEN': os.getenv('DAGSTER_CLOUD_API_TOKEN'),
            
            # Blockchain APIs
            'ALCHEMY_API_KEY': os.getenv('ALCHEMY_API_KEY'),
            'INFURA_PROJECT_ID': os.getenv('INFURA_PROJECT_ID'),
            'INFURA_API_SECRET': os.getenv('INFURA_API_SECRET'),
            'THEGRAPH_API_KEY': os.getenv('THEGRAPH_API_KEY'),
        }
        return required_vars
    
    def check_integration_ready(self) -> Dict[str, bool]:
        """Check if all required services are configured for integration tests."""
        env_vars = self.get_required_env_vars()
        service_status = {
            'gcp': bool(env_vars['GOOGLE_CLOUD_PROJECT'] and env_vars['GOOGLE_APPLICATION_CREDENTIALS']),
            'bigquery': bool(env_vars['BIGQUERY_DATASET'] and env_vars['BIGQUERY_TABLE_RAW']),
            'pubsub': bool(env_vars['PUBSUB_TOPIC_RAW'] and env_vars['PUBSUB_TOPIC_SIGNALS']),
            'neo4j': bool(env_vars['NEO4J_URI'] and env_vars['NEO4J_USER'] and env_vars['NEO4J_PASSWORD']),
            'vertex_ai': bool(env_vars['VERTEX_AI_REGION'] and env_vars['VERTEX_AI_ENDPOINT']),
            'elevenlabs': bool(env_vars['ELEVENLABS_API_KEY'] and env_vars['ELEVENLABS_VOICE_ID']),
            'slack': bool(env_vars['SLACK_BOT_TOKEN'] and env_vars['SLACK_APP_TOKEN']),
            'stripe': bool(env_vars['STRIPE_SECRET_KEY']),
            'dagster': bool(env_vars['DAGSTER_CLOUD_API_TOKEN']),
            'blockchain': bool(env_vars['ALCHEMY_API_KEY'] or env_vars['INFURA_PROJECT_ID']),
        }
        return service_status
    
    def should_use_mock(self, service: str) -> bool:
        """Determine if a service should use mock based on environment."""
        # Check if explicitly set to use mock
        mock_env_var = f"USE_MOCK_{service.upper()}"
        if os.getenv(mock_env_var, "0") == "1":
            return True
        
        # Check if service is not configured
        service_status = self.check_integration_ready()
        return not service_status.get(service, False)
    
    def get_service_config(self, service: str) -> Dict[str, Any]:
        """Get configuration for a specific service."""
        env_vars = self.get_required_env_vars()
        
        configs = {
            'gcp': {
                'project_id': env_vars['GOOGLE_CLOUD_PROJECT'],
                'credentials_path': env_vars['GOOGLE_APPLICATION_CREDENTIALS'],
            },
            'bigquery': {
                'dataset': env_vars['BIGQUERY_DATASET'],
                'raw_table': env_vars['BIGQUERY_TABLE_RAW'],
                'curated_table': env_vars['BIGQUERY_TABLE_CURATED'],
            },
            'pubsub': {
                'raw_topic': env_vars['PUBSUB_TOPIC_RAW'],
                'signals_topic': env_vars['PUBSUB_TOPIC_SIGNALS'],
            },
            'neo4j': {
                'uri': env_vars['NEO4J_URI'],
                'user': env_vars['NEO4J_USER'],
                'password': env_vars['NEO4J_PASSWORD'],
            },
            'vertex_ai': {
                'region': env_vars['VERTEX_AI_REGION'],
                'endpoint': env_vars['VERTEX_AI_ENDPOINT'],
                'model_name': env_vars['VERTEX_AI_MODEL_NAME'],
            },
            'elevenlabs': {
                'api_key': env_vars['ELEVENLABS_API_KEY'],
                'voice_id': env_vars['ELEVENLABS_VOICE_ID'],
            },
            'slack': {
                'bot_token': env_vars['SLACK_BOT_TOKEN'],
                'app_token': env_vars['SLACK_APP_TOKEN'],
                'signing_secret': env_vars['SLACK_SIGNING_SECRET'],
            },
            'stripe': {
                'secret_key': env_vars['STRIPE_SECRET_KEY'],
                'webhook_secret': env_vars['STRIPE_WEBHOOK_SECRET'],
            },
            'dagster': {
                'api_token': env_vars['DAGSTER_CLOUD_API_TOKEN'],
            },
            'blockchain': {
                'alchemy_key': env_vars['ALCHEMY_API_KEY'],
                'infura_project_id': env_vars['INFURA_PROJECT_ID'],
                'infura_secret': env_vars['INFURA_API_SECRET'],
                'thegraph_key': env_vars['THEGRAPH_API_KEY'],
            },
        }
        
        return configs.get(service, {})

# Global instance
env_manager = EnvironmentManager() 