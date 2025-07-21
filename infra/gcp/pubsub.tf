# Pub/Sub topics for event streaming
resource "google_pubsub_topic" "raw_events" {
  name = "raw-chain-events"

  message_storage_policy {
    allowed_persistence_regions = [var.region]
  }

  message_retention_duration = "604800s" # 7 days
}

resource "google_pubsub_topic" "ai_signals" {
  name = "ai-signals"

  message_storage_policy {
    allowed_persistence_regions = [var.region]
  }
}

resource "google_pubsub_topic" "user_feedback" {
  name = "user-feedback"

  message_storage_policy {
    allowed_persistence_regions = [var.region]
  }
}

# Subscriptions for ingestion service
resource "google_pubsub_subscription" "ingestion_raw_events" {
  name  = "ingestion-raw-events-sub"
  topic = google_pubsub_topic.raw_events.name

  message_retention_duration = "1200s"
  retain_acked_messages      = false
  ack_deadline_seconds       = 120

  expiration_policy {
    ttl = "300000.5s"
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter.id
    max_delivery_attempts = 5
  }
}

# Subscriptions for AI agents
resource "google_pubsub_subscription" "agents_raw_events" {
  name  = "agents-raw-events-sub"
  topic = google_pubsub_topic.raw_events.name

  message_retention_duration = "1200s"
  retain_acked_messages      = false
  ack_deadline_seconds       = 60

  filter = "attributes.event_type=\"TRANSFER\" OR attributes.event_type=\"SWAP\""
}

resource "google_pubsub_subscription" "agents_feedback" {
  name  = "agents-feedback-sub"
  topic = google_pubsub_topic.user_feedback.name

  message_retention_duration = "1200s"
  retain_acked_messages      = false
  ack_deadline_seconds       = 60
}

# Dead letter topic
resource "google_pubsub_topic" "dead_letter" {
  name = "dead-letter-topic"

  message_storage_policy {
    allowed_persistence_regions = [var.region]
  }
}

# IAM bindings for Pub/Sub
resource "google_pubsub_topic_iam_binding" "ingestion_publisher" {
  topic = google_pubsub_topic.raw_events.name
  role  = "roles/pubsub.publisher"

  members = [
    "serviceAccount:${google_service_account.ingestion.email}"
  ]
}

resource "google_pubsub_subscription_iam_binding" "ingestion_subscriber" {
  subscription = google_pubsub_subscription.ingestion_raw_events.name
  role         = "roles/pubsub.subscriber"

  members = [
    "serviceAccount:${google_service_account.ingestion.email}"
  ]
}

resource "google_pubsub_topic_iam_binding" "agents_publisher" {
  topic = google_pubsub_topic.ai_signals.name
  role  = "roles/pubsub.publisher"

  members = [
    "serviceAccount:${google_service_account.agents.email}"
  ]
}

resource "google_pubsub_subscription_iam_binding" "agents_subscriber" {
  subscription = google_pubsub_subscription.agents_raw_events.name
  role         = "roles/pubsub.subscriber"

  members = [
    "serviceAccount:${google_service_account.agents.email}"
  ]
}
