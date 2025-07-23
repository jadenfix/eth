# BigQuery to Neo4j CDC (Change Data Capture) Pipeline
resource "google_dataflow_flex_template_job" "neo4j_sync" {
  name                    = "neo4j-bigquery-cdc"
  container_spec_gcs_path = "gs://${var.project_id}-dataflow-templates/neo4j-sync.json"
  region                  = var.region
  
  parameters = {
    inputSubscription     = google_pubsub_subscription.bq_cdc.id
    neo4jUri             = var.neo4j_uri
    neo4jUser            = var.neo4j_user
    neo4jPasswordSecret  = google_secret_manager_secret_version.neo4j_password.name
    batchSize            = "100"
    windowDurationSec    = "30"
  }

  on_delete = "cancel"

  depends_on = [
    google_pubsub_topic.bq_cdc,
    google_pubsub_subscription.bq_cdc
  ]
}

# Pub/Sub topic for BigQuery CDC events
resource "google_pubsub_topic" "bq_cdc" {
  name = "bq-cdc-events"
  
  message_retention_duration = "604800s" # 7 days
  
  labels = {
    component = "cdc"
    layer     = "semantic-fusion"
  }
}

# Subscription for Neo4j sync job
resource "google_pubsub_subscription" "bq_cdc" {
  name  = "neo4j-sync-subscription"
  topic = google_pubsub_topic.bq_cdc.name

  # Message retention for 7 days
  message_retention_duration = "604800s"
  
  # Acknowledge deadline
  ack_deadline_seconds = 120

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.bq_cdc_dlq.id
    max_delivery_attempts = 5
  }
}

# Dead letter queue for failed CDC events
resource "google_pubsub_topic" "bq_cdc_dlq" {
  name = "bq-cdc-dlq"
  
  labels = {
    component = "cdc"
    purpose   = "dead-letter"
  }
}

# Neo4j to BigQuery sync topic
resource "google_pubsub_topic" "neo4j_changes" {
  name = "neo4j-change-events"
  
  message_retention_duration = "604800s"
  
  labels = {
    component = "cdc"
    direction = "neo4j-to-bq"
  }
}

# IAM for Dataflow CDC job
resource "google_service_account" "dataflow_cdc" {
  account_id   = "dataflow-cdc-sa"
  display_name = "Dataflow CDC Service Account"
  description  = "Service account for BigQuery-Neo4j CDC pipeline"
}

resource "google_project_iam_member" "dataflow_cdc_worker" {
  project = var.project_id
  role    = "roles/dataflow.worker"
  member  = "serviceAccount:${google_service_account.dataflow_cdc.email}"
}

resource "google_project_iam_member" "dataflow_cdc_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.dataflow_cdc.email}"
}

resource "google_project_iam_member" "dataflow_cdc_bq" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.dataflow_cdc.email}"
}

# Secret for Neo4j password
resource "google_secret_manager_secret" "neo4j_password" {
  secret_id = "neo4j-password"
  
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "neo4j_password" {
  secret      = google_secret_manager_secret.neo4j_password.id
  secret_data = var.neo4j_password
}

# Variables for CDC configuration
variable "neo4j_uri" {
  description = "Neo4j connection URI"
  type        = string
  default     = "neo4j+s://your-instance.databases.neo4j.io"
}

variable "neo4j_user" {
  description = "Neo4j username"
  type        = string
  default     = "neo4j"
}

variable "neo4j_password" {
  description = "Neo4j password"
  type        = string
  sensitive   = true
}

# Outputs
output "bq_cdc_topic" {
  description = "Pub/Sub topic for BigQuery CDC events"
  value       = google_pubsub_topic.bq_cdc.name
}

output "neo4j_changes_topic" {
  description = "Pub/Sub topic for Neo4j change events"
  value       = google_pubsub_topic.neo4j_changes.name
}
