"""
Circuit breaker utilities for E2E tests
"""

import time
from enum import Enum
from typing import Callable, Any, Optional, Dict
from functools import wraps


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, calls fail fast
    HALF_OPEN = "half_open"  # Testing if service is back


class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, 
                 failure_threshold: int = 5, 
                 timeout: int = 60,
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = CircuitState.CLOSED
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator to apply circuit breaker to a function"""
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise Exception(f"Circuit breaker is OPEN for {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                if self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                return result
            except self.expected_exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitState.OPEN
                raise e
        return wrapper
    
    def reset(self):
        """Reset circuit breaker to closed state"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
    
    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "time_since_last_failure": time.time() - self.last_failure_time
        }


class ServiceCircuitBreaker:
    """Circuit breaker for specific services"""
    
    def __init__(self):
        self.circuit_breakers = {}
    
    def get_circuit_breaker(self, service_name: str, **kwargs) -> CircuitBreaker:
        """Get or create circuit breaker for a service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(**kwargs)
        return self.circuit_breakers[service_name]
    
    def reset_service(self, service_name: str):
        """Reset circuit breaker for a specific service"""
        if service_name in self.circuit_breakers:
            self.circuit_breakers[service_name].reset()
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers"""
        return {
            service: cb.get_status() 
            for service, cb in self.circuit_breakers.items()
        }


# Global service circuit breaker instance
service_circuit_breaker = ServiceCircuitBreaker()


def circuit_break(service_name: str, **kwargs):
    """Decorator to apply circuit breaker to a service function"""
    def decorator(func: Callable) -> Callable:
        cb = service_circuit_breaker.get_circuit_breaker(service_name, **kwargs)
        return cb(func)
    return decorator


# Example usage:
@circuit_break('bigquery', failure_threshold=3, timeout=30)
def bigquery_operation(query: str) -> Dict[str, Any]:
    """BigQuery operation with circuit breaker"""
    # BigQuery operation implementation would go here
    return {"status": "success", "query": query}


@circuit_break('neo4j', failure_threshold=5, timeout=60)
def neo4j_operation(query: str) -> Dict[str, Any]:
    """Neo4j operation with circuit breaker"""
    # Neo4j operation implementation would go here
    return {"status": "success", "query": query}


@circuit_break('external_api', failure_threshold=2, timeout=120)
def external_api_call(endpoint: str) -> Dict[str, Any]:
    """External API call with circuit breaker"""
    # External API call implementation would go here
    return {"status": "success", "endpoint": endpoint}


# Utility functions
def reset_all_circuit_breakers():
    """Reset all circuit breakers"""
    for service_name in service_circuit_breaker.circuit_breakers:
        service_circuit_breaker.reset_service(service_name)


def get_circuit_breaker_status() -> Dict[str, Dict[str, Any]]:
    """Get status of all circuit breakers"""
    return service_circuit_breaker.get_all_status()


def is_service_available(service_name: str) -> bool:
    """Check if a service is available (circuit breaker not open)"""
    if service_name not in service_circuit_breaker.circuit_breakers:
        return True  # No circuit breaker means service is available
    
    cb = service_circuit_breaker.circuit_breakers[service_name]
    return cb.state != CircuitState.OPEN 