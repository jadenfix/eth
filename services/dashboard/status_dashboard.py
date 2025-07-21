"""
Status Dashboard API - Real-time system status and metrics endpoint.

Provides REST API for system health, metrics, and operational status
for the blockchain intelligence platform dashboard.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import asyncio
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

import structlog

# Configure logging
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

app = FastAPI(
    title="Onchain Command Center - Status API",
    description="Real-time system status and metrics",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.logger = logger.bind(service="websocket-manager")
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.logger.info("WebSocket connected", 
                        active_connections=len(self.active_connections))
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            self.logger.info("WebSocket disconnected",
                           active_connections=len(self.active_connections))
    
    async def broadcast(self, data: dict):
        if self.active_connections:
            message = json.dumps(data)
            disconnected = []
            
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                except Exception:
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for conn in disconnected:
                self.disconnect(conn)

manager = ConnectionManager()

# Mock data store - in production this would connect to real services
class StatusStore:
    def __init__(self):
        self.start_time = time.time()
        self.signals_history = []
        self.metrics_history = []
        self.service_status = {
            "ethereum-ingester": {"status": "healthy", "last_update": time.time()},
            "graph-api": {"status": "healthy", "last_update": time.time()},
            "mev-agent": {"status": "healthy", "last_update": time.time()},
            "entity-resolution": {"status": "healthy", "last_update": time.time()},
            "bigquery": {"status": "healthy", "last_update": time.time()},
            "neo4j": {"status": "healthy", "last_update": time.time()}
        }
        
        # Start background data generation
        asyncio.create_task(self.generate_mock_data())
    
    async def generate_mock_data(self):
        """Generate mock real-time data."""
        signal_id = 1
        
        while True:
            try:
                # Generate mock signal
                signal = {
                    "signal_id": f"SIG-{signal_id:06d}",
                    "timestamp": datetime.now().isoformat(),
                    "signal_type": "MEV_ATTACK" if signal_id % 3 == 0 else "HIGH_VALUE_TRANSFER",
                    "severity": "HIGH" if signal_id % 5 == 0 else "MEDIUM",
                    "description": f"Detected anomalous transaction pattern #{signal_id}",
                    "confidence_score": 0.85 + (signal_id % 10) / 100,
                    "related_addresses": [f"0x{hex(signal_id*123)[2:]:0>40}"],
                    "metadata": {
                        "value_usd": 100000 + (signal_id * 1000),
                        "gas_used": 21000 + (signal_id % 1000)
                    }
                }
                
                self.signals_history.append(signal)
                
                # Keep only recent signals
                cutoff = datetime.now() - timedelta(hours=1)
                self.signals_history = [
                    s for s in self.signals_history 
                    if datetime.fromisoformat(s['timestamp']) > cutoff
                ]
                
                # Generate mock metrics
                metrics = {
                    "timestamp": datetime.now().isoformat(),
                    "ingestion_rate": 150 + (signal_id % 50),
                    "processing_latency_ms": 250 + (signal_id % 100),
                    "active_agents": 5,
                    "signal_accuracy": 0.87 + (signal_id % 10) / 100,
                    "system_cpu": 45 + (signal_id % 20),
                    "system_memory": 60 + (signal_id % 15)
                }
                
                self.metrics_history.append(metrics)
                
                # Keep only recent metrics
                self.metrics_history = [
                    m for m in self.metrics_history
                    if datetime.fromisoformat(m['timestamp']) > cutoff
                ]
                
                # Broadcast to WebSocket clients
                await manager.broadcast({
                    "type": "signal_update",
                    "signal": signal
                })
                
                await manager.broadcast({
                    "type": "metrics_update", 
                    "metrics": metrics
                })
                
                signal_id += 1
                await asyncio.sleep(5)  # New data every 5 seconds
                
            except Exception as e:
                logger.error("Error generating mock data", error=str(e))
                await asyncio.sleep(10)

status_store = StatusStore()

@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "service": "Onchain Command Center Status API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": int(time.time() - status_store.start_time)
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "api": "healthy",
            "websockets": "healthy",
            "data_store": "healthy"
        }
    }

@app.get("/system/status")
async def get_system_status():
    """Get overall system status."""
    uptime = int(time.time() - status_store.start_time)
    
    # Calculate service health summary
    healthy_services = sum(1 for s in status_store.service_status.values() 
                          if s["status"] == "healthy")
    total_services = len(status_store.service_status)
    
    return {
        "overall_status": "operational" if healthy_services == total_services else "degraded",
        "uptime_seconds": uptime,
        "services": {
            "healthy": healthy_services,
            "total": total_services,
            "degraded": total_services - healthy_services
        },
        "recent_signals": len(status_store.signals_history),
        "ingestion_active": True,
        "processing_active": True,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/system/metrics")
async def get_system_metrics():
    """Get current system metrics."""
    if not status_store.metrics_history:
        return {"error": "No metrics available"}
    
    latest = status_store.metrics_history[-1]
    
    # Calculate averages over last hour
    recent_metrics = status_store.metrics_history[-12:]  # Last 12 samples (1 hour)
    
    avg_ingestion = sum(m["ingestion_rate"] for m in recent_metrics) / len(recent_metrics)
    avg_latency = sum(m["processing_latency_ms"] for m in recent_metrics) / len(recent_metrics)
    avg_accuracy = sum(m["signal_accuracy"] for m in recent_metrics) / len(recent_metrics)
    
    return {
        "current": latest,
        "averages": {
            "ingestion_rate": round(avg_ingestion, 1),
            "processing_latency_ms": round(avg_latency, 1),
            "signal_accuracy": round(avg_accuracy, 3)
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/system/services")
async def get_service_status():
    """Get individual service statuses."""
    services = []
    
    for name, info in status_store.service_status.items():
        services.append({
            "name": name,
            "status": info["status"],
            "last_update": datetime.fromtimestamp(info["last_update"]).isoformat(),
            "uptime_seconds": int(time.time() - info.get("start_time", status_store.start_time))
        })
    
    return {
        "services": services,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/signals/recent")
async def get_recent_signals(limit: int = 20):
    """Get recent AI signals."""
    signals = sorted(
        status_store.signals_history,
        key=lambda x: x["timestamp"],
        reverse=True
    )[:limit]
    
    return {
        "signals": signals,
        "total_count": len(status_store.signals_history),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/signals/stats")
async def get_signal_stats():
    """Get signal statistics."""
    if not status_store.signals_history:
        return {"error": "No signals available"}
    
    # Count by type
    type_counts = {}
    severity_counts = {}
    
    for signal in status_store.signals_history:
        signal_type = signal["signal_type"]
        severity = signal["severity"]
        
        type_counts[signal_type] = type_counts.get(signal_type, 0) + 1
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    # Calculate average confidence
    avg_confidence = sum(s["confidence_score"] for s in status_store.signals_history) / len(status_store.signals_history)
    
    return {
        "total_signals": len(status_store.signals_history),
        "by_type": type_counts,
        "by_severity": severity_counts,
        "average_confidence": round(avg_confidence, 3),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/metrics/timeseries")
async def get_metrics_timeseries(hours: int = 1):
    """Get metrics time series data."""
    cutoff = datetime.now() - timedelta(hours=hours)
    
    metrics = [
        m for m in status_store.metrics_history
        if datetime.fromisoformat(m["timestamp"]) > cutoff
    ]
    
    return {
        "metrics": metrics,
        "count": len(metrics),
        "hours": hours,
        "timestamp": datetime.now().isoformat()
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    
    try:
        # Send initial data
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": "Connected to Onchain Command Center",
            "timestamp": datetime.now().isoformat()
        }))
        
        # Send current status
        system_status = await get_system_status()
        await websocket.send_text(json.dumps({
            "type": "system_status",
            "data": system_status
        }))
        
        # Send recent signals
        recent_signals = await get_recent_signals(5)
        await websocket.send_text(json.dumps({
            "type": "recent_signals",
            "data": recent_signals
        }))
        
        # Keep connection alive
        while True:
            await websocket.receive_text()  # Wait for client messages
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket error", error=str(e))
        manager.disconnect(websocket)

@app.get("/dashboard")
async def dashboard():
    """Simple HTML dashboard for testing."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Onchain Command Center Status</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }
            .container { max-width: 1200px; margin: 0 auto; }
            .status-card { 
                background: #2d2d2d; 
                border: 1px solid #444; 
                border-radius: 8px; 
                padding: 20px; 
                margin: 10px 0; 
            }
            .status-healthy { border-left: 4px solid #00ff00; }
            .status-degraded { border-left: 4px solid #ffff00; }
            .status-critical { border-left: 4px solid #ff0000; }
            .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
            .metric { background: #333; padding: 15px; border-radius: 6px; text-align: center; }
            .signal { 
                background: #2a2a2a; 
                border-left: 3px solid #0088ff; 
                padding: 10px; 
                margin: 5px 0; 
                border-radius: 4px; 
            }
            .signal-high { border-left-color: #ff4444; }
            .signal-medium { border-left-color: #ffaa00; }
            h1, h2 { color: #00aaff; }
            .timestamp { color: #888; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔗 Onchain Command Center</h1>
            <div id="status" class="status-card">
                <h2>System Status</h2>
                <p>Loading...</p>
            </div>
            
            <div class="status-card">
                <h2>📊 Live Metrics</h2>
                <div id="metrics" class="metrics">Loading...</div>
            </div>
            
            <div class="status-card">
                <h2>🚨 Recent Signals</h2>
                <div id="signals">Loading...</div>
            </div>
        </div>

        <script>
            // WebSocket connection
            const ws = new WebSocket('ws://localhost:8004/ws');
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                
                if (data.type === 'system_status') {
                    updateSystemStatus(data.data);
                } else if (data.type === 'metrics_update') {
                    updateMetrics(data.metrics);
                } else if (data.type === 'signal_update') {
                    addSignal(data.signal);
                }
            };
            
            function updateSystemStatus(status) {
                const statusDiv = document.getElementById('status');
                const statusClass = status.overall_status === 'operational' ? 'status-healthy' : 'status-degraded';
                
                statusDiv.className = `status-card ${statusClass}`;
                statusDiv.innerHTML = `
                    <h2>System Status: ${status.overall_status.toUpperCase()}</h2>
                    <p>Uptime: ${Math.floor(status.uptime_seconds / 3600)}h ${Math.floor((status.uptime_seconds % 3600) / 60)}m</p>
                    <p>Services: ${status.services.healthy}/${status.services.total} healthy</p>
                    <p>Recent Signals: ${status.recent_signals}</p>
                    <p class="timestamp">Last updated: ${new Date().toLocaleTimeString()}</p>
                `;
            }
            
            function updateMetrics(metrics) {
                const metricsDiv = document.getElementById('metrics');
                metricsDiv.innerHTML = `
                    <div class="metric">
                        <h3>${metrics.ingestion_rate}</h3>
                        <p>Events/sec</p>
                    </div>
                    <div class="metric">
                        <h3>${metrics.processing_latency_ms}ms</h3>
                        <p>Latency</p>
                    </div>
                    <div class="metric">
                        <h3>${metrics.active_agents}</h3>
                        <p>Active Agents</p>
                    </div>
                    <div class="metric">
                        <h3>${(metrics.signal_accuracy * 100).toFixed(1)}%</h3>
                        <p>Accuracy</p>
                    </div>
                    <div class="metric">
                        <h3>${metrics.system_cpu}%</h3>
                        <p>CPU Usage</p>
                    </div>
                    <div class="metric">
                        <h3>${metrics.system_memory}%</h3>
                        <p>Memory Usage</p>
                    </div>
                `;
            }
            
            function addSignal(signal) {
                const signalsDiv = document.getElementById('signals');
                const severityClass = `signal-${signal.severity.toLowerCase()}`;
                
                const signalElement = document.createElement('div');
                signalElement.className = `signal ${severityClass}`;
                signalElement.innerHTML = `
                    <strong>${signal.signal_type}</strong> - ${signal.severity}
                    <br>${signal.description}
                    <br><small>Confidence: ${(signal.confidence_score * 100).toFixed(1)}% | ${new Date(signal.timestamp).toLocaleTimeString()}</small>
                `;
                
                signalsDiv.insertBefore(signalElement, signalsDiv.firstChild);
                
                // Keep only latest 10 signals
                while (signalsDiv.children.length > 10) {
                    signalsDiv.removeChild(signalsDiv.lastChild);
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

# Background task to update service statuses
async def update_service_statuses():
    """Background task to simulate service status updates."""
    while True:
        try:
            # Simulate occasional service issues
            import random
            
            for service_name in status_store.service_status.keys():
                # 95% chance service stays healthy
                if random.random() < 0.95:
                    status_store.service_status[service_name]["status"] = "healthy"
                else:
                    # 5% chance of degraded status
                    status_store.service_status[service_name]["status"] = "degraded"
                
                status_store.service_status[service_name]["last_update"] = time.time()
            
            await asyncio.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            logger.error("Error updating service statuses", error=str(e))
            await asyncio.sleep(60)

# Start background task
@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Starting Onchain Command Center Status API")
    asyncio.create_task(update_service_statuses())

@app.on_event("shutdown") 
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down Onchain Command Center Status API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "status_dashboard:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )
