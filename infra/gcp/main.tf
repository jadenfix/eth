terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "bigquery.googleapis.com",
    "pubsub.googleapis.com",
    "dataflow.googleapis.com",
    "aiplatform.googleapis.com",
    "cloudfunctions.googleapis.com",
    "run.googleapis.com",
    "container.googleapis.com",
    "dlp.googleapis.com",
    "datacatalog.googleapis.com",
    "dataplex.googleapis.com"
  ])
  
  service            = each.value
  disable_on_destroy = false
}

# Service accounts
resource "google_service_account" "ingestion" {
  account_id   = "ingestion-sa"
  display_name = "Ingestion Service Account"
}

resource "google_service_account" "agents" {
  account_id   = "agents-sa"
  display_name = "AI Agents Service Account"
}

resource "google_service_account" "api_gateway" {
  account_id   = "api-gateway-sa"
  display_name = "API Gateway Service Account"
}
