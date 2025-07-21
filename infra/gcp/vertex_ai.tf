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
