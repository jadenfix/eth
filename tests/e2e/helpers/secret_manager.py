"""
Secret Manager utilities for E2E tests
"""

import os
from typing import Optional, Dict, Any
from google.cloud import secretmanager


class SecretManagerHelper:
    """Helper for Google Secret Manager operations"""
    
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT', 'ethhackathon')
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Secret Manager client"""
        try:
            self.client = secretmanager.SecretManagerServiceClient()
        except Exception as e:
            print(f"Warning: Could not initialize Secret Manager client: {e}")
            self.client = None
    
    def get_secret(self, secret_id: str) -> Optional[str]:
        """Retrieve secret from Google Secret Manager"""
        if not self.client:
            print(f"Warning: Secret Manager not available, using environment variable for {secret_id}")
            return os.getenv(secret_id)
        
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/latest"
            response = self.client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            print(f"Warning: Could not retrieve secret {secret_id}: {e}")
            return os.getenv(secret_id)
    
    def create_secret(self, secret_id: str, secret_value: str) -> bool:
        """Create a new secret in Secret Manager"""
        if not self.client:
            print(f"Warning: Secret Manager not available, cannot create {secret_id}")
            return False
        
        try:
            parent = f"projects/{self.project_id}"
            
            # Create the secret
            secret = secretmanager.Secret()
            secret.replication.automatic = secretmanager.Replication.Automatic()
            
            secret_path = self.client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_id,
                    "secret": secret,
                }
            )
            
            # Add the secret version
            secret_version = self.client.add_secret_version(
                request={
                    "parent": secret_path.name,
                    "payload": secretmanager.SecretPayload(data=secret_value.encode("UTF-8")),
                }
            )
            
            print(f"Created secret: {secret_version.name}")
            return True
            
        except Exception as e:
            print(f"Error creating secret {secret_id}: {e}")
            return False
    
    def update_secret(self, secret_id: str, secret_value: str) -> bool:
        """Update an existing secret in Secret Manager"""
        if not self.client:
            print(f"Warning: Secret Manager not available, cannot update {secret_id}")
            return False
        
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}"
            
            # Add new version
            secret_version = self.client.add_secret_version(
                request={
                    "parent": name,
                    "payload": secretmanager.SecretPayload(data=secret_value.encode("UTF-8")),
                }
            )
            
            print(f"Updated secret: {secret_version.name}")
            return True
            
        except Exception as e:
            print(f"Error updating secret {secret_id}: {e}")
            return False
    
    def delete_secret(self, secret_id: str) -> bool:
        """Delete a secret from Secret Manager"""
        if not self.client:
            print(f"Warning: Secret Manager not available, cannot delete {secret_id}")
            return False
        
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}"
            self.client.delete_secret(request={"name": name})
            print(f"Deleted secret: {secret_id}")
            return True
            
        except Exception as e:
            print(f"Error deleting secret {secret_id}: {e}")
            return False
    
    def list_secrets(self) -> list:
        """List all secrets in the project"""
        if not self.client:
            print("Warning: Secret Manager not available")
            return []
        
        try:
            parent = f"projects/{self.project_id}"
            secrets = []
            
            for secret in self.client.list_secrets(request={"parent": parent}):
                secrets.append(secret.name.split("/")[-1])
            
            return secrets
            
        except Exception as e:
            print(f"Error listing secrets: {e}")
            return []


# Global secret manager instance
secret_manager = SecretManagerHelper()


def get_secret(secret_id: str) -> Optional[str]:
    """Convenience function to get a secret"""
    return secret_manager.get_secret(secret_id)


def create_secret(secret_id: str, secret_value: str) -> bool:
    """Convenience function to create a secret"""
    return secret_manager.create_secret(secret_id, secret_value)


def update_secret(secret_id: str, secret_value: str) -> bool:
    """Convenience function to update a secret"""
    return secret_manager.update_secret(secret_id, secret_value)


def delete_secret(secret_id: str) -> bool:
    """Convenience function to delete a secret"""
    return secret_manager.delete_secret(secret_id)


def list_secrets() -> list:
    """Convenience function to list secrets"""
    return secret_manager.list_secrets()


# Example usage for common secrets
def get_api_key(service: str) -> Optional[str]:
    """Get API key for a specific service"""
    secret_mapping = {
        'elevenlabs': 'ELEVENLABS_API_KEY',
        'slack': 'SLACK_BOT_TOKEN',
        'stripe': 'STRIPE_SECRET_KEY',
        'alchemy': 'ALCHEMY_API_KEY',
        'infura': 'INFURA_PROJECT_ID',
        'neo4j': 'NEO4J_PASSWORD'
    }
    
    secret_id = secret_mapping.get(service.lower())
    if secret_id:
        return get_secret(secret_id)
    
    return None


def migrate_env_to_secrets() -> Dict[str, bool]:
    """Migrate environment variables to Secret Manager"""
    env_secrets = {
        'ELEVENLABS_API_KEY': os.getenv('ELEVENLABS_API_KEY'),
        'SLACK_BOT_TOKEN': os.getenv('SLACK_BOT_TOKEN'),
        'STRIPE_SECRET_KEY': os.getenv('STRIPE_SECRET_KEY'),
        'ALCHEMY_API_KEY': os.getenv('ALCHEMY_API_KEY'),
        'INFURA_PROJECT_ID': os.getenv('INFURA_PROJECT_ID'),
        'NEO4J_PASSWORD': os.getenv('NEO4J_PASSWORD'),
        'DAGSTER_CLOUD_API_TOKEN': os.getenv('DAGSTER_CLOUD_API_TOKEN')
    }
    
    results = {}
    for secret_id, value in env_secrets.items():
        if value and not value.startswith('your-') and not value.startswith('sk_test_'):
            results[secret_id] = create_secret(secret_id, value)
        else:
            results[secret_id] = False
    
    return results 