"""
Workflow Builder Service - Dagster job definitions for low-code signal building.

Provides visual workflow composition for non-technical users to create
custom blockchain monitoring and alerting workflows.
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from dagster import (
    job,
    op,
    Config,
    In,
    Out,
    DynamicOut,
    DynamicPartitionsDefinition,
    resource,
    sensor,
    schedule,
    asset,
    AssetMaterialization,
    get_dagster_logger,
    OpExecutionContext,
    JobDefinition,
)
import asyncio
import inspect
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
    from google.cloud import bigquery

    return bigquery.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))


@resource
def notification_resource():
    """Notification service resource."""
    from services.voiceops.voice_service import NotificationService

    return NotificationService()


# Basic building block operations


def fetch_blockchain_data(context: OpExecutionContext, bigquery) -> pd.DataFrame:
    """Fetch blockchain data from BigQuery."""
    logger = get_dagster_logger()

    query = context.op_config["query"]
    parameters = context.op_config.get("parameters", {})

    logger.info(f"Executing query: {query}")

    try:
        # Execute BigQuery query
        client = bigquery.get_client() if hasattr(bigquery, "get_client") else bigquery
        if parameters:
            raise ValueError(
                "Use typed BigQuery QueryJobConfig parameters; untyped parameters are unsupported"
            )
        df = client.query(query, job_config=None).to_dataframe()

        context.log_event(
            AssetMaterialization(
                asset_key="blockchain_data",
                metadata={"num_records": len(df), "query": query},
            )
        )

        return df

    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        raise


def filter_data(context: OpExecutionContext, data: pd.DataFrame) -> pd.DataFrame:
    """Apply filters to data based on conditions."""
    logger = get_dagster_logger()
    conditions = context.op_config["conditions"]

    filtered_data = data.copy()

    for column, condition in conditions.items():
        if column not in filtered_data.columns:
            raise ValueError(f"Unknown filter column: {column}")

        operator = condition.get("operator", "eq")
        value = condition.get("value")

        if operator == "gt":
            filtered_data = filtered_data[filtered_data[column] > value]
        elif operator == "lt":
            filtered_data = filtered_data[filtered_data[column] < value]
        elif operator == "eq":
            filtered_data = filtered_data[filtered_data[column] == value]
        elif operator == "contains":
            filtered_data = filtered_data[
                filtered_data[column]
                .astype("string")
                .str.contains(value, na=False, regex=False)
            ]

        else:
            raise ValueError(f"Unknown filter operator: {operator}")

    logger.info(f"Filtered {len(data)} records to {len(filtered_data)}")

    return filtered_data


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
            raise ValueError(f"Unknown aggregation: {agg_type}")

        logger.info(f"Aggregated data: {len(result)} groups")
        return result

    except Exception as e:
        logger.error(f"Error aggregating data: {str(e)}")
        raise


def detect_anomalies(context: OpExecutionContext, data: pd.DataFrame) -> pd.DataFrame:
    """Detect anomalies based on thresholds."""
    logger = get_dagster_logger()

    threshold = context.op_config["threshold"]
    comparison = context.op_config["comparison"]
    metric = context.op_config["metric"]

    if metric not in data.columns:
        logger.warning(f"Metric {metric} not found in data")
        raise ValueError(f"Unknown anomaly metric: {metric}")

    if comparison == "greater_than":
        anomalies = data[data[metric] > threshold]
    elif comparison == "less_than":
        anomalies = data[data[metric] < threshold]
    elif comparison == "std_deviation":
        mean_val = data[metric].mean()
        std_val = data[metric].std()
        anomalies = data[abs(data[metric] - mean_val) > threshold * std_val]
    else:
        raise ValueError(f"Unknown comparison: {comparison}")

    logger.info(f"Detected {len(anomalies)} anomalies")

    return anomalies


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

    if "from_address" in anomalies.columns:
        related_addresses.extend(anomalies["from_address"].dropna().tolist())
    if "to_address" in anomalies.columns:
        related_addresses.extend(anomalies["to_address"].dropna().tolist())
    if "transaction_hash" in anomalies.columns:
        related_transactions.extend(anomalies["transaction_hash"].dropna().tolist())

    # Generate signal
    signal = {
        "signal_id": f"workflow_{context.run_id}_{int(datetime.now().timestamp())}",
        "agent_name": "workflow_builder",
        "signal_type": signal_type,
        "confidence_score": min(0.9, len(anomalies) / 100.0),  # Simple scoring
        "related_addresses": list(set(related_addresses))[:10],  # Limit to 10
        "related_transactions": list(set(related_transactions))[:10],
        "description": f"{description} - Found {len(anomalies)} anomalies",
        "severity": severity,
        "metadata": {
            "anomaly_count": len(anomalies),
            "workflow_name": context.job_name,
            "generated_by": "workflow_builder",
        },
        "timestamp": datetime.now().isoformat(),
    }

    logger.info(f"Generated signal: {signal['signal_id']}")

    return signal


def send_alert(context: OpExecutionContext, signal: dict, notification_service) -> bool:
    """Send alert through configured channels."""
    logger = get_dagster_logger()

    if not signal:
        return True

    channels = context.op_config["channels"]

    try:
        for channel in channels:
            if channel == "slack":
                result = notification_service.send_slack_alert(signal)
                if inspect.isawaitable(result):
                    asyncio.run(result)
            elif channel == "email":
                result = notification_service.send_email_alert(signal)
                if inspect.isawaitable(result):
                    asyncio.run(result)
            elif channel == "webhook":
                result = notification_service.send_webhook_alert(signal)
                if inspect.isawaitable(result):
                    asyncio.run(result)

        logger.info(f"Alert sent to {len(channels)} channels")
        return True

    except Exception as e:
        logger.error(f"Error sending alert: {str(e)}")
        return False


# Register the pure operations with Dagster; direct callers use the same implementation.
@op(
    name="fetch_blockchain_data",
    required_resource_keys={"bigquery"},
    config_schema={"query": str, "parameters": dict},
)
def fetch_blockchain_data_op(context):
    return fetch_blockchain_data(context, context.resources.bigquery)


@op(name="filter_data", config_schema={"conditions": dict})
def filter_data_op(context, data: pd.DataFrame):
    return filter_data(context, data)


@op(
    name="aggregate_data",
    config_schema={"aggregation_type": str, "group_by": list, "metrics": list},
)
def aggregate_data_op(context, data: pd.DataFrame):
    return aggregate_data(context, data)


@op(
    name="detect_anomalies",
    config_schema={"threshold": float, "comparison": str, "metric": str},
)
def detect_anomalies_op(context, data: pd.DataFrame):
    return detect_anomalies(context, data)


@op(
    name="generate_signal",
    config_schema={"signal_type": str, "description": str, "severity": str},
)
def generate_signal_op(context, anomalies: pd.DataFrame):
    return generate_signal(context, anomalies)


@op(
    name="send_alert",
    required_resource_keys={"notification_service"},
    config_schema={"channels": list},
)
def send_alert_op(context, signal: dict):
    return send_alert(context, signal, context.resources.notification_service)


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
                    """.format(
                        project=os.getenv("GOOGLE_CLOUD_PROJECT")
                    ),
                    "parameters": {},
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
                    "metric": "value_usd",
                }
            },
            "generate_signal": {
                "config": {
                    "signal_type": "HIGH_VALUE_TRANSFER",
                    "description": "Large transfer detected",
                    "severity": "HIGH",
                }
            },
            "send_alert": {"config": {"channels": ["slack", "email"]}},
        }
    },
    resource_defs={
        "bigquery": bigquery_resource,
        "notification_service": notification_resource,
    },
)
def high_value_transfer_monitor():
    """Monitor for high-value transfers."""
    data = fetch_blockchain_data_op()
    filtered_data = filter_data_op(data)
    anomalies = detect_anomalies_op(filtered_data)
    signal = generate_signal_op(anomalies)
    send_alert_op(signal)


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
                    """.format(
                        project=os.getenv("GOOGLE_CLOUD_PROJECT")
                    ),
                    "parameters": {},
                }
            },
            "detect_anomalies": {
                "config": {
                    "threshold": 2.0,
                    "comparison": "std_deviation",
                    "metric": "tx_count",
                }
            },
            "generate_signal": {
                "config": {
                    "signal_type": "SUSPICIOUS_ACTIVITY",
                    "description": "Unusual transaction pattern detected",
                    "severity": "MEDIUM",
                }
            },
            "send_alert": {"config": {"channels": ["slack"]}},
        }
    },
    resource_defs={
        "bigquery": bigquery_resource,
        "notification_service": notification_resource,
    },
)
def suspicious_activity_monitor():
    """Monitor for suspicious transaction patterns."""
    data = fetch_blockchain_data_op()
    anomalies = detect_anomalies_op(data)
    signal = generate_signal_op(anomalies)
    send_alert_op(signal)


# Schedules for regular execution


@schedule(
    job=high_value_transfer_monitor, cron_schedule="*/15 * * * *"  # Every 15 minutes
)
def high_value_transfer_schedule():
    """Schedule for high-value transfer monitoring."""
    return {}


@schedule(job=suspicious_activity_monitor, cron_schedule="0 */4 * * *")  # Every 4 hours
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
            "notification_service": notification_resource,
        },
    )
    def custom_workflow():
        """Dynamically generated workflow."""
        data = fetch_blockchain_data_op()

        # Apply filters if configured
        if "filter_data" in ops_config:
            data = filter_data_op(data)

        # Apply aggregation if configured
        if "aggregate_data" in ops_config:
            data = aggregate_data_op(data)

        # Detect anomalies
        anomalies = detect_anomalies_op(data)

        # Generate and send signal
        if "generate_signal" in ops_config:
            signal = generate_signal_op(anomalies)
            if "send_alert" in ops_config:
                send_alert_op(signal)

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
