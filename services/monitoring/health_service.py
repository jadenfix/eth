"""
System Health and Monitoring Service.

Provides comprehensive health checks, performance metrics, and 
operational insights for the blockchain intelligence platform.
"""

import os
import asyncio
import json
import time
import logging
import psutil
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

import structlog
import aiohttp
import aioredis
from google.cloud import bigquery
from google.cloud import monitoring_v3
from prometheus_client import start_http_server, Counter, Histogram, Gauge

# Configure structured logging
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


class HealthStatus(Enum):
    """Health check status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class ServiceType(Enum):
    """Types of services to monitor."""
    INGESTER = "ingester"
    API = "api"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    ML_SERVICE = "ml_service"
    EXTERNAL_API = "external_api"


@dataclass
class HealthCheck:
    """Health check result."""
    service_name: str
    service_type: ServiceType
    status: HealthStatus
    response_time_ms: float
    message: str
    metadata: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        data['service_type'] = self.service_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass 
class SystemMetrics:
    """System performance metrics."""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Tuple[int, int]  # bytes_sent, bytes_recv
    active_connections: int
    timestamp: datetime


@dataclass
class ServiceMetrics:
    """Service-specific metrics."""
    service_name: str
    requests_per_second: float
    avg_response_time_ms: float
    error_rate_percent: float
    active_connections: int
    queue_size: int
    uptime_seconds: int
    timestamp: datetime


# Prometheus metrics
REQUEST_COUNT = Counter('service_requests_total', 'Total requests', ['service', 'method', 'status'])
REQUEST_DURATION = Histogram('service_request_duration_seconds', 'Request duration', ['service', 'method'])
ACTIVE_CONNECTIONS = Gauge('service_active_connections', 'Active connections', ['service'])
QUEUE_SIZE = Gauge('service_queue_size', 'Queue size', ['service', 'queue_type'])
SYSTEM_CPU = Gauge('system_cpu_percent', 'CPU usage percentage')
SYSTEM_MEMORY = Gauge('system_memory_percent', 'Memory usage percentage')
SYSTEM_DISK = Gauge('system_disk_percent', 'Disk usage percentage')


class HealthChecker:
    """Performs health checks on various services."""
    
    def __init__(self):
        self.logger = logger.bind(service="health-checker")
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def check_http_service(self, name: str, url: str, 
                                service_type: ServiceType = ServiceType.API) -> HealthCheck:
        """Check HTTP service health."""
        start_time = time.time()
        
        try:
            async with self.session.get(f"{url}/health") as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    status = HealthStatus.HEALTHY
                    message = "Service is healthy"
                    metadata = data
                else:
                    status = HealthStatus.UNHEALTHY
                    message = f"HTTP {response.status}"
                    metadata = {"status_code": response.status}
                    
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            status = HealthStatus.UNHEALTHY
            message = "Request timeout"
            metadata = {"timeout": True}
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            status = HealthStatus.CRITICAL
            message = f"Connection failed: {str(e)}"
            metadata = {"error": str(e)}
        
        return HealthCheck(
            service_name=name,
            service_type=service_type,
            status=status,
            response_time_ms=response_time,
            message=message,
            metadata=metadata,
            timestamp=datetime.now()
        )
    
    async def check_bigquery(self) -> HealthCheck:
        """Check BigQuery health."""
        start_time = time.time()
        
        try:
            client = bigquery.Client()
            
            # Simple query to test connection
            query = "SELECT 1 as test"
            job = client.query(query)
            results = list(job.result())
            
            response_time = (time.time() - start_time) * 1000
            
            if len(results) == 1:
                status = HealthStatus.HEALTHY
                message = "BigQuery connection successful"
                metadata = {"query_time_ms": response_time}
            else:
                status = HealthStatus.DEGRADED
                message = "Unexpected query result"
                metadata = {"result_count": len(results)}
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            status = HealthStatus.CRITICAL
            message = f"BigQuery error: {str(e)}"
            metadata = {"error": str(e)}
        
        return HealthCheck(
            service_name="bigquery",
            service_type=ServiceType.DATABASE,
            status=status,
            response_time_ms=response_time,
            message=message,
            metadata=metadata,
            timestamp=datetime.now()
        )
    
    async def check_redis(self, redis_url: str) -> HealthCheck:
        """Check Redis health."""
        start_time = time.time()
        
        try:
            redis = aioredis.from_url(redis_url)
            
            # Test connection with ping
            await redis.ping()
            
            # Test set/get
            test_key = "health_check"
            await redis.set(test_key, "ok", ex=10)
            result = await redis.get(test_key)
            
            await redis.close()
            
            response_time = (time.time() - start_time) * 1000
            
            if result == b"ok":
                status = HealthStatus.HEALTHY
                message = "Redis connection successful"
                metadata = {"ping_time_ms": response_time}
            else:
                status = HealthStatus.DEGRADED
                message = "Redis set/get failed"
                metadata = {"result": result}
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            status = HealthStatus.CRITICAL
            message = f"Redis error: {str(e)}"
            metadata = {"error": str(e)}
        
        return HealthCheck(
            service_name="redis",
            service_type=ServiceType.DATABASE,
            status=status,
            response_time_ms=response_time,
            message=message,
            metadata=metadata,
            timestamp=datetime.now()
        )
    
    async def check_external_api(self, name: str, url: str, api_key: str = None) -> HealthCheck:
        """Check external API health."""
        start_time = time.time()
        
        headers = {}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        try:
            async with self.session.get(url, headers=headers) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status in [200, 201]:
                    status = HealthStatus.HEALTHY
                    message = "External API accessible"
                    metadata = {"status_code": response.status}
                elif response.status in [429, 503]:
                    status = HealthStatus.DEGRADED
                    message = "API rate limited or temporarily unavailable"
                    metadata = {"status_code": response.status}
                else:
                    status = HealthStatus.UNHEALTHY
                    message = f"API returned {response.status}"
                    metadata = {"status_code": response.status}
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            status = HealthStatus.CRITICAL
            message = f"API connection failed: {str(e)}"
            metadata = {"error": str(e)}
        
        return HealthCheck(
            service_name=name,
            service_type=ServiceType.EXTERNAL_API,
            status=status,
            response_time_ms=response_time,
            message=message,
            metadata=metadata,
            timestamp=datetime.now()
        )


class MetricsCollector:
    """Collects system and service metrics."""
    
    def __init__(self):
        self.logger = logger.bind(service="metrics-collector")
        self._start_time = time.time()
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect system-level metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        # Network I/O
        net_io = psutil.net_io_counters()
        network_io = (net_io.bytes_sent, net_io.bytes_recv)
        
        # Active connections
        connections = psutil.net_connections()
        active_connections = len([c for c in connections if c.status == 'ESTABLISHED'])
        
        # Update Prometheus metrics
        SYSTEM_CPU.set(cpu_percent)
        SYSTEM_MEMORY.set(memory_percent)
        SYSTEM_DISK.set(disk_percent)
        
        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_percent=disk_percent,
            network_io=network_io,
            active_connections=active_connections,
            timestamp=datetime.now()
        )
    
    def collect_service_metrics(self, service_name: str) -> ServiceMetrics:
        """Collect service-specific metrics."""
        # In a real implementation, these would come from actual service monitoring
        
        uptime_seconds = int(time.time() - self._start_time)
        
        # Mock metrics - in production these would be real
        return ServiceMetrics(
            service_name=service_name,
            requests_per_second=10.5,
            avg_response_time_ms=250.0,
            error_rate_percent=2.1,
            active_connections=45,
            queue_size=12,
            uptime_seconds=uptime_seconds,
            timestamp=datetime.now()
        )


class AlertManager:
    """Manages health-based alerting."""
    
    def __init__(self):
        self.logger = logger.bind(service="alert-manager")
        self.alert_rules: List[Dict[str, Any]] = []
        self.alert_history: List[Dict[str, Any]] = []
    
    def add_alert_rule(self, rule: Dict[str, Any]):
        """Add an alert rule."""
        self.alert_rules.append(rule)
        self.logger.info("Added alert rule", rule=rule)
    
    def evaluate_health_check(self, health_check: HealthCheck) -> List[Dict[str, Any]]:
        """Evaluate health check against alert rules."""
        alerts = []
        
        for rule in self.alert_rules:
            if self._matches_rule(health_check, rule):
                alert = {
                    "rule_name": rule["name"],
                    "service": health_check.service_name,
                    "severity": rule["severity"],
                    "message": self._format_alert_message(health_check, rule),
                    "timestamp": datetime.now().isoformat(),
                    "health_check": health_check.to_dict()
                }
                
                alerts.append(alert)
                self.alert_history.append(alert)
                
                self.logger.warning("Health alert triggered",
                                  rule=rule["name"],
                                  service=health_check.service_name,
                                  status=health_check.status.value)
        
        return alerts
    
    def _matches_rule(self, health_check: HealthCheck, rule: Dict[str, Any]) -> bool:
        """Check if health check matches alert rule."""
        # Service name match
        if rule.get("service_pattern") and rule["service_pattern"] not in health_check.service_name:
            return False
        
        # Status condition
        if rule.get("status") and health_check.status != HealthStatus(rule["status"]):
            return False
        
        # Response time threshold
        if rule.get("response_time_threshold_ms"):
            if health_check.response_time_ms < rule["response_time_threshold_ms"]:
                return False
        
        # Service type match
        if rule.get("service_types"):
            if health_check.service_type not in [ServiceType(st) for st in rule["service_types"]]:
                return False
        
        return True
    
    def _format_alert_message(self, health_check: HealthCheck, rule: Dict[str, Any]) -> str:
        """Format alert message."""
        template = rule.get("message_template", 
                          "Service {service} is {status}: {message}")
        
        return template.format(
            service=health_check.service_name,
            status=health_check.status.value,
            message=health_check.message,
            response_time=health_check.response_time_ms
        )


class HealthMonitoringService:
    """Main health monitoring service."""
    
    def __init__(self):
        self.logger = logger.bind(service="health-monitoring")
        self.health_checker = HealthChecker()
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        
        # Service registry
        self.services = {
            "ethereum-ingester": {
                "url": "http://localhost:8001",
                "type": ServiceType.INGESTER
            },
            "graph-api": {
                "url": "http://localhost:8002", 
                "type": ServiceType.API
            },
            "mev-agent": {
                "url": "http://localhost:8003",
                "type": ServiceType.ML_SERVICE
            }
        }
        
        # External APIs to monitor
        self.external_apis = {
            "ethereum-rpc": {
                "url": os.getenv('ETHEREUM_RPC_URL', 'https://eth.public.blastapi.io'),
                "api_key": os.getenv('ETHEREUM_API_KEY')
            },
            "coingecko": {
                "url": "https://api.coingecko.com/api/v3/ping",
                "api_key": None
            }
        }
        
        # Set up default alert rules
        self._setup_default_alerts()
        
        # Background tasks
        self._monitoring_task: Optional[asyncio.Task] = None
        self._metrics_task: Optional[asyncio.Task] = None
    
    def _setup_default_alerts(self):
        """Set up default alerting rules."""
        rules = [
            {
                "name": "service_critical",
                "status": "critical",
                "severity": "critical",
                "message_template": "CRITICAL: {service} is down - {message}"
            },
            {
                "name": "service_unhealthy", 
                "status": "unhealthy",
                "severity": "warning",
                "message_template": "WARNING: {service} is unhealthy - {message}"
            },
            {
                "name": "slow_response",
                "response_time_threshold_ms": 5000,
                "severity": "warning",
                "message_template": "WARNING: {service} slow response time ({response_time:.0f}ms)"
            },
            {
                "name": "external_api_down",
                "service_types": ["external_api"],
                "status": "critical",
                "severity": "warning",
                "message_template": "External API {service} is unavailable"
            }
        ]
        
        for rule in rules:
            self.alert_manager.add_alert_rule(rule)
    
    async def start(self):
        """Start health monitoring service."""
        self.logger.info("Starting health monitoring service")
        
        # Start Prometheus metrics server
        start_http_server(8000)
        self.logger.info("Started Prometheus metrics server on port 8000")
        
        # Start background monitoring tasks
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._metrics_task = asyncio.create_task(self._metrics_loop())
    
    async def stop(self):
        """Stop health monitoring service."""
        self.logger.info("Stopping health monitoring service")
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
        
        if self._metrics_task:
            self._metrics_task.cancel()
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        async with self.health_checker:
            while True:
                try:
                    # Check internal services
                    for service_name, config in self.services.items():
                        health_check = await self.health_checker.check_http_service(
                            service_name,
                            config["url"],
                            config["type"]
                        )
                        
                        # Evaluate alerts
                        alerts = self.alert_manager.evaluate_health_check(health_check)
                        
                        # Log health status
                        self.logger.info("Service health check",
                                       service=service_name,
                                       status=health_check.status.value,
                                       response_time=health_check.response_time_ms)
                    
                    # Check external APIs
                    for api_name, config in self.external_apis.items():
                        health_check = await self.health_checker.check_external_api(
                            api_name,
                            config["url"],
                            config.get("api_key")
                        )
                        
                        alerts = self.alert_manager.evaluate_health_check(health_check)
                    
                    # Check BigQuery
                    bq_health = await self.health_checker.check_bigquery()
                    alerts = self.alert_manager.evaluate_health_check(bq_health)
                    
                    # Check Redis if configured
                    redis_url = os.getenv('REDIS_URL')
                    if redis_url:
                        redis_health = await self.health_checker.check_redis(redis_url)
                        alerts = self.alert_manager.evaluate_health_check(redis_health)
                    
                    # Wait before next check
                    await asyncio.sleep(30)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error("Error in monitoring loop", error=str(e))
                    await asyncio.sleep(10)
    
    async def _metrics_loop(self):
        """Metrics collection loop."""
        while True:
            try:
                # Collect system metrics
                system_metrics = self.metrics_collector.collect_system_metrics()
                
                self.logger.info("System metrics collected",
                               cpu_percent=system_metrics.cpu_percent,
                               memory_percent=system_metrics.memory_percent,
                               disk_percent=system_metrics.disk_percent,
                               active_connections=system_metrics.active_connections)
                
                # Collect service metrics
                for service_name in self.services.keys():
                    service_metrics = self.metrics_collector.collect_service_metrics(service_name)
                    
                    # Update Prometheus metrics
                    ACTIVE_CONNECTIONS.labels(service=service_name).set(
                        service_metrics.active_connections
                    )
                    QUEUE_SIZE.labels(service=service_name, queue_type="main").set(
                        service_metrics.queue_size
                    )
                
                # Wait before next collection
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Error in metrics loop", error=str(e))
                await asyncio.sleep(10)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": int(time.time() - self.metrics_collector._start_time),
            "services_monitored": len(self.services),
            "external_apis_monitored": len(self.external_apis),
            "recent_alerts": len([a for a in self.alert_manager.alert_history 
                                if datetime.fromisoformat(a['timestamp']) > 
                                datetime.now() - timedelta(hours=1)])
        }


async def main():
    """Main entry point for health monitoring service."""
    service = HealthMonitoringService()
    
    try:
        await service.start()
        
        # Run indefinitely
        while True:
            await asyncio.sleep(3600)
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
