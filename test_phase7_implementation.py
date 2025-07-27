#!/usr/bin/env python3
"""
Phase 7 Implementation Test
Voice & Mobile Implementation
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
import aiohttp
import websockets

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.voiceops.voice_operations import voice_ops, VoiceCommand, VoiceAlert
from services.mobile.mobile_api import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Phase7TestSuite:
    """Comprehensive test suite for Phase 7 implementation"""
    
    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.total_tests = 0
        self.base_url = "http://localhost:5005"
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            logger.info(f"✅ {test_name}: PASSED")
        else:
            logger.error(f"❌ {test_name}: FAILED - {details}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    async def test_voice_operations_initialization(self):
        """Test voice operations initialization"""
        try:
            # Test voice operations initialization
            assert voice_ops is not None
            assert hasattr(voice_ops, 'voices')
            assert hasattr(voice_ops, 'command_history')
            
            self.log_test("Voice Operations Initialization", True)
        except Exception as e:
            self.log_test("Voice Operations Initialization", False, str(e))
    
    async def test_text_to_speech(self):
        """Test text-to-speech functionality"""
        try:
            test_text = "Hello, this is a test message"
            audio_data = await voice_ops.text_to_speech(test_text, "Rachel")
            
            assert audio_data is not None
            assert isinstance(audio_data, bytes)
            
            self.log_test("Text-to-Speech", True)
        except Exception as e:
            self.log_test("Text-to-Speech", False, str(e))
    
    async def test_voice_command_processing(self):
        """Test voice command processing"""
        try:
            command_text = "show dashboard"
            user_id = "test_user_123"
            
            command = await voice_ops.process_voice_command(command_text, user_id)
            
            assert isinstance(command, VoiceCommand)
            assert command.command_text == command_text
            assert command.user_id == user_id
            assert command.intent == "show_dashboard"
            assert command.confidence > 0.5
            
            self.log_test("Voice Command Processing", True)
        except Exception as e:
            self.log_test("Voice Command Processing", False, str(e))
    
    async def test_voice_command_execution(self):
        """Test voice command execution"""
        try:
            command_text = "show analytics"
            user_id = "test_user_123"
            
            command = await voice_ops.process_voice_command(command_text, user_id)
            result = await voice_ops.execute_voice_command(command)
            
            assert isinstance(result, dict)
            assert result.get('success') == True
            assert result.get('action') == 'navigate'
            assert result.get('page') == 'analytics'
            
            self.log_test("Voice Command Execution", True)
        except Exception as e:
            self.log_test("Voice Command Execution", False, str(e))
    
    async def test_intent_extraction(self):
        """Test intent extraction from various commands"""
        try:
            test_commands = [
                ("show dashboard", "show_dashboard"),
                ("display analytics", "show_analytics"),
                ("get mev data", "show_mev"),
                ("check alerts", "check_alerts"),
                ("freeze address 0x1234567890123456789012345678901234567890", "freeze_address"),
                ("system status", "system_status")
            ]
            
            for command_text, expected_intent in test_commands:
                command = await voice_ops.process_voice_command(command_text, "test_user")
                assert command.intent == expected_intent
                assert command.confidence > 0.1
            
            self.log_test("Intent Extraction", True)
        except Exception as e:
            self.log_test("Intent Extraction", False, str(e))
    
    async def test_mobile_api_health(self):
        """Test mobile API health endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    assert response.status == 200
                    data = await response.json()
                    assert data['status'] == 'healthy'
                    assert data['service'] == 'mobile_api'
            
            self.log_test("Mobile API Health Check", True)
        except Exception as e:
            self.log_test("Mobile API Health Check", False, str(e))
    
    async def test_voice_command_api(self):
        """Test voice command API endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "command_text": "show dashboard",
                    "user_id": "test_user_123",
                    "voice_enabled": True
                }
                
                async with session.post(f"{self.base_url}/voice/command", json=payload) as response:
                    assert response.status == 200
                    data = await response.json()
                    assert 'command_id' in data
                    assert data['intent'] == 'show_dashboard'
                    assert data['confidence'] > 0.5
                    assert data['result']['success'] == True
            
            self.log_test("Voice Command API", True)
        except Exception as e:
            self.log_test("Voice Command API", False, str(e))
    
    async def test_text_to_speech_api(self):
        """Test text-to-speech API endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "text": "Hello, this is a test message",
                    "voice": "Rachel"
                }
                
                async with session.post(f"{self.base_url}/voice/text-to-speech", json=payload) as response:
                    assert response.status == 200
                    data = await response.json()
                    assert 'audio_data' in data
                    assert data['voice'] == 'Rachel'
                    assert data['text'] == payload['text']
            
            self.log_test("Text-to-Speech API", True)
        except Exception as e:
            self.log_test("Text-to-Speech API", False, str(e))
    
    async def test_mobile_alert_api(self):
        """Test mobile alert API endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "alert_type": "high_risk",
                    "message": "High risk transaction detected",
                    "priority": "high",
                    "user_id": "test_user_123",
                    "push_enabled": True
                }
                
                async with session.post(f"{self.base_url}/mobile/alert", json=payload) as response:
                    assert response.status == 200
                    data = await response.json()
                    assert data['success'] == True
                    assert 'alert_id' in data
            
            self.log_test("Mobile Alert API", True)
        except Exception as e:
            self.log_test("Mobile Alert API", False, str(e))
    
    async def test_mobile_notification_api(self):
        """Test mobile notification API endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "title": "Test Notification",
                    "body": "This is a test notification",
                    "user_id": "test_user_123",
                    "notification_type": "info"
                }
                
                async with session.post(f"{self.base_url}/mobile/notification", json=payload) as response:
                    assert response.status == 200
                    data = await response.json()
                    assert data['success'] == True
                    assert 'notification_id' in data
            
            self.log_test("Mobile Notification API", True)
        except Exception as e:
            self.log_test("Mobile Notification API", False, str(e))
    
    async def test_mobile_dashboard_api(self):
        """Test mobile dashboard API endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "user_id": "test_user_123",
                    "include_analytics": True,
                    "include_alerts": True
                }
                
                async with session.post(f"{self.base_url}/mobile/dashboard", json=payload) as response:
                    assert response.status == 200
                    data = await response.json()
                    assert data['user_id'] == 'test_user_123'
                    assert 'dashboard_id' in data
                    assert 'analytics' in data
                    assert 'alerts' in data
            
            self.log_test("Mobile Dashboard API", True)
        except Exception as e:
            self.log_test("Mobile Dashboard API", False, str(e))
    
    async def test_available_voices_api(self):
        """Test available voices API endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/mobile/voices") as response:
                    assert response.status == 200
                    data = await response.json()
                    assert 'voices' in data
                    assert 'count' in data
                    assert 'default_voice' in data
                    assert len(data['voices']) > 0
            
            self.log_test("Available Voices API", True)
        except Exception as e:
            self.log_test("Available Voices API", False, str(e))
    
    async def test_command_history_api(self):
        """Test command history API endpoint"""
        try:
            # First, create some commands
            await voice_ops.process_voice_command("show dashboard", "test_user_456")
            await voice_ops.process_voice_command("check alerts", "test_user_456")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/mobile/command-history?user_id=test_user_456&limit=5") as response:
                    assert response.status == 200
                    data = await response.json()
                    assert data['user_id'] == 'test_user_456'
                    assert 'commands' in data
                    assert 'total_commands' in data
                    assert len(data['commands']) > 0
            
            self.log_test("Command History API", True)
        except Exception as e:
            self.log_test("Command History API", False, str(e))
    
    async def test_mobile_status_api(self):
        """Test mobile status API endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/mobile/status") as response:
                    assert response.status == 200
                    data = await response.json()
                    assert data['status'] == 'operational'
                    assert 'active_connections' in data
                    assert 'voice_ops_available' in data
            
            self.log_test("Mobile Status API", True)
        except Exception as e:
            self.log_test("Mobile Status API", False, str(e))
    
    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        try:
            uri = f"ws://localhost:5005/ws/mobile"
            
            async with websockets.connect(uri) as websocket:
                # Send a ping message
                await websocket.send(json.dumps({"type": "ping"}))
                
                # Wait for pong response
                response = await websocket.recv()
                data = json.loads(response)
                
                assert data['type'] == 'pong'
                assert 'timestamp' in data
            
            self.log_test("WebSocket Connection", True)
        except Exception as e:
            self.log_test("WebSocket Connection", False, str(e))
    
    async def test_voice_alert_creation(self):
        """Test voice alert creation"""
        try:
            alert = VoiceAlert(
                alert_id="test_alert_1",
                alert_type="high_risk",
                message="Test alert message",
                priority="high",
                voice_enabled=True,
                timestamp=datetime.now()
            )
            
            assert alert.alert_id == "test_alert_1"
            assert alert.alert_type == "high_risk"
            assert alert.priority == "high"
            assert alert.voice_enabled == True
            
            self.log_test("Voice Alert Creation", True)
        except Exception as e:
            self.log_test("Voice Alert Creation", False, str(e))
    
    async def test_complex_voice_commands(self):
        """Test complex voice commands"""
        try:
            complex_commands = [
                ("freeze the address 0x1234567890123456789012345678901234567890 immediately", "freeze_address"),
                ("what's the system status right now", "system_status"),
                ("show me the analytics dashboard", "show_analytics"),
                ("check for any alerts or warnings", "check_alerts")
            ]
            
            for command_text, expected_intent in complex_commands:
                command = await voice_ops.process_voice_command(command_text, "test_user")
                assert command.intent == expected_intent
                assert command.confidence > 0.1
            
            self.log_test("Complex Voice Commands", True)
        except Exception as e:
            self.log_test("Complex Voice Commands", False, str(e))
    
    async def run_all_tests(self):
        """Run all Phase 7 tests"""
        logger.info("🚀 Starting Phase 7 Implementation Tests...")
        logger.info("=" * 60)
        
        # Test Voice Operations
        await self.test_voice_operations_initialization()
        await self.test_text_to_speech()
        await self.test_voice_command_processing()
        await self.test_voice_command_execution()
        await self.test_intent_extraction()
        await self.test_voice_alert_creation()
        await self.test_complex_voice_commands()
        
        # Test Mobile API
        await self.test_mobile_api_health()
        await self.test_voice_command_api()
        await self.test_text_to_speech_api()
        await self.test_mobile_alert_api()
        await self.test_mobile_notification_api()
        await self.test_mobile_dashboard_api()
        await self.test_available_voices_api()
        await self.test_command_history_api()
        await self.test_mobile_status_api()
        await self.test_websocket_connection()
        
        # Print results
        logger.info("=" * 60)
        logger.info(f"📊 Phase 7 Test Results: {self.passed_tests}/{self.total_tests} tests passed")
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            logger.info("🎉 Phase 7 Implementation: EXCELLENT - All core features working!")
        elif success_rate >= 80:
            logger.info("✅ Phase 7 Implementation: GOOD - Most features working!")
        elif success_rate >= 70:
            logger.info("⚠️ Phase 7 Implementation: FAIR - Some issues need attention!")
        else:
            logger.error("❌ Phase 7 Implementation: NEEDS WORK - Significant issues found!")
        
        # Save detailed results
        with open('phase7_test_results.json', 'w') as f:
            json.dump({
                'phase': 'Phase 7 - Voice & Mobile',
                'timestamp': datetime.now().isoformat(),
                'total_tests': self.total_tests,
                'passed_tests': self.passed_tests,
                'success_rate': success_rate,
                'test_results': self.test_results
            }, f, indent=2)
        
        return success_rate >= 80

async def main():
    """Main test runner"""
    test_suite = Phase7TestSuite()
    success = await test_suite.run_all_tests()
    
    if success:
        logger.info("🎯 Phase 7 implementation is ready for production!")
        return 0
    else:
        logger.error("🔧 Phase 7 implementation needs fixes before production!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 