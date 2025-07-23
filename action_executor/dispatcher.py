"""
Autonomous Action Executor
Executes automated trading and risk management actions based on AI signals
"""

import os
import json
import yaml
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import redis
from google.cloud import pubsub_v1
from google.cloud import secretmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment configuration
GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
PUBSUB_TOPIC_SIGNALS = os.getenv('PUBSUB_TOPIC_SIGNALS', 'ai-signals')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
DRY_RUN_MODE = os.getenv('DRY_RUN_MODE', 'true').lower() == 'true'

app = FastAPI(
    title="Autonomous Action Executor",
    description="Executes automated actions based on AI signals and playbooks",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
redis_client = redis.from_url(REDIS_URL)
publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()
secret_client = secretmanager.SecretManagerServiceClient()

class ActionType(str, Enum):
    FREEZE_POSITION = "freeze_position"
    HEDGE_LIQUIDITY = "hedge_liquidity"
    DEX_ARBITRAGE = "dex_arb"
    RISK_ALERT = "risk_alert"
    PORTFOLIO_REBALANCE = "portfolio_rebalance"

class ActionStatus(str, Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DRY_RUN = "dry_run"

@dataclass
class ActionContext:
    signal_hash: str
    confidence: float
    risk_score: float
    market_conditions: Dict[str, Any]
    portfolio_state: Dict[str, Any]
    timestamp: datetime

class ActionRequest(BaseModel):
    action_type: ActionType
    signal_hash: str = Field(..., description="Hash of the triggering signal")
    confidence: float = Field(..., ge=0, le=1, description="Signal confidence")
    risk_score: float = Field(..., ge=0, le=1, description="Risk assessment score")
    parameters: Dict[str, Any] = Field(..., description="Action-specific parameters")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    force_execute: bool = Field(False, description="Force execution even in high-risk conditions")
    dry_run: bool = Field(True, description="Execute in dry-run mode")

class ActionResponse(BaseModel):
    action_id: str
    status: ActionStatus
    action_type: ActionType
    estimated_completion: Optional[datetime] = None
    result_preview: Optional[Dict[str, Any]] = None
    risk_assessment: Dict[str, Any]
    execution_plan: List[str]

class ExecutionResult(BaseModel):
    action_id: str
    status: ActionStatus
    execution_time: float
    gas_used: Optional[int] = None
    transaction_hashes: List[str] = Field(default_factory=list)
    error_details: Optional[str] = None
    result_data: Dict[str, Any] = Field(default_factory=dict)

class PlaybookEngine:
    """Loads and executes YAML-defined action playbooks"""
    
    def __init__(self):
        self.playbooks = {}
        self.load_playbooks()
    
    def load_playbooks(self):
        """Load all playbook YAML files"""
        playbook_dir = "action_executor/playbooks"
        if not os.path.exists(playbook_dir):
            logger.warning(f"Playbook directory {playbook_dir} not found")
            return
        
        for filename in os.listdir(playbook_dir):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                try:
                    filepath = os.path.join(playbook_dir, filename)
                    with open(filepath, 'r') as f:
                        playbook_data = yaml.safe_load(f)
                    
                    action_type = filename.replace('.yaml', '').replace('.yml', '')
                    self.playbooks[action_type] = playbook_data
                    logger.info(f"Loaded playbook: {action_type}")
                    
                except Exception as e:
                    logger.error(f"Failed to load playbook {filename}: {e}")
    
    def get_playbook(self, action_type: str) -> Optional[Dict]:
        """Get playbook by action type"""
        return self.playbooks.get(action_type)
    
    def validate_playbook_parameters(self, action_type: str, parameters: Dict) -> List[str]:
        """Validate parameters against playbook requirements"""
        playbook = self.get_playbook(action_type)
        if not playbook:
            return [f"Playbook not found for action type: {action_type}"]
        
        errors = []
        required_params = playbook.get('required_parameters', [])
        
        for param in required_params:
            if param not in parameters:
                errors.append(f"Missing required parameter: {param}")
        
        return errors

class RiskAssessment:
    """Evaluates risk before executing actions"""
    
    @staticmethod
    def assess_action_risk(
        action_type: ActionType, 
        context: ActionContext, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess risk for a proposed action"""
        
        base_risk = context.risk_score
        confidence_factor = 1 - context.confidence
        
        # Action-specific risk adjustments
        action_risk_multipliers = {
            ActionType.FREEZE_POSITION: 0.5,  # Lower risk
            ActionType.HEDGE_LIQUIDITY: 0.7,
            ActionType.DEX_ARBITRAGE: 1.2,    # Higher risk
            ActionType.RISK_ALERT: 0.1,       # Very low risk
            ActionType.PORTFOLIO_REBALANCE: 0.9
        }
        
        multiplier = action_risk_multipliers.get(action_type, 1.0)
        adjusted_risk = min(1.0, base_risk * multiplier + confidence_factor * 0.3)
        
        # Market condition adjustments
        market_volatility = context.market_conditions.get('volatility', 0.5)
        if market_volatility > 0.8:
            adjusted_risk *= 1.3
        
        # Portfolio size considerations
        portfolio_value = context.portfolio_state.get('total_value', 0)
        position_size = parameters.get('position_size', 0)
        
        if portfolio_value > 0:
            size_ratio = position_size / portfolio_value
            if size_ratio > 0.1:  # More than 10% of portfolio
                adjusted_risk *= (1 + size_ratio)
        
        risk_level = "LOW" if adjusted_risk < 0.3 else "MEDIUM" if adjusted_risk < 0.7 else "HIGH"
        
        return {
            "risk_score": adjusted_risk,
            "risk_level": risk_level,
            "base_risk": base_risk,
            "confidence_factor": confidence_factor,
            "market_volatility": market_volatility,
            "position_size_ratio": position_size / portfolio_value if portfolio_value > 0 else 0,
            "recommendation": "APPROVE" if adjusted_risk < 0.6 else "REVIEW" if adjusted_risk < 0.8 else "REJECT"
        }

class ActionExecutor:
    """Executes specific action types"""
    
    def __init__(self, playbook_engine: PlaybookEngine):
        self.playbook_engine = playbook_engine
        self.execution_history = {}
    
    async def execute_action(
        self, 
        action_request: ActionRequest, 
        context: ActionContext
    ) -> ExecutionResult:
        """Execute an action based on its type and parameters"""
        
        action_id = f"{action_request.action_type}_{int(datetime.utcnow().timestamp())}"
        start_time = datetime.utcnow()
        
        try:
            # Get playbook
            playbook = self.playbook_engine.get_playbook(action_request.action_type.value)
            if not playbook:
                raise ValueError(f"No playbook found for {action_request.action_type}")
            
            # Execute based on action type
            if action_request.action_type == ActionType.FREEZE_POSITION:
                result = await self._execute_freeze_position(action_request, context, playbook)
            elif action_request.action_type == ActionType.HEDGE_LIQUIDITY:
                result = await self._execute_hedge_liquidity(action_request, context, playbook)
            elif action_request.action_type == ActionType.DEX_ARBITRAGE:
                result = await self._execute_dex_arbitrage(action_request, context, playbook)
            elif action_request.action_type == ActionType.RISK_ALERT:
                result = await self._execute_risk_alert(action_request, context, playbook)
            elif action_request.action_type == ActionType.PORTFOLIO_REBALANCE:
                result = await self._execute_portfolio_rebalance(action_request, context, playbook)
            else:
                raise ValueError(f"Unknown action type: {action_request.action_type}")
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ExecutionResult(
                action_id=action_id,
                status=ActionStatus.DRY_RUN if action_request.dry_run else ActionStatus.COMPLETED,
                execution_time=execution_time,
                result_data=result
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Action execution failed: {e}")
            
            return ExecutionResult(
                action_id=action_id,
                status=ActionStatus.FAILED,
                execution_time=execution_time,
                error_details=str(e)
            )
    
    async def _execute_freeze_position(
        self, 
        request: ActionRequest, 
        context: ActionContext,
        playbook: Dict
    ) -> Dict[str, Any]:
        """Execute position freeze action"""
        
        position_id = request.parameters.get('position_id')
        freeze_duration = request.parameters.get('freeze_duration_hours', 24)
        
        if request.dry_run or DRY_RUN_MODE:
            logger.info(f"DRY RUN: Would freeze position {position_id} for {freeze_duration} hours")
            return {
                "action": "position_freeze",
                "position_id": position_id,
                "freeze_duration": freeze_duration,
                "simulated": True,
                "estimated_impact": "Trading disabled for specified position"
            }
        
        # Actual implementation would integrate with trading platform API
        logger.info(f"Freezing position {position_id}")
        
        return {
            "action": "position_freeze",
            "position_id": position_id,
            "freeze_duration": freeze_duration,
            "executed_at": datetime.utcnow().isoformat(),
            "status": "active"
        }
    
    async def _execute_hedge_liquidity(
        self, 
        request: ActionRequest, 
        context: ActionContext,
        playbook: Dict
    ) -> Dict[str, Any]:
        """Execute liquidity hedging action"""
        
        hedge_amount = request.parameters.get('hedge_amount')
        hedge_asset = request.parameters.get('hedge_asset', 'USDC')
        target_pools = request.parameters.get('target_pools', [])
        
        if request.dry_run or DRY_RUN_MODE:
            logger.info(f"DRY RUN: Would hedge {hedge_amount} {hedge_asset} across {len(target_pools)} pools")
            return {
                "action": "liquidity_hedge",
                "hedge_amount": hedge_amount,
                "hedge_asset": hedge_asset,
                "target_pools": target_pools,
                "simulated": True,
                "estimated_slippage": "0.15%",
                "estimated_gas": "~0.05 ETH"
            }
        
        # Actual implementation would execute DEX transactions
        logger.info(f"Executing liquidity hedge: {hedge_amount} {hedge_asset}")
        
        return {
            "action": "liquidity_hedge",
            "hedge_amount": hedge_amount,
            "hedge_asset": hedge_asset,
            "executed_pools": target_pools,
            "transaction_count": len(target_pools),
            "executed_at": datetime.utcnow().isoformat()
        }
    
    async def _execute_dex_arbitrage(
        self, 
        request: ActionRequest, 
        context: ActionContext,
        playbook: Dict
    ) -> Dict[str, Any]:
        """Execute DEX arbitrage action"""
        
        source_dex = request.parameters.get('source_dex')
        target_dex = request.parameters.get('target_dex')
        token_pair = request.parameters.get('token_pair')
        arb_amount = request.parameters.get('arb_amount')
        
        if request.dry_run or DRY_RUN_MODE:
            logger.info(f"DRY RUN: Would execute arbitrage {token_pair} from {source_dex} to {target_dex}")
            return {
                "action": "dex_arbitrage",
                "source_dex": source_dex,
                "target_dex": target_dex,
                "token_pair": token_pair,
                "arb_amount": arb_amount,
                "simulated": True,
                "estimated_profit": "0.12 ETH",
                "estimated_gas": "~0.08 ETH",
                "net_profit": "0.04 ETH"
            }
        
        # Actual implementation would execute arbitrage transactions
        logger.info(f"Executing DEX arbitrage: {token_pair}")
        
        return {
            "action": "dex_arbitrage",
            "source_dex": source_dex,
            "target_dex": target_dex,
            "token_pair": token_pair,
            "executed_amount": arb_amount,
            "profit_realized": "TBD",
            "executed_at": datetime.utcnow().isoformat()
        }
    
    async def _execute_risk_alert(
        self, 
        request: ActionRequest, 
        context: ActionContext,
        playbook: Dict
    ) -> Dict[str, Any]:
        """Execute risk alert action"""
        
        alert_type = request.parameters.get('alert_type', 'risk_threshold_breach')
        recipients = request.parameters.get('recipients', [])
        severity = request.parameters.get('severity', 'medium')
        
        # Always execute alerts (even in dry-run mode)
        logger.info(f"Sending {severity} risk alert: {alert_type}")
        
        # Publish to Pub/Sub for alert processing
        alert_message = {
            "alert_type": alert_type,
            "severity": severity,
            "signal_hash": request.signal_hash,
            "risk_score": context.risk_score,
            "confidence": context.confidence,
            "parameters": request.parameters,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        topic_path = publisher.topic_path(GOOGLE_CLOUD_PROJECT, "risk-alerts")
        publisher.publish(topic_path, json.dumps(alert_message).encode())
        
        return {
            "action": "risk_alert",
            "alert_type": alert_type,
            "severity": severity,
            "recipients_notified": len(recipients),
            "alert_id": f"alert_{int(datetime.utcnow().timestamp())}",
            "sent_at": datetime.utcnow().isoformat()
        }
    
    async def _execute_portfolio_rebalance(
        self, 
        request: ActionRequest, 
        context: ActionContext,
        playbook: Dict
    ) -> Dict[str, Any]:
        """Execute portfolio rebalancing action"""
        
        target_allocation = request.parameters.get('target_allocation', {})
        rebalance_threshold = request.parameters.get('rebalance_threshold', 0.05)
        
        if request.dry_run or DRY_RUN_MODE:
            logger.info(f"DRY RUN: Would rebalance portfolio to {target_allocation}")
            return {
                "action": "portfolio_rebalance",
                "target_allocation": target_allocation,
                "rebalance_threshold": rebalance_threshold,
                "simulated": True,
                "estimated_trades": 3,
                "estimated_gas": "~0.15 ETH"
            }
        
        # Actual implementation would execute rebalancing trades
        logger.info(f"Executing portfolio rebalance")
        
        return {
            "action": "portfolio_rebalance",
            "target_allocation": target_allocation,
            "trades_executed": len(target_allocation),
            "executed_at": datetime.utcnow().isoformat()
        }

# Initialize services
playbook_engine = PlaybookEngine()
action_executor = ActionExecutor(playbook_engine)

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "action-executor",
        "dry_run_mode": DRY_RUN_MODE,
        "playbooks_loaded": len(playbook_engine.playbooks),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/execute", response_model=ActionResponse)
async def execute_action(request: ActionRequest, background_tasks: BackgroundTasks):
    """Execute an action based on signal and playbook"""
    
    # Validate playbook parameters
    validation_errors = playbook_engine.validate_playbook_parameters(
        request.action_type.value, 
        request.parameters
    )
    if validation_errors:
        raise HTTPException(status_code=400, detail=f"Parameter validation failed: {validation_errors}")
    
    # Create action context
    context = ActionContext(
        signal_hash=request.signal_hash,
        confidence=request.confidence,
        risk_score=request.risk_score,
        market_conditions=request.context.get('market_conditions', {}) if request.context else {},
        portfolio_state=request.context.get('portfolio_state', {}) if request.context else {},
        timestamp=datetime.utcnow()
    )
    
    # Assess risk
    risk_assessment = RiskAssessment.assess_action_risk(
        request.action_type, context, request.parameters
    )
    
    # Check if action should be blocked by risk assessment
    if (risk_assessment['recommendation'] == 'REJECT' and 
        not request.force_execute and 
        not request.dry_run):
        raise HTTPException(
            status_code=403, 
            detail=f"Action rejected due to high risk score: {risk_assessment['risk_score']:.3f}"
        )
    
    # Generate action ID
    action_id = f"{request.action_type.value}_{int(datetime.utcnow().timestamp())}"
    
    # Create execution plan
    playbook = playbook_engine.get_playbook(request.action_type.value)
    execution_plan = playbook.get('execution_steps', []) if playbook else []
    
    # Schedule background execution
    background_tasks.add_task(
        execute_action_background,
        action_id,
        request,
        context
    )
    
    return ActionResponse(
        action_id=action_id,
        status=ActionStatus.PENDING,
        action_type=request.action_type,
        estimated_completion=datetime.utcnow() + timedelta(minutes=5),
        risk_assessment=risk_assessment,
        execution_plan=execution_plan
    )

async def execute_action_background(action_id: str, request: ActionRequest, context: ActionContext):
    """Execute action in background and store result"""
    try:
        # Update status to executing
        redis_client.hset(f"action:{action_id}", "status", ActionStatus.EXECUTING.value)
        
        # Execute the action
        result = await action_executor.execute_action(request, context)
        
        # Store result in Redis
        redis_client.hset(f"action:{action_id}", mapping={
            "status": result.status.value,
            "execution_time": result.execution_time,
            "result_data": json.dumps(result.result_data),
            "completed_at": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Action {action_id} completed with status {result.status}")
        
    except Exception as e:
        logger.error(f"Background execution failed for {action_id}: {e}")
        redis_client.hset(f"action:{action_id}", mapping={
            "status": ActionStatus.FAILED.value,
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        })

@app.get("/actions/{action_id}/status")
async def get_action_status(action_id: str):
    """Get the status of a specific action"""
    action_data = redis_client.hgetall(f"action:{action_id}")
    
    if not action_data:
        raise HTTPException(status_code=404, detail="Action not found")
    
    return {
        "action_id": action_id,
        "status": action_data.get("status"),
        "execution_time": action_data.get("execution_time"),
        "result_data": json.loads(action_data.get("result_data", "{}")),
        "completed_at": action_data.get("completed_at"),
        "error": action_data.get("error")
    }

@app.get("/playbooks")
async def list_playbooks():
    """List all available action playbooks"""
    return {
        "playbooks": list(playbook_engine.playbooks.keys()),
        "details": {
            name: {
                "description": data.get("description", ""),
                "required_parameters": data.get("required_parameters", []),
                "risk_level": data.get("risk_level", "medium")
            }
            for name, data in playbook_engine.playbooks.items()
        }
    }

@app.post("/playbooks/reload")
async def reload_playbooks():
    """Reload all playbooks from disk"""
    playbook_engine.load_playbooks()
    return {
        "message": "Playbooks reloaded",
        "loaded_count": len(playbook_engine.playbooks),
        "playbooks": list(playbook_engine.playbooks.keys())
    }

@app.get("/actions/history")
async def get_action_history(limit: int = 50):
    """Get recent action execution history"""
    # Get all action keys from Redis
    action_keys = redis_client.keys("action:*")
    
    actions = []
    for key in action_keys[-limit:]:  # Get most recent
        action_data = redis_client.hgetall(key)
        if action_data:
            action_id = key.decode().replace("action:", "")
            actions.append({
                "action_id": action_id,
                "status": action_data.get("status"),
                "execution_time": action_data.get("execution_time"),
                "completed_at": action_data.get("completed_at"),
                "error": action_data.get("error")
            })
    
    return {"actions": actions, "total": len(actions)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
