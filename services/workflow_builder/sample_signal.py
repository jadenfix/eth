"""
Workflow Builder Service - Dagster job definitions for low-code signal building.

Provides visual workflow composition for non-technical users to create
custom blockchain monitoring and alerting workflows.
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from dagster import (
    job, op, Config, In, Out, DynamicOut, DynamicPartitionsDefinition,
    resource, sensor, schedule, asset, AssetMaterialization,
    get_dagster_logger, OpExecutionContext, JobDefinition
)
from dagster_gcp import BigQueryResource
import pandas as pd
import numpy as np


class WorkflowConfig(Config):
    """Configuration for workflow execution."""
    blockchain: str = "ethereum"
    lookback_hours: int = 24
    confidence_threshold: float = 0.7
    alert_channels: List[str] = ["slack", "email"]


@resource
def bigquery_resource():
    """BigQuery resource for data access."""
    return BigQueryResource(
        project=os.getenv('GOOGLE_CLOUD_PROJECT')
    )


@resource  
def notification_resource():
    """Notification service resource."""
    from services.voiceops.notification_service import NotificationService
    return NotificationService()


# Basic building block operations

@op(
    config_schema={"query": str, "parameters": dict},
    out=Out(pd.DataFrame)
)
def fetch_blockchain_data(context: OpExecutionContext, bigquery: BigQueryResource) -> pd.DataFrame:
    """Fetch blockchain data from BigQuery."""
    logger = get_dagster_logger()
    
    query = context.op_config["query"]
    parameters = context.op_config.get("parameters", {})
    
    logger.info(f"Executing query: {query}")
    
    try:
        # Execute BigQuery query
        df = bigquery.get_client().query(query, job_config=None).to_dataframe()
        
        context.log_event(AssetMaterialization(
            asset_key="blockchain_data",
            metadata={
                "num_records": len(df),
                "query": query
            }
        ))
        
        return df
        
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        raise


@op(
    config_schema={"conditions": dict},
    ins={"data": In(pd.DataFrame)},
    out=Out(pd.DataFrame)
)
def filter_data(context: OpExecutionContext, data: pd.DataFrame) -> pd.DataFrame:
    """Apply filters to data based on conditions."""
    logger = get_dagster_logger()
    conditions = context.op_config["conditions"]
    
    filtered_data = data.copy()
    
    for column, condition in conditions.items():
        if column not in filtered_data.columns:
            continue
            
        operator = condition.get("operator", "eq")
        value = condition.get("value")
        
        if operator == "gt":
            filtered_data = filtered_data[filtered_data[column] > value]
        elif operator == "lt":
            filtered_data = filtered_data[filtered_data[column] < value]
        elif operator == "eq":
            filtered_data = filtered_data[filtered_data[column] == value]
        elif operator == "contains":
            filtered_data = filtered_data[filtered_data[column].str.contains(value, na=False)]
    
    logger.info(f"Filtered {len(data)} records to {len(filtered_data)}")
    
    return filtered_data


@op(
    config_schema={"aggregation_type": str, "group_by": list, "metrics": list},
    ins={"data": In(pd.DataFrame)},
    out=Out(pd.DataFrame)
)
def aggregate_data(context: OpExecutionContext, data: pd.DataFrame) -> pd.DataFrame:
    """Aggregate data based on configuration."""
    logger = get_dagster_logger()
    
    agg_type = context.op_config["aggregation_type"]
    group_by = context.op_config.get("group_by", [])
    metrics = context.op_config.get("metrics", [])
    
    if not group_by or not metrics:
        return data
    
    try:
        if agg_type == "sum":
            result = data.groupby(group_by)[metrics].sum().reset_index()
        elif agg_type == "mean":
            result = data.groupby(group_by)[metrics].mean().reset_index()
        elif agg_type == "count":
            result = data.groupby(group_by)[metrics].count().reset_index()
        elif agg_type == "max":
            result = data.groupby(group_by)[metrics].max().reset_index()
        else:
            result = data.groupby(group_by)[metrics].sum().reset_index()
        
        logger.info(f"Aggregated data: {len(result)} groups")
        return result
        
    except Exception as e:
        logger.error(f"Error aggregating data: {str(e)}")
        return data


@op(
    config_schema={"threshold": float, "comparison": str, "metric": str},
    ins={"data": In(pd.DataFrame)},
    out=Out(pd.DataFrame)
)
def detect_anomalies(context: OpExecutionContext, data: pd.DataFrame) -> pd.DataFrame:
    """Detect anomalies based on thresholds."""
    logger = get_dagster_logger()
    
    threshold = context.op_config["threshold"]
    comparison = context.op_config["comparison"]
    metric = context.op_config["metric"]
    
    if metric not in data.columns:
        logger.warning(f"Metric {metric} not found in data")
        return pd.DataFrame()
    
    if comparison == "greater_than":
        anomalies = data[data[metric] > threshold]
    elif comparison == "less_than":
        anomalies = data[data[metric] < threshold]
    elif comparison == "std_deviation":
        mean_val = data[metric].mean()
        std_val = data[metric].std()
        anomalies = data[abs(data[metric] - mean_val) > threshold * std_val]
    else:
        anomalies = pd.DataFrame()
    
    logger.info(f"Detected {len(anomalies)} anomalies")
    
    return anomalies


@op(
    config_schema={"signal_type": str, "description": str, "severity": str},
    ins={"anomalies": In(pd.DataFrame)},
    out=Out(dict)
)
def generate_signal(context: OpExecutionContext, anomalies: pd.DataFrame) -> dict:
    """Generate AI signal from anomalies."""
    logger = get_dagster_logger()
    
    if len(anomalies) == 0:
        return {}
    
    signal_type = context.op_config["signal_type"]
    description = context.op_config["description"]
    severity = context.op_config["severity"]
    
    # Extract relevant information
    related_addresses = []
    related_transactions = []
    
    if 'from_address' in anomalies.columns:
        related_addresses.extend(anomalies['from_address'].dropna().tolist())
    if 'to_address' in anomalies.columns:
        related_addresses.extend(anomalies['to_address'].dropna().tolist())
    if 'transaction_hash' in anomalies.columns:
        related_transactions.extend(anomalies['transaction_hash'].dropna().tolist())
    
    # Generate signal
    signal = {
        'signal_id': f"workflow_{context.run_id}_{int(datetime.now().timestamp())}",
        'agent_name': 'workflow_builder',
        'signal_type': signal_type,
        'confidence_score': min(0.9, len(anomalies) / 100.0),  # Simple scoring
        'related_addresses': list(set(related_addresses))[:10],  # Limit to 10
        'related_transactions': list(set(related_transactions))[:10],
        'description': f"{description} - Found {len(anomalies)} anomalies",
        'severity': severity,
        'metadata': {
            'anomaly_count': len(anomalies),
            'workflow_name': context.job_name,
            'generated_by': 'workflow_builder'
        },
        'timestamp': datetime.now().isoformat()
    }
    
    logger.info(f"Generated signal: {signal['signal_id']}")
    
    return signal


@op(
    config_schema={"channels": list},
    ins={"signal": In(dict)},
    out=Out(bool)
)
def send_alert(context: OpExecutionContext, signal: dict, notification_service) -> bool:
    """Send alert through configured channels."""
    logger = get_dagster_logger()
    
    if not signal:
        return True
    
    channels = context.op_config["channels"]
    
    try:
        for channel in channels:
            if channel == "slack":
                notification_service.send_slack_alert(signal)
            elif channel == "email":
                notification_service.send_email_alert(signal)
            elif channel == "webhook":
                notification_service.send_webhook_alert(signal)
        
        logger.info(f"Alert sent to {len(channels)} channels")
        return True
        
    except Exception as e:
        logger.error(f"Error sending alert: {str(e)}")
        return False


# Sample workflow definitions

@job(
    config={
        "ops": {
            "fetch_blockchain_data": {
                "config": {
                    "query": """
                        SELECT * FROM `{project}.onchain_data.curated_events`
                        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
                        AND value_usd > 100000
                    """.format(project=os.getenv('GOOGLE_CLOUD_PROJECT')),
                    "parameters": {}
                }
            },
            "filter_data": {
                "config": {
                    "conditions": {
                        "event_type": {"operator": "eq", "value": "TRANSFER"}
                    }
                }
            },
            "detect_anomalies": {
                "config": {
                    "threshold": 1000000,
                    "comparison": "greater_than",
                    "metric": "value_usd"
                }
            },
            "generate_signal": {
                "config": {
                    "signal_type": "HIGH_VALUE_TRANSFER",
                    "description": "Large transfer detected",
                    "severity": "HIGH"
                }
            },
            "send_alert": {
                "config": {
                    "channels": ["slack", "email"]
                }
            }
        }
    },
    resource_defs={
        "bigquery": bigquery_resource,
        "notification_service": notification_resource
    }
)
def high_value_transfer_monitor():
    """Monitor for high-value transfers."""
    data = fetch_blockchain_data()
    filtered_data = filter_data(data)
    anomalies = detect_anomalies(filtered_data)
    signal = generate_signal(anomalies)
    send_alert(signal)


@job(
    config={
        "ops": {
            "fetch_blockchain_data": {
                "config": {
                    "query": """
                        SELECT 
                            from_address,
                            COUNT(*) as tx_count,
                            SUM(value_usd) as total_value,
                            AVG(value_usd) as avg_value
                        FROM `{project}.onchain_data.curated_events`
                        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
                        GROUP BY from_address
                        HAVING COUNT(*) > 100
                    """.format(project=os.getenv('GOOGLE_CLOUD_PROJECT')),
                    "parameters": {}
                }
            },
            "detect_anomalies": {
                "config": {
                    "threshold": 2.0,
                    "comparison": "std_deviation",
                    "metric": "tx_count"
                }
            },
            "generate_signal": {
                "config": {
                    "signal_type": "SUSPICIOUS_ACTIVITY",
                    "description": "Unusual transaction pattern detected",
                    "severity": "MEDIUM"
                }
            },
            "send_alert": {
                "config": {
                    "channels": ["slack"]
                }
            }
        }
    },
    resource_defs={
        "bigquery": bigquery_resource,
        "notification_service": notification_resource
    }
)
def suspicious_activity_monitor():
    """Monitor for suspicious transaction patterns."""
    data = fetch_blockchain_data()
    anomalies = detect_anomalies(data)
    signal = generate_signal(anomalies)
    send_alert(signal)


# Schedules for regular execution

@schedule(
    job=high_value_transfer_monitor,
    cron_schedule="*/15 * * * *"  # Every 15 minutes
)
def high_value_transfer_schedule():
    """Schedule for high-value transfer monitoring."""
    return {}


@schedule(
    job=suspicious_activity_monitor,
    cron_schedule="0 */4 * * *"  # Every 4 hours
)
def suspicious_activity_schedule():
    """Schedule for suspicious activity monitoring."""
    return {}


# Dynamic job builder for custom workflows

def build_custom_workflow(config: Dict[str, Any]) -> JobDefinition:
    """Build a custom workflow from configuration."""
    
    workflow_name = config.get("name", "custom_workflow")
    ops_config = config.get("ops", {})
    
    @job(
        name=workflow_name,
        config={"ops": ops_config},
        resource_defs={
            "bigquery": bigquery_resource,
            "notification_service": notification_resource
        }
    )
    def custom_workflow():
        """Dynamically generated workflow."""
        data = fetch_blockchain_data()
        
        # Apply filters if configured
        if "filter_data" in ops_config:
            data = filter_data(data)
        
        # Apply aggregation if configured  
        if "aggregate_data" in ops_config:
            data = aggregate_data(data)
        
        # Detect anomalies
        anomalies = detect_anomalies(data)
        
        # Generate and send signal
        signal = generate_signal(anomalies)
        send_alert(signal)
    
    return custom_workflow


# Asset definitions for data lineage

@asset
def blockchain_events_daily():
    """Daily blockchain events asset."""
    # This would materialize daily event summaries
    pass


@asset
def signal_accuracy_metrics():
    """Signal accuracy tracking asset."""
    # This would calculate and store accuracy metrics
    pass
