#!/usr/bin/env python3
"""
Voice Operations Service
ElevenLabs TTS with WebSocket support for real-time audio
"""
import os
import json
import asyncio
import websockets
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
from dotenv import load_dotenv
import logging
from datetime import datetime
import base64

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice Operations Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VoiceOpsService:
    def __init__(self):
        self.elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
        self.voice_id = os.getenv('ELEVENLABS_VOICE_ID')
        self.connections = set()
        
    def text_to_speech(self, text, voice_id=None):
        """Convert text to speech using ElevenLabs"""
        if not voice_id:
            voice_id = self.voice_id
            
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.elevenlabs_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None
    
    def get_voices(self):
        """Get available voices from ElevenLabs"""
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {"xi-api-key": self.elevenlabs_key}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error fetching voices: {e}")
            return None
    
    async def broadcast_audio(self, audio_data, text):
        """Broadcast audio to all WebSocket connections"""
        if self.connections and audio_data:
            # Encode audio as base64 for transmission
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            message = json.dumps({
                "type": "audio",
                "text": text,
                "audio": audio_b64,
                "timestamp": datetime.now().isoformat()
            })
            
            await asyncio.gather(
                *[conn.send(message) for conn in self.connections],
                return_exceptions=True
            )

# Initialize service
voice_service = VoiceOpsService()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        voices = voice_service.get_voices()
        voice_count = len(voices.get('voices', [])) if voices else 0
        return {
            "status": "healthy", 
            "elevenlabs": "connected",
            "available_voices": voice_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/api/voices")
async def get_voices():
    """Get available ElevenLabs voices"""
    try:
        voices = voice_service.get_voices()
        return voices or {"error": "Failed to fetch voices"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/tts")
async def text_to_speech(request: dict):
    """Convert text to speech"""
    try:
        text = request.get('text', '')
        voice_id = request.get('voice_id', voice_service.voice_id)
        
        if not text:
            return {"error": "Text is required"}
        
        # Generate speech
        audio_data = voice_service.text_to_speech(text, voice_id)
        
        if audio_data:
            # Broadcast to WebSocket connections
            await voice_service.broadcast_audio(audio_data, text)
            
            # Return base64 encoded audio
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            return {
                "status": "success",
                "text": text,
                "audio": audio_b64,
                "voice_id": voice_id
            }
        else:
            return {"error": "Failed to generate speech"}
            
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return {"error": str(e)}

@app.post("/api/alert")
async def send_voice_alert(request: dict):
    """Send voice alert for important events"""
    try:
        alert_type = request.get('type', 'info')
        message = request.get('message', '')
        
        # Create alert text
        alert_text = f"Alert: {alert_type}. {message}"
        
        # Generate speech
        audio_data = voice_service.text_to_speech(alert_text)
        
        if audio_data:
            # Broadcast to all connected clients
            await voice_service.broadcast_audio(audio_data, alert_text)
            
            logger.info(f"✅ Voice alert sent: {alert_type}")
            return {
                "status": "success",
                "alert_type": alert_type,
                "message": message
            }
        else:
            return {"error": "Failed to generate alert"}
            
    except Exception as e:
        logger.error(f"Alert error: {e}")
        return {"error": str(e)}

@app.websocket("/voice")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time voice updates"""
    await websocket.accept()
    voice_service.connections.add(websocket)
    logger.info(f"Voice WebSocket connected. Total connections: {len(voice_service.connections)}")
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connection_ack",
            "timestamp": datetime.now().isoformat()
        })
        
        # Listen for messages
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            if data.get('type') == 'tts_request':
                text = data.get('text', '')
                if text:
                    audio_data = voice_service.text_to_speech(text)
                    if audio_data:
                        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
                        await websocket.send_json({
                            "type": "audio",
                            "text": text,
                            "audio": audio_b64,
                            "timestamp": datetime.now().isoformat()
                        })
            
    except Exception as e:
        logger.error(f"Voice WebSocket error: {e}")
    finally:
        voice_service.connections.discard(websocket)
        logger.info(f"Voice WebSocket disconnected. Total connections: {len(voice_service.connections)}")

if __name__ == "__main__":
    logger.info("🚀 Starting Voice Operations Service...")
    logger.info(f"ElevenLabs Voice ID: {os.getenv('ELEVENLABS_VOICE_ID')}")
    logger.info(f"Server will run on: http://localhost:5000")
    logger.info(f"WebSocket endpoint: ws://localhost:5000/voice")
    
    uvicorn.run(app, host="0.0.0.0", port=5000)
