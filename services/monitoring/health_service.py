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
from datetime import datetime, timedelta, timezone
from enum import Enum

import structlog
import aiohttp
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
    UNKNOWN = "unknown"
    UNCONFIGURED = "unconfigured"
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
    active_connections: Optional[int]
    queue_size: Optional[int]
    uptime_seconds: int
    timestamp: datetime
    observed_requests: int = 0


# Prometheus metrics
REQUEST_COUNT = Counter('service_requests_total', 'Total requests', ['service', 'method', 'status'])
REQUEST_DURATION = Histogram('service_request_duration_seconds', 'Request duration', ['service', 'method'])
ACTIVE_CONNECTIONS = Gauge('service_active_connections', 'Active connections', ['service'])
QUEUE_SIZE = Gauge('service_queue_size', 'Queue size', ['service', 'queue_type'])
SYSTEM_CPU = Gauge('system_cpu_percent', 'CPU usage percentage')
SYSTEM_MEMORY = Gauge('system_memory_percent', 'Memory usage percentage')
SYSTEM_DISK = Gauge('system_disk_percent', 'Disk usage percentage')


class HealthChecker:
    """Explicit dependency probes. Construction never discovers credentials."""
    def __init__(self, bigquery_client=None, redis_client=None, timeout_seconds=10):
        self.bigquery_client = bigquery_client
        self.redis_client = redis_client
        self.timeout_seconds = timeout_seconds
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout_seconds))
        return self

    async def __aexit__(self, *args):
        if self.session is not None:
            await self.session.close()
            self.session = None

    def _result(self, name, service_type, status, started, message, metadata=None):
        return HealthCheck(name, service_type, status, (time.monotonic()-started)*1000,
                           message, metadata or {}, datetime.now(timezone.utc))

    async def check_http_service(self, name, url, service_type=ServiceType.API):
        started = time.monotonic()
        if not url:
            return self._result(name, service_type, HealthStatus.UNCONFIGURED, started, 'URL not configured')
        if self.session is None:
            return self._result(name, service_type, HealthStatus.UNKNOWN, started, 'HTTP session not started')
        try:
            async with self.session.get(url.rstrip('/')+'/health') as response:
                if response.status != 200:
                    return self._result(name, service_type, HealthStatus.UNHEALTHY, started, f'HTTP {response.status}', {'status_code': response.status})
                data = await response.json()
                # HTTP200 alone must not hide an unhealthy dependency report.
                reported = data.get('status') if isinstance(data, dict) else None
                try:
                    status = HealthStatus(reported)
                except (ValueError, TypeError):
                    status = HealthStatus.UNKNOWN
                return self._result(name, service_type, status, started, 'Reported health status', data if isinstance(data,dict) else {'invalid_payload':True})
        except asyncio.TimeoutError:
            return self._result(name, service_type, HealthStatus.UNHEALTHY, started, 'Request timeout', {'timeout':True})
        except Exception as error:
            return self._result(name, service_type, HealthStatus.CRITICAL, started, 'HTTP probe failed', {'error_type':type(error).__name__})

    async def check_bigquery(self):
        started = time.monotonic()
        if self.bigquery_client is None:
            return self._result('bigquery', ServiceType.DATABASE, HealthStatus.UNCONFIGURED, started, 'Explicit BigQuery client required')
        def query():
            return list(self.bigquery_client.query('SELECT 1 as test', timeout=self.timeout_seconds).result(timeout=self.timeout_seconds))
        try:
            results = await asyncio.wait_for(asyncio.to_thread(query), timeout=self.timeout_seconds)
            valid = len(results)==1 and results[0]['test']==1
            return self._result('bigquery',ServiceType.DATABASE,HealthStatus.HEALTHY if valid else HealthStatus.DEGRADED,started,'Query validated' if valid else 'Unexpected query result', {'result_count':len(results)})
        except Exception as error:
            return self._result('bigquery',ServiceType.DATABASE,HealthStatus.CRITICAL,started,'BigQuery probe failed',{'error_type':type(error).__name__})

    async def check_redis(self, redis_url=None):
        started = time.monotonic()
        if self.redis_client is None:
            return self._result('redis',ServiceType.DATABASE,HealthStatus.UNCONFIGURED,started,'Explicit Redis client required')
        # Unique keys prevent one concurrent checker from validating another.
        import uuid
        key='health-check:'+str(uuid.uuid4())
        try:
            async def probe():
                if not await self.redis_client.ping():
                    return False
                await self.redis_client.set(key,'ok',ex=10)
                value=await self.redis_client.get(key)
                await self.redis_client.delete(key)
                return value in (b'ok','ok')
            valid=await asyncio.wait_for(probe(),self.timeout_seconds)
            return self._result('redis',ServiceType.DATABASE,HealthStatus.HEALTHY if valid else HealthStatus.DEGRADED,started,'Redis roundtrip validated' if valid else 'Redis roundtrip mismatch')
        except Exception as error:
            return self._result('redis',ServiceType.DATABASE,HealthStatus.CRITICAL,started,'Redis probe failed',{'error_type':type(error).__name__})

    async def check_external_api(self,name,url,api_key=None):
        started=time.monotonic()
        if not url:
            return self._result(name,ServiceType.EXTERNAL_API,HealthStatus.UNCONFIGURED,started,'URL not configured')
        if self.session is None:
            return self._result(name,ServiceType.EXTERNAL_API,HealthStatus.UNKNOWN,started,'HTTP session not started')
        try:
            headers={'Authorization':'Bearer '+api_key} if api_key else {}
            async with self.session.get(url,headers=headers) as response:
                status=HealthStatus.HEALTHY if response.status in (200,201) else HealthStatus.DEGRADED if response.status in (429,503) else HealthStatus.UNHEALTHY
                return self._result(name,ServiceType.EXTERNAL_API,status,started,'HTTP availability only; not RPC semantic validation',{'status_code':response.status})
        except Exception as error:
            return self._result(name,ServiceType.EXTERNAL_API,HealthStatus.CRITICAL,started,'External probe failed',{'error_type':type(error).__name__})


class MetricsCollector:
    """Observed request instrumentation; never substitutes invented service data."""
    def __init__(self, clock=time.monotonic):
        self.clock=clock
        self._start_time=clock()
        self.observations={}

    def record_request(self,service_name,duration_ms,status_code,active_connections=None,queue_size=None):
        import math
        if duration_ms<0 or not math.isfinite(duration_ms) or not 100<=status_code<=599:
            raise ValueError('Invalid request observation')
        for value in (active_connections,queue_size):
            if value is not None and (not isinstance(value,int) or value<0):
                raise ValueError('Invalid gauge observation')
        state=self.observations.setdefault(service_name,{'count':0,'errors':0,'duration':0.,'connections':None,'queue':None})
        state['count']+=1;state['errors']+=int(status_code>=400);state['duration']+=duration_ms
        if active_connections is not None:state['connections']=active_connections
        if queue_size is not None:state['queue']=queue_size
        REQUEST_COUNT.labels(service=service_name,method='observed',status=str(status_code)).inc()
        REQUEST_DURATION.labels(service=service_name,method='observed').observe(duration_ms/1000)

    def collect_system_metrics(self):
        cpu=psutil.cpu_percent(interval=None);memory=psutil.virtual_memory().percent;disk=psutil.disk_usage('/').percent
        net=psutil.net_io_counters();connections=psutil.net_connections()
        SYSTEM_CPU.set(cpu);SYSTEM_MEMORY.set(memory);SYSTEM_DISK.set(disk)
        return SystemMetrics(cpu,memory,disk,(net.bytes_sent,net.bytes_recv),sum(c.status=='ESTABLISHED' for c in connections),datetime.now(timezone.utc))

    def collect_service_metrics(self,service_name):
        if service_name not in self.observations:
            raise ValueError('No observed request metrics for '+service_name)
        state=self.observations[service_name];elapsed=max(self.clock()-self._start_time,1e-9)
        return ServiceMetrics(service_name,state['count']/elapsed,state['duration']/state['count'],100*state['errors']/state['count'],state['connections'],state['queue'],int(elapsed),datetime.now(timezone.utc),state['count'])


class AlertManager:
    """Manages health-based alerting."""
    
    def __init__(self):
        self.logger = logger.bind(service="alert-manager")
        self.alert_rules: List[Dict[str, Any]] = []
        self.alert_history: List[Dict[str, Any]] = []
    
    def add_alert_rule(self, rule: Dict[str, Any]):
        """Add an alert rule."""
        if not rule.get("name") or not rule.get("severity"):
            raise ValueError("Alert rule requires name and severity")
        if rule.get("status"):
            HealthStatus(rule["status"])
        self.alert_rules.append(dict(rule))
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
                self.alert_history = self.alert_history[-1000:]
                
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
    """Aggregate only observed fresh dependency states; no default public calls."""
    def __init__(self,services=None,external_apis=None,health_checker=None,freshness_seconds=90,alert_sink=None):
        self.logger=logger.bind(service='health-monitoring')
        self.health_checker=health_checker or HealthChecker()
        self.metrics_collector=MetricsCollector()
        self.alert_manager=AlertManager()
        self.services=dict(services or {})
        self.external_apis=dict(external_apis or {})
        self.health_results={}
        self.freshness_seconds=freshness_seconds
        self.alert_sink=alert_sink
        self._monitoring_task=None;self._metrics_task=None;self._metrics_server=None
        self._setup_default_alerts()

    @classmethod
    def from_environment(cls):
        """Deployment entry point: provider clients require explicit settings.

        BigQuery never falls back to metadata or application-default credentials.
        Redis URL and HTTP registries are opt-in; caller owns their credentials.
        """
        services=json.loads(os.getenv('MONITOR_SERVICES_JSON','{}'))
        external=json.loads(os.getenv('MONITOR_EXTERNAL_APIS_JSON','{}'))
        for config in services.values():
            if 'type' in config:config['type']=ServiceType(config['type'])
        client=None;redis=None
        credentials_path=os.getenv('MONITOR_BIGQUERY_CREDENTIALS')
        if credentials_path:
            project=os.getenv('MONITOR_BIGQUERY_PROJECT')
            if not project:raise ValueError('Explicit MONITOR_BIGQUERY_PROJECT required')
            from google.oauth2 import service_account
            from google.cloud import bigquery
            credentials=service_account.Credentials.from_service_account_file(credentials_path)
            client=bigquery.Client(project=project,credentials=credentials)
        redis_url=os.getenv('MONITOR_REDIS_URL')
        if redis_url:
            from redis.asyncio import from_url
            redis=from_url(redis_url)
        return cls(services,external,HealthChecker(client,redis))

    def _setup_default_alerts(self):
        for status,severity in [('critical','critical'),('unhealthy','warning'),('unconfigured','warning'),('unknown','warning')]:
            self.alert_manager.add_alert_rule({'name':'service_'+status,'status':status,'severity':severity})
        self.alert_manager.add_alert_rule({'name':'slow_response','response_time_threshold_ms':5000,'severity':'warning'})

    async def check_once(self):
        checks=[]
        for name,config in self.services.items():
            checks.append(await self.health_checker.check_http_service(name,config.get('url'),config.get('type',ServiceType.API)))
        for name,config in self.external_apis.items():
            checks.append(await self.health_checker.check_external_api(name,config.get('url'),config.get('api_key')))
        # Required database dependencies remain visible when absent.
        checks.append(await self.health_checker.check_bigquery())
        checks.append(await self.health_checker.check_redis())
        for check in checks:
            self.health_results[check.service_name]=check
            for alert in self.alert_manager.evaluate_health_check(check):
                if self.alert_sink is not None:
                    result=self.alert_sink(alert)
                    if asyncio.iscoroutine(result):await result
        return checks

    async def start(self,metrics_port=None):
        if self._monitoring_task is not None:raise RuntimeError('Monitoring already started')
        if metrics_port is not None:self._metrics_server=start_http_server(metrics_port)
        self._monitoring_task=asyncio.create_task(self._monitoring_loop())
        self._metrics_task=asyncio.create_task(self._metrics_loop())

    async def stop(self):
        if self._monitoring_task is not None:
            self._monitoring_task.cancel()
            await asyncio.gather(self._monitoring_task,return_exceptions=True)
            self._monitoring_task=None
        if self._metrics_task is not None:
            self._metrics_task.cancel()
            await asyncio.gather(self._metrics_task,return_exceptions=True)
            self._metrics_task=None
        if self._metrics_server is not None:
            server,thread=self._metrics_server;server.shutdown();server.server_close();thread.join(timeout=2)
            self._metrics_server=None

    async def _monitoring_loop(self):
        async with self.health_checker:
            while True:
                try:
                    await self.check_once()
                except asyncio.CancelledError:raise
                except Exception as error:
                    self.logger.error('Monitoring or alert delivery failed',error_type=type(error).__name__)
                await asyncio.sleep(30)

    async def _metrics_loop(self):
        while True:
            try:
                await asyncio.to_thread(self.metrics_collector.collect_system_metrics)
            except asyncio.CancelledError:
                raise
            except Exception as error:
                self.logger.error('Host metrics unavailable',error_type=type(error).__name__)
            await asyncio.sleep(60)

    def get_system_status(self):
        now=datetime.now(timezone.utc)
        expected=set(self.services)|set(self.external_apis)|{'bigquery','redis'}
        statuses={}
        for name in expected:
            result=self.health_results.get(name)
            statuses[name]=HealthStatus.UNKNOWN.value if result is None or (now-result.timestamp).total_seconds()>self.freshness_seconds else result.status.value
        ranking=['healthy','degraded','unknown','unconfigured','unhealthy','critical']
        status=max(statuses.values(),key=ranking.index) if self.health_results else 'unconfigured'
        return {'status':status,'timestamp':now.isoformat(),'uptime_seconds':int(time.monotonic()-self.metrics_collector._start_time),'services_monitored':len(self.services),'external_apis_monitored':len(self.external_apis),'dependencies':statuses,'recent_alerts':sum(datetime.fromisoformat(a['timestamp']).replace(tzinfo=timezone.utc)>now-timedelta(hours=1) for a in self.alert_manager.alert_history),'scope':'Explicit configured dependencies; HTTP availability is not deployed end-to-end validation'}


async def main():
    service=HealthMonitoringService.from_environment()
    try:
        await service.start(metrics_port=8000)
        await asyncio.Event().wait()
    finally:
        await service.stop()

if __name__=='__main__':asyncio.run(main())
