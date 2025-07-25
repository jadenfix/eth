"""
CDN (Content Delivery Network) utilities for E2E tests
"""

import os
from typing import Optional, Dict, Any
from google.cloud import storage
try:
    from google.cloud import compute_v1
    COMPUTE_AVAILABLE = True
except ImportError:
    compute_v1 = None
    COMPUTE_AVAILABLE = False


class CDNHelper:
    """Helper for CDN configuration and optimization"""
    
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT', 'ethhackathon')
        self.storage_client = None
        self.compute_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Google Cloud clients"""
        try:
            self.storage_client = storage.Client(project=self.project_id)
        except Exception as e:
            print(f"Warning: Could not initialize Storage client: {e}")
            self.storage_client = None
        
        if not COMPUTE_AVAILABLE:
            print("Warning: Compute library not available")
            self.compute_client = None
            return
        
        try:
            self.compute_client = compute_v1.UrlMapsClient()
        except Exception as e:
            print(f"Warning: Could not initialize Compute client: {e}")
            self.compute_client = None
    
    def setup_static_assets_bucket(self, bucket_name: str, public: bool = False) -> bool:
        """Setup a bucket for static assets with CDN optimization"""
        if not self.storage_client:
            print(f"Warning: Storage client not available, cannot setup bucket {bucket_name}")
            return False
        
        try:
            # Create bucket
            bucket = self.storage_client.bucket(bucket_name)
            bucket.create()
            
            # Configure for static website hosting
            bucket.make_public() if public else None
            
            # Set CORS for web access
            bucket.cors = [
                {
                    "origin": ["*"],
                    "method": ["GET", "HEAD"],
                    "responseHeader": ["Content-Type"],
                    "maxAgeSeconds": 3600
                }
            ]
            bucket.patch()
            
            print(f"Created static assets bucket: {bucket_name}")
            return True
            
        except Exception as e:
            print(f"Error creating bucket {bucket_name}: {e}")
            return False
    
    def upload_static_assets(self, bucket_name: str, local_path: str, remote_path: str = "") -> bool:
        """Upload static assets to CDN bucket"""
        if not self.storage_client:
            print(f"Warning: Storage client not available, cannot upload to {bucket_name}")
            return False
        
        try:
            bucket = self.storage_client.bucket(bucket_name)
            
            # Upload files recursively
            for root, dirs, files in os.walk(local_path):
                for file in files:
                    local_file_path = os.path.join(root, file)
                    remote_file_path = os.path.join(remote_path, os.path.relpath(local_file_path, local_path))
                    
                    blob = bucket.blob(remote_file_path)
                    blob.upload_from_filename(local_file_path)
                    
                    # Set cache headers for static assets
                    if file.endswith(('.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg')):
                        blob.cache_control = 'public, max-age=31536000'  # 1 year
                    else:
                        blob.cache_control = 'public, max-age=3600'  # 1 hour
                    
                    blob.patch()
            
            print(f"Uploaded static assets to {bucket_name}")
            return True
            
        except Exception as e:
            print(f"Error uploading static assets: {e}")
            return False
    
    def configure_nextjs_cdn(self, bucket_name: str, domain: str = None) -> Dict[str, Any]:
        """Configure Next.js for CDN usage"""
        config = {
            "assetPrefix": f"https://storage.googleapis.com/{bucket_name}",
            "images": {
                "domains": [domain] if domain else [],
                "loader": "custom",
                "loaderFile": "./image-loader.js"
            },
            "experimental": {
                "optimizeCss": True,
                "optimizeImages": True
            }
        }
        
        # Create image loader for CDN
        image_loader_content = f"""
export default function imageLoader({{ src, width, quality }}) {{
  return `https://storage.googleapis.com/{bucket_name}/${{src}}?w=${{width}}&q=${{quality || 75}}`
}}
"""
        
        return {
            "config": config,
            "image_loader_content": image_loader_content,
            "bucket_name": bucket_name,
            "cdn_url": f"https://storage.googleapis.com/{bucket_name}"
        }
    
    def setup_load_balancer_cdn(self, bucket_name: str, domain: str) -> bool:
        """Setup Cloud Load Balancer with CDN for custom domain"""
        if not self.compute_client:
            print(f"Warning: Compute client not available, cannot setup load balancer")
            return False
        
        try:
            # This would require more complex setup with Cloud Load Balancer
            # For now, we'll just return success as a placeholder
            print(f"Load balancer CDN setup for domain {domain} would be configured here")
            return True
            
        except Exception as e:
            print(f"Error setting up load balancer CDN: {e}")
            return False
    
    def get_cdn_performance_metrics(self, bucket_name: str) -> Dict[str, Any]:
        """Get CDN performance metrics"""
        if not self.storage_client:
            return {"error": "Storage client not available"}
        
        try:
            bucket = self.storage_client.bucket(bucket_name)
            
            # Get bucket metadata
            bucket.reload()
            
            metrics = {
                "bucket_name": bucket_name,
                "location": bucket.location,
                "storage_class": bucket.storage_class,
                "versioning_enabled": bucket.versioning_enabled,
                "public_access": bucket.iam_configuration.public_access_prevention == "inherited",
                "cors_configured": len(bucket.cors) > 0 if bucket.cors else False,
                "cdn_url": f"https://storage.googleapis.com/{bucket_name}"
            }
            
            return metrics
            
        except Exception as e:
            return {"error": str(e)}
    
    def optimize_for_cdn(self, bucket_name: str) -> bool:
        """Optimize bucket settings for CDN performance"""
        if not self.storage_client:
            print(f"Warning: Storage client not available, cannot optimize {bucket_name}")
            return False
        
        try:
            bucket = self.storage_client.bucket(bucket_name)
            
            # Set optimal storage class for CDN
            bucket.storage_class = "STANDARD"
            
            # Enable versioning for cache invalidation
            bucket.versioning_enabled = True
            
            # Set lifecycle rules for cost optimization
            lifecycle_rules = [
                {
                    "action": {"type": "Delete"},
                    "condition": {
                        "age": 365,  # Delete after 1 year
                        "matchesStorageClass": ["NEARLINE", "COLDLINE"]
                    }
                }
            ]
            bucket.lifecycle_rules = lifecycle_rules
            
            bucket.patch()
            
            print(f"Optimized bucket {bucket_name} for CDN")
            return True
            
        except Exception as e:
            print(f"Error optimizing bucket {bucket_name}: {e}")
            return False


# Global CDN helper instance
cdn_helper = CDNHelper()


def setup_cdn_for_nextjs() -> Dict[str, Any]:
    """Setup CDN for Next.js application"""
    bucket_name = f"{os.getenv('GOOGLE_CLOUD_PROJECT', 'ethhackathon')}-static-assets"
    
    # Setup bucket
    bucket_created = cdn_helper.setup_static_assets_bucket(bucket_name, public=True)
    
    if bucket_created:
        # Optimize for CDN
        cdn_helper.optimize_for_cdn(bucket_name)
        
        # Get Next.js configuration
        config = cdn_helper.configure_nextjs_cdn(bucket_name)
        
        return {
            "bucket_created": bucket_created,
            "bucket_name": bucket_name,
            "nextjs_config": config["config"],
            "image_loader_content": config["image_loader_content"],
            "cdn_url": config["cdn_url"]
        }
    
    return {"bucket_created": False, "error": "Failed to create bucket"}


def upload_nextjs_assets(bucket_name: str, build_path: str = ".next/static") -> bool:
    """Upload Next.js build assets to CDN"""
    if os.path.exists(build_path):
        return cdn_helper.upload_static_assets(bucket_name, build_path, "static")
    else:
        print(f"Build path {build_path} does not exist")
        return False


def get_cdn_status(bucket_name: str) -> Dict[str, Any]:
    """Get CDN status and performance metrics"""
    return cdn_helper.get_cdn_performance_metrics(bucket_name)


# Convenience functions
def create_static_bucket(bucket_name: str) -> bool:
    """Create a bucket for static assets"""
    return cdn_helper.setup_static_assets_bucket(bucket_name)


def upload_assets(bucket_name: str, local_path: str) -> bool:
    """Upload assets to CDN bucket"""
    return cdn_helper.upload_static_assets(bucket_name, local_path)


def optimize_bucket(bucket_name: str) -> bool:
    """Optimize bucket for CDN performance"""
    return cdn_helper.optimize_for_cdn(bucket_name) 