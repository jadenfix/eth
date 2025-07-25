"""
CMEK (Customer Managed Encryption Keys) utilities for E2E tests
"""

import os
from typing import Optional, Dict, Any
try:
    from google.cloud import kms_v1
    KMS_AVAILABLE = True
except ImportError:
    kms_v1 = None
    KMS_AVAILABLE = False
from google.cloud import bigquery
from google.cloud import storage


class CMEKHelper:
    """Helper for Customer Managed Encryption Keys"""
    
    def __init__(self, project_id: Optional[str] = None, location: str = "us-central1"):
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT', 'ethhackathon')
        self.location = location
        self.kms_client = None
        self._initialize_kms_client()
    
    def _initialize_kms_client(self):
        """Initialize KMS client"""
        if not KMS_AVAILABLE:
            print("Warning: KMS library not available")
            self.kms_client = None
            return
        
        try:
            self.kms_client = kms_v1.KeyManagementServiceClient()
        except Exception as e:
            print(f"Warning: Could not initialize KMS client: {e}")
            self.kms_client = None
    
    def create_keyring(self, keyring_id: str) -> Optional[str]:
        """Create a new keyring"""
        if not self.kms_client:
            print(f"Warning: KMS not available, cannot create keyring {keyring_id}")
            return None
        
        try:
            parent = f"projects/{self.project_id}/locations/{self.location}"
            keyring_path = f"{parent}/keyRings/{keyring_id}"
            
            # Create the keyring
            keyring = kms_v1.KeyRing()
            keyring = self.kms_client.create_keyring(
                request={
                    "parent": parent,
                    "keyring_id": keyring_id,
                    "keyring": keyring,
                }
            )
            
            print(f"Created keyring: {keyring.name}")
            return keyring.name
            
        except Exception as e:
            print(f"Error creating keyring {keyring_id}: {e}")
            return None
    
    def create_key(self, keyring_id: str, key_id: str, purpose: str = "ENCRYPT_DECRYPT") -> Optional[str]:
        """Create a new encryption key"""
        if not self.kms_client:
            print(f"Warning: KMS not available, cannot create key {key_id}")
            return None
        
        try:
            keyring_path = f"projects/{self.project_id}/locations/{self.location}/keyRings/{keyring_id}"
            
            # Create the key
            key = kms_v1.CryptoKey()
            key.purpose = kms_v1.CryptoKey.CryptoKeyPurpose.ENCRYPT_DECRYPT
            
            # Create the key version
            crypto_key = self.kms_client.create_crypto_key(
                request={
                    "parent": keyring_path,
                    "crypto_key_id": key_id,
                    "crypto_key": key,
                }
            )
            
            print(f"Created key: {crypto_key.name}")
            return crypto_key.name
            
        except Exception as e:
            print(f"Error creating key {key_id}: {e}")
            return None
    
    def get_key_path(self, keyring_id: str, key_id: str) -> str:
        """Get the full path for a key"""
        return f"projects/{self.project_id}/locations/{self.location}/keyRings/{keyring_id}/cryptoKeys/{key_id}"
    
    def enable_bigquery_cmek(self, dataset_id: str, key_path: str) -> bool:
        """Enable CMEK for BigQuery dataset"""
        try:
            client = bigquery.Client(project=self.project_id)
            
            # Get the dataset
            dataset_ref = client.dataset(dataset_id)
            dataset = client.get_dataset(dataset_ref)
            
            # Update dataset with CMEK
            dataset.default_encryption_configuration = bigquery.EncryptionConfiguration(
                kms_key_name=key_path
            )
            
            # Update the dataset
            updated_dataset = client.update_dataset(dataset, ["default_encryption_configuration"])
            
            print(f"Enabled CMEK for BigQuery dataset: {dataset_id}")
            return True
            
        except Exception as e:
            print(f"Error enabling CMEK for BigQuery dataset {dataset_id}: {e}")
            return False
    
    def enable_storage_cmek(self, bucket_name: str, key_path: str) -> bool:
        """Enable CMEK for Cloud Storage bucket"""
        try:
            client = storage.Client(project=self.project_id)
            bucket = client.bucket(bucket_name)
            
            # Update bucket with CMEK
            bucket.default_kms_key_name = key_path
            bucket.patch()
            
            print(f"Enabled CMEK for Cloud Storage bucket: {bucket_name}")
            return True
            
        except Exception as e:
            print(f"Error enabling CMEK for Cloud Storage bucket {bucket_name}: {e}")
            return False
    
    def list_keys(self, keyring_id: str) -> list:
        """List all keys in a keyring"""
        if not self.kms_client:
            print("Warning: KMS not available")
            return []
        
        try:
            keyring_path = f"projects/{self.project_id}/locations/{self.location}/keyRings/{keyring_id}"
            keys = []
            
            for key in self.kms_client.list_crypto_keys(request={"parent": keyring_path}):
                keys.append(key.name.split("/")[-1])
            
            return keys
            
        except Exception as e:
            print(f"Error listing keys: {e}")
            return []
    
    def rotate_key(self, keyring_id: str, key_id: str) -> bool:
        """Rotate a key (create new version)"""
        if not self.kms_client:
            print(f"Warning: KMS not available, cannot rotate key {key_id}")
            return False
        
        try:
            key_path = self.get_key_path(keyring_id, key_id)
            
            # Create new version
            crypto_key_version = kms_v1.CryptoKeyVersion()
            crypto_key_version.state = kms_v1.CryptoKeyVersion.CryptoKeyVersionState.ENABLED
            
            version = self.kms_client.create_crypto_key_version(
                request={
                    "parent": key_path,
                    "crypto_key_version": crypto_key_version,
                }
            )
            
            print(f"Rotated key: {version.name}")
            return True
            
        except Exception as e:
            print(f"Error rotating key {key_id}: {e}")
            return False


# Global CMEK helper instance
cmek_helper = CMEKHelper()


def setup_cmek_for_project() -> Dict[str, bool]:
    """Setup CMEK for the entire project"""
    results = {}
    
    # Create keyring and key
    keyring_id = "bigquery-keyring"
    key_id = "bigquery-key"
    
    # Create keyring
    keyring_path = cmek_helper.create_keyring(keyring_id)
    results["keyring_created"] = keyring_path is not None
    
    if keyring_path:
        # Create key
        key_path = cmek_helper.create_key(keyring_id, key_id)
        results["key_created"] = key_path is not None
        
        if key_path:
            # Enable CMEK for BigQuery
            dataset_id = os.getenv('BIGQUERY_DATASET', 'onchain_data')
            results["bigquery_cmek_enabled"] = cmek_helper.enable_bigquery_cmek(dataset_id, key_path)
            
            # Enable CMEK for Cloud Storage (if needed)
            bucket_name = f"{os.getenv('GOOGLE_CLOUD_PROJECT', 'ethhackathon')}-dataflow-temp"
            results["storage_cmek_enabled"] = cmek_helper.enable_storage_cmek(bucket_name, key_path)
    
    return results


def get_cmek_status() -> Dict[str, Any]:
    """Get CMEK status for the project"""
    keyring_id = "bigquery-keyring"
    
    return {
        "project_id": cmek_helper.project_id,
        "location": cmek_helper.location,
        "keyring_id": keyring_id,
        "keys": cmek_helper.list_keys(keyring_id),
        "kms_available": cmek_helper.kms_client is not None
    }


# Convenience functions
def create_keyring(keyring_id: str) -> Optional[str]:
    """Create a keyring"""
    return cmek_helper.create_keyring(keyring_id)


def create_key(keyring_id: str, key_id: str) -> Optional[str]:
    """Create a key"""
    return cmek_helper.create_key(keyring_id, key_id)


def enable_bigquery_cmek(dataset_id: str, key_path: str) -> bool:
    """Enable CMEK for BigQuery"""
    return cmek_helper.enable_bigquery_cmek(dataset_id, key_path)


def enable_storage_cmek(bucket_name: str, key_path: str) -> bool:
    """Enable CMEK for Cloud Storage"""
    return cmek_helper.enable_storage_cmek(bucket_name, key_path) 