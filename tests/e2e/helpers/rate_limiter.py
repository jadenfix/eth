"""
Rate limiting utilities for E2E tests
"""

import time
from functools import wraps
from typing import Dict, Any, Optional


class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, calls_per_second: int = 10):
        self.calls_per_second = calls_per_second
        self.last_call_time = 0
        self.min_interval = 1.0 / calls_per_second
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            time_since_last = current_time - self.last_call_time
            
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                time.sleep(sleep_time)
            
            self.last_call_time = time.time()
            return func(*args, **kwargs)
        return wrapper


class APIRateLimiter:
    """API-specific rate limiter with different limits per endpoint"""
    
    def __init__(self):
        self.limits = {
            'bigquery': 5,  # 5 calls per second
            'neo4j': 10,    # 10 calls per second
            'pubsub': 20,   # 20 calls per second
            'vertex_ai': 2, # 2 calls per second (more expensive)
            'external_api': 1  # 1 call per second for external APIs
        }
        self.last_calls = {}
    
    def limit(self, api_type: str):
        """Decorator to limit calls to specific API type"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if api_type not in self.last_calls:
                    self.last_calls[api_type] = 0
                
                current_time = time.time()
                time_since_last = current_time - self.last_calls[api_type]
                min_interval = 1.0 / self.limits.get(api_type, 10)
                
                if time_since_last < min_interval:
                    sleep_time = min_interval - time_since_last
                    time.sleep(sleep_time)
                
                self.last_calls[api_type] = time.time()
                return func(*args, **kwargs)
            return wrapper
        return decorator


# Global rate limiter instances
rate_limiter = RateLimiter(calls_per_second=10)
api_rate_limiter = APIRateLimiter()


# Convenience decorators
def rate_limit(calls_per_second: int = 10):
    """Rate limit decorator"""
    return RateLimiter(calls_per_second)


def api_limit(api_type: str):
    """API-specific rate limit decorator"""
    return api_rate_limiter.limit(api_type)


# Example usage:
@rate_limit(calls_per_second=5)
def call_external_api(endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Example API call with rate limiting"""
    # API call implementation would go here
    return {"status": "success", "endpoint": endpoint}


@api_limit('bigquery')
def bigquery_query(query: str) -> Dict[str, Any]:
    """BigQuery query with rate limiting"""
    # BigQuery query implementation would go here
    return {"status": "success", "query": query}


@api_limit('neo4j')
def neo4j_query(query: str) -> Dict[str, Any]:
    """Neo4j query with rate limiting"""
    # Neo4j query implementation would go here
    return {"status": "success", "query": query} 