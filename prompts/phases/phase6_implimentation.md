I'll create Phase 6 implementation guide based on the existing phases and final plans. Let me generate the complete Phase 6 implementation:

# Phase 6: Voice Operations & Advanced UI Implementation Guide

## �� **PHASE 6 OVERVIEW**

**Goal:** Build voice operations capabilities and advanced UI components for the "Palantir of Compliance" system

**Duration:** 2 Weeks (Week 11: Voice Operations, Week 12: Advanced UI & Integration)

**Prerequisites:** ✅ Phase 1 completed (Authentication, Multi-chain data), ✅ Phase 2 completed (Entity resolution, Graph database), ✅ Phase 3 completed (MEV detection, Risk scoring, Sanctions screening), ✅ Phase 4 completed (Automated actions, Workflow builder), ✅ Phase 5 completed (Advanced analytics, Predictive modeling)
**Target Status:** 🎤 Voice command system + Advanced UI components + Real-time alerts + Mobile responsiveness

---

## 📋 **WEEK 11: VOICE OPERATIONS**

### **Day 1-2: ElevenLabs Integration**

#### **Step 1: Create Voice Operations Service**
**File:** `services/voiceops/voice_operations.py`

```python
import asyncio
import json
import websockets
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import aiohttp
import base64
import logging
from elevenlabs import generate, save, set_api_key
from elevenlabs import voices, Voice, VoiceSettings

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
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        set_api_key(self.api_key)
        self.voices = self._load_voices()
        self.active_connections = set()
        self.command_history = []
        self.alert_queue = asyncio.Queue()
        
    def _load_voices(self) -> Dict[str, Voice]:
        """Load available ElevenLabs voices"""
        try:
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
        return "placeholder speech to text result"
    
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
            
            return command
            
        except Exception as e:
            logging.error(f"Error processing voice command: {e}")
            raise
    
    async def _extract_intent(self, command_text: str) -> tuple:
        """Extract intent from command text"""
        command_lower = command_text.lower()
        
        # Simple keyword-based intent recognition
        if any(word in command_lower for word in ['show', 'display', 'get']):
            if 'dashboard' in command_lower:
                return 'show_dashboard', 0.9, {'page': 'dashboard'}
            elif 'analytics' in command_lower:
                return 'show_analytics', 0.9, {'page': 'analytics'}
            elif 'mev' in command_lower:
                return 'show_mev', 0.9, {'page': 'mev'}
            elif 'risk' in command_lower:
                return 'show_risk', 0.9, {'page': 'risk'}
        
        elif any(word in command_lower for word in ['alert', 'alarm', 'warning']):
            return 'check_alerts', 0.8, {}
        
        elif any(word in command_lower for word in ['freeze', 'block', 'stop']):
            if 'address' in command_lower:
                # Extract address from command
                import re
                address_match = re.search(r'0x[a-fA-F0-9]{40}', command_text)
                if address_match:
                    return 'freeze_address', 0.7, {'address': address_match.group()}
        
        elif any(word in command_lower for word in ['status', 'health', 'system']):
            return 'system_status', 0.9, {}
        
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
```

#### **Step 2: Create WebSocket Voice Handler**
**File:** `services/voiceops/websocket_handler.py`

```python
import asyncio
import json
import websockets
from typing import Dict, Set, Any
from datetime import datetime
import logging
from .voice_operations import VoiceOperations, VoiceCommand, VoiceAlert

class VoiceWebSocketHandler:
    def __init__(self):
        self.voice_ops = VoiceOperations()
        self.active_connections: Set[websockets.WebSocketServerProtocol] = set()
        self.connection_users: Dict[websockets.WebSocketServerProtocol, str] = {}
        
    async def handle_connection(self, websocket, path):
        """Handle WebSocket connection"""
        try:
            self.active_connections.add(websocket)
            
            # Send welcome message
            await websocket.send(json.dumps({
                'type': 'connection_established',
                'message': 'Voice operations connected',
                'timestamp': datetime.now().isoformat()
            }))
            
            # Handle messages
            async for message in websocket:
                await self._handle_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logging.error(f"WebSocket error: {e}")
        finally:
            await self._cleanup_connection(websocket)
    
    async def _handle_message(self, websocket, message):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'voice_command':
                await self._handle_voice_command(websocket, data)
            elif message_type == 'text_command':
                await self._handle_text_command(websocket, data)
            elif message_type == 'authenticate':
                await self._handle_authentication(websocket, data)
            else:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))
                
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logging.error(f"Error handling message: {e}")
            await websocket.send(json.dumps({
                'type': 'error',
                'message': f'Internal error: {str(e)}'
            }))
    
    async def _handle_voice_command(self, websocket, data):
        """Handle voice command (audio data)"""
        try:
            user_id = self.connection_users.get(websocket, 'anonymous')
            audio_data = data.get('audio_data')
            
            if not audio_data:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': 'No audio data provided'
                }))
                return
            
            # Convert audio to text
            command_text = await self.voice_ops.speech_to_text(audio_data)
            
            # Process command
            command = await self.voice_ops.process_voice_command(command_text, user_id)
            result = await self.voice_ops.execute_voice_command(command)
            
            # Send response
            await websocket.send(json.dumps({
                'type': 'command_result',
                'command_id': command.command_id,
                'command_text': command_text,
                'intent': command.intent,
                'confidence': command.confidence,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }))
            
        except Exception as e:
            logging.error(f"Error handling voice command: {e}")
            await websocket.send(json.dumps({
                'type': 'error',
                'message': f'Error processing voice command: {str(e)}'
            }))
    
    async def _handle_text_command(self, websocket, data):
        """Handle text command"""
        try:
            user_id = self.connection_users.get(websocket, 'anonymous')
            command_text = data.get('command_text')
            
            if not command_text:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': 'No command text provided'
                }))
                return
            
            # Process command
            command = await self.voice_ops.process_voice_command(command_text, user_id)
            result = await self.voice_ops.execute_voice_command(command)
            
            # Send response
            await websocket.send(json.dumps({
                'type': 'command_result',
                'command_id': command.command_id,
                'command_text': command_text,
                'intent': command.intent,
                'confidence': command.confidence,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }))
            
        except Exception as e:
            logging.error(f"Error handling text command: {e}")
            await websocket.send(json.dumps({
                'type': 'error',
                'message': f'Error processing text command: {str(e)}'
            }))
    
    async def _handle_authentication(self, websocket, data):
        """Handle user authentication"""
        try:
            user_id = data.get('user_id')
            token = data.get('token')
            
            # In real implementation, validate token
            if user_id and token:
                self.connection_users[websocket] = user_id
                await websocket.send(json.dumps({
                    'type': 'authenticated',
                    'user_id': user_id,
                    'message': 'Authentication successful'
                }))
            else:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': 'Invalid authentication credentials'
                }))
                
        except Exception as e:
            logging.error(f"Error handling authentication: {e}")
            await websocket.send(json.dumps({
                'type': 'error',
                'message': f'Authentication error: {str(e)}'
            }))
    
    async def broadcast_alert(self, alert: VoiceAlert):
        """Broadcast voice alert to all connected clients"""
        if not alert.voice_enabled:
            return
        
        try:
            # Generate speech for alert
            audio_data = await self.voice_ops.text_to_speech(alert.message)
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            alert_message = {
                'type': 'voice_alert',
                'alert_id': alert.alert_id,
                'alert_type': alert.alert_type,
                'message': alert.message,
                'priority': alert.priority,
                'audio_data': audio_base64,
                'timestamp': datetime.now().isoformat()
            }
            
            # Send to all connected clients
            disconnected = set()
            for websocket in self.active_connections:
                try:
                    await websocket.send(json.dumps(alert_message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(websocket)
                except Exception as e:
                    logging.error(f"Error sending alert to client: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected clients
            for websocket in disconnected:
                await self._cleanup_connection(websocket)
                
        except Exception as e:
            logging.error(f"Error broadcasting alert: {e}")
    
    async def _cleanup_connection(self, websocket):
        """Clean up WebSocket connection"""
        self.active_connections.discard(websocket)
        self.connection_users.pop(websocket, None)
```

### **Day 3-4: Voice Alert System**

#### **Step 1: Create Voice Alert Manager**
**File:** `services/voiceops/alert_manager.py`

```python
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from .voice_operations import VoiceAlert

@dataclass
class AlertRule:
    rule_id: str
    name: str
    condition: str
    threshold: float
    voice_enabled: bool
    priority: str
    message_template: str
    enabled: bool = True

@dataclass
class AlertHistory:
    alert_id: str
    rule_id: str
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None

class VoiceAlertManager:
    def __init__(self, websocket_handler):
        self.websocket_handler = websocket_handler
        self.alert_rules: Dict[str, AlertRule] = {}
        self.alert_history: List[AlertHistory] = []
        self.active_alerts: Dict[str, VoiceAlert] = {}
        self.alert_queue = asyncio.Queue()
        
        # Initialize default alert rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        default_rules = [
            AlertRule(
                rule_id="high_risk_transaction",
                name="High Risk Transaction",
                condition="risk_score > 0.8",
                threshold=0.8,
                voice_enabled=True,
                priority="high",
                message_template="High risk transaction detected with score {risk_score}"
            ),
            AlertRule(
                rule_id="mev_attack_detected",
                name="MEV Attack Detected",
                condition="mev_opportunities > 5",
                threshold=5,
                voice_enabled=True,
                priority="critical",
                message_template="MEV attack detected with {count} opportunities"
            ),
            AlertRule(
                rule_id="large_transfer",
                name="Large Transfer",
                condition="transfer_value > 1000000",
                threshold=1000000,
                voice_enabled=True,
                priority="medium",
                message_template="Large transfer detected: {value} USD"
            ),
            AlertRule(
                rule_id="system_health",
                name="System Health Alert",
                condition="health_score < 0.7",
                threshold=0.7,
                voice_enabled=True,
                priority="high",
                message_template="System health degraded: {health_score}"
            )
        ]
        
        for rule in default_rules:
            self.alert_rules[rule.rule_id] = rule
    
    async def check_alerts(self, metrics: Dict[str, Any]) -> List[VoiceAlert]:
        """Check if any alert rules are triggered"""
        triggered_alerts = []
        
        for rule_id, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
            
            # Check if rule is triggered
            if await self._evaluate_condition(rule.condition, metrics):
                # Check if alert is already active
                if rule_id not in self.active_alerts:
                    alert = await self._create_alert(rule, metrics)
                    triggered_alerts.append(alert)
                    self.active_alerts[rule_id] = alert
                    
                    # Add to history
                    self.alert_history.append(AlertHistory(
                        alert_id=alert.alert_id,
                        rule_id=rule_id,
                        triggered_at=datetime.now()
                    ))
        
        return triggered_alerts
    
    async def _evaluate_condition(self, condition: str, metrics: Dict[str, Any]) -> bool:
        """Evaluate alert condition"""
        try:
            # Simple condition evaluation (in real implementation, use a proper expression evaluator)
            if "risk_score >" in condition:
                threshold = float(condition.split(">")[1].strip())
                return metrics.get('risk_score', 0) > threshold
            elif "mev_opportunities >" in condition:
                threshold = float(condition.split(">")[1].strip())
                return metrics.get('mev_opportunities', 0) > threshold
            elif "transfer_value >" in condition:
                threshold = float(condition.split(">")[1].strip())
                return metrics.get('transfer_value', 0) > threshold
            elif "health_score <" in condition:
                threshold = float(condition.split("<")[1].strip())
                return metrics.get('health_score', 1.0) < threshold
            else:
                return False
        except Exception as e:
            logging.error(f"Error evaluating condition {condition}: {e}")
            return False
    
    async def _create_alert(self, rule: AlertRule, metrics: Dict[str, Any]) -> VoiceAlert:
        """Create voice alert from rule"""
        alert_id = f"alert_{rule.rule_id}_{datetime.now().timestamp()}"
        
        # Format message using template
        message = rule.message_template.format(**metrics)
        
        alert = VoiceAlert(
            alert_id=alert_id,
            alert_type=rule.name,
            message=message,
            priority=rule.priority,
            voice_enabled=rule.voice_enabled,
            timestamp=datetime.now()
        )
        
        return alert
    
    async def resolve_alert(self, alert_id: str, user_id: str):
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            del self.active_alerts[alert_id]
            
            # Update history
            for history in self.alert_history:
                if history.alert_id == alert_id:
                    history.resolved_at = datetime.now()
                    history.acknowledged_by = user_id
                    break
    
    async def get_active_alerts(self) -> List[VoiceAlert]:
        """Get all active alerts"""
        return list(self.active_alerts.values())
    
    async def get_alert_history(self, hours: int = 24) -> List[AlertHistory]:
        """Get alert history for specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            history for history in self.alert_history
            if history.triggered_at >= cutoff_time
        ]
    
    async def add_alert_rule(self, rule: AlertRule):
        """Add new alert rule"""
        self.alert_rules[rule.rule_id] = rule
    
    async def update_alert_rule(self, rule_id: str, updates: Dict[str, Any]):
        """Update existing alert rule"""
        if rule_id in self.alert_rules:
            rule = self.alert_rules[rule_id]
            for key, value in updates.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
    
    async def delete_alert_rule(self, rule_id: str):
        """Delete alert rule"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
```

### **Day 5-7: Voice Command Processing**

#### **Step 1: Create Voice Command Processor**
**File:** `services/voiceops/command_processor.py`

```python
import asyncio
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from .voice_operations import VoiceCommand

@dataclass
class CommandPattern:
    pattern: str
    intent: str
    confidence: float
    parameters: List[str]

class VoiceCommandProcessor:
    def __init__(self):
        self.command_patterns = self._initialize_patterns()
        self.context_history: List[Dict[str, Any]] = []
        
    def _initialize_patterns(self) -> List[CommandPattern]:
        """Initialize command patterns"""
        return [
            # Navigation commands
            CommandPattern(
                pattern=r"show\s+(dashboard|main\s+page)",
                intent="show_dashboard",
                confidence=0.95,
                parameters=[]
            ),
            CommandPattern(
                pattern=r"go\s+to\s+(dashboard|main)",
                intent="show_dashboard",
                confidence=0.95,
                parameters=[]
            ),
            CommandPattern(
                pattern=r"show\s+analytics",
                intent="show_analytics",
                confidence=0.95,
                parameters=[]
            ),
            CommandPattern(
                pattern=r"show\s+mev",
                intent="show_mev",
                confidence=0.95,
                parameters=[]
            ),
            CommandPattern(
                pattern=r"show\s+risk",
                intent="show_risk",
                confidence=0.95,
                parameters=[]
            ),
            
            # Alert commands
            CommandPattern(
                pattern=r"check\s+alerts",
                intent="check_alerts",
                confidence=0.9,
                parameters=[]
            ),
            CommandPattern(
                pattern=r"show\s+alerts",
                intent="check_alerts",
                confidence=0.9,
                parameters=[]
            ),
            CommandPattern(
                pattern=r"any\s+alerts",
                intent="check_alerts",
                confidence=0.8,
                parameters=[]
            ),
            
            # Action commands
            CommandPattern(
                pattern=r"freeze\s+address\s+(0x[a-fA-F0-9]{40})",
                intent="freeze_address",
                confidence=0.9,
                parameters=["address"]
            ),
            CommandPattern(
                pattern=r"block\s+address\s+(0x[a-fA-F0-9]{40})",
                intent="freeze_address",
                confidence=0.9,
                parameters=["address"]
            ),
            CommandPattern(
                pattern=r"stop\s+address\s+(0x[a-fA-F0-9]{40})",
                intent="freeze_address",
                confidence=0.8,
                parameters=["address"]
            ),
            
            # System commands
            CommandPattern(
                pattern=r"system\s+status",
                intent="system_status",
                confidence=0.95,
                parameters=[]
            ),
            CommandPattern(
                pattern=r"health\s+check",
                intent="system_status",
                confidence=0.9,
                parameters=[]
            ),
            CommandPattern(
                pattern=r"how\s+are\s+systems",
                intent="system_status",
                confidence=0.8,
                parameters=[]
            ),
            
            # Data queries
            CommandPattern(
                pattern=r"show\s+transactions",
                intent="show_transactions",
                confidence=0.9,
                parameters=[]
            ),
            CommandPattern(
                pattern=r"recent\s+activity",
                intent="show_transactions",
                confidence=0.8,
                parameters=[]
            ),
            CommandPattern(
                pattern=r"latest\s+blocks",
                intent="show_blocks",
                confidence=0.9,
                parameters=[]
            ),
        ]
    
    async def process_command(self, command_text: str, user_id: str) -> VoiceCommand:
        """Process voice command and extract intent"""
        try:
            # Clean command text
            cleaned_text = self._clean_command_text(command_text)
            
            # Find matching pattern
            intent, confidence, parameters = await self._match_pattern(cleaned_text)
            
            # Create command object
            command = VoiceCommand(
                command_id=f"cmd_{datetime.now().timestamp()}",
                user_id=user_id,
                command_text=cleaned_text,
                intent=intent,
                confidence=confidence,
                parameters=parameters,
                timestamp=datetime.now()
            )
            
            # Add to context history
            self.context_history.append({
                'command': command,
                'timestamp': datetime.now()
            })
            
            # Keep only last 10 commands
            if len(self.context_history) > 10:
                self.context_history = self.context_history[-10:]
            
            return command
            
        except Exception as e:
            logging.error(f"Error processing command: {e}")
            # Return unknown command
            return VoiceCommand(
                command_id=f"cmd_{datetime.now().timestamp()}",
                user_id=user_id,
                command_text=command_text,
                intent="unknown",
                confidence=0.1,
                parameters={},
                timestamp=datetime.now()
            )
    
    def _clean_command_text(self, text: str) -> str:
        """Clean and normalize command text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common filler words
        filler_words = ['um', 'uh', 'like', 'you know', 'i mean']
        for word in filler_words:
            text = text.replace(word, '')
        
        # Clean up whitespace again
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    async def _match_pattern(self, command_text: str) -> Tuple[str, float, Dict[str, Any]]:
        """Match command text against patterns"""
        best_match = None
        best_confidence = 0.0
        
        for pattern in self.command_patterns:
            match = re.search(pattern.pattern, command_text, re.IGNORECASE)
            if match:
                confidence = pattern.confidence
                
                # Extract parameters
                parameters = {}
                for param_name in pattern.parameters:
                    if param_name == "address":
                        # Extract Ethereum address
                        address_match = re.search(r'0x[a-fA-F0-9]{40}', command_text)
                        if address_match:
                            parameters[param_name] = address_match.group()
                
                # Check if this is a better match
                if confidence > best_confidence:
                    best_match = (pattern.intent, confidence, parameters)
                    best_confidence = confidence
        
        if best_match:
            return best_match
        else:
            return "unknown", 0.1, {}
    
    async def get_command_suggestions(self, partial_text: str) -> List[str]:
        """Get command suggestions based on partial text"""
        suggestions = []
        partial_lower = partial_text.lower()
        
        # Common command starters
        starters = [
            "show dashboard",
            "show analytics",
            "show mev",
            "check alerts",
            "system status",
            "freeze address",
            "show transactions"
        ]
        
        for starter in starters:
            if starter.startswith(partial_lower):
                suggestions.append(starter)
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    async def get_context_aware_suggestions(self, user_id: str) -> List[str]:
        """Get context-aware command suggestions"""
        # Get recent commands for this user
        user_commands = [
            ctx['command'] for ctx in self.context_history
            if ctx['command'].user_id == user_id
        ]
        
        if not user_commands:
            return ["show dashboard", "check alerts", "system status"]
        
        # Suggest related commands based on recent activity
        recent_intents = [cmd.intent for cmd in user_commands[-3:]]
        
        suggestions = []
        if "show_dashboard" in recent_intents:
            suggestions.extend(["show analytics", "show mev", "check alerts"])
        elif "check_alerts" in recent_intents:
            suggestions.extend(["system status", "show dashboard", "show transactions"])
        elif "system_status" in recent_intents:
            suggestions.extend(["check alerts", "show dashboard", "show analytics"])
        else:
            suggestions.extend(["show dashboard", "check alerts", "system status"])
        
        return suggestions
```

---

## 📋 **WEEK 12: ADVANCED UI & INTEGRATION**

### **Day 1-2: Voice UI Components**

#### **Step 1: Create Voice Control Component**
**File:** `services/ui/nextjs-app/src/components/voice/VoiceControl.tsx`

```typescript
import React, { useState, useEffect, useRef } from 'react'
import {
  Box,
  Button,
  VStack,
  HStack,
  Text,
  useToast,
  IconButton,
  Badge,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure,
  List,
  ListItem,
  ListIcon
} from '@chakra-ui/react'
import { FiMic, FiMicOff, FiVolume2, FiVolumeX, FiSettings } from 'react-icons/fi'

interface VoiceCommand {
  command_id: string
  command_text: string
  intent: string
  confidence: number
  result: any
  timestamp: string
}

interface VoiceControlProps {
  onCommand?: (command: VoiceCommand) => void
  onNavigate?: (page: string) => void
}

export const VoiceControl: React.FC<VoiceControlProps> = ({ 
  onCommand, 
  onNavigate 
}) => {
  const [isListening, setIsListening] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [currentCommand, setCurrentCommand] = useState('')
  const [commandHistory, setCommandHistory] = useState<VoiceCommand[]>([])
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [audioContext, setAudioContext] = useState<AudioContext | null>(null)
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null)
  const [websocket, setWebsocket] = useState<WebSocket | null>(null)
  
  const toast = useToast()
  const { isOpen, onOpen, onClose } = useDisclosure()
  const audioChunks = useRef<Blob[]>([])

  useEffect(() => {
    initializeVoiceControl()
    return () => {
      cleanupVoiceControl()
    }
  }, [])

  const initializeVoiceControl = async () => {
    try {
      // Initialize WebSocket connection
      const ws = new WebSocket('ws://localhost:5000/voice')
      
      ws.onopen = () => {
        setIsConnected(true)
        toast({
          title: 'Voice control connected',
          status: 'success',
          duration: 3000
        })
      }
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        handleWebSocketMessage(data)
      }
      
      ws.onclose = () => {
        setIsConnected(false)
        toast({
          title: 'Voice control disconnected',
          status: 'warning',
          duration: 3000
        })
      }
      
      setWebsocket(ws)
      
      // Initialize audio context
      const context = new (window.AudioContext || (window as any).webkitAudioContext)()
      setAudioContext(context)
      
    } catch (error) {
      console.error('Error initializing voice control:', error)
      toast({
        title: 'Voice control initialization failed',
        description: error.message,
        status: 'error',
        duration: 5000
      })
    }
  }

  const cleanupVoiceControl = () => {
    if (websocket) {
      websocket.close()
    }
    if (mediaRecorder) {
      mediaRecorder.stop()
    }
    if (audioContext) {
      audioContext.close()
    }
  }

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'command_result':
        handleCommandResult(data)
        break
      case 'voice_alert':
        handleVoiceAlert(data)
        break
      case 'error':
        toast({
          title: 'Voice control error',
          description: data.message,
          status: 'error',
          duration: 5000
        })
        break
    }
  }

  const handleCommandResult = (data: any) => {
    const command: VoiceCommand = {
      command_id: data.command_id,
      command_text: data.command_text,
      intent: data.intent,
      confidence: data.confidence,
      result: data.result,
      timestamp: data.timestamp
    }
    
    setCommandHistory(prev => [command, ...prev.slice(0, 9)])
    setCurrentCommand('')
    
    // Handle navigation
    if (data.result?.action === 'navigate' && onNavigate) {
      onNavigate(data.result.page)
    }
    
    // Call callback
    if (onCommand) {
      onCommand(command)
    }
    
    // Show result toast
    toast({
      title: `Command: ${data.command_text}`,
      description: data.result?.message || 'Command executed',
      status: data.result?.success ? 'success' : 'error',
      duration: 3000
    })
  }

  const handleVoiceAlert = (data: any) => {
    // Play audio alert
    if (data.audio_data) {
      playAudioAlert(data.audio_data)
    }
    
    // Show alert toast
    toast({
      title: `Voice Alert: ${data.alert_type}`,
      description: data.message,
      status: data.priority === 'critical' ? 'error' : 'warning',
      duration: 5000,
      isClosable: true
    })
  }

  const playAudioAlert = async (audioData: string) => {
    try {
      const audioBuffer = Uint8Array.from(atob(audioData), c => c.charCodeAt(0))
      const audioBlob = new Blob([audioBuffer], { type: 'audio/mpeg' })
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)
      await audio.play()
    } catch (error) {
      console.error('Error playing audio alert:', error)
    }
  }

  const startListening = async () => {
    try {
      if (!audioContext || !websocket) return
      
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.current.push(event.data)
        }
      }
      
      recorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' })
        audioChunks.current = []
        
        // Convert to base64
        const reader = new FileReader()
        reader.onload = () => {
          const base64Audio = (reader.result as string).split(',')[1]
          
          // Send to WebSocket
          if (websocket) {
            websocket.send(JSON.stringify({
              type: 'voice_command',
              audio_data: base64Audio
            }))
          }
        }
        reader.readAsDataURL(audioBlob)
      }
      
      setMediaRecorder(recorder)
      recorder.start()
      setIsListening(true)
      setCurrentCommand('Listening...')
      
    } catch (error) {
      console.error('Error starting voice recording:', error)
      toast({
        title: 'Microphone access denied',
        description: 'Please allow microphone access to use voice control',
        status: 'error',
        duration: 5000
      })
    }
  }

  const stopListening = () => {
    if (mediaRecorder) {
      mediaRecorder.stop()
      mediaRecorder.stream.getTracks().forEach(track => track.stop())
    }
    setIsListening(false)
    setCurrentCommand('')
  }

  const sendTextCommand = async (commandText: string) => {
    if (!websocket) return
    
    setCurrentCommand(commandText)
    
    websocket.send(JSON.stringify({
      type: 'text_command',
      command_text: commandText
    }))
  }

  const getCommandSuggestions = () => {
    return [
      "Show dashboard",
      "Check alerts",
      "System status",
      "Show analytics",
      "Show MEV detection"
    ]
  }

  return (
    <Box>
      <VStack spacing={4}>
        {/* Voice Control Button */}
        <HStack spacing={4}>
          <IconButton
            aria-label="Voice control"
            icon={isListening ? <FiMicOff /> : <FiMic />}
            colorScheme={isListening ? 'red' : isConnected ? 'green' : 'gray'}
            size="lg"
            onClick={isListening ? stopListening : startListening}
            isDisabled={!isConnected}
          />
          
          <Badge colorScheme={isConnected ? 'green' : 'red'}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </Badge>
          
          <IconButton
            aria-label="Voice settings"
            icon={<FiSettings />}
            size="sm"
            onClick={onOpen}
          />
        </HStack>
        
        {/* Current Command Display */}
        {currentCommand && (
          <Text fontSize="sm" color="gray.600">
            {currentCommand}
          </Text>
        )}
        
        {/* Quick Commands */}
        <HStack spacing={2} wrap="wrap">
          {getCommandSuggestions().map((suggestion, index) => (
            <Button
              key={index}
              size="sm"
              variant="outline"
              onClick={() => sendTextCommand(suggestion)}
              isDisabled={!isConnected}
            >
              {suggestion}
            </Button>
          ))}
        </HStack>
      </VStack>
      
      {/* Settings Modal */}
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Voice Control Settings</ModalHeader>
          <ModalBody>
            <VStack spacing={4} align="stretch">
              <Text fontWeight="bold">Recent Commands:</Text>
              <List spacing={2}>
                {commandHistory.slice(0, 5).map((cmd, index) => (
                  <ListItem key={index}>
                    <ListIcon as={FiMic} color="green.500" />
                    <Text fontSize="sm">
                      "{cmd.command_text}" → {cmd.intent}
                    </Text>
                    <Text fontSize="xs" color="gray.500">
                      Confidence: {(cmd.confidence * 100).toFixed(1)}%
                    </Text>
                  </ListItem>
                ))}
              </List>
              
              {commandHistory.length === 0 && (
                <Text color="gray.500">No commands yet</Text>
              )}
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button onClick={onClose}>Close</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  )
}
```

#### **Step 2: Create Voice Alert Component**
**File:** `services/ui/nextjs-app/src/components/voice/VoiceAlert

I'll continue with the Phase 6 implementation guide:

#### **Step 2: Create Voice Alert Component**
**File:** `services/ui/nextjs-app/src/components/voice/VoiceAlert.tsx`

```typescript
import React, { useState, useEffect } from 'react'
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  IconButton,
  useToast,
  Collapse,
  Button,
  Progress,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription
} from '@chakra-ui/react'
import { FiVolume2, FiVolumeX, FiX, FiAlertTriangle, FiInfo } from 'react-icons/fi'

interface VoiceAlertProps {
  alert: {
    alert_id: string
    alert_type: string
    message: string
    priority: string
    timestamp: string
  }
  onDismiss?: (alertId: string) => void
  onAcknowledge?: (alertId: string) => void
}

export const VoiceAlert: React.FC<VoiceAlertProps> = ({ 
  alert, 
  onDismiss, 
  onAcknowledge 
}) => {
  const [isPlaying, setIsPlaying] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const toast = useToast()

  const priorityColors = {
    low: 'blue',
    medium: 'yellow',
    high: 'orange',
    critical: 'red'
  }

  const priorityIcons = {
    low: FiInfo,
    medium: FiInfo,
    high: FiAlertTriangle,
    critical: FiAlertTriangle
  }

  const IconComponent = priorityIcons[alert.priority as keyof typeof priorityIcons]

  const playAlert = async () => {
    try {
      if (!audioUrl) {
        // Generate TTS for the alert message
        const response = await fetch('/api/voice/tts', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            text: alert.message,
            voice: 'Rachel'
          })
        })

        if (response.ok) {
          const audioBlob = await response.blob()
          const url = URL.createObjectURL(audioBlob)
          setAudioUrl(url)
          
          const audio = new Audio(url)
          audio.onended = () => setIsPlaying(false)
          audio.play()
          setIsPlaying(true)
        }
      } else {
        const audio = new Audio(audioUrl)
        audio.onended = () => setIsPlaying(false)
        audio.play()
        setIsPlaying(true)
      }
    } catch (error) {
      console.error('Error playing alert:', error)
      toast({
        title: 'Error playing alert',
        description: 'Failed to play voice alert',
        status: 'error',
        duration: 3000
      })
    }
  }

  const stopAlert = () => {
    setIsPlaying(false)
    // Stop any playing audio
    const audios = document.querySelectorAll('audio')
    audios.forEach(audio => audio.pause())
  }

  const handleDismiss = () => {
    if (onDismiss) {
      onDismiss(alert.alert_id)
    }
  }

  const handleAcknowledge = () => {
    if (onAcknowledge) {
      onAcknowledge(alert.alert_id)
    }
  }

  return (
    <Alert
      status={alert.priority === 'critical' ? 'error' : 'warning'}
      variant="left-accent"
      borderRadius="md"
      mb={2}
    >
      <AlertIcon as={IconComponent} />
      <Box flex="1">
        <AlertTitle>
          <HStack justify="space-between">
            <Text>{alert.alert_type}</Text>
            <Badge colorScheme={priorityColors[alert.priority as keyof typeof priorityColors]}>
              {alert.priority}
            </Badge>
          </HStack>
        </AlertTitle>
        
        <AlertDescription>
          <VStack align="stretch" spacing={2}>
            <Text>{alert.message}</Text>
            
            <HStack spacing={2}>
              <IconButton
                aria-label={isPlaying ? 'Stop alert' : 'Play alert'}
                icon={isPlaying ? <FiVolumeX /> : <FiVolume2 />}
                size="sm"
                onClick={isPlaying ? stopAlert : playAlert}
                colorScheme="blue"
                variant="ghost"
              />
              
              <Button
                size="sm"
                variant="outline"
                onClick={() => setIsExpanded(!isExpanded)}
              >
                {isExpanded ? 'Less' : 'More'}
              </Button>
              
              <Button
                size="sm"
                colorScheme="green"
                onClick={handleAcknowledge}
              >
                Acknowledge
              </Button>
              
              <IconButton
                aria-label="Dismiss alert"
                icon={<FiX />}
                size="sm"
                onClick={handleDismiss}
                colorScheme="red"
                variant="ghost"
              />
            </HStack>
            
            <Collapse in={isExpanded}>
              <Box p={2} bg="gray.50" borderRadius="md">
                <Text fontSize="sm" color="gray.600">
                  Alert ID: {alert.alert_id}
                </Text>
                <Text fontSize="sm" color="gray.600">
                  Time: {new Date(alert.timestamp).toLocaleString()}
                </Text>
              </Box>
            </Collapse>
          </VStack>
        </AlertDescription>
      </Box>
    </Alert>
  )
}
```

### **Day 3-4: Advanced Dashboard Components**

#### **Step 1: Create Advanced Analytics Dashboard**
**File:** `services/ui/nextjs-app/src/components/dashboard/AdvancedAnalytics.tsx`

```typescript
import React, { useState, useEffect } from 'react'
import {
  Box,
  Grid,
  GridItem,
  VStack,
  HStack,
  Text,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  useColorModeValue,
  Card,
  CardBody,
  Heading,
  Badge,
  Progress,
  Select,
  Button,
  useToast
} from '@chakra-ui/react'
import { FiTrendingUp, FiTrendingDown, FiActivity, FiAlertTriangle } from 'react-icons/fi'
import dynamic from 'next/dynamic'

// Dynamically import charts to avoid SSR issues
const LineChart = dynamic(() => import('react-chartjs-2').then(mod => mod.Line), { ssr: false })
const BarChart = dynamic(() => import('react-chartjs-2').then(mod => mod.Bar), { ssr: false })
const DoughnutChart = dynamic(() => import('react-chartjs-2').then(mod => mod.Doughnut), { ssr: false })

interface AnalyticsData {
  riskMetrics: {
    transactionVolumeRisk: number
    gasPriceVolatilityRisk: number
    failureRateRisk: number
    mevActivityRisk: number
    largeTransferRisk: number
    suspiciousActivityRisk: number
  }
  predictions: {
    transactionVolume: { current: number; predicted: number; confidence: number }
    gasPrice: { current: number; predicted: number; confidence: number }
    mevOpportunities: { current: number; predicted: number; confidence: number }
    riskScore: { current: number; predicted: number; confidence: number }
  }
  timeSeriesData: {
    labels: string[]
    transactionCount: number[]
    gasPrice: number[]
    riskScore: number[]
  }
  insights: string[]
  recommendations: string[]
}

export const AdvancedAnalytics: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null)
  const [timeRange, setTimeRange] = useState('24h')
  const [loading, setLoading] = useState(true)
  const toast = useToast()

  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  useEffect(() => {
    fetchAnalyticsData()
  }, [timeRange])

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true)
      const response = await fetch(`/api/analytics/advanced?timeRange=${timeRange}`)
      if (response.ok) {
        const data = await response.json()
        setAnalyticsData(data)
      } else {
        throw new Error('Failed to fetch analytics data')
      }
    } catch (error) {
      console.error('Error fetching analytics:', error)
      toast({
        title: 'Error loading analytics',
        description: error.message,
        status: 'error',
        duration: 5000
      })
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (risk: number) => {
    if (risk < 0.3) return 'green'
    if (risk < 0.6) return 'yellow'
    if (risk < 0.8) return 'orange'
    return 'red'
  }

  const getRiskStatus = (risk: number) => {
    if (risk < 0.3) return 'Low'
    if (risk < 0.6) return 'Medium'
    if (risk < 0.8) return 'High'
    return 'Critical'
  }

  if (loading) {
    return (
      <Box p={6}>
        <Text>Loading advanced analytics...</Text>
      </Box>
    )
  }

  if (!analyticsData) {
    return (
      <Box p={6}>
        <Text>No analytics data available</Text>
      </Box>
    )
  }

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between">
          <Heading size="lg">Advanced Analytics Dashboard</Heading>
          <HStack spacing={4}>
            <Select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              width="200px"
            >
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </Select>
            <Button onClick={fetchAnalyticsData} size="sm">
              Refresh
            </Button>
          </HStack>
        </HStack>

        {/* Risk Metrics Grid */}
        <Grid templateColumns="repeat(auto-fit, minmax(300px, 1fr))" gap={6}>
          <GridItem>
            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>Transaction Volume Risk</StatLabel>
                  <StatNumber>
                    <HStack>
                      <Text>{(analyticsData.riskMetrics.transactionVolumeRisk * 100).toFixed(1)}%</Text>
                      <Badge colorScheme={getRiskColor(analyticsData.riskMetrics.transactionVolumeRisk)}>
                        {getRiskStatus(analyticsData.riskMetrics.transactionVolumeRisk)}
                      </Badge>
                    </HStack>
                  </StatNumber>
                  <Progress
                    value={analyticsData.riskMetrics.transactionVolumeRisk * 100}
                    colorScheme={getRiskColor(analyticsData.riskMetrics.transactionVolumeRisk)}
                    size="sm"
                    mt={2}
                  />
                </Stat>
              </CardBody>
            </Card>
          </GridItem>

          <GridItem>
            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>Gas Price Volatility Risk</StatLabel>
                  <StatNumber>
                    <HStack>
                      <Text>{(analyticsData.riskMetrics.gasPriceVolatilityRisk * 100).toFixed(1)}%</Text>
                      <Badge colorScheme={getRiskColor(analyticsData.riskMetrics.gasPriceVolatilityRisk)}>
                        {getRiskStatus(analyticsData.riskMetrics.gasPriceVolatilityRisk)}
                      </Badge>
                    </HStack>
                  </StatNumber>
                  <Progress
                    value={analyticsData.riskMetrics.gasPriceVolatilityRisk * 100}
                    colorScheme={getRiskColor(analyticsData.riskMetrics.gasPriceVolatilityRisk)}
                    size="sm"
                    mt={2}
                  />
                </Stat>
              </CardBody>
            </Card>
          </GridItem>

          <GridItem>
            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>MEV Activity Risk</StatLabel>
                  <StatNumber>
                    <HStack>
                      <Text>{(analyticsData.riskMetrics.mevActivityRisk * 100).toFixed(1)}%</Text>
                      <Badge colorScheme={getRiskColor(analyticsData.riskMetrics.mevActivityRisk)}>
                        {getRiskStatus(analyticsData.riskMetrics.mevActivityRisk)}
                      </Badge>
                    </HStack>
                  </StatNumber>
                  <Progress
                    value={analyticsData.riskMetrics.mevActivityRisk * 100}
                    colorScheme={getRiskColor(analyticsData.riskMetrics.mevActivityRisk)}
                    size="sm"
                    mt={2}
                  />
                </Stat>
              </CardBody>
            </Card>
          </GridItem>

          <GridItem>
            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>Suspicious Activity Risk</StatLabel>
                  <StatNumber>
                    <HStack>
                      <Text>{(analyticsData.riskMetrics.suspiciousActivityRisk * 100).toFixed(1)}%</Text>
                      <Badge colorScheme={getRiskColor(analyticsData.riskMetrics.suspiciousActivityRisk)}>
                        {getRiskStatus(analyticsData.riskMetrics.suspiciousActivityRisk)}
                      </Badge>
                    </HStack>
                  </StatNumber>
                  <Progress
                    value={analyticsData.riskMetrics.suspiciousActivityRisk * 100}
                    colorScheme={getRiskColor(analyticsData.riskMetrics.suspiciousActivityRisk)}
                    size="sm"
                    mt={2}
                  />
                </Stat>
              </CardBody>
            </Card>
          </GridItem>
        </Grid>

        {/* Predictions Section */}
        <Card>
          <CardBody>
            <Heading size="md" mb={4}>Predictive Analytics</Heading>
            <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={4}>
              <Box>
                <Text fontWeight="bold">Transaction Volume</Text>
                <HStack>
                  <Text>Current: {analyticsData.predictions.transactionVolume.current}</Text>
                  <Text>Predicted: {analyticsData.predictions.transactionVolume.predicted}</Text>
                  <Badge colorScheme="blue">
                    {(analyticsData.predictions.transactionVolume.confidence * 100).toFixed(1)}% confidence
                  </Badge>
                </HStack>
              </Box>
              
              <Box>
                <Text fontWeight="bold">Gas Price</Text>
                <HStack>
                  <Text>Current: {analyticsData.predictions.gasPrice.current} gwei</Text>
                  <Text>Predicted: {analyticsData.predictions.gasPrice.predicted} gwei</Text>
                  <Badge colorScheme="blue">
                    {(analyticsData.predictions.gasPrice.confidence * 100).toFixed(1)}% confidence
                  </Badge>
                </HStack>
              </Box>
              
              <Box>
                <Text fontWeight="bold">MEV Opportunities</Text>
                <HStack>
                  <Text>Current: {analyticsData.predictions.mevOpportunities.current}</Text>
                  <Text>Predicted: {analyticsData.predictions.mevOpportunities.predicted}</Text>
                  <Badge colorScheme="blue">
                    {(analyticsData.predictions.mevOpportunities.confidence * 100).toFixed(1)}% confidence
                  </Badge>
                </HStack>
              </Box>
              
              <Box>
                <Text fontWeight="bold">Risk Score</Text>
                <HStack>
                  <Text>Current: {(analyticsData.predictions.riskScore.current * 100).toFixed(1)}%</Text>
                  <Text>Predicted: {(analyticsData.predictions.riskScore.predicted * 100).toFixed(1)}%</Text>
                  <Badge colorScheme="blue">
                    {(analyticsData.predictions.riskScore.confidence * 100).toFixed(1)}% confidence
                  </Badge>
                </HStack>
              </Box>
            </Grid>
          </CardBody>
        </Card>

        {/* Insights and Recommendations */}
        <Grid templateColumns="repeat(auto-fit, minmax(400px, 1fr))" gap={6}>
          <Card>
            <CardBody>
              <Heading size="md" mb={4}>Key Insights</Heading>
              <VStack align="stretch" spacing={2}>
                {analyticsData.insights.map((insight, index) => (
                  <HStack key={index}>
                    <FiInfo color="blue" />
                    <Text fontSize="sm">{insight}</Text>
                  </HStack>
                ))}
              </VStack>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Heading size="md" mb={4}>Recommendations</Heading>
              <VStack align="stretch" spacing={2}>
                {analyticsData.recommendations.map((recommendation, index) => (
                  <HStack key={index}>
                    <FiAlertTriangle color="orange" />
                    <Text fontSize="sm">{recommendation}</Text>
                  </HStack>
                ))}
              </VStack>
            </CardBody>
          </Card>
        </Grid>
      </VStack>
    </Box>
  )
}
```

### **Day 5-6: Real-time Data Visualization**

#### **Step 1: Create Real-time Charts Component**
**File:** `services/ui/nextjs-app/src/components/visualization/RealTimeCharts.tsx`

```typescript
import React, { useState, useEffect, useRef } from 'react'
import {
  Box,
  VStack,
  HStack,
  Text,
  Select,
  Button,
  useColorModeValue,
  Card,
  CardBody,
  Heading,
  Badge,
  Switch,
  FormControl,
  FormLabel
} from '@chakra-ui/react'
import { FiPlay, FiPause, FiRefreshCw } from 'react-icons/fi'
import dynamic from 'next/dynamic'

const LineChart = dynamic(() => import('react-chartjs-2').then(mod => mod.Line), { ssr: false })
const BarChart = dynamic(() => import('react-chartjs-2').then(mod => mod.Bar), { ssr: false })

interface ChartData {
  labels: string[]
  datasets: {
    label: string
    data: number[]
    borderColor: string
    backgroundColor: string
    tension: number
  }[]
}

interface RealTimeChartsProps {
  initialData?: ChartData
  updateInterval?: number
}

export const RealTimeCharts: React.FC<RealTimeChartsProps> = ({
  initialData,
  updateInterval = 5000
}) => {
  const [isLive, setIsLive] = useState(true)
  const [chartType, setChartType] = useState('line')
  const [dataType, setDataType] = useState('transactions')
  const [chartData, setChartData] = useState<ChartData>(initialData || {
    labels: [],
    datasets: []
  })
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const bgColor = useColorModeValue('white', 'gray.800')

  useEffect(() => {
    if (isLive) {
      startLiveUpdates()
    } else {
      stopLiveUpdates()
    }

    return () => stopLiveUpdates()
  }, [isLive, dataType])

  const startLiveUpdates = () => {
    stopLiveUpdates()
    intervalRef.current = setInterval(fetchNewData, updateInterval)
  }

  const stopLiveUpdates = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }

  const fetchNewData = async () => {
    try {
      const response = await fetch(`/api/real-time/${dataType}`)
      if (response.ok) {
        const newData = await response.json()
        updateChartData(newData)
      }
    } catch (error) {
      console.error('Error fetching real-time data:', error)
    }
  }

  const updateChartData = (newData: any) => {
    setChartData(prevData => {
      const now = new Date().toLocaleTimeString()
      const newLabels = [...prevData.labels, now].slice(-20) // Keep last 20 points
      
      const newDatasets = prevData.datasets.map(dataset => ({
        ...dataset,
        data: [...dataset.data, newData[dataset.label.toLowerCase()] || 0].slice(-20)
      }))

      return {
        labels: newLabels,
        datasets: newDatasets
      }
    })
  }

  const getChartOptions = () => ({
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 0
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Time'
        }
      },
      y: {
        display: true,
        title: {
          display: true,
          text: getYAxisLabel()
        }
      }
    },
    plugins: {
      legend: {
        display: true,
        position: 'top' as const
      }
    }
  })

  const getYAxisLabel = () => {
    switch (dataType) {
      case 'transactions':
        return 'Transaction Count'
      case 'gas':
        return 'Gas Price (gwei)'
      case 'volume':
        return 'Volume (ETH)'
      case 'risk':
        return 'Risk Score'
      default:
        return 'Value'
    }
  }

  const getChartColors = () => {
    const colors = {
      transactions: ['#3182CE', '#63B3ED'],
      gas: ['#E53E3E', '#FC8181'],
      volume: ['#38A169', '#68D391'],
      risk: ['#D69E2E', '#F6E05E']
    }
    return colors[dataType as keyof typeof colors] || ['#3182CE', '#63B3ED']
  }

  const initializeChartData = () => {
    const colors = getChartColors()
    const baseData = {
      transactions: { count: 150, value: 1000 },
      gas: { price: 30, volatility: 5 },
      volume: { total: 5000, average: 100 },
      risk: { score: 0.3, trend: 0.1 }
    }

    const data = baseData[dataType as keyof typeof baseData]
    const labels = Array.from({ length: 10 }, (_, i) => 
      new Date(Date.now() - (9 - i) * 1000).toLocaleTimeString()
    )

    const datasets = Object.entries(data).map(([key, value], index) => ({
      label: key.charAt(0).toUpperCase() + key.slice(1),
      data: Array.from({ length: 10 }, () => value + Math.random() * 20 - 10),
      borderColor: colors[index % colors.length],
      backgroundColor: colors[index % colors.length] + '20',
      tension: 0.4
    }))

    setChartData({ labels, datasets })
  }

  useEffect(() => {
    initializeChartData()
  }, [dataType])

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Controls */}
        <Card>
          <CardBody>
            <HStack justify="space-between" wrap="wrap">
              <HStack spacing={4}>
                <FormControl display="flex" alignItems="center">
                  <FormLabel htmlFor="live-mode" mb="0">
                    Live Mode
                  </FormLabel>
                  <Switch
                    id="live-mode"
                    isChecked={isLive}
                    onChange={(e) => setIsLive(e.target.checked)}
                  />
                </FormControl>

                <Select
                  value={dataType}
                  onChange={(e) => setDataType(e.target.value)}
                  width="200px"
                >
                  <option value="transactions">Transactions</option>
                  <option value="gas">Gas Prices</option>
                  <option value="volume">Volume</option>
                  <option value="risk">Risk Scores</option>
                </Select>

                <Select
                  value={chartType}
                  onChange={(e) => setChartType(e.target.value)}
                  width="150px"
                >
                  <option value="line">Line Chart</option>
                  <option value="bar">Bar Chart</option>
                </Select>
              </HStack>

              <HStack spacing={2}>
                <Button
                  size="sm"
                  leftIcon={isLive ? <FiPause /> : <FiPlay />}
                  onClick={() => setIsLive(!isLive)}
                >
                  {isLive ? 'Pause' : 'Start'}
                </Button>
                <Button
                  size="sm"
                  leftIcon={<FiRefreshCw />}
                  onClick={fetchNewData}
                >
                  Refresh
                </Button>
              </HStack>
            </HStack>

            <HStack mt={2}>
              <Badge colorScheme={isLive ? 'green' : 'gray'}>
                {isLive ? 'Live' : 'Paused'}
              </Badge>
              <Text fontSize="sm" color="gray.600">
                Updates every {updateInterval / 1000} seconds
              </Text>
            </HStack>
          </CardBody>
        </Card>

        {/* Chart */}
        <Card>
          <CardBody>
            <Heading size="md" mb={4}>
              Real-time {dataType.charAt(0).toUpperCase() + dataType.slice(1)} Data
            </Heading>
            <Box height="400px">
              {chartType === 'line' ? (
                <LineChart data={chartData} options={getChartOptions()} />
              ) : (
                <BarChart data={chartData} options={getChartOptions()} />
              )}
            </Box>
          </CardBody>
        </Card>

        {/* Statistics */}
        <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4}>
          {chartData.datasets.map((dataset, index) => (
            <Card key={index}>
              <CardBody>
                <VStack>
                  <Text fontWeight="bold">{dataset.label}</Text>
                  <Text fontSize="2xl">
                    {dataset.data[dataset.data.length - 1]?.toFixed(2) || '0'}
                  </Text>
                  <Text fontSize="sm" color="gray.600">
                    Latest value
                  </Text>
                </VStack>
              </CardBody>
            </Card>
          ))}
        </Grid>
      </VStack>
    </Box>
  )
}
```

### **Day 7: Integration & Testing**

#### **Step 1: Create Integration Test Suite**
**File:** `tests/integration/test_voice_operations.py`

```python
import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from services.voiceops.voice_operations import VoiceOperations, VoiceCommand
from services.voiceops.websocket_handler import VoiceWebSocketHandler
from services.voiceops.alert_manager import VoiceAlertManager

class TestVoiceOperations:
    @pytest.fixture
    def voice_ops(self):
        return VoiceOperations()
    
    @pytest.mark.asyncio
    async def test_text_to_speech(self, voice_ops):
        """Test text-to-speech functionality"""
        with patch('services.voiceops.voice_operations.generate') as mock_generate:
            mock_generate.return_value = b'fake_audio_data'
            
            audio = await voice_ops.text_to_speech("Test message")
            
            assert audio == b'fake_audio_data'
            mock_generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_voice_command(self, voice_ops):
        """Test voice command processing"""
        command = await voice_ops.process_voice_command("show dashboard", "user123")
        
        assert command.command_text == "show dashboard"
        assert command.user_id == "user123"
        assert command.intent == "show_dashboard"
        assert command.confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_execute_voice_command(self, voice_ops):
        """Test voice command execution"""
        command = VoiceCommand(
            command_id="test_cmd",
            user_id="user123",
            command_text="show dashboard",
            intent="show_dashboard",
            confidence=0.9,
            parameters={},
            timestamp=None
        )
        
        result = await voice_ops.execute_voice_command(command)
        
        assert result['success'] == True
        assert result['action'] == 'navigate'
        assert result['page'] == 'dashboard'

class TestWebSocketHandler:
    @pytest.fixture
    def handler(self):
        return VoiceWebSocketHandler()
    
    @pytest.mark.asyncio
    async def test_handle_voice_command(self, handler):
        """Test WebSocket voice command handling"""
        mock_websocket = Mock()
        mock_websocket.send = AsyncMock()
        
        message = {
            'type': 'voice_command',
            'audio_data': 'base64_encoded_audio'
        }
        
        with patch.object(handler.voice_ops, 'speech_to_text') as mock_stt, \
             patch.object(handler.voice_ops, 'process_voice_command') as mock_process, \
             patch.object(handler.voice_ops, 'execute_voice_command') as mock_execute:
            
            mock_stt.return_value = "show dashboard"
            mock_process.return_value = Mock(
                command_id="test_cmd",
                command_text="show dashboard",
                intent="show_dashboard",
                confidence=0.9,
                parameters={},
                timestamp=None
            )
            mock_execute.return_value = {
                'success': True,
                'action': 'navigate',
                'page': 'dashboard'
            }
            
            await handler._handle_voice_command(mock_websocket, message)
            
            mock_websocket.send.assert_called_once()
            sent_data = json.loads(mock_websocket.send.call_args[0][0])
            assert sent_data['type'] == 'command_result'
            assert sent_data['result']['success'] == True

class TestAlertManager:
    @pytest.fixture
    def alert_manager(self):
        mock_handler = Mock()
        return VoiceAlertManager(mock_handler)
    
    @pytest.mark.asyncio
    async def test_check_alerts(self, alert_manager):
        """Test alert checking functionality"""
        metrics = {
            'risk_score': 0.9,
            'mev_opportunities': 10,
            'transfer_value': 2000000,
            'health_score': 0.5
        }
        
        alerts = await alert_manager.check_alerts(metrics)
        
        assert len(alerts) > 0
        assert any(alert.alert_type == "High Risk Transaction" for alert in alerts)
        assert any(alert.alert_type == "MEV Attack Detected" for alert in alerts)
    
    @pytest.mark.asyncio
    async def test_resolve_alert(self, alert_manager):
        """Test alert resolution"""
        # Create a test alert
        alert = Mock(alert_id="test_alert")
        alert_manager.active_alerts["test_rule"] = alert
        
        await alert_manager.resolve_alert("test_alert", "user123")
        
        assert "test_rule" not in alert_manager.active_alerts
        assert len(alert_manager.alert_history) > 0
        assert alert_manager.alert_history[-1].acknowledged_by == "user123"

@pytest.mark.asyncio
async def test_end_to_end_voice_flow():
    """Test complete voice operations flow"""
    # Initialize services
    voice_ops = VoiceOperations()
    handler = VoiceWebSocketHandler()
    alert_manager = VoiceAlertManager(handler)
    
    # Test voice command flow
    command = await voice_ops.process_voice_command("check alerts", "user123")
    result = await voice_ops.execute_voice_command(command)
    
    assert result['success'] == True
    assert result['action'] == 'show_alerts'
    
    # Test alert generation
    metrics = {'risk_score': 0.9}
    alerts = await alert_manager.check_alerts(metrics)
    
    assert len(alerts) > 0
    
    # Test alert broadcasting
    if alerts:
        await handler.broadcast_alert(alerts[0])
        # Verify alert was processed (in real implementation, check WebSocket messages)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

#### **Step 2: Create Frontend Integration Test**
**File:** `tests/frontend/test_voice_components.test.tsx`

```typescript
import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { VoiceControl } from '../../src/components/voice/VoiceControl'
import { VoiceAlert } from '../../src/components/voice/VoiceAlert'
import { AdvancedAnalytics } from '../../src/components/dashboard/AdvancedAnalytics'

// Mock WebSocket
const mockWebSocket = {
  send: jest.fn(),
  close: jest.fn(),
  onopen: null,
  onmessage: null,
  onclose: null
}

global.WebSocket = jest.fn(() => mockWebSocket)

// Mock fetch
global.fetch = jest.fn()

const renderWithChakra = (component: React.ReactElement) => {
  return render(<ChakraProvider>{component}</ChakraProvider>)
}

describe('VoiceControl Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('renders voice control button', () => {
    renderWithChakra(<VoiceControl />)
    expect(screen.getByLabelText('Voice control')).toBeInTheDocument()
  })

  test('shows connection status', () => {
    renderWithChakra(<VoiceControl />)
    expect(screen.getByText('Disconnected')).toBeInTheDocument()
  })

  test('handles text command input', async () => {
    const mockOnCommand = jest.fn()
    renderWithChakra(<VoiceControl onCommand={mockOnCommand} />)
    
    const suggestionButton = screen.getByText('Show dashboard')
    fireEvent.click(suggestionButton)
    
    await waitFor(() => {
      expect(mockWebSocket.send).toHaveBeenCalledWith(
        JSON.stringify({
          type: 'text_command',
          command_text: 'Show dashboard'
        })
      )
    })
  })
})

describe('VoiceAlert Component', () => {
  const mockAlert = {
    alert_id: 'test-alert',
    alert_type: 'High Risk',
    message: 'High risk transaction detected',
    priority: 'high',
    timestamp: new Date().toISOString()
  }

  test('renders alert with correct priority', () => {
    renderWithChakra(<VoiceAlert alert={mockAlert} />)
    expect(screen.getByText('High Risk')).toBeInTheDocument()
    expect(screen.getByText('high')).toBeInTheDocument()
  })

  test('handles dismiss action', () => {
    const mockOnDismiss = jest.fn()
    renderWithChakra(<VoiceAlert alert={mockAlert} onDismiss={mockOnDismiss} />)
    
    const dismissButton = screen.getByLabelText('Dismiss alert')
    fireEvent.click(dismissButton)
    
    expect(mockOnDismiss).toHaveBeenCalledWith('test-alert')
  })

  test('handles acknowledge action', () => {
    const mockOnAcknowledge = jest.fn()
    renderWithChakra(<VoiceAlert alert={mockAlert} onAcknowledge={mockOnAcknowledge} />)
    
    const acknowledgeButton = screen.getByText('Acknowledge')
    fireEvent.click(acknowledgeButton)
    
    expect(mockOnAcknowledge).toHaveBeenCalledWith('test-alert')
  })
})

describe('AdvancedAnalytics Component', () => {
  beforeEach(() => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({
        riskMetrics: {
          transactionVolumeRisk: 0.7,
          gasPriceVolatilityRisk: 0.5,
          failureRateRisk: 0.3,
          mevActivityRisk: 0.8,
          largeTransferRisk: 0.4,
          suspiciousActivityRisk: 0.6
        },
        predictions: {
          transactionVolume: { current: 150, predicted: 160, confidence: 0.85 },
          gasPrice: { current: 30, predicted: 35, confidence: 0.75 },
          mevOpportunities: { current: 5, predicted: 7, confidence: 0.8 },
          riskScore: { current: 0.6, predicted: 0.65, confidence: 0.9 }
        },
        timeSeriesData: {
          labels: ['12:00', '12:01', '12:02'],
          transactionCount: [150, 155, 160],
          gasPrice: [30, 32, 35],
          riskScore: [0.6, 0.62, 0.65]
        },
        insights: ['High transaction volume detected', 'MEV activity increasing'],
        recommendations: ['Monitor MEV patterns', 'Review risk thresholds']
      })
    })
  })

  test('renders analytics dashboard', async () => {
    renderWithChakra(<AdvancedAnalytics />)
    
    await waitFor(() => {
      expect(screen.getByText('Advanced Analytics Dashboard')).toBeInTheDocument()
    })
  })

  test('displays risk metrics', async () => {
    renderWithChakra(<AdvancedAnalytics />)
    
    await waitFor(() => {
      expect(screen.getByText('Transaction Volume Risk')).toBeInTheDocument()
      expect(screen.getByText('70.0%')).toBeInTheDocument()
    })
  })

  test('shows predictions', async () => {
    renderWithChakra(<AdvancedAnalytics />)
    
    await waitFor(() => {
      expect(screen.getByText('Predictive Analytics')).toBeInTheDocument()
      expect(screen.getByText('Current: 150')).toBeInTheDocument()
      expect(screen.getByText('Predicted: 160')).toBeInTheDocument()
    })
  })

  test('displays insights and recommendations', async () => {
    renderWithChakra(<AdvancedAnalytics />)
    
    await waitFor(() => {
      expect(screen.getByText('Key Insights')).toBeInTheDocument()
      expect(screen.getByText('High transaction volume detected')).toBeInTheDocument()
      expect(screen.getByText('Recommendations')).toBeInTheDocument()
      expect(screen.getByText('Monitor MEV patterns')).toBeInTheDocument()
    })
  })
})
```

---

## 🚀 **IMPLEMENTATION CHECKLIST**

### **Week 11 Checklist:**
- [ ] Create VoiceOperations service with ElevenLabs integration
- [ ] Implement WebSocket handler for real-time voice communication
- [ ] Build VoiceAlertManager for automated alert generation
- [ ] Create VoiceCommandProcessor for intent recognition
- [ ] Test voice-to-text and text-to-speech functionality
- [ ] Implement voice command execution pipeline
- [ ] Set up alert broadcasting system

### **Week 12 Checklist:**
- [ ] Create VoiceControl React component
- [ ] Build VoiceAlert component for displaying alerts
- [ ] Implement AdvancedAnalytics dashboard
- [ ] Create RealTimeCharts component
- [ ] Set up WebSocket connections for real-time updates
- [ ] Test voice command processing end-to-end
- [ ] Verify alert system integration

---

## �� **TESTING STRATEGY**

### **Voice Operations Tests:**
```bash
# Test voice operations service
python -m pytest tests/integration/test_voice_operations.py -v

# Test WebSocket connections
python -m pytest tests/integration/test_websocket_handler.py -v

# Test alert system
python -m pytest tests/integration/test_alert_manager.py -v
```

### **Frontend Component Tests:**
```bash
# Test voice components
npm test -- tests/frontend/test_voice_components.test.tsx

# Test analytics components
npm test -- tests/frontend/test_analytics_components.test.tsx

# Test real-time charts
npm test -- tests/frontend/test_realtime_charts.test.tsx
```

### **End-to-End Voice Tests:**
```bash
# Test complete voice flow
python -m pytest tests/e2e/test_voice_flow.py -v

# Test voice alert integration
python -m pytest tests/e2e/test_voice_alerts.py -v
```

---

## 📊 **SUCCESS METRICS**

### **Week 11 Success Criteria:**
- ✅ Voice commands are processed and executed correctly
- ✅ Text-to-speech and speech-to-text working
- ✅ WebSocket connections handle real-time communication
- ✅ Alert system generates and broadcasts voice alerts
- ✅ Intent recognition accuracy > 80%

### **Week 12 Success Criteria:**
- ✅ Voice control UI components render correctly
- ✅ Real-time charts update automatically
- ✅ Advanced analytics dashboard displays data
- ✅ Voice alerts play audio and show notifications
- ✅ Mobile-responsive design working

---

## 🔧 **TROUBLESHOOTING**

### **Common Issues:**

1. **Voice commands not working:**
   - Check ElevenLabs API key configuration
   - Verify WebSocket connection status
   - Check microphone permissions in browser

2. **Real-time charts not updating:**
   - Verify WebSocket connection
   - Check data source endpoints
   - Monitor network connectivity

3. **Voice alerts not playing:**
   - Check audio permissions
   - Verify TTS service is working
   - Test audio output device

### **Debug Commands:**
```bash
# Test voice operations
python -c "from services.voiceops.voice_operations import VoiceOperations; VoiceOperations().text_to_speech('test')"

# Check WebSocket connections
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Key: test" http://localhost:5000/voice

# Test alert system
python -c "from services.voiceops.alert_manager import VoiceAlertManager; VoiceAlertManager(None).check_alerts({'risk_score': 0.9})"
```

---

## 📈 **NEXT STEPS**

After completing Phase 6, you'll have:
- ✅ Voice command system with ElevenLabs integration
- ✅ Real-time voice alerts and notifications
- ✅ Advanced analytics dashboard with predictions
- ✅ Real-time data visualization
- ✅ Mobile-responsive UI components

**Ready for Phase 7:** Final Integration & Deployment

This completes the voice operations and advanced UI capabilities, providing a comprehensive "Palantir of Compliance" system with voice control and real-time analytics.