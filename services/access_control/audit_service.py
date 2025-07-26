import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import aiohttp
from google.cloud import bigquery
from google.cloud import logging as cloud_logging

@dataclass
class AuditEvent:
    user_id: str
    action: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    severity: str = 'INFO'

class AuditService:
    def __init__(self):
        self.bigquery_client = bigquery.Client()
        self.cloud_logger = cloud_logging.Client()
        self.logger = logging.getLogger(__name__)
        
        # BigQuery table configuration
        self.dataset_id = 'onchain_audit'
        self.table_id = 'audit_logs'
        self.table_ref = self.bigquery_client.dataset(self.dataset_id).table(self.table_id)
        
    async def log_event(self, event: AuditEvent) -> bool:
        """Log an audit event to BigQuery and Cloud Logging"""
        try:
            if event.timestamp is None:
                event.timestamp = datetime.utcnow()
            
            # Prepare event data
            event_data = {
                'user_id': event.user_id,
                'action': event.action,
                'details': json.dumps(event.details),
                'ip_address': event.ip_address,
                'user_agent': event.user_agent,
                'timestamp': event.timestamp.isoformat(),
                'resource_type': event.resource_type,
                'resource_id': event.resource_id,
                'severity': event.severity
            }
            
            # Log to BigQuery
            await self._log_to_bigquery(event_data)
            
            # Log to Cloud Logging
            await self._log_to_cloud_logging(event)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error logging audit event: {e}")
            return False
    
    async def _log_to_bigquery(self, event_data: Dict[str, Any]):
        """Log event to BigQuery"""
        try:
            # Insert row into BigQuery
            errors = self.bigquery_client.insert_rows_json(
                self.table_ref,
                [event_data]
            )
            
            if errors:
                self.logger.error(f"BigQuery insert errors: {errors}")
                
        except Exception as e:
            self.logger.error(f"BigQuery logging error: {e}")
    
    async def _log_to_cloud_logging(self, event: AuditEvent):
        """Log event to Cloud Logging"""
        try:
            logger = self.cloud_logger.logger('onchain-audit')
            
            log_entry = {
                'user_id': event.user_id,
                'action': event.action,
                'details': event.details,
                'ip_address': event.ip_address,
                'user_agent': event.user_agent,
                'resource_type': event.resource_type,
                'resource_id': event.resource_id,
                'severity': event.severity
            }
            
            logger.log_struct(log_entry, severity=event.severity)
            
        except Exception as e:
            self.logger.error(f"Cloud Logging error: {e}")
    
    async def log_user_action(self, user_id: str, action: str, details: Dict[str, Any], 
                            ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Log a user action"""
        event = AuditEvent(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return await self.log_event(event)
    
    async def log_system_event(self, action: str, details: Dict[str, Any], severity: str = 'INFO'):
        """Log a system event"""
        event = AuditEvent(
            user_id='system',
            action=action,
            details=details,
            severity=severity
        )
        
        return await self.log_event(event)
    
    async def log_data_access(self, user_id: str, resource_type: str, resource_id: str,
                            access_type: str, ip_address: Optional[str] = None):
        """Log data access events"""
        details = {
            'access_type': access_type,
            'resource_type': resource_type,
            'resource_id': resource_id
        }
        
        event = AuditEvent(
            user_id=user_id,
            action='DATA_ACCESS',
            details=details,
            ip_address=ip_address,
            resource_type=resource_type,
            resource_id=resource_id
        )
        
        return await self.log_event(event)
    
    async def log_admin_action(self, user_id: str, action: str, details: Dict[str, Any],
                             ip_address: Optional[str] = None):
        """Log admin actions with higher severity"""
        event = AuditEvent(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address,
            severity='WARNING'
        )
        
        return await self.log_event(event)
    
    async def get_user_audit_logs(self, user_id: str, limit: int = 100) -> list:
        """Get audit logs for a specific user"""
        try:
            query = f"""
            SELECT *
            FROM `{self.dataset_id}.{self.table_id}`
            WHERE user_id = @user_id
            ORDER BY timestamp DESC
            LIMIT @limit
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("limit", "INT64", limit)
                ]
            )
            
            query_job = self.bigquery_client.query(query, job_config=job_config)
            results = query_job.result()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Error getting user audit logs: {e}")
            return []
    
    async def get_recent_audit_logs(self, hours: int = 24, limit: int = 1000) -> list:
        """Get recent audit logs"""
        try:
            query = f"""
            SELECT *
            FROM `{self.dataset_id}.{self.table_id}`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @hours HOUR)
            ORDER BY timestamp DESC
            LIMIT @limit
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("hours", "INT64", hours),
                    bigquery.ScalarQueryParameter("limit", "INT64", limit)
                ]
            )
            
            query_job = self.bigquery_client.query(query, job_config=job_config)
            results = query_job.result()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Error getting recent audit logs: {e}")
            return []

# Global audit service instance
audit_service = AuditService() 