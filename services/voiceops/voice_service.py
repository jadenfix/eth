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
import io

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
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
        # Parsing and alert formatting do not require a provider or microphone.
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.logger = logger.bind(service="voice-service")
        self.recognizer = None
        self.microphone = None

    def _recognizer(self):
        import speech_recognition as sr

        if self.recognizer is None:
            self.recognizer = sr.Recognizer()
        return self.recognizer

    async def text_to_speech(
        self,
        text: str,
        voice_id: str = None,
        priority: AlertPriority = AlertPriority.MEDIUM,
    ) -> bytes:
        """Call the declared ElevenLabs SDK; missing credentials fail explicitly."""
        from elevenlabs import generate, Voice, VoiceSettings

        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable not set")
        settings = {
            AlertPriority.LOW: (0.7, 0.3),
            AlertPriority.MEDIUM: (0.6, 0.5),
            AlertPriority.HIGH: (0.4, 0.7),
            AlertPriority.CRITICAL: (0.2, 0.9),
        }
        stability, similarity = settings[priority]
        return await asyncio.to_thread(
            generate,
            text=text,
            api_key=self.api_key,
            voice=Voice(
                voice_id=voice_id
                or os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
                settings=VoiceSettings(
                    stability=stability, similarity_boost=similarity
                ),
            ),
            model="eleven_multilingual_v2",
        )

    async def speech_to_text(self, audio_data: bytes) -> str:
        """Decode an actual WAV/AIFF/FLAC file and request Google recognition."""
        import speech_recognition as sr

        recognizer = self._recognizer()

        def transcribe():
            with sr.AudioFile(io.BytesIO(audio_data)) as source:
                audio = recognizer.record(source)
            return recognizer.recognize_google(audio)

        return await asyncio.to_thread(transcribe)

    async def listen_for_command(self, timeout: int = 5) -> Optional[str]:
        """Microphone/PyAudio are optional until this hardware operation is invoked."""
        import speech_recognition as sr

        recognizer = self._recognizer()

        def listen():
            if self.microphone is None:
                self.microphone = sr.Microphone()
            with self.microphone as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=timeout)
            return recognizer.recognize_google(audio)

        try:
            return await asyncio.to_thread(listen)
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return None


class AlertTemplates:
    """Pre-defined alert message templates."""

    MEV_ATTACK = "Critical MEV attack detected! {description}. Confidence: {confidence}%. Immediate attention required."

    HIGH_VALUE_TRANSFER = "High value transfer alert: {value} dollars moved from {from_addr} to {to_addr}."

    WHALE_MOVEMENT = (
        "Whale activity detected: {description}. This could impact market conditions."
    )

    SANCTIONS_VIOLATION = (
        "URGENT: Potential sanctions violation detected involving address {address}."
    )

    SYSTEM_ERROR = "System alert: {service} is experiencing issues. {description}"

    NETWORK_ANOMALY = (
        "Network anomaly detected: {description}. Risk score: {risk_score}."
    )


class CommandProcessor:
    """Process and route voice commands."""

    def __init__(self):
        self.logger = logger.bind(service="command-processor")

        # Command patterns
        self.command_patterns = {
            r"show.*signals?": "show_signals",
            r"what.*happening": "system_status",
            r"alert.*level": "alert_level",
            r"unmute.*alerts?": "unmute_alerts",
            r"\bmute.*alerts?": "mute_alerts",
            r"search.*address": "search_address",
            r"get.*entity": "get_entity",
            r"risk.*score": "get_risk_score",
        }

    def parse_command(self, text: str) -> VoiceCommand:
        """Parse voice command text into structured command."""
        import re

        original_text = text.strip()
        text = original_text.lower()

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
            addr_match = re.search(r"0x[a-fA-F0-9]{40}\b", original_text)
            if addr_match:
                entities["address"] = addr_match.group()

        elif intent == "alert_level":
            # Look for severity levels
            for level in ["low", "medium", "high", "critical"]:
                if level in text:
                    entities["level"] = level
                    break

        return VoiceCommand(
            command=original_text,
            intent=intent,
            entities=entities,
            confidence=0.8,  # Simple confidence score
            timestamp=datetime.now(),
        )

    async def execute_command(self, command: VoiceCommand) -> str:
        """Execute parsed voice command."""
        try:
            if command.intent == "show_signals":
                return await self._get_recent_signals()

            elif command.intent == "system_status":
                return await self._get_system_status()

            elif command.intent == "search_address":
                address = command.entities.get("address")
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
        raise RuntimeError("Signal provider is not connected")

    async def _get_system_status(self) -> str:
        """Get system health status."""
        raise RuntimeError("System health provider is not connected")

    async def _search_address(self, address: str) -> str:
        """Search for address information."""
        raise RuntimeError("Address intelligence provider is not connected")

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
                    alert.message, alert.voice_id, alert.priority
                )

                # Play audio (in production, this would use proper audio output)
                self.logger.info(
                    "Generated voice audio; playback sink is not configured",
                    audio_bytes=len(audio),
                )

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
                        alert = VoiceAlert(message=response, priority=AlertPriority.LOW)
                        await self.queue_alert(alert)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Error in command listening", error=str(e))
                await asyncio.sleep(1)

    def create_signal_alert(self, signal: Dict[str, Any]) -> VoiceAlert:
        """Create voice alert from AI signal."""
        signal_type = signal.get("signal_type", "UNKNOWN")
        description = signal.get("description", "Signal detected")
        severity = signal.get("severity", "LOW")
        confidence = signal.get("confidence_score", 0) * 100

        # Map severity to priority
        priority_map = {
            "LOW": AlertPriority.LOW,
            "MEDIUM": AlertPriority.MEDIUM,
            "HIGH": AlertPriority.HIGH,
            "CRITICAL": AlertPriority.CRITICAL,
        }
        priority = priority_map.get(severity, AlertPriority.MEDIUM)

        # Choose appropriate template
        if signal_type == "MEV_ATTACK" or signal_type == "SANDWICH_ATTACK":
            message = AlertTemplates.MEV_ATTACK.format(
                description=description, confidence=int(confidence)
            )
        elif signal_type == "HIGH_VALUE_TRANSFER":
            addresses = signal.get("related_addresses") or ["Unknown"]
            message = (
                description
                + ". "
                + AlertTemplates.HIGH_VALUE_TRANSFER.format(
                    value=signal.get("metadata", {}).get("value_usd", "Unknown"),
                    from_addr=addresses[0][:10],
                    to_addr=addresses[-1][:10],
                )
            )
        else:
            message = f"Alert: {description}. Confidence: {int(confidence)}%."

        return VoiceAlert(message=message, priority=priority)


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

    async def _post(self, url: str, payload: dict):
        if not url or not url.startswith(("http://", "https://")):
            raise ValueError("A valid notification webhook URL is required")
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.post(url, json=payload) as response:
                response.raise_for_status()

    async def send_slack_alert(self, signal: Dict[str, Any]):
        await self._post(
            os.getenv("SLACK_WEBHOOK_URL", ""),
            {"text": signal.get("description", "Signal alert")},
        )

    async def send_email_alert(self, signal: Dict[str, Any]):
        import smtplib
        from email.message import EmailMessage

        host, recipient, sender = (
            os.getenv(key)
            for key in ("SMTP_HOST", "ALERT_EMAIL_TO", "ALERT_EMAIL_FROM")
        )
        if not all((host, recipient, sender)):
            raise ValueError(
                "SMTP_HOST, ALERT_EMAIL_TO and ALERT_EMAIL_FROM are required"
            )
        message = EmailMessage()
        message["From"], message["To"], message["Subject"] = (
            sender,
            recipient,
            "Onchain signal alert",
        )
        message.set_content(json.dumps(signal, default=str))

        def deliver():
            with smtplib.SMTP(
                host, int(os.getenv("SMTP_PORT", "587")), timeout=10
            ) as client:
                client.starttls()
                if os.getenv("SMTP_USER"):
                    client.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
                client.send_message(message)

        await asyncio.to_thread(deliver)

    async def send_webhook_alert(self, signal: Dict[str, Any]):
        await self._post(os.getenv("ALERT_WEBHOOK_URL", ""), signal)


async def main():
    """Main VoiceOps service entry point."""
    service = VoiceOpsService()

    try:
        await service.start()

        # Example: Queue a test alert
        test_alert = VoiceAlert(
            message="VoiceOps service started successfully. Ready for commands.",
            priority=AlertPriority.LOW,
        )
        await service.queue_alert(test_alert)

        # Keep running
        await asyncio.sleep(3600)  # Run for 1 hour

    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
