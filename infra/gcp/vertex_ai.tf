# Current Workbench resource, replacing the deprecated Notebooks instance type.
resource "google_workbench_instance" "ai_workbench" {
  name     = "onchain-ai-workbench"
  location = var.workbench_zone
  gce_setup {
    machine_type = "n1-standard-4"
    vm_image {
      project = "cloud-notebooks-managed"
      family  = "workbench-instances"
    }
    service_accounts {
      email = google_service_account.agents.email
    }
    metadata = {
      terraform = "true"
    }
  }
  labels = {
    environment = var.environment
  }
}

# Model upload/registration is not a resource supported by hashicorp/google 5.x.
# Supply an actual model resource created through the Vertex AI SDK/API.
variable "vertex_model_resource" {
  description = "Externally registered Vertex model resource; no model is fabricated or uploaded by this module."
  type        = string
  default     = null
  validation {
    condition     = var.vertex_model_resource == null ? true : can(regex("^projects/[^/]+/locations/[^/]+/models/[^/]+$", var.vertex_model_resource))
    error_message = "Use an actual projects/PROJECT/locations/REGION/models/MODEL resource."
  }
}

variable "workbench_zone" {
  description = "Compute zone for the notebook VM, not a region."
  type        = string
  default     = "us-central1-a"
}

# Vertex AI Endpoint for model serving
resource "google_vertex_ai_endpoint" "risk_scoring" {
  name         = "risk-scoring-endpoint"
  display_name = "Risk Scoring Endpoint"
  location     = var.region

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

# Only launch a Dataflow job when an actual caller-provided template exists.
variable "batch_prediction_template_gcs_path" {
  description = "Real custom Dataflow template URI. The formerly hardcoded Vertex_AI_Batch_Prediction template was not a verified template."
  type        = string
  default     = null
  validation {
    condition     = var.batch_prediction_template_gcs_path == null ? true : can(regex("^gs://[^/]+/.+", var.batch_prediction_template_gcs_path))
    error_message = "The template must be a GCS URI."
  }
}

resource "google_dataflow_job" "batch_prediction" {
  count             = var.batch_prediction_template_gcs_path == null ? 0 : 1
  name              = "batch-prediction-job"
  template_gcs_path = var.batch_prediction_template_gcs_path
  temp_gcs_location = "gs://${google_storage_bucket.dataflow_temp.name}/temp"
  parameters = {
    modelName        = var.vertex_model_resource
    inputFilePattern = "gs://${google_storage_bucket.ml_artifacts.name}/batch_input/*.jsonl"
    outputFilePrefix = "gs://${google_storage_bucket.ml_artifacts.name}/batch_output/"
    region           = var.region
  }
  lifecycle {
    precondition {
      condition     = var.vertex_model_resource != null
      error_message = "An externally registered Vertex model is required before launching the template."
    }
  }
}

# No training job or trained model is provisioned by this Terraform module.
# google_vertex_ai_training_pipeline is not a supported Google provider resource.
# The application SDK owns training, upload, and model-quality validation.
output "vertex_ml_integration" {
  description = "Actual provisioned endpoint and explicit external model boundary. This is not evidence of a deployed/trained model."
  value = {
    endpoint_id      = google_vertex_ai_endpoint.risk_scoring.id
    model_resource   = var.vertex_model_resource
    training_managed = false
    model_uploaded   = false
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
