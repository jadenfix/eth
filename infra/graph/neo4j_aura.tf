# Neo4j Aura database configuration
# This file is included in the GCP root module via its tracked symlink.
# Aura itself is configured externally; all resources here use hashicorp/google.
# Note: Neo4j Aura requires manual setup through their console
# This configuration provides the connection details

variable "neo4j_uri" {
  description = "Neo4j Aura connection URI"
  type        = string
  default     = ""
}

variable "neo4j_username" {
  description = "Neo4j username"
  type        = string
  default     = "neo4j"
}

variable "neo4j_password" {
  description = "Neo4j password"
  type        = string
  sensitive   = true
  default     = ""
}

# Store Neo4j connection details in Secret Manager
resource "google_secret_manager_secret_version" "neo4j_uri" {
  count = var.neo4j_uri != "" ? 1 : 0

  secret      = google_secret_manager_secret.neo4j_uri.id
  secret_data = var.neo4j_uri
}

resource "google_secret_manager_secret" "neo4j_uri" {
  secret_id = "neo4j-uri"

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret_version" "neo4j_password_version" {
  count = var.neo4j_password != "" ? 1 : 0

  secret      = google_secret_manager_secret.neo4j_password.id
  secret_data = var.neo4j_password
}

# Cloud SQL instance as alternative to Neo4j Aura for development
resource "google_sql_database_instance" "graph_dev" {
  count            = var.environment == "dev" ? 1 : 0
  name             = "graph-dev-instance"
  database_version = "POSTGRES_14"
  region           = var.region

  settings {
    tier = "db-f1-micro"

    backup_configuration {
      enabled    = true
      start_time = "03:00"
    }

    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        value = var.dev_postgres_allowed_cidr
        name  = "configured-client"
      }
    }
  }

  deletion_protection = false
}

resource "google_sql_database" "ontology" {
  count    = var.environment == "dev" ? 1 : 0
  name     = "ontology"
  instance = google_sql_database_instance.graph_dev[0].name
}

resource "google_sql_user" "ontology_user" {
  count    = var.environment == "dev" ? 1 : 0
  name     = "ontology"
  instance = google_sql_database_instance.graph_dev[0].name
  password = var.dev_postgres_password
}

# Output connection details
output "neo4j_connection_info" {
  description = "Neo4j connection information"
  value = {
    uri_secret      = google_secret_manager_secret.neo4j_uri.secret_id
    password_secret = google_secret_manager_secret.neo4j_password.secret_id
    username        = var.neo4j_username
  }
  sensitive = true
}

output "dev_postgres_info" {
  description = "Development PostgreSQL instance info"
  value = var.environment == "dev" ? {
    connection_name = google_sql_database_instance.graph_dev[0].connection_name
    ip_address      = google_sql_database_instance.graph_dev[0].ip_address[0].ip_address
  } : null
}

variable "dev_postgres_password" {
  description = "Explicit PostgreSQL password. Terraform state contains this sensitive value; protect the backend."
  type        = string
  sensitive   = true
  validation {
    condition     = length(var.dev_postgres_password) >= 16 && var.dev_postgres_password != "change-me-in-production"
    error_message = "Provide a unique PostgreSQL password of at least 16 characters."
  }
}

variable "dev_postgres_allowed_cidr" {
  description = "Explicit client CIDR; unrestricted public access is rejected."
  type        = string
  validation {
    condition     = can(cidrhost(var.dev_postgres_allowed_cidr, 0)) && !contains(["0.0.0.0/0", "::/0"], var.dev_postgres_allowed_cidr)
    error_message = "Provide a valid restricted client CIDR."
  }
}
