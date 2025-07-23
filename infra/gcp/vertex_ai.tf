# Vertex AI Workbench for model development
resource "google_notebooks_instance" "ai_workbench" {
  name         = "onchain-ai-workbench"
  location     = var.region
  machine_type = "n1-standard-4"

  vm_image {
    project      = "deeplearning-platform-release"
    image_family = "tf-ent-2-11-cu113-notebooks"
  }

  service_account = google_service_account.agents.email

  metadata = {
    terraform = "true"
  }

  labels = {
    environment = var.environment
  }
}

# Model registry for storing trained models
resource "google_vertex_ai_model" "ethereum_risk_model" {
  display_name = "ethereum-risk-model"
  region       = var.region

  artifact_uri          = "gs://${google_storage_bucket.ml_artifacts.name}/models/risk/"
  container_image_uri   = "us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-11:latest"
  serving_container_ports = [8080]

  labels = {
    environment = var.environment
    model_type  = "risk_scoring"
  }
}

# Vertex AI Endpoint for model serving
resource "google_vertex_ai_endpoint" "risk_scoring" {
  name         = "risk-scoring-endpoint"
  display_name = "Risk Scoring Endpoint"
  region       = var.region

  labels = {
    environment = var.environment
  }
}

# Feature Store for ML features
resource "google_vertex_ai_featurestore" "onchain_features" {
  name   = "onchain-features"
  region = var.region

  labels = {
    environment = var.environment
  }

  online_serving_config {
    fixed_node_count = 1
  }
}

resource "google_vertex_ai_featurestore_entitytype" "wallet_features" {
  name         = "wallet-features"
  featurestore = google_vertex_ai_featurestore.onchain_features.id

  monitoring_config {
    snapshot_analysis {
      disabled = false
    }
  }

  labels = {
    environment = var.environment
  }
}

# Batch prediction job template
resource "google_dataflow_job" "batch_prediction" {
  name              = "batch-prediction-job"
  template_gcs_path = "gs://dataflow-templates-${var.region}/latest/Vertex_AI_Batch_Prediction"
  temp_gcs_location = "gs://${google_storage_bucket.dataflow_temp.name}/temp"
  
  parameters = {
    modelName          = google_vertex_ai_model.ethereum_risk_model.name
    inputFilePattern   = "gs://${google_storage_bucket.ml_artifacts.name}/batch_input/*.jsonl"
    outputFilePrefix   = "gs://${google_storage_bucket.ml_artifacts.name}/batch_output/"
    region            = var.region
  }

  labels = {
    environment = var.environment
  }
}

# Training pipeline
resource "google_vertex_ai_training_pipeline" "risk_model_training" {
  display_name = "risk-model-training"
  region       = var.region

  training_task_definition = jsonencode({
    "trainingTaskInputs" : {
      "workerPoolSpecs" : [{
        "machineSpec" : {
          "machineType" : "n1-standard-4"
        },
        "replicaCount" : 1,
        "containerSpec" : {
          "imageUri" : "gcr.io/${var.project_id}/risk-model-trainer:latest"
        }
      }]
    }
  })

  labels = {
    environment = var.environment
  }
}

# Storage bucket for ML artifacts
resource "google_storage_bucket" "ml_artifacts" {
  name     = "${var.project_id}-ml-artifacts"
  location = var.region

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 90
    }
  }
}

resource "google_storage_bucket" "dataflow_temp" {
  name     = "${var.project_id}-dataflow-temp"
  location = var.region

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 1
    }
  }
}

# ========================================
# Gemini 2-Pro Explainability Service
# ========================================

# Vertex AI Endpoint for Gemini Explainer
resource "google_vertex_ai_endpoint" "gemini_explainer" {
  name         = "gemini-explainer-endpoint"
  display_name = "Gemini 2-Pro Explainability Service"
  region       = var.region

  labels = {
    environment = var.environment
    service     = "gemini-explainer"
    version     = "v3"
  }
}

# Service account for Gemini explainer
resource "google_service_account" "gemini_explainer_sa" {
  account_id   = "gemini-explainer"
  display_name = "Gemini Explainer Service Account"
  description  = "Service account for Gemini explainer service"
}

# IAM bindings for Gemini service account
resource "google_project_iam_member" "gemini_explainer_aiplatform" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.gemini_explainer_sa.email}"
}

resource "google_project_iam_member" "gemini_explainer_storage" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.gemini_explainer_sa.email}"
}

# Secret for Gemini API key
resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "gemini-api-key"

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }

  labels = {
    environment = var.environment
    service     = "gemini-explainer"
  }
}

# IAM for secret access
resource "google_secret_manager_secret_iam_member" "gemini_api_key_access" {
  secret_id = google_secret_manager_secret.gemini_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.gemini_explainer_sa.email}"
}

# Cloud Run service for Gemini explainer API
resource "google_cloud_run_service" "gemini_explainer_api" {
  name     = "gemini-explainer-api"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.gemini_explainer_sa.email
      
      containers {
        image = "gcr.io/${var.project_id}/gemini-explainer:latest"
        
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }
        
        env {
          name  = "VERTEX_AI_REGION"
          value = var.region
        }
        
        env {
          name = "GEMINI_API_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.gemini_api_key.secret_id
              key  = "latest"
            }
          }
        }
        
        resources {
          limits = {
            cpu    = "2"
            memory = "4Gi"
          }
          requests = {
            cpu    = "1"
            memory = "2Gi"
          }
        }
        
        ports {
          container_port = 8001
        }
      }
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "1"
        "autoscaling.knative.dev/maxScale" = "10"
        "run.googleapis.com/cpu-throttling" = "false"
      }
      
      labels = {
        environment = var.environment
        service     = "gemini-explainer"
        version     = "v3"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# IAM to allow public access to Cloud Run
resource "google_cloud_run_service_iam_member" "gemini_explainer_public" {
  location = google_cloud_run_service.gemini_explainer_api.location
  project  = google_cloud_run_service.gemini_explainer_api.project
  service  = google_cloud_run_service.gemini_explainer_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Monitoring for Gemini explainer service
resource "google_monitoring_alert_policy" "gemini_explainer_errors" {
  display_name = "Gemini Explainer Error Rate"
  
  conditions {
    display_name = "High error rate"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${google_cloud_run_service.gemini_explainer_api.name}\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  alert_strategy {
    auto_close = "1800s"
  }
}

# Output the Cloud Run URL
output "gemini_explainer_url" {
  description = "URL of the Gemini explainer Cloud Run service"
  value       = google_cloud_run_service.gemini_explainer_api.status[0].url
}

output "gemini_explainer_endpoint_id" {
  description = "The ID of the Gemini explainer Vertex AI endpoint"
  value       = google_vertex_ai_endpoint.gemini_explainer.id
}
