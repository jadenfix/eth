"""Actual local status API lifecycle and HTTP observations, without cloud calls."""

import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
from fastapi.testclient import TestClient

from services.dashboard.status_dashboard import (
    StatusStore,
    create_app,
)


def test_import_has_no_async_tasks_or_fabricated_telemetry():
    code = """from services.dashboard.status_dashboard import status_store
assert status_store.tasks == []
assert status_store.signals_history == []
assert status_store.metrics_history == []
assert all(s['status'] == 'unknown' for s in status_store.service_status.values())
"""
    subprocess.run(
        [sys.executable, "-c", code],
        check=True,
        env={**os.environ, "STATUS_DEMO_MODE": "0", "STATUS_SERVICE_URLS": "{}"},
    )


def test_real_host_metrics_lifespan_and_shutdown():
    store = StatusStore()
    with TestClient(create_app(store)) as client:
        assert len(store.tasks) == 1
        assert client.get("/health").json()["scope"] == "responding_status_api_only"
        status = client.get("/system/status").json()
        assert status["overall_status"] == "unknown"
        assert status["services"]["healthy"] == 0
        assert status["ingestion_active"] is None
        assert status["processing_active"] is None
        metrics = client.get("/system/metrics").json()
        assert metrics["measurement_status"] == "observed"
        assert metrics["current"]["source"] == "observed_local_host"
        assert 0 <= metrics["current"]["system_cpu"] <= 100
        assert 0 <= metrics["current"]["system_memory"] <= 100
        assert metrics["current"]["signal_accuracy"] is None
        assert metrics["current"]["ingestion_rate"] is None
        assert client.get("/signals/recent").json()["signals"] == []
        assert client.get("/signals/recent?limit=-1").status_code == 422
        assert client.get("/metrics/timeseries?hours=0").status_code == 422
        assert "No chain ingestion" in client.get("/dashboard").text
    assert store.tasks == []


def test_explicit_samples_are_labeled_and_do_not_claim_external_health():
    store = StatusStore(demo_mode=True)
    with TestClient(create_app(store)) as client:
        signals = client.get("/signals/recent").json()
        assert signals["provenance"]["signals"] == "synthetic_fixture"
        assert signals["signals"]
        assert all(
            s["source"] == "synthetic_fixture" and s["confidence_score"] is None
            for s in signals["signals"]
        )
        assert client.get("/system/status").json()["overall_status"] == "unknown"


@pytest.mark.asyncio
async def test_configured_service_probe_uses_actual_http_status():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200 if self.path == "/ready" else 503)
            self.end_headers()

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}"
        store = StatusStore(
            service_urls={
                "ready-service": url + "/ready",
                "failed-service": url + "/unavailable",
            }
        )
        await store.probe_once()
        assert store.service_status["ready-service"]["status"] == "healthy"
        assert store.service_status["failed-service"]["status"] == "degraded"
        assert store.service_status["neo4j"]["status"] == "unknown"
        assert store.system_status()["overall_status"] == "degraded"
        assert store.service_status["ready-service"]["source"] == "observed_http"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_bad_probe_configuration_fails_explicitly():
    with pytest.raises(ValueError, match="JSON object"):
        StatusStore(service_urls=["not a mapping"])
    with pytest.raises(ValueError, match="HTTP URLs"):
        StatusStore(service_urls={"service": "not-http"})
