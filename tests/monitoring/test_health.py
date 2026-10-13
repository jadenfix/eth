import asyncio
from datetime import datetime,timedelta,timezone
from unittest import IsolatedAsyncioTestCase,TestCase
from aiohttp import web
from aiohttp.test_utils import TestServer
from services.monitoring.health_service import HealthChecker,HealthMonitoringService,HealthStatus,MetricsCollector,AlertManager,HealthCheck,ServiceType

class QueryFixture:
    def __init__(self,value=1,error=None):self.value=value;self.error=error;self.calls=[]
    def query(self,sql,timeout):
        self.calls.append(sql)
        if self.error:raise self.error
        return self
    def result(self,timeout):return [{'test':self.value}]

class RedisFixture:
    def __init__(self):self.data={};self.keys=[]
    async def ping(self):return True
    async def set(self,key,value,ex):self.keys.append(key);self.data[key]=value.encode()
    async def get(self,key):return self.data[key]
    async def delete(self,key):del self.data[key]

class HealthTests(IsolatedAsyncioTestCase):
    async def test_real_http_status_payload_and_failures(self):
        state={'status':'healthy','code':200}
        async def health(request):
            if state['status']=='slow':await asyncio.sleep(.1)
            if state['status']=='invalid':return web.Response(text='broken',content_type='application/json')
            return web.json_response({'status':state['status']},status=state['code'])
        app=web.Application();app.router.add_get('/health',health)
        server=TestServer(app);await server.start_server()
        async with HealthChecker(timeout_seconds=.03) as checker:
            url=str(server.make_url('/')).rstrip('/')
            self.assertEqual((await checker.check_http_service('local',url)).status,HealthStatus.HEALTHY)
            state['status']='degraded'
            self.assertEqual((await checker.check_http_service('local',url)).status,HealthStatus.DEGRADED)
            state['status']='arbitrary'
            self.assertEqual((await checker.check_http_service('local',url)).status,HealthStatus.UNKNOWN)
            state['status']='invalid'
            self.assertEqual((await checker.check_http_service('local',url)).status,HealthStatus.CRITICAL)
            state['status']='slow'
            self.assertEqual((await checker.check_http_service('local',url)).status,HealthStatus.UNHEALTHY)
            state.update(status='healthy',code=503)
            self.assertEqual((await checker.check_http_service('local',url)).status,HealthStatus.UNHEALTHY)
            self.assertEqual((await checker.check_external_api('local',url+'/health')).status,HealthStatus.DEGRADED)
            await server.close()
            self.assertEqual((await checker.check_http_service('local',url)).status,HealthStatus.CRITICAL)
        self.assertIsNone(checker.session)

    async def test_no_config_does_not_connect_or_report_healthy(self):
        checker=HealthChecker();service=HealthMonitoringService(health_checker=checker)
        self.assertEqual(service.get_system_status()['status'],'unconfigured')
        checks=await service.check_once()
        self.assertEqual({x.status for x in checks},{HealthStatus.UNCONFIGURED})
        self.assertNotEqual(service.get_system_status()['status'],'healthy')
        self.assertEqual(len(service.alert_manager.alert_history),2)
        self.assertEqual((await checker.check_http_service('missing',None)).status,HealthStatus.UNCONFIGURED)

    async def test_explicit_provider_fixture_roundtrip_and_rejection(self):
        query=QueryFixture();redis=RedisFixture();checker=HealthChecker(query,redis)
        self.assertEqual((await checker.check_bigquery()).status,HealthStatus.HEALTHY)
        self.assertEqual(query.calls,['SELECT 1 as test'])
        self.assertEqual((await checker.check_redis()).status,HealthStatus.HEALTHY)
        self.assertEqual(redis.data,{})
        await checker.check_redis();self.assertNotEqual(redis.keys[0],redis.keys[1])
        checker.bigquery_client=QueryFixture(0)
        self.assertEqual((await checker.check_bigquery()).status,HealthStatus.DEGRADED)
        checker.bigquery_client=QueryFixture(error=PermissionError('permission denied'))
        result=await checker.check_bigquery();self.assertEqual(result.status,HealthStatus.CRITICAL)
        self.assertEqual(result.metadata,{'error_type':'PermissionError'})

    async def test_aggregate_freshness_and_alert_delivery_failure(self):
        checker=HealthChecker(QueryFixture(),RedisFixture());service=HealthMonitoringService(health_checker=checker)
        await service.check_once();self.assertEqual(service.get_system_status()['status'],'healthy')
        service.health_results['redis'].timestamp-=timedelta(seconds=100)
        self.assertEqual(service.get_system_status()['dependencies']['redis'],'unknown')
        self.assertNotEqual(service.get_system_status()['status'],'healthy')
        def failing_sink(alert):raise ConnectionError('sink unavailable')
        service=HealthMonitoringService(alert_sink=failing_sink)
        with self.assertRaises(ConnectionError):await service.check_once()

    async def test_start_stop_closes_sessions_and_tasks(self):
        service=HealthMonitoringService()
        await service.start()
        await asyncio.sleep(.01)
        with self.assertRaises(RuntimeError):await service.start()
        await service.stop()
        self.assertIsNone(service.health_checker.session)
        self.assertIsNone(service._monitoring_task)

class MetricsTests(TestCase):
    def test_observed_values_no_invented_metrics(self):
        clock=[100.];c=MetricsCollector(clock=lambda:clock[0])
        with self.assertRaises(ValueError):c.collect_service_metrics('unobserved')
        c.record_request('api',50,200);c.record_request('api',100,503,active_connections=3,queue_size=2)
        clock[0]=102.;m=c.collect_service_metrics('api')
        self.assertEqual((m.requests_per_second,m.avg_response_time_ms,m.error_rate_percent),(1,75,50))
        self.assertEqual((m.active_connections,m.queue_size,m.observed_requests),(3,2,2))
        with self.assertRaises(ValueError):c.record_request('api',float('nan'),200)

    def test_environment_entrypoint_has_no_implicit_credentials(self):
        from unittest.mock import patch
        with patch.dict('os.environ',{'GOOGLE_CLOUD_PROJECT':'does-not-enable-client'},clear=True):
            service=HealthMonitoringService.from_environment()
        self.assertIsNone(service.health_checker.bigquery_client)
        self.assertIsNone(service.health_checker.redis_client)
        self.assertEqual(service.get_system_status()['status'],'unconfigured')

    def test_real_host_metrics_and_threshold_alert(self):
        metrics=MetricsCollector().collect_system_metrics()
        self.assertTrue(0<=metrics.memory_percent<=100);self.assertTrue(0<=metrics.disk_percent<=100)
        manager=AlertManager();manager.add_alert_rule({'name':'slow','severity':'warning','response_time_threshold_ms':5000})
        check=HealthCheck('api',ServiceType.API,HealthStatus.HEALTHY,4999,'ok',{},datetime.now(timezone.utc))
        self.assertEqual(manager.evaluate_health_check(check),[])
        check.response_time_ms=5000
        self.assertEqual(len(manager.evaluate_health_check(check)),1)
