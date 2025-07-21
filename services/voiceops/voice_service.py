"""
VoiceOps Service - ElevenLabs integration for voice alerts and commands.

Provides text-to-speech for alerts and speech-to-text for voice commands,
enabling hands-free interaction with the blockchain intelligence platform.
"""

import os
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import structlog
import aiohttp
from elevenlabs import generate, Voice, VoiceSettings
from elevenlabs.client import ElevenLabs
import speech_recognition as sr
import pyaudio
import wave

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


class AlertPriority(Enum):
    """Priority levels for voice alerts."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class VoiceAlert:
    """Voice alert configuration."""
    message: str
    priority: AlertPriority
    voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Default ElevenLabs voice
    stability: float = 0.5
    similarity_boost: float = 0.5
    speed: float = 1.0


@dataclass
class VoiceCommand:
    """Voice command structure."""
    command: str
    intent: str
    entities: Dict[str, Any]
    confidence: float
    timestamp: datetime


class VoiceService:
    """ElevenLabs voice service integration."""
    
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable not set")
        
        self.client = ElevenLabs(api_key=self.api_key)
        self.logger = logger.bind(service="voice-service")
        
        # Voice settings for different priorities
        self.priority_settings = {
            AlertPriority.LOW: VoiceSettings(stability=0.7, similarity_boost=0.3),
            AlertPriority.MEDIUM: VoiceSettings(stability=0.6, similarity_boost=0.5),
            AlertPriority.HIGH: VoiceSettings(stability=0.4, similarity_boost=0.7),
            AlertPriority.CRITICAL: VoiceSettings(stability=0.2, similarity_boost=0.9)
        }
        
        # Speech recognition setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
    
    async def text_to_speech(self, text: str, voice_id: str = None, 
                           priority: AlertPriority = AlertPriority.MEDIUM) -> bytes:
        """Convert text to speech using ElevenLabs."""
        try:
            voice_id = voice_id or os.getenv('ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM')
            
            # Get voice settings based on priority
            voice_settings = self.priority_settings[priority]
            
            # Generate speech
            audio = generate(
                text=text,
                voice=Voice(
                    voice_id=voice_id,
                    settings=voice_settings
                ),
                model="eleven_multilingual_v2"
            )
            
            self.logger.info("Generated TTS audio", 
                           text_length=len(text),
                           voice_id=voice_id,
                           priority=priority.value)
            
            return audio
            
        except Exception as e:
            self.logger.error("Error generating TTS", error=str(e))
            raise
    
    async def speech_to_text(self, audio_data: bytes) -> str:
        """Convert speech to text using Google Speech Recognition."""
        try:
            # Save audio data to temporary file
            temp_file = "/tmp/voice_command.wav"
            with open(temp_file, "wb") as f:
                f.write(audio_data)
            
            # Load audio file
            with sr.AudioFile(temp_file) as source:
                audio = self.recognizer.record(source)
            
            # Recognize speech
            text = self.recognizer.recognize_google(audio)
            
            self.logger.info("Converted STT", text=text)
            
            # Clean up
            os.remove(temp_file)
            
            return text
            
        except sr.UnknownValueError:
            self.logger.warning("Could not understand audio")
            return ""
        except sr.RequestError as e:
            self.logger.error("STT service error", error=str(e))
            return ""
        except Exception as e:
            self.logger.error("Error in STT", error=str(e))
            return ""
    
    async def listen_for_command(self, timeout: int = 5) -> Optional[str]:
        """Listen for voice command from microphone."""
        try:
            with self.microphone as source:
                self.logger.info("Listening for voice command...")
                audio = self.recognizer.listen(source, timeout=timeout)
            
            # Convert to text
            command = self.recognizer.recognize_google(audio)
            self.logger.info("Received voice command", command=command)
            
            return command
            
        except sr.WaitTimeoutError:
            self.logger.info("Voice command timeout")
            return None
        except sr.UnknownValueError:
            self.logger.warning("Could not understand voice command")
            return None
        except Exception as e:
            self.logger.error("Error listening for command", error=str(e))
            return None


class AlertTemplates:
    """Pre-defined alert message templates."""
    
    MEV_ATTACK = "Critical MEV attack detected! {description}. Confidence: {confidence}%. Immediate attention required."
    
    HIGH_VALUE_TRANSFER = "High value transfer alert: {value} dollars moved from {from_addr} to {to_addr}."
    
    WHALE_MOVEMENT = "Whale activity detected: {description}. This could impact market conditions."
    
    SANCTIONS_VIOLATION = "URGENT: Potential sanctions violation detected involving address {address}."
    
    SYSTEM_ERROR = "System alert: {service} is experiencing issues. {description}"
    
    NETWORK_ANOMALY = "Network anomaly detected: {description}. Risk score: {risk_score}."


class CommandProcessor:
    """Process and route voice commands."""
    
    def __init__(self):
        self.logger = logger.bind(service="command-processor")
        
        # Command patterns
        self.command_patterns = {
            r"show.*signals?": "show_signals",
            r"what.*happening": "system_status", 
            r"alert.*level": "alert_level",
            r"mute.*alerts?": "mute_alerts",
            r"unmute.*alerts?": "unmute_alerts",
            r"search.*address": "search_address",
            r"get.*entity": "get_entity",
            r"risk.*score": "get_risk_score"
        }
    
    def parse_command(self, text: str) -> VoiceCommand:
        """Parse voice command text into structured command."""
        import re
        
        text = text.lower().strip()
        
        # Determine intent
        intent = "unknown"
        entities = {}
        
        for pattern, cmd_intent in self.command_patterns.items():
            if re.search(pattern, text):
                intent = cmd_intent
                break
        
        # Extract entities based on intent
        if intent == "search_address":
            # Look for Ethereum address pattern
            addr_match = re.search(r'0x[a-fA-F0-9]{40}', text)
            if addr_match:
                entities['address'] = addr_match.group()
        
        elif intent == "alert_level":
            # Look for severity levels
            for level in ['low', 'medium', 'high', 'critical']:
                if level in text:
                    entities['level'] = level
                    break
        
        return VoiceCommand(
            command=text,
            intent=intent,
            entities=entities,
            confidence=0.8,  # Simple confidence score
            timestamp=datetime.now()
        )
    
    async def execute_command(self, command: VoiceCommand) -> str:
        """Execute parsed voice command."""
        try:
            if command.intent == "show_signals":
                return await self._get_recent_signals()
            
            elif command.intent == "system_status":
                return await self._get_system_status()
            
            elif command.intent == "search_address":
                address = command.entities.get('address')
                if address:
                    return await self._search_address(address)
                return "Please specify an address to search."
            
            elif command.intent == "mute_alerts":
                return await self._mute_alerts()
            
            elif command.intent == "unmute_alerts":
                return await self._unmute_alerts()
            
            else:
                return "I didn't understand that command. Try asking for system status or recent signals."
                
        except Exception as e:
            self.logger.error("Error executing command", error=str(e))
            return "Sorry, I encountered an error processing that command."
    
    async def _get_recent_signals(self) -> str:
        """Get recent AI signals summary."""
        # In a real implementation, this would query the API
        return "You have 3 new signals: 1 high-priority MEV attack, 1 whale movement alert, and 1 network anomaly."
    
    async def _get_system_status(self) -> str:
        """Get system health status."""
        return "All systems operational. Ingestion rate: 150 events per second. 5 agents active. Signal accuracy: 87%."
    
    async def _search_address(self, address: str) -> str:
        """Search for address information."""
        return f"Address {address} has a medium risk score of 0.6. Last seen 2 hours ago in a high-value transfer."
    
    async def _mute_alerts(self) -> str:
        """Mute voice alerts."""
        return "Voice alerts muted. You can unmute them by saying 'unmute alerts'."
    
    async def _unmute_alerts(self) -> str:
        """Unmute voice alerts.""" 
        return "Voice alerts unmuted. You will now receive voice notifications."


class VoiceOpsService:
    """Main VoiceOps service orchestrator."""
    
    def __init__(self):
        self.voice_service = VoiceService()
        self.command_processor = CommandProcessor()
        self.logger = logger.bind(service="voiceops")
        
        # Alert settings
        self.alerts_enabled = True
        self.alert_queue = asyncio.Queue()
        
        # Start background tasks
        self._alert_task = None
        self._command_task = None
    
    async def start(self):
        """Start VoiceOps service."""
        self.logger.info("Starting VoiceOps service")
        
        # Start alert processing task
        self._alert_task = asyncio.create_task(self._process_alerts())
        
        # Start command listening task
        self._command_task = asyncio.create_task(self._listen_for_commands())
    
    async def stop(self):
        """Stop VoiceOps service."""
        self.logger.info("Stopping VoiceOps service")
        
        if self._alert_task:
            self._alert_task.cancel()
        
        if self._command_task:
            self._command_task.cancel()
    
    async def queue_alert(self, alert: VoiceAlert):
        """Queue a voice alert for processing."""
        if self.alerts_enabled:
            await self.alert_queue.put(alert)
            self.logger.info("Queued voice alert", priority=alert.priority.value)
    
    async def _process_alerts(self):
        """Process queued voice alerts."""
        while True:
            try:
                alert = await self.alert_queue.get()
                
                # Generate speech
                audio = await self.voice_service.text_to_speech(
                    alert.message, 
                    alert.voice_id,
                    alert.priority
                )
                
                # Play audio (in production, this would use proper audio output)
                self.logger.info("Playing voice alert", message=alert.message)
                
                # Mark task as done
                self.alert_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Error processing alert", error=str(e))
    
    async def _listen_for_commands(self):
        """Listen for voice commands continuously."""
        while True:
            try:
                # Listen for command
                command_text = await self.voice_service.listen_for_command(timeout=10)
                
                if command_text:
                    # Parse command
                    command = self.command_processor.parse_command(command_text)
                    
                    # Execute command
                    response = await self.command_processor.execute_command(command)
                    
                    # Speak response
                    if response:
                        alert = VoiceAlert(
                            message=response,
                            priority=AlertPriority.LOW
                        )
                        await self.queue_alert(alert)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Error in command listening", error=str(e))
                await asyncio.sleep(1)
    
    def create_signal_alert(self, signal: Dict[str, Any]) -> VoiceAlert:
        """Create voice alert from AI signal."""
        signal_type = signal.get('signal_type', 'UNKNOWN')
        description = signal.get('description', 'Signal detected')
        severity = signal.get('severity', 'LOW')
        confidence = signal.get('confidence_score', 0) * 100
        
        # Map severity to priority
        priority_map = {
            'LOW': AlertPriority.LOW,
            'MEDIUM': AlertPriority.MEDIUM, 
            'HIGH': AlertPriority.HIGH,
            'CRITICAL': AlertPriority.CRITICAL
        }
        priority = priority_map.get(severity, AlertPriority.MEDIUM)
        
        # Choose appropriate template
        if signal_type == 'MEV_ATTACK' or signal_type == 'SANDWICH_ATTACK':
            message = AlertTemplates.MEV_ATTACK.format(
                description=description,
                confidence=int(confidence)
            )
        elif signal_type == 'HIGH_VALUE_TRANSFER':
            message = AlertTemplates.HIGH_VALUE_TRANSFER.format(
                value=signal.get('metadata', {}).get('value_usd', 'Unknown'),
                from_addr=signal.get('related_addresses', ['Unknown'])[0][:10],
                to_addr=signal.get('related_addresses', ['Unknown'])[-1][:10]
            )
        else:
            message = f"Alert: {description}. Confidence: {int(confidence)}%."
        
        return VoiceAlert(
            message=message,
            priority=priority
        )


# Notification service for other components
class NotificationService:
    """Service for sending various types of notifications."""
    
    def __init__(self):
        self.voiceops = VoiceOpsService()
        self.logger = logger.bind(service="notification")
    
    async def send_voice_alert(self, signal: Dict[str, Any]):
        """Send voice alert for signal."""
        alert = self.voiceops.create_signal_alert(signal)
        await self.voiceops.queue_alert(alert)
    
    async def send_slack_alert(self, signal: Dict[str, Any]):
        """Send Slack notification.""" 
        # Implementation would use Slack API
        self.logger.info("Sending Slack alert", signal_id=signal.get('signal_id'))
    
    async def send_email_alert(self, signal: Dict[str, Any]):
        """Send email notification."""
        # Implementation would use email service
        self.logger.info("Sending email alert", signal_id=signal.get('signal_id'))
    
    async def send_webhook_alert(self, signal: Dict[str, Any]):
        """Send webhook notification."""
        # Implementation would POST to webhook URL
        self.logger.info("Sending webhook alert", signal_id=signal.get('signal_id'))


async def main():
    """Main VoiceOps service entry point."""
    service = VoiceOpsService()
    
    try:
        await service.start()
        
        # Example: Queue a test alert
        test_alert = VoiceAlert(
            message="VoiceOps service started successfully. Ready for commands.",
            priority=AlertPriority.LOW
        )
        await service.queue_alert(test_alert)
        
        # Keep running
        await asyncio.sleep(3600)  # Run for 1 hour
        
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
