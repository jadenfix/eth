#!/usr/bin/env python3
"""
Create BigQuery tables for Phase 4 implementation
"""

import os
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

def create_bigquery_tables():
    """Create BigQuery tables for Phase 4"""
    
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'ethhackathon')
    dataset_id = 'onchain_data'
    
    client = bigquery.Client(project=project_id)
    
    # Create dataset if it doesn't exist
    dataset_ref = client.dataset(dataset_id)
    try:
        client.get_dataset(dataset_ref)
        print(f"✅ Dataset {dataset_id} already exists")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        dataset = client.create_dataset(dataset, timeout=30)
        print(f"✅ Created dataset {dataset_id}")
    
    # Table schemas
    tables = {
        'action_results': [
            bigquery.SchemaField("action_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("success", "BOOLEAN", mode="REQUIRED"),
            bigquery.SchemaField("transaction_hash", "STRING"),
            bigquery.SchemaField("error_message", "STRING"),
            bigquery.SchemaField("execution_time_seconds", "FLOAT64"),
            bigquery.SchemaField("gas_used", "INTEGER"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("metadata", "STRING")
        ],
        'positions': [
            bigquery.SchemaField("position_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("address", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("asset", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("amount", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("value_usd", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("risk_score", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("frozen_at", "TIMESTAMP"),
            bigquery.SchemaField("frozen_reason", "STRING")
        ],
        'hedge_positions': [
            bigquery.SchemaField("hedge_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("risk_amount", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("hedge_amount", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("hedge_token", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("risk_token", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("hedge_ratio", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("closed_at", "TIMESTAMP"),
            bigquery.SchemaField("pnl", "FLOAT64")
        ]
    }
    
    # Create tables
    for table_name, schema in tables.items():
        table_id = f"{project_id}.{dataset_id}.{table_name}"
        
        try:
            client.get_table(table_id)
            print(f"✅ Table {table_name} already exists")
        except Exception:
            table = bigquery.Table(table_id, schema=schema)
            table = client.create_table(table, timeout=30)
            print(f"✅ Created table {table_name}")
    
    print("\n🎉 All BigQuery tables created successfully!")

if __name__ == "__main__":
    create_bigquery_tables() 