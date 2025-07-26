from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Audit Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AuditLogRequest(BaseModel):
    action: str
    details: Dict[str, Any]
    timestamp: Optional[str] = None
    user_id: Optional[str] = None

# In-memory storage for audit logs (in production, this would be BigQuery)
audit_logs = []

@app.post("/audit/log")
async def log_audit_event(request: AuditLogRequest):
    """Log an audit event"""
    try:
        log_entry = {
            "action": request.action,
            "details": request.details,
            "timestamp": request.timestamp or datetime.utcnow().isoformat(),
            "user_id": request.user_id,
            "ip_address": "127.0.0.1",  # In production, get from request
            "user_agent": "NextJS Frontend"
        }
        
        audit_logs.append(log_entry)
        logger.info(f"Audit log created: {request.action}")
        
        return {"status": "success", "message": "Audit event logged successfully"}
    
    except Exception as e:
        logger.error(f"Error logging audit event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audit/logs")
async def get_audit_logs():
    """Get all audit logs"""
    return {"logs": audit_logs, "count": len(audit_logs)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "audit-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4001) 