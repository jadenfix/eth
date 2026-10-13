# Monitoring with observed dependency states

Run `python -m unittest discover -s tests/monitoring -v` from the repository root. Runtime dependencies are aiohttp, psutil, structlog and prometheus-client. Tests use a real loopback HTTP server and explicitly labeled provider fixtures; they do not certify live BigQuery or Redis infrastructure.

`HealthChecker(bigquery_client=..., redis_client=...)` probes explicitly supplied clients. The BigQuery SELECT must actually return scalar `test=1`. Redis ping and a unique expiring set/get/delete roundtrip must succeed. Missing clients return `unconfigured`, permission/connection errors return `critical`, and wrong returned data is `degraded`. Construction/import does not discover credentials or call metadata services.

HTTP service checks require a `/health` JSON status; HTTP200 alone cannot override an unhealthy or unknown status. Timeouts, malformed JSON and disconnects remain failure outcomes. External API checks establish HTTP availability only, not JSON-RPC or business-operation correctness. All HTTP calls are bounded by the configured timeout.

`HealthMonitoringService.check_once()` records those observations, evaluates alert rules and optionally delivers alerts to an injected sink. Sink errors propagate. The aggregate includes absent required BigQuery/Redis dependencies, unchecked services and stale observations; it reports healthy only when every expected dependency has a fresh healthy result. The background loop logs failures and closes/cancels its resources on stop. The Prometheus listener is explicitly enabled with `start(metrics_port=8000)`; process start alone is not system health.

`MetricsCollector.record_request(...)` instruments actual observed requests. Service rates, latency and errors derive from those records, not invented constants. Unobserved services raise an explicit error; absent connection/queue observations are `None`. Host CPU/memory/disk/network/connection metrics come from psutil; unavailable host permissions are errors, not fabricated zeros. These instrumented request measurements describe the supplied observations and need integration at each actual service request boundary for business traffic.

For deployment, `python -m services.monitoring.health_service` uses explicit environment configuration:

- `MONITOR_SERVICES_JSON`: object mapping names to `{ "url": "...", "type": "api" }`.
- `MONITOR_EXTERNAL_APIS_JSON`: object mapping names to explicit HTTP endpoint configurations.
- `MONITOR_BIGQUERY_CREDENTIALS`: service-account credential file path, with `MONITOR_BIGQUERY_PROJECT`. The adapter intentionally has no metadata/application-default fallback.
- `MONITOR_REDIS_URL`: explicitly configured Redis endpoint. No local/default Redis is assumed.

Credential files and API keys are deployment secrets and must remain uncommitted. With no configuration the monitor runs and reports unconfigured dependencies; it does not make public-network calls or assert that an undeployed platform is healthy.
