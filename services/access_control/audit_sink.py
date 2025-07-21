"""
Access Control Service - Policy-based access management.

Implements fine-grained access control policies for blockchain data,
including column-level security and audit trail generation.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

import structlog
from google.cloud import bigquery
from google.cloud import logging as cloud_logging
from google.cloud import pubsub_v1
import yaml

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


class AccessLevel(Enum):
    """Access levels for data classification."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class Action(Enum):
    """Possible actions on data."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXPORT = "export"


@dataclass
class AccessRequest:
    """Request for data access."""
    user_id: str
    service_account: str
    resource: str
    action: Action
    context: Dict[str, Any]
    timestamp: datetime


@dataclass
class AccessDecision:
    """Result of access control evaluation."""
    granted: bool
    reason: str
    conditions: List[str]
    audit_required: bool
    redacted_fields: List[str]


@dataclass
class AuditEvent:
    """Audit event for compliance tracking."""
    event_id: str
    user_id: str
    service_account: str
    resource: str
    action: Action
    decision: AccessDecision
    timestamp: datetime
    request_context: Dict[str, Any]


class PolicyEngine:
    """Policy-based access control engine."""
    
    def __init__(self):
        self.bigquery_client = bigquery.Client()
        self.logging_client = cloud_logging.Client()
        self.publisher = pubsub_v1.PublisherClient()
        self.logger = logger.bind(service="access-control")
        
        # Load access policies
        self.policies = self._load_policies()
        
        # Setup audit logging
        self.audit_topic = self.publisher.topic_path(
            os.getenv('GOOGLE_CLOUD_PROJECT'),
            'audit-events'
        )
        
    def _load_policies(self) -> Dict[str, Any]:
        """Load access control policies from configuration."""
        try:
            policy_path = os.path.join(os.path.dirname(__file__), 'policies.yaml')
            with open(policy_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error("Error loading policies", error=str(e))
            return self._get_default_policies()
    
    def _get_default_policies(self) -> Dict[str, Any]:
        """Get default access control policies."""
        return {
            'roles': {
                'analyst': {
                    'permissions': ['read'],
                    'resources': ['curated_events', 'ai_signals'],
                    'conditions': ['no_pii_access'],
                    'redacted_fields': ['from_address', 'to_address']
                },
                'admin': {
                    'permissions': ['read', 'write', 'delete', 'export'],
                    'resources': ['*'],
                    'conditions': [],
                    'redacted_fields': []
                },
                'service': {
                    'permissions': ['read', 'write'],
                    'resources': ['raw_events', 'curated_events'],
                    'conditions': ['service_account_only'],
                    'redacted_fields': []
                }
            },
            'data_classification': {
                'raw_events': 'confidential',
                'curated_events': 'internal',
                'ai_signals': 'internal',
                'entity_resolutions': 'restricted'
            },
            'audit_rules': {
                'always_audit': ['restricted', 'confidential'],
                'audit_actions': ['export', 'delete'],
                'retention_days': 2557  # 7 years for SOC-2
            }
        }
    
    def evaluate_access(self, request: AccessRequest) -> AccessDecision:
        """Evaluate access request against policies."""
        try:
            # Determine user role
            user_role = self._determine_user_role(request.user_id, request.service_account)
            
            # Get resource classification
            resource_classification = self._get_resource_classification(request.resource)
            
            # Check basic permissions
            if not self._check_basic_permissions(user_role, request.action, request.resource):
                return AccessDecision(
                    granted=False,
                    reason="Insufficient permissions",
                    conditions=[],
                    audit_required=True,
                    redacted_fields=[]
                )
            
            # Check conditions
            conditions_met, failed_conditions = self._evaluate_conditions(
                user_role, request, resource_classification
            )
            
            if not conditions_met:
                return AccessDecision(
                    granted=False,
                    reason=f"Failed conditions: {', '.join(failed_conditions)}",
                    conditions=failed_conditions,
                    audit_required=True,
                    redacted_fields=[]
                )
            
            # Determine redacted fields
            redacted_fields = self._get_redacted_fields(user_role, request.resource)
            
            # Determine if audit is required
            audit_required = self._is_audit_required(resource_classification, request.action)
            
            decision = AccessDecision(
                granted=True,
                reason="Access granted",
                conditions=[],
                audit_required=audit_required,
                redacted_fields=redacted_fields
            )
            
            # Log audit event if required
            if audit_required:
                self._log_audit_event(request, decision)
            
            return decision
            
        except Exception as e:
            self.logger.error("Error evaluating access", error=str(e))
            return AccessDecision(
                granted=False,
                reason=f"Evaluation error: {str(e)}",
                conditions=[],
                audit_required=True,
                redacted_fields=[]
            )
    
    def _determine_user_role(self, user_id: str, service_account: str) -> str:
        """Determine user role based on identity."""
        # Service account mapping
        if service_account:
            if 'ingestion' in service_account:
                return 'service'
            elif 'agents' in service_account:
                return 'service'
            elif 'api-gateway' in service_account:
                return 'service'
        
        # User role mapping (would integrate with IAM in production)
        admin_users = ['admin@company.com', 'devops@company.com']
        if user_id in admin_users:
            return 'admin'
        
        return 'analyst'  # Default role
    
    def _get_resource_classification(self, resource: str) -> AccessLevel:
        """Get classification level for a resource."""
        classifications = self.policies.get('data_classification', {})
        classification = classifications.get(resource, 'internal')
        return AccessLevel(classification)
    
    def _check_basic_permissions(self, user_role: str, action: Action, resource: str) -> bool:
        """Check basic role permissions."""
        role_config = self.policies['roles'].get(user_role, {})
        
        # Check action permission
        if action.value not in role_config.get('permissions', []):
            return False
        
        # Check resource access
        allowed_resources = role_config.get('resources', [])
        if '*' not in allowed_resources and resource not in allowed_resources:
            return False
        
        return True
    
    def _evaluate_conditions(self, user_role: str, request: AccessRequest, 
                           classification: AccessLevel) -> tuple[bool, List[str]]:
        """Evaluate access conditions."""
        role_config = self.policies['roles'].get(user_role, {})
        conditions = role_config.get('conditions', [])
        
        failed_conditions = []
        
        for condition in conditions:
            if condition == 'no_pii_access':
                # Check if request involves PII data
                if self._involves_pii(request.resource):
                    failed_conditions.append(condition)
            
            elif condition == 'service_account_only':
                # Must be service account request
                if not request.service_account:
                    failed_conditions.append(condition)
            
            elif condition == 'business_hours_only':
                # Check if within business hours
                if not self._is_business_hours(request.timestamp):
                    failed_conditions.append(condition)
        
        return len(failed_conditions) == 0, failed_conditions
    
    def _involves_pii(self, resource: str) -> bool:
        """Check if resource contains PII data."""
        pii_resources = ['raw_events', 'entity_resolutions']
        return resource in pii_resources
    
    def _is_business_hours(self, timestamp: datetime) -> bool:
        """Check if timestamp is within business hours."""
        # Business hours: 9 AM - 6 PM UTC, Monday-Friday
        weekday = timestamp.weekday()  # 0 = Monday
        hour = timestamp.hour
        
        return 0 <= weekday <= 4 and 9 <= hour <= 18
    
    def _get_redacted_fields(self, user_role: str, resource: str) -> List[str]:
        """Get fields that should be redacted for this user/resource."""
        role_config = self.policies['roles'].get(user_role, {})
        return role_config.get('redacted_fields', [])
    
    def _is_audit_required(self, classification: AccessLevel, action: Action) -> bool:
        """Determine if audit is required for this access."""
        audit_rules = self.policies.get('audit_rules', {})
        
        # Always audit certain classifications
        if classification.value in audit_rules.get('always_audit', []):
            return True
        
        # Always audit certain actions
        if action.value in audit_rules.get('audit_actions', []):
            return True
        
        return False
    
    def _log_audit_event(self, request: AccessRequest, decision: AccessDecision):
        """Log audit event for compliance."""
        try:
            audit_event = AuditEvent(
                event_id=self._generate_event_id(),
                user_id=request.user_id,
                service_account=request.service_account,
                resource=request.resource,
                action=request.action,
                decision=decision,
                timestamp=datetime.now(timezone.utc),
                request_context=request.context
            )
            
            # Send to Pub/Sub for processing
            message_data = json.dumps({
                'event_id': audit_event.event_id,
                'user_id': audit_event.user_id,
                'service_account': audit_event.service_account,
                'resource': audit_event.resource,
                'action': audit_event.action.value,
                'granted': audit_event.decision.granted,
                'reason': audit_event.decision.reason,
                'timestamp': audit_event.timestamp.isoformat(),
                'context': audit_event.request_context
            }).encode('utf-8')
            
            self.publisher.publish(self.audit_topic, message_data)
            
            # Also log to Cloud Logging for immediate visibility
            self.logging_client.logger('audit').log_struct({
                'event_type': 'data_access',
                'event_id': audit_event.event_id,
                'user_id': audit_event.user_id,
                'resource': audit_event.resource,
                'action': audit_event.action.value,
                'granted': audit_event.decision.granted,
                'severity': 'INFO' if audit_event.decision.granted else 'WARNING'
            })
            
            self.logger.info("Logged audit event", 
                           event_id=audit_event.event_id,
                           granted=decision.granted)
            
        except Exception as e:
            self.logger.error("Error logging audit event", error=str(e))
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        import uuid
        return str(uuid.uuid4())
    
    def get_audit_trail(self, user_id: str, start_date: datetime, 
                       end_date: datetime) -> List[AuditEvent]:
        """Get audit trail for a user within date range."""
        try:
            query = """
            SELECT *
            FROM `{project}.onchain_data.audit_events`
            WHERE user_id = @user_id
            AND timestamp BETWEEN @start_date AND @end_date
            ORDER BY timestamp DESC
            """.format(project=os.getenv('GOOGLE_CLOUD_PROJECT'))
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_date),
                    bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", end_date)
                ]
            )
            
            results = self.bigquery_client.query(query, job_config=job_config)
            
            audit_events = []
            for row in results:
                # Convert row to AuditEvent (simplified)
                audit_events.append(dict(row))
            
            return audit_events
            
        except Exception as e:
            self.logger.error("Error retrieving audit trail", error=str(e))
            return []


class AuditSink:
    """Processes audit events from Pub/Sub."""
    
    def __init__(self):
        self.bigquery_client = bigquery.Client()
        self.subscriber = pubsub_v1.SubscriberClient()
        self.logger = logger.bind(service="audit-sink")
        
        self.subscription_path = self.subscriber.subscription_path(
            os.getenv('GOOGLE_CLOUD_PROJECT'),
            'audit-events-sub'
        )
    
    def start_processing(self):
        """Start processing audit events."""
        self.logger.info("Starting audit event processing")
        
        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path,
            callback=self._process_audit_event
        )
        
        try:
            streaming_pull_future.result()
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
            self.logger.info("Audit sink stopped")
    
    def _process_audit_event(self, message):
        """Process a single audit event."""
        try:
            event_data = json.loads(message.data.decode('utf-8'))
            
            # Store in BigQuery
            self._store_audit_event(event_data)
            
            # Check for anomalies
            self._check_audit_anomalies(event_data)
            
            message.ack()
            
        except Exception as e:
            self.logger.error("Error processing audit event", error=str(e))
            message.nack()
    
    def _store_audit_event(self, event_data: Dict[str, Any]):
        """Store audit event in BigQuery."""
        try:
            table_id = f"{os.getenv('GOOGLE_CLOUD_PROJECT')}.onchain_data.audit_events"
            
            rows_to_insert = [event_data]
            errors = self.bigquery_client.insert_rows_json(table_id, rows_to_insert)
            
            if errors:
                self.logger.error("Error storing audit event", errors=errors)
            
        except Exception as e:
            self.logger.error("Error storing audit event", error=str(e))
    
    def _check_audit_anomalies(self, event_data: Dict[str, Any]):
        """Check for suspicious patterns in audit events."""
        # Implement anomaly detection logic
        # e.g., unusual access patterns, failed access attempts
        pass


if __name__ == "__main__":
    # Example usage
    engine = PolicyEngine()
    
    request = AccessRequest(
        user_id="analyst@company.com",
        service_account="",
        resource="curated_events",
        action=Action.READ,
        context={"ip_address": "192.168.1.1"},
        timestamp=datetime.now(timezone.utc)
    )
    
    decision = engine.evaluate_access(request)
    print(f"Access granted: {decision.granted}")
    print(f"Reason: {decision.reason}")
    print(f"Redacted fields: {decision.redacted_fields}")
