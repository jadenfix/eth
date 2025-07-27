import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from collections import defaultdict

logger = logging.getLogger(__name__)

app = FastAPI(title="Real-time Visualization Dashboard", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.dashboard_data = defaultdict(list)
        self.update_task = None
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
        
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
        
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                # Remove failed connection
                if connection in self.active_connections:
                    self.active_connections.remove(connection)
    
    async def start_data_updates(self):
        """Start periodic data updates"""
        while True:
            try:
                # Generate real-time data
                data = await self._generate_real_time_data()
                
                # Create visualizations
                visualizations = await self._create_real_time_visualizations(data)
                
                # Broadcast to all connected clients
                message = {
                    "type": "dashboard_update",
                    "timestamp": datetime.now().isoformat(),
                    "data": data,
                    "visualizations": visualizations
                }
                
                await self.broadcast(json.dumps(message))
                
                # Wait before next update
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in data updates: {e}")
                await asyncio.sleep(5)
    
    async def _generate_real_time_data(self) -> Dict[str, Any]:
        """Generate real-time blockchain data"""
        now = datetime.now()
        
        # Generate mock real-time data
        data = {
            "timestamp": now.isoformat(),
            "block_number": 18500000 + int(now.timestamp() / 12),  # ~12 second blocks
            "transaction_count": np.random.poisson(150),
            "gas_price": np.random.exponential(30),
            "total_value": np.random.lognormal(10, 1),
            "unique_addresses": np.random.poisson(1000),
            "failed_transactions": np.random.binomial(150, 0.05),
            "mev_opportunities": np.random.poisson(5),
            "large_transfers": np.random.poisson(10),
            "suspicious_activity": np.random.poisson(2),
            "network_hashrate": np.random.normal(300, 50),  # TH/s
            "pending_transactions": np.random.poisson(5000),
            "average_block_time": np.random.normal(12, 1),  # seconds
            "total_fees": np.random.lognormal(8, 1),
            "active_validators": np.random.normal(800000, 1000)
        }
        
        # Store historical data for trends
        self.dashboard_data["transaction_count"].append(data["transaction_count"])
        self.dashboard_data["gas_price"].append(data["gas_price"])
        self.dashboard_data["total_value"].append(data["total_value"])
        
        # Keep only last 1000 points
        for key in self.dashboard_data:
            if len(self.dashboard_data[key]) > 1000:
                self.dashboard_data[key] = self.dashboard_data[key][-1000:]
        
        return data
    
    async def _create_real_time_visualizations(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create real-time visualizations"""
        visualizations = []
        
        # 1. Transaction Volume Chart
        if len(self.dashboard_data["transaction_count"]) > 10:
            tx_chart = go.Figure()
            tx_chart.add_trace(go.Scatter(
                y=self.dashboard_data["transaction_count"][-100:],
                mode='lines',
                name='Transaction Count',
                line=dict(color='blue', width=2)
            ))
            tx_chart.update_layout(
                title="Real-time Transaction Volume",
                xaxis_title="Time",
                yaxis_title="Transaction Count",
                height=300,
                showlegend=False
            )
            visualizations.append({
                'type': 'transaction_volume',
                'chart': tx_chart.to_json(),
                'title': 'Real-time Transaction Volume'
            })
        
        # 2. Gas Price Chart
        if len(self.dashboard_data["gas_price"]) > 10:
            gas_chart = go.Figure()
            gas_chart.add_trace(go.Scatter(
                y=self.dashboard_data["gas_price"][-100:],
                mode='lines',
                name='Gas Price',
                line=dict(color='orange', width=2)
            ))
            gas_chart.update_layout(
                title="Real-time Gas Price",
                xaxis_title="Time",
                yaxis_title="Gas Price (gwei)",
                height=300,
                showlegend=False
            )
            visualizations.append({
                'type': 'gas_price',
                'chart': gas_chart.to_json(),
                'title': 'Real-time Gas Price'
            })
        
        # 3. Network Activity Gauge
        network_activity = min(data["transaction_count"] / 200, 1.0)  # Normalize to 0-1
        gauge_chart = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=network_activity * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Network Activity"},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        gauge_chart.update_layout(height=300)
        visualizations.append({
            'type': 'network_activity_gauge',
            'chart': gauge_chart.to_json(),
            'title': 'Network Activity Gauge'
        })
        
        # 4. Risk Metrics
        risk_metrics = {
            "Transaction Failure Rate": data["failed_transactions"] / data["transaction_count"] * 100,
            "MEV Activity": data["mev_opportunities"] / 10 * 100,
            "Suspicious Activity": data["suspicious_activity"] / 5 * 100,
            "Large Transfer Volume": data["large_transfers"] / 20 * 100
        }
        
        risk_chart = go.Figure()
        risk_chart.add_trace(go.Bar(
            x=list(risk_metrics.keys()),
            y=list(risk_metrics.values()),
            marker_color=['red' if v > 50 else 'orange' if v > 25 else 'green' for v in risk_metrics.values()]
        ))
        risk_chart.update_layout(
            title="Real-time Risk Metrics",
            xaxis_title="Risk Metric",
            yaxis_title="Risk Score (%)",
            height=300
        )
        visualizations.append({
            'type': 'risk_metrics',
            'chart': risk_chart.to_json(),
            'title': 'Real-time Risk Metrics'
        })
        
        return visualizations

manager = ConnectionManager()

@app.get("/")
async def get_dashboard():
    """Serve the real-time dashboard HTML"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Real-time Blockchain Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
            .dashboard { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .chart-container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }
            .metric-card { background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metric-value { font-size: 24px; font-weight: bold; color: #333; }
            .metric-label { font-size: 12px; color: #666; margin-top: 5px; }
            .status { padding: 10px; background: #e8f5e8; border-radius: 5px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <h1>Real-time Blockchain Dashboard</h1>
        <div class="status" id="status">Connecting...</div>
        
        <div class="metrics" id="metrics">
            <div class="metric-card">
                <div class="metric-value" id="tx-count">-</div>
                <div class="metric-label">Transactions</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="gas-price">-</div>
                <div class="metric-label">Gas Price (gwei)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="total-value">-</div>
                <div class="metric-label">Total Value ($)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="block-number">-</div>
                <div class="metric-label">Block Number</div>
            </div>
        </div>
        
        <div class="dashboard" id="dashboard">
            <div class="chart-container">
                <div id="tx-chart"></div>
            </div>
            <div class="chart-container">
                <div id="gas-chart"></div>
            </div>
            <div class="chart-container">
                <div id="gauge-chart"></div>
            </div>
            <div class="chart-container">
                <div id="risk-chart"></div>
            </div>
        </div>
        
        <script>
            const ws = new WebSocket('ws://localhost:5001/ws');
            const statusDiv = document.getElementById('status');
            
            ws.onopen = function(event) {
                statusDiv.innerHTML = 'Connected - Receiving real-time updates';
                statusDiv.style.background = '#e8f5e8';
            };
            
            ws.onclose = function(event) {
                statusDiv.innerHTML = 'Disconnected - Attempting to reconnect...';
                statusDiv.style.background = '#ffe8e8';
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'dashboard_update') {
                    updateDashboard(data);
                }
            };
            
            function updateDashboard(data) {
                // Update metrics
                document.getElementById('tx-count').textContent = data.data.transaction_count.toLocaleString();
                document.getElementById('gas-price').textContent = data.data.gas_price.toFixed(2);
                document.getElementById('total-value').textContent = '$' + (data.data.total_value / 1e6).toFixed(1) + 'M';
                document.getElementById('block-number').textContent = data.data.block_number.toLocaleString();
                
                // Update charts
                data.visualizations.forEach(viz => {
                    const chartData = JSON.parse(viz.chart);
                    if (viz.type === 'transaction_volume') {
                        Plotly.newPlot('tx-chart', chartData.data, chartData.layout);
                    } else if (viz.type === 'gas_price') {
                        Plotly.newPlot('gas-chart', chartData.data, chartData.layout);
                    } else if (viz.type === 'network_activity_gauge') {
                        Plotly.newPlot('gauge-chart', chartData.data, chartData.layout);
                    } else if (viz.type === 'risk_metrics') {
                        Plotly.newPlot('risk-chart', chartData.data, chartData.layout);
                    }
                });
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    """Start the data update task when the app starts"""
    manager.update_task = asyncio.create_task(manager.start_data_updates())
    logger.info("Real-time dashboard started")

@app.on_event("shutdown")
async def shutdown_event():
    """Cancel the data update task when the app shuts down"""
    if manager.update_task:
        manager.update_task.cancel()
    logger.info("Real-time dashboard stopped")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(manager.active_connections)
    }

@app.get("/api/metrics")
async def get_current_metrics():
    """Get current dashboard metrics"""
    if manager.dashboard_data:
        latest_data = {
            "transaction_count": manager.dashboard_data["transaction_count"][-1] if manager.dashboard_data["transaction_count"] else 0,
            "gas_price": manager.dashboard_data["gas_price"][-1] if manager.dashboard_data["gas_price"] else 0,
            "total_value": manager.dashboard_data["total_value"][-1] if manager.dashboard_data["total_value"] else 0,
            "timestamp": datetime.now().isoformat()
        }
        return latest_data
    else:
        return {"message": "No data available yet"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001) 