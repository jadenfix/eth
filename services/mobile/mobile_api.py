#!/usr/bin/env python3
"""
Mobile API Service
Phase 7: Voice & Mobile Implementation
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import aiohttp
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from services.voiceops.voice_operations import voice_ops, VoiceCommand

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mobile API Service",
    description="Mobile and voice interface API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class VoiceCommandRequest(BaseModel):
    command_text: str
    user_id: str
    voice_enabled: bool = True

class MobileAlertRequest(BaseModel):
    alert_type: str
    message: str
    priority: str = "medium"
    user_id: str
    push_enabled: bool = True

class MobileNotificationRequest(BaseModel):
    title: str
    body: str
    user_id: str
    notification_type: str = "info"

class MobileDashboardRequest(BaseModel):
    user_id: str
    include_analytics: bool = True
    include_alerts: bool = True

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected clients
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "mobile_api",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/voice/command")
async def process_voice_command(request: VoiceCommandRequest) -> Dict[str, Any]:
    """Process voice command and return response"""
    try:
        logger.info(f"Processing voice command: {request.command_text}")
        
        # Process the voice command
        command = await voice_ops.process_voice_command(
            request.command_text, 
            request.user_id
        )
        
        # Execute the command
        result = await voice_ops.execute_voice_command(command)
        
        # Generate voice response if enabled
        voice_response = None
        if request.voice_enabled:
            response_text = result.get('message', 'Command processed')
            voice_response = await voice_ops.text_to_speech(response_text)
        
        return {
            "command_id": command.command_id,
            "intent": command.intent,
            "confidence": command.confidence,
            "result": result,
            "voice_response": voice_response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing voice command: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/text-to-speech")
async def text_to_speech(request: Dict[str, Any]) -> Dict[str, Any]:
    """Convert text to speech"""
    try:
        text = request.get('text', '')
        voice_name = request.get('voice', 'Rachel')
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        audio_data = await voice_ops.text_to_speech(text, voice_name)
        
        return {
            "audio_data": audio_data,
            "voice": voice_name,
            "text": text,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in text-to-speech: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mobile/alert")
async def send_mobile_alert(request: MobileAlertRequest) -> Dict[str, Any]:
    """Send mobile alert"""
    try:
        logger.info(f"Sending mobile alert: {request.alert_type}")
        
        # In real implementation, this would send push notification
        alert_data = {
            "alert_id": f"alert_{datetime.now().timestamp()}",
            "alert_type": request.alert_type,
            "message": request.message,
            "priority": request.priority,
            "user_id": request.user_id,
            "push_enabled": request.push_enabled,
            "timestamp": datetime.now().isoformat()
        }
        
        # Broadcast to connected WebSocket clients
        await manager.broadcast(json.dumps({
            "type": "alert",
            "data": alert_data
        }))
        
        return {
            "success": True,
            "alert_id": alert_data["alert_id"],
            "message": "Alert sent successfully"
        }
        
    except Exception as e:
        logger.error(f"Error sending mobile alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mobile/notification")
async def send_mobile_notification(request: MobileNotificationRequest) -> Dict[str, Any]:
    """Send mobile notification"""
    try:
        logger.info(f"Sending mobile notification: {request.title}")
        
        notification_data = {
            "notification_id": f"notif_{datetime.now().timestamp()}",
            "title": request.title,
            "body": request.body,
            "user_id": request.user_id,
            "notification_type": request.notification_type,
            "timestamp": datetime.now().isoformat()
        }
        
        # Broadcast to connected WebSocket clients
        await manager.broadcast(json.dumps({
            "type": "notification",
            "data": notification_data
        }))
        
        return {
            "success": True,
            "notification_id": notification_data["notification_id"],
            "message": "Notification sent successfully"
        }
        
    except Exception as e:
        logger.error(f"Error sending mobile notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mobile/dashboard")
async def get_mobile_dashboard(request: MobileDashboardRequest) -> Dict[str, Any]:
    """Get mobile dashboard data"""
    try:
        logger.info(f"Getting mobile dashboard for user: {request.user_id}")
        
        dashboard_data = {
            "user_id": request.user_id,
            "dashboard_id": f"dashboard_{datetime.now().timestamp()}",
            "last_updated": datetime.now().isoformat()
        }
        
        if request.include_analytics:
            # Get analytics data
            dashboard_data["analytics"] = {
                "total_transactions": 15000,
                "active_addresses": 5000,
                "risk_score": 0.15,
                "mev_opportunities": 25
            }
        
        if request.include_alerts:
            # Get recent alerts
            dashboard_data["alerts"] = [
                {
                    "id": "alert_1",
                    "type": "high_risk",
                    "message": "High risk transaction detected",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error getting mobile dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mobile/voices")
async def get_available_voices() -> Dict[str, Any]:
    """Get available voices for TTS"""
    try:
        voices = list(voice_ops.voices.keys())
        return {
            "voices": voices,
            "count": len(voices),
            "default_voice": "Rachel"
        }
        
    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mobile/command-history")
async def get_command_history(user_id: str, limit: int = 10) -> Dict[str, Any]:
    """Get voice command history for user"""
    try:
        # Filter commands by user_id
        user_commands = [
            cmd for cmd in voice_ops.command_history 
            if cmd.user_id == user_id
        ]
        
        # Sort by timestamp and limit
        sorted_commands = sorted(
            user_commands, 
            key=lambda x: x.timestamp, 
            reverse=True
        )[:limit]
        
        return {
            "user_id": user_id,
            "commands": [
                {
                    "command_id": cmd.command_id,
                    "command_text": cmd.command_text,
                    "intent": cmd.intent,
                    "confidence": cmd.confidence,
                    "timestamp": cmd.timestamp.isoformat()
                }
                for cmd in sorted_commands
            ],
            "total_commands": len(user_commands)
        }
        
    except Exception as e:
        logger.error(f"Error getting command history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/mobile")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time mobile updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "subscribe":
                # Subscribe to specific updates
                await manager.send_personal_message(
                    json.dumps({
                        "type": "subscribed",
                        "message": "Successfully subscribed to updates"
                    }),
                    websocket
                )
            
            elif message.get("type") == "ping":
                # Respond to ping
                await manager.send_personal_message(
                    json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/mobile/status")
async def get_mobile_status() -> Dict[str, Any]:
    """Get mobile service status"""
    return {
        "status": "operational",
        "active_connections": len(manager.active_connections),
        "voice_ops_available": len(voice_ops.voices) > 0,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Mobile API Service")
    parser.add_argument("--port", type=int, default=5005, help="Port to run on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    args = parser.parse_args()
    
    logger.info(f"Starting Mobile API Service on {args.host}:{args.port}")
    uvicorn.run(
        "mobile_api:app",
        host=args.host,
        port=args.port,
        reload=True,
        log_level="info"
    ) 