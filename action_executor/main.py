#!/usr/bin/env python3
"""
Action Executor Service
Provides automated action execution capabilities for blockchain monitoring
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from action_executor.position_manager import PositionManager
from action_executor.liquidity_hedger import LiquidityHedger
from action_executor.dispatcher import ActionDispatcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Action Executor Service",
    description="Automated action execution for blockchain monitoring",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
position_manager = PositionManager()
liquidity_hedger = LiquidityHedger()
action_dispatcher = ActionDispatcher()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "position_manager": "active",
            "liquidity_hedger": "active",
            "action_dispatcher": "active"
        }
    }

@app.get("/positions")
async def get_positions():
    """Get all positions"""
    try:
        # This would return actual positions from the database
        return {
            "positions": [],
            "total": 0,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/positions/create")
async def create_position(position_data: Dict[str, Any]):
    """Create a new position"""
    try:
        # This would create a position using the position manager
        return {
            "position_id": "pos_001",
            "status": "created",
            "message": "Position created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating position: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/positions/{position_id}/freeze")
async def freeze_position(position_id: str, reason: str = "Risk threshold exceeded"):
    """Freeze a position"""
    try:
        success = await position_manager.freeze_position(position_id, reason)
        if success:
            return {
                "position_id": position_id,
                "status": "frozen",
                "reason": reason,
                "message": "Position frozen successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Position not found")
    except Exception as e:
        logger.error(f"Error freezing position: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/hedges")
async def get_hedges():
    """Get all hedge positions"""
    try:
        active_hedges = await liquidity_hedger.get_active_hedges()
        return {
            "hedges": [hedge.__dict__ for hedge in active_hedges],
            "total": len(active_hedges),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error getting hedges: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/hedges/create")
async def create_hedge(hedge_params: Dict[str, Any]):
    """Create a new hedge"""
    try:
        hedge_id = await liquidity_hedger.create_hedge(hedge_params)
        if hedge_id:
            return {
                "hedge_id": hedge_id,
                "status": "created",
                "message": "Hedge created successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create hedge")
    except Exception as e:
        logger.error(f"Error creating hedge: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/hedges/{hedge_id}/execute")
async def execute_hedge(hedge_id: str):
    """Execute a hedge"""
    try:
        success = await liquidity_hedger.execute_hedge(hedge_id)
        if success:
            return {
                "hedge_id": hedge_id,
                "status": "executed",
                "message": "Hedge executed successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Hedge not found")
    except Exception as e:
        logger.error(f"Error executing hedge: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/actions")
async def get_actions():
    """Get all actions"""
    try:
        return {
            "actions": [],
            "total": 0,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error getting actions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/actions/trigger")
async def trigger_action(action_data: Dict[str, Any]):
    """Trigger an action"""
    try:
        # This would trigger an action using the dispatcher
        return {
            "action_id": "action_001",
            "status": "triggered",
            "message": "Action triggered successfully"
        }
    except Exception as e:
        logger.error(f"Error triggering action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Action Executor Service")
    parser.add_argument("--port", type=int, default=5003, help="Port to run on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    
    args = parser.parse_args()
    
    logger.info(f"Starting Action Executor Service on {args.host}:{args.port}")
    
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=True,
        log_level="info"
    ) 