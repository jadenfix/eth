# Secret Manager for production credentials
resource "google_secret_manager_secret" "alchemy_api_key" {
  secret_id = "alchemy-api-key"
  
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret" "neo4j_password" {
  secret_id = "neo4j-password"
  
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret" "elevenlabs_api_key" {
  secret_id = "elevenlabs-api-key"
  
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret" "slack_bot_token" {
  secret_id = "slack-bot-token"
  
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret" "stripe_secret_key" {
  secret_id = "stripe-secret-key"
  
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

# IAM bindings for secret access
resource "google_secret_manager_secret_iam_binding" "alchemy_access" {
  secret_id = google_secret_manager_secret.alchemy_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  
  members = [
    "serviceAccount:${google_service_account.ingestion.email}",
    "serviceAccount:${google_service_account.agents.email}"
  ]
}

resource "google_secret_manager_secret_iam_binding" "neo4j_access" {
  secret_id = google_secret_manager_secret.neo4j_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  
  members = [
    "serviceAccount:${google_service_account.api_gateway.email}"
  ]
}

resource "google_secret_manager_secret_iam_binding" "elevenlabs_access" {
  secret_id = google_secret_manager_secret.elevenlabs_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  
  members = [
    "serviceAccount:${google_service_account.api_gateway.email}"
  ]
}

# Additional IAM roles for services
resource "google_project_iam_binding" "ingestion_bigquery_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  
  members = [
    "serviceAccount:${google_service_account.ingestion.email}"
  ]
}

resource "google_project_iam_binding" "ingestion_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  
  members = [
    "serviceAccount:${google_service_account.ingestion.email}"
  ]
}

resource "google_project_iam_binding" "agents_pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  
  members = [
    "serviceAccount:${google_service_account.agents.email}"
  ]
}

resource "google_project_iam_binding" "agents_vertex_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  
  members = [
    "serviceAccount:${google_service_account.agents.email}"
  ]
}

resource "google_project_iam_binding" "api_gateway_bigquery_viewer" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  
  members = [
    "serviceAccount:${google_service_account.api_gateway.email}"
  ]
}
