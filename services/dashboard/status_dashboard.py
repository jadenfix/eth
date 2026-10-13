"""Status API: observed local metrics and explicitly configured service probes.

No chain, model, or worker telemetry is inferred. STATUS_DEMO_MODE=1 opts into
labeled synthetic signals. STATUS_SERVICE_URLS is an admin-provided JSON mapping
of service names to actual HTTP health endpoints; absent endpoints stay unknown.
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
import json
import os
import time
from typing import Dict, List, Optional

import aiohttp
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import structlog

logger = structlog.get_logger(__name__)


def timestamp():
    return datetime.now(timezone.utc).isoformat()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_text(json.dumps(data))
            except Exception:
                self.disconnect(connection)


class StatusStore:
    def __init__(self, demo_mode=False, service_urls=None):
        self.start_time = time.time()
        self.demo_mode = demo_mode
        if service_urls is not None and not isinstance(service_urls, dict):
            raise ValueError("STATUS_SERVICE_URLS must be a JSON object")
        self.service_urls = dict(service_urls or {})
        if any(
            not isinstance(name, str)
            or not isinstance(url, str)
            or not url.startswith(("http://", "https://"))
            for name, url in self.service_urls.items()
        ):
            raise ValueError("Service names and HTTP URLs must be strings")
        self._sample_counter = 0
        self.signals_history = []
        self.metrics_history = []
        self.metrics_error = None
        self.tasks = []
        names = {
            "ethereum-ingester",
            "graph-api",
            "mev-agent",
            "entity-resolution",
            "bigquery",
            "neo4j",
        } | set(self.service_urls)
        self.service_status = {
            name: {"status": "unknown", "last_update": None, "source": "not_observed"}
            for name in sorted(names)
        }

    @property
    def provenance(self):
        return {
            "signals": "synthetic_fixture" if self.demo_mode else "no_signal_provider",
            "metrics": "observed_local_host",
            "services": "configured_http_probes_only",
            "live_chain_connected": False,
            "model_accuracy_validated": False,
        }

    def collect_metrics(self):
        import psutil

        return {
            "timestamp": timestamp(),
            "source": "observed_local_host",
            "system_cpu": psutil.cpu_percent(),
            "system_memory": psutil.virtual_memory().percent,
            "ingestion_rate": None,
            "processing_latency_ms": None,
            "active_agents": None,
            "signal_accuracy": None,
        }

    async def sample_once(self, connections):
        try:
            metrics = await asyncio.to_thread(self.collect_metrics)
            self.metrics_history = (self.metrics_history + [metrics])[-720:]
            self.metrics_error = None
            await connections.broadcast({"type": "metrics_update", "metrics": metrics})
        except Exception as exc:
            self.metrics_error = str(exc)
            logger.warning("Host metric collection unavailable", error=str(exc))
        if self.demo_mode:
            self._sample_counter += 1
            number = self._sample_counter
            signal = {
                "signal_id": f"SAMPLE-{number}",
                "timestamp": timestamp(),
                "signal_type": "SAMPLE_EVENT",
                "severity": "LOW",
                "description": "Synthetic demonstration event; no blockchain observation",
                "confidence_score": None,
                "source": "synthetic_fixture",
            }
            self.signals_history = (self.signals_history + [signal])[-720:]
            await connections.broadcast({"type": "signal_update", "signal": signal})

    async def probe_once(self):
        if not self.service_urls:
            return
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=3)
        ) as session:
            for name, url in self.service_urls.items():
                try:
                    async with session.get(url) as response:
                        status = (
                            "healthy" if 200 <= response.status < 300 else "degraded"
                        )
                        detail = f"HTTP {response.status}"
                except Exception as exc:
                    status, detail = "degraded", str(exc)
                self.service_status[name] = {
                    "status": status,
                    "last_update": time.time(),
                    "source": "observed_http",
                    "detail": detail,
                }

    async def _run(self, connections):
        while True:
            await self.sample_once(connections)
            await self.probe_once()
            await connections.broadcast(
                {"type": "system_status", "data": self.system_status()}
            )
            await asyncio.sleep(5)

    def system_status(self):
        statuses = [info["status"] for info in self.service_status.values()]
        unknown = statuses.count("unknown")
        degraded = statuses.count("degraded")
        return {
            "overall_status": (
                "degraded" if degraded else "unknown" if unknown else "operational"
            ),
            "uptime_seconds": int(time.time() - self.start_time),
            "uptime_scope": "status_api",
            "services": {
                "healthy": statuses.count("healthy"),
                "total": len(statuses),
                "unknown": unknown,
                "degraded": degraded,
            },
            "recent_signals": len(self.signals_history),
            "ingestion_active": None,
            "processing_active": None,
            "provenance": self.provenance,
            "timestamp": timestamp(),
        }

    async def start(self, connections):
        if self.tasks:
            raise RuntimeError("Status collection already running")
        self.start_time = time.time()
        await self.sample_once(connections)
        await self.probe_once()
        self.tasks.append(asyncio.create_task(self._run(connections)))

    async def stop(self):
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks.clear()


manager = ConnectionManager()
status_store = StatusStore(
    demo_mode=os.getenv("STATUS_DEMO_MODE") == "1",
    service_urls=json.loads(os.getenv("STATUS_SERVICE_URLS", "{}")),
)


def create_app(store=None, connections=None):
    store = store or status_store
    connections = connections or manager

    @asynccontextmanager
    async def lifespan(app):
        await store.start(connections)
        try:
            yield
        finally:
            await store.stop()

    application = FastAPI(
        title="Onchain Status API", version="1.1.0", lifespan=lifespan
    )
    application.state.store = store

    @application.get("/")
    async def root():
        return {
            "service": "Onchain Status API",
            "version": "1.1.0",
            "provenance": store.provenance,
            "uptime_seconds": int(time.time() - store.start_time),
        }

    @application.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "scope": "responding_status_api_only",
            "external_service_health": "not_inferred",
            "timestamp": timestamp(),
        }

    @application.get("/system/status")
    async def get_system_status():
        return store.system_status()

    @application.get("/system/metrics")
    async def get_system_metrics():
        latest = store.metrics_history[-1] if store.metrics_history else None
        return {
            "current": latest,
            "measurement_status": "observed" if latest else "unavailable",
            "error": store.metrics_error,
            "provenance": store.provenance,
            "timestamp": timestamp(),
        }

    @application.get("/system/services")
    async def get_service_status():
        return {
            "services": [
                {"name": name, **info} for name, info in store.service_status.items()
            ],
            "provenance": store.provenance,
            "timestamp": timestamp(),
        }

    @application.get("/signals/recent")
    async def get_recent_signals(limit: int = Query(20, ge=1, le=1000)):
        return {
            "signals": list(reversed(store.signals_history))[:limit],
            "total_count": len(store.signals_history),
            "provenance": store.provenance,
        }

    @application.get("/signals/stats")
    async def get_signal_stats():
        return {
            "total_signals": len(store.signals_history),
            "average_confidence": None,
            "provenance": store.provenance,
        }

    @application.get("/metrics/timeseries")
    async def get_metrics_timeseries(hours: int = Query(1, ge=1, le=24)):
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        metrics = [
            m
            for m in store.metrics_history
            if datetime.fromisoformat(m["timestamp"]) > cutoff
        ]
        return {
            "metrics": metrics,
            "count": len(metrics),
            "hours": hours,
            "provenance": store.provenance,
        }

    @application.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await connections.connect(websocket)
        try:
            await websocket.send_json(
                {"type": "connected", "provenance": store.provenance}
            )
            await websocket.send_json(
                {"type": "system_status", "data": store.system_status()}
            )
            await websocket.send_json(
                {
                    "type": "recent_signals",
                    "data": {"signals": store.signals_history[-5:]},
                }
            )
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            pass
        finally:
            connections.disconnect(websocket)

    @application.get("/dashboard", response_class=HTMLResponse)
    async def dashboard():
        return DASHBOARD_HTML

    return application


DASHBOARD_HTML = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Observed status</title><style>
body{margin:0;background:#102322;color:#e4efeb;font:16px system-ui;line-height:1.6}main{max-width:900px;margin:auto;padding:36px 20px}h1{font-size:36px;line-height:1.15}.label{color:#95c5b4;letter-spacing:.1em;font-size:12px;text-transform:uppercase}.notice{border:1px solid #789184;padding:16px;border-radius:12px;background:#203c35}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px;margin:22px 0}section{background:#19332e;padding:20px;border-radius:12px;min-width:0}strong{display:block;font-size:26px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px system-ui}li{margin:10px 0}.muted{color:#b0c4bc}</style><main><div class="label">Onchain command center / observed status</div><h1>Measured locally.<br>Unknown where unconnected.</h1><p id="provenance" class="notice">Loading telemetry provenance…</p><div class="cards"><section><div class="label">Service observations</div><strong id="status">Loading</strong><p id="coverage"></p></section><section><div class="label">Observed host CPU</div><strong id="cpu">Unavailable</strong><p class="muted">Local host usage; not blockchain throughput.</p></section><section><div class="label">Observed host memory</div><strong id="memory">Unavailable</strong><p class="muted">Local host usage; not model accuracy.</p></section></div><section><h2>Configured services</h2><ul id="services"></ul></section><section style="margin-top:16px"><h2>Signals</h2><p id="signal-status">No signal provider connected.</p><ul id="signals"></ul></section><p id="error" role="status"></p></main><script>
const set=(id,value)=>document.getElementById(id).textContent=value;
function renderStatus(s){set('status',s.overall_status);set('coverage',s.services.healthy+' healthy, '+s.services.unknown+' unobserved, '+s.services.degraded+' degraded');set('provenance',s.provenance.signals==='synthetic_fixture'?'SAMPLE MODE: synthetic demonstration signals. CPU/memory are measured on this host. No live chain or validated model accuracy.':'Observed local host metrics. Unconfigured services remain unknown. No chain ingestion, processing throughput, or model accuracy is inferred.');}
function renderMetrics(m){set('cpu',m?m.system_cpu+'%':'Unavailable');set('memory',m?m.system_memory+'%':'Unavailable');}
function renderSignals(signals){const list=document.getElementById('signals');list.replaceChildren();for(const s of signals){const li=document.createElement('li');li.textContent=s.description+' · '+s.source;list.append(li);}set('signal-status',signals.length?'Explicit synthetic fixture events; not blockchain detections.':'No signal provider connected.');}
async function refresh(){try{const urls=['/system/status','/system/metrics','/system/services','/signals/recent'];const data=await Promise.all(urls.map(async url=>{const response=await fetch(url);if(!response.ok)throw Error('HTTP '+response.status);return response.json();}));renderStatus(data[0]);renderMetrics(data[1].current);renderSignals(data[3].signals);const list=document.getElementById('services');list.replaceChildren();for(const s of data[2].services){const li=document.createElement('li');li.textContent=s.name+': '+s.status+' · '+s.source;list.append(li);}set('error','');}catch(e){set('error','Telemetry unavailable: '+e.message);}}
refresh();const ws=new WebSocket((location.protocol==='https:'?'wss://':'ws://')+location.host+'/ws');ws.onmessage=e=>{const d=JSON.parse(e.data);if(d.type==='system_status')renderStatus(d.data);if(d.type==='metrics_update')renderMetrics(d.metrics);if(d.type==='signal_update')refresh();};ws.onerror=()=>set('error','Live updates unavailable; showing the last HTTP observation.');</script></html>"""

app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8004)
