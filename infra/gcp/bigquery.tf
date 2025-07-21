# BigQuery dataset for onchain data
resource "google_bigquery_dataset" "onchain_data" {
  dataset_id  = "onchain_data"
  description = "Blockchain data warehouse"
  location    = var.region

  access {
    role          = "OWNER"
    user_by_email = google_service_account.ingestion.email
  }

  access {
    role          = "READER"
    user_by_email = google_service_account.agents.email
  }

  access {
    role          = "READER"
    user_by_email = google_service_account.api_gateway.email
  }
}

# Raw events table
resource "google_bigquery_table" "raw_events" {
  dataset_id = google_bigquery_dataset.onchain_data.dataset_id
  table_id   = "raw_events"

  schema = jsonencode([
    {
      name = "block_number"
      type = "INTEGER"
      mode = "REQUIRED"
    },
    {
      name = "transaction_hash"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "log_index"
      type = "INTEGER"
      mode = "NULLABLE"
    },
    {
      name = "contract_address"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "event_name"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "event_data"
      type = "JSON"
      mode = "REQUIRED"
    },
    {
      name = "timestamp"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "chain_id"
      type = "INTEGER"
      mode = "REQUIRED"
    },
    {
      name = "ingestion_timestamp"
      type = "TIMESTAMP"
      mode = "REQUIRED"
      default_value_expression = "CURRENT_TIMESTAMP()"
    }
  ])

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  clustering = ["chain_id", "contract_address", "event_name"]
}

# Curated events table with entity resolution
resource "google_bigquery_table" "curated_events" {
  dataset_id = google_bigquery_dataset.onchain_data.dataset_id
  table_id   = "curated_events"

  schema = jsonencode([
    {
      name = "event_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "entity_id"
      type = "STRING"
      mode = "NULLABLE"
      description = "Resolved entity identifier from ontology"
    },
    {
      name = "block_number"
      type = "INTEGER"
      mode = "REQUIRED"
    },
    {
      name = "transaction_hash"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "from_address"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "to_address"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "value_usd"
      type = "NUMERIC"
      mode = "NULLABLE"
    },
    {
      name = "event_type"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "risk_score"
      type = "FLOAT"
      mode = "NULLABLE"
    },
    {
      name = "labels"
      type = "STRING"
      mode = "REPEATED"
    },
    {
      name = "metadata"
      type = "JSON"
      mode = "REQUIRED"
    },
    {
      name = "timestamp"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    }
  ])

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  clustering = ["event_type", "entity_id"]
}

# AI signals table
resource "google_bigquery_table" "ai_signals" {
  dataset_id = google_bigquery_dataset.onchain_data.dataset_id
  table_id   = "ai_signals"

  schema = jsonencode([
    {
      name = "signal_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "agent_name"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "signal_type"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "confidence_score"
      type = "FLOAT"
      mode = "REQUIRED"
    },
    {
      name = "related_addresses"
      type = "STRING"
      mode = "REPEATED"
    },
    {
      name = "related_transactions"
      type = "STRING"
      mode = "REPEATED"
    },
    {
      name = "description"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "severity"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "metadata"
      type = "JSON"
      mode = "REQUIRED"
    },
    {
      name = "timestamp"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "feedback_rating"
      type = "INTEGER"
      mode = "NULLABLE"
    }
  ])

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  clustering = ["agent_name", "signal_type", "severity"]
}

# Views for common queries
resource "google_bigquery_table" "high_value_transfers" {
  dataset_id = google_bigquery_dataset.onchain_data.dataset_id
  table_id   = "high_value_transfers_view"

  view {
    query = <<EOF
SELECT 
  event_id,
  entity_id,
  from_address,
  to_address,
  value_usd,
  risk_score,
  labels,
  timestamp
FROM `${var.project_id}.${google_bigquery_dataset.onchain_data.dataset_id}.curated_events`
WHERE event_type = 'TRANSFER'
  AND value_usd > 100000
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
ORDER BY timestamp DESC
EOF
    use_legacy_sql = false
  }
}
