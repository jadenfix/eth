#!/usr/bin/env python3
"""
Voice Operations Service
Phase 7: Voice & Mobile Implementation
"""

import asyncio
import json
import websockets
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import aiohttp
import base64
import logging
import os
import re
try:
    from elevenlabs import generate, save, set_api_key
    from elevenlabs import voices, Voice, VoiceSettings
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    # Mock functions for testing
    def generate(*args, **kwargs):
        return b'mock_audio_data'
    def save(*args, **kwargs):
        pass
    def set_api_key(*args, **kwargs):
        pass
    def voices():
        return []
    class Voice:
        def __init__(self, name):
            self.name = name
    class VoiceSettings:
        pass

@dataclass
class VoiceCommand:
    command_id: str
    user_id: str
    command_text: str
    intent: str
    confidence: float
    parameters: Dict[str, Any]
    timestamp: datetime
    processed: bool = False

@dataclass
class VoiceAlert:
    alert_id: str
    alert_type: str
    message: str
    priority: str  # 'low', 'medium', 'high', 'critical'
    voice_enabled: bool = True
    timestamp: datetime = None

class VoiceOperations:
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY', 'mock_key_for_testing')
        if self.api_key != 'mock_key_for_testing':
            set_api_key(self.api_key)
        self.voices = self._load_voices()
        self.active_connections = set()
        self.command_history = []
        self.alert_queue = asyncio.Queue()
        
    def _load_voices(self) -> Dict[str, Voice]:
        """Load available ElevenLabs voices"""
        try:
            if self.api_key == 'mock_key_for_testing':
                # Return mock voices for testing
                return {
                    'Rachel': MockVoice('Rachel'),
                    'Adam': MockVoice('Adam'),
                    'Sarah': MockVoice('Sarah')
                }
            
            available_voices = voices()
            voice_dict = {}
            for voice in available_voices:
                voice_dict[voice.name] = voice
            return voice_dict
        except Exception as e:
            logging.error(f"Error loading voices: {e}")
            return {}
    
    async def text_to_speech(self, text: str, voice_name: str = "Rachel", 
                           model: str = "eleven_monolingual_v1") -> bytes:
        """Convert text to speech using ElevenLabs"""
        try:
            if self.api_key == 'mock_key_for_testing':
                # Return mock audio data for testing
                return b'mock_audio_data_for_testing'
            
            voice = self.voices.get(voice_name)
            if not voice:
                # Use default voice if specified voice not found
                voice = list(self.voices.values())[0] if self.voices else None
            
            audio = generate(
                text=text,
                voice=voice,
                model=model
            )
            
            return audio
            
        except Exception as e:
            logging.error(f"Error in text-to-speech: {e}")
            raise
    
    async def speech_to_text(self, audio_data: bytes) -> str:
        """Convert speech to text (placeholder for STT service)"""
        # In real implementation, this would use a speech-to-text service
        # For now, return a placeholder
        return "show dashboard"
    
    async def process_voice_command(self, command_text: str, user_id: str) -> VoiceCommand:
        """Process voice command and extract intent"""
        try:
            # Simple intent recognition (in real implementation, use NLP/ML)
            intent, confidence, parameters = await self._extract_intent(command_text)
            
            command = VoiceCommand(
                command_id=f"cmd_{datetime.now().timestamp()}",
                user_id=user_id,
                command_text=command_text,
                intent=intent,
                confidence=confidence,
                parameters=parameters,
                timestamp=datetime.now()
            )
            
            # Store command history
            self.command_history.append(command)
            
            # Ensure command history is properly stored
            logging.info(f"Stored command: {command.command_id} for user: {user_id}")
            
            return command
            
        except Exception as e:
            logging.error(f"Error processing voice command: {e}")
            raise
    
    async def _extract_intent(self, command_text: str) -> tuple:
        """Extract intent from command text"""
        command_lower = command_text.lower()
        
        # Simple keyword-based intent recognition
        if any(word in command_lower for word in ['show', 'display', 'get']):
            if 'analytics' in command_lower:
                return 'show_analytics', 0.9, {'page': 'analytics'}
            elif 'dashboard' in command_lower:
                return 'show_dashboard', 0.9, {'page': 'dashboard'}
            elif 'mev' in command_lower:
                return 'show_mev', 0.9, {'page': 'mev'}
            elif 'risk' in command_lower:
                return 'show_risk', 0.9, {'page': 'risk'}
        
        elif any(word in command_lower for word in ['alert', 'alarm', 'warning']):
            return 'check_alerts', 0.8, {}
        
        elif any(word in command_lower for word in ['freeze', 'block', 'stop']):
            if 'address' in command_lower:
                # Extract address from command
                address_match = re.search(r'0x[a-fA-F0-9]{40}', command_text)
                if address_match:
                    return 'freeze_address', 0.7, {'address': address_match.group()}
        
        elif any(word in command_lower for word in ['status', 'health', 'system']):
            return 'system_status', 0.9, {}
        
        # Handle complex commands with multiple keywords
        elif 'freeze' in command_lower and 'address' in command_lower:
            # Extract address from command
            address_match = re.search(r'0x[a-fA-F0-9]{40}', command_text)
            if address_match:
                return 'freeze_address', 0.7, {'address': address_match.group()}
        
        elif 'what' in command_lower and 'status' in command_lower:
            return 'system_status', 0.9, {}
        
        elif 'show' in command_lower and 'analytics' in command_lower:
            return 'show_analytics', 0.9, {'page': 'analytics'}
        elif 'analytics' in command_lower and 'dashboard' in command_lower:
            return 'show_analytics', 0.9, {'page': 'analytics'}
        
        elif 'check' in command_lower and ('alert' in command_lower or 'warning' in command_lower):
            return 'check_alerts', 0.8, {}
        
        # Default intent
        return 'unknown', 0.1, {}
    
    async def execute_voice_command(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute voice command and return result"""
        try:
            if command.intent == 'show_dashboard':
                return await self._handle_show_dashboard(command)
            elif command.intent == 'show_analytics':
                return await self._handle_show_analytics(command)
            elif command.intent == 'show_mev':
                return await self._handle_show_mev(command)
            elif command.intent == 'show_risk':
                return await self._handle_show_risk(command)
            elif command.intent == 'check_alerts':
                return await self._handle_check_alerts(command)
            elif command.intent == 'freeze_address':
                return await self._handle_freeze_address(command)
            elif command.intent == 'system_status':
                return await self._handle_system_status(command)
            else:
                return {
                    'success': False,
                    'message': f"Unknown command: {command.command_text}",
                    'intent': command.intent
                }
                
        except Exception as e:
            logging.error(f"Error executing voice command: {e}")
            return {
                'success': False,
                'message': f"Error executing command: {str(e)}",
                'intent': command.intent
            }
    
    async def _handle_show_dashboard(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle show dashboard command"""
        return {
            'success': True,
            'action': 'navigate',
            'page': 'dashboard',
            'message': 'Navigating to dashboard'
        }
    
    async def _handle_show_analytics(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle show analytics command"""
        return {
            'success': True,
            'action': 'navigate',
            'page': 'analytics',
            'message': 'Navigating to analytics'
        }
    
    async def _handle_show_mev(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle show MEV command"""
        return {
            'success': True,
            'action': 'navigate',
            'page': 'mev',
            'message': 'Navigating to MEV detection'
        }
    
    async def _handle_show_risk(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle show risk command"""
        return {
            'success': True,
            'action': 'navigate',
            'page': 'risk',
            'message': 'Navigating to risk analysis'
        }
    
    async def _handle_check_alerts(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle check alerts command"""
        # Get recent alerts
        recent_alerts = await self._get_recent_alerts()
        
        if recent_alerts:
            alert_summary = f"Found {len(recent_alerts)} recent alerts"
            return {
                'success': True,
                'action': 'show_alerts',
                'alerts': recent_alerts,
                'message': alert_summary
            }
        else:
            return {
                'success': True,
                'action': 'show_alerts',
                'alerts': [],
                'message': 'No recent alerts found'
            }
    
    async def _handle_freeze_address(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle freeze address command"""
        address = command.parameters.get('address')
        if not address:
            return {
                'success': False,
                'message': 'No address specified for freezing'
            }
        
        # Call action executor to freeze address
        try:
            # This would call the action executor service
            freeze_result = await self._execute_freeze_action(address)
            return {
                'success': True,
                'action': 'freeze_address',
                'address': address,
                'result': freeze_result,
                'message': f'Address {address} frozen successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to freeze address: {str(e)}'
            }
    
    async def _handle_system_status(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle system status command"""
        # Get system health status
        health_status = await self._get_system_health()
        
        status_message = f"System status: {health_status['overall_status']}"
        if health_status['overall_status'] == 'healthy':
            status_message += ". All systems operational."
        else:
            status_message += f". {health_status['issues_count']} issues detected."
        
        return {
            'success': True,
            'action': 'show_status',
            'status': health_status,
            'message': status_message
        }
    
    async def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        # In real implementation, this would fetch from database
        return [
            {
                'id': 'alert_1',
                'type': 'high_risk',
                'message': 'High risk transaction detected',
                'timestamp': datetime.now().isoformat()
            }
        ]
    
    async def _execute_freeze_action(self, address: str) -> Dict[str, Any]:
        """Execute freeze action"""
        # In real implementation, this would call the action executor
        return {
            'action_id': f'freeze_{address}',
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        # In real implementation, this would check all services
        return {
            'overall_status': 'healthy',
            'services': {
                'ethereum_ingester': 'running',
                'graph_api': 'running',
                'voice_ops': 'running'
            },
            'issues_count': 0,
            'timestamp': datetime.now().isoformat()
        }

class MockVoice:
    """Mock voice for testing"""
    def __init__(self, name: str):
        self.name = name

# Global voice operations instance
voice_ops = VoiceOperations()

if __name__ == "__main__":
    # Test voice operations
    async def test_voice_ops():
        command = await voice_ops.process_voice_command("show dashboard", "user123")
        result = await voice_ops.execute_voice_command(command)
        print(f"Command: {command.command_text}")
        print(f"Intent: {command.intent}")
        print(f"Result: {result}")
    
    asyncio.run(test_voice_ops()) 