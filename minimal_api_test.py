#!/usr/bin/env python3

import asyncio
import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = FastAPI()

class PredictiveRequest(BaseModel):
    horizon: str = "24h"

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/predictive")
async def test_predictive(request: PredictiveRequest) -> Dict[str, Any]:
    """Test predictive analytics endpoint"""
    try:
        print(f"Received request: {request}")
        
        from services.analytics.predictive_analytics import PredictiveAnalytics
        print("Import successful")
        
        predictive_analytics = PredictiveAnalytics()
        print("Service initialized")
        
        report = await predictive_analytics.generate_predictions(request.horizon)
        print("Predictions generated")
        
        return {
            "report_id": report.report_id,
            "predictions_count": len(report.predictions),
            "alerts_count": len(report.alerts)
        }
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003) 