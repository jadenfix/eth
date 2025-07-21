# Neo4j Aura database configuration
terraform {
  required_providers {
    neo4j = {
      source  = "neo4j/neo4j"
      version = "~> 0.1"
    }
  }
}

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
        value = "0.0.0.0/0"  # Restrict this in production
        name  = "all"
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
  password = "change-me-in-production"
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
    ip_address     = google_sql_database_instance.graph_dev[0].ip_address[0].ip_address
  } : null
}
