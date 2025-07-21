# DLP policies for column-level data redaction
resource "google_data_loss_prevention_inspect_template" "blockchain_pii" {
  parent       = "projects/${var.project_id}"
  description  = "Inspect template for blockchain PII detection"
  display_name = "Blockchain PII Detection"

  inspect_config {
    info_types {
      name = "EMAIL_ADDRESS"
    }
    info_types {
      name = "PHONE_NUMBER"
    }
    info_types {
      name = "CREDIT_CARD_NUMBER"
    }
    info_types {
      name = "US_SOCIAL_SECURITY_NUMBER"
    }
    
    custom_info_types {
      info_type {
        name = "CRYPTO_WALLET_ADDRESS"
      }
      regex {
        pattern = "0x[a-fA-F0-9]{40}"
      }
      likelihood = "LIKELY"
    }

    min_likelihood = "LIKELY"
    
    limits {
      max_findings_per_info_type {
        info_type {
          name = "EMAIL_ADDRESS"
        }
        max_findings = 100
      }
    }
  }
}

resource "google_data_loss_prevention_deidentify_template" "blockchain_redaction" {
  parent       = "projects/${var.project_id}"
  description  = "De-identification template for blockchain data"
  display_name = "Blockchain Data Redaction"

  deidentify_config {
    info_type_transformations {
      transformations {
        info_types {
          name = "EMAIL_ADDRESS"
        }
        info_types {
          name = "PHONE_NUMBER"
        }
        primitive_transformation {
          replace_config {
            new_value {
              string_value = "[REDACTED]"
            }
          }
        }
      }
      
      transformations {
        info_types {
          name = "CRYPTO_WALLET_ADDRESS"
        }
        primitive_transformation {
          crypto_hash_config {
            crypto_key {
              kms_wrapped {
                wrapped_key     = base64encode("placeholder-key")
                crypto_key_name = google_kms_crypto_key.dlp_key.id
              }
            }
          }
        }
      }
    }
  }
}

# KMS key for DLP
resource "google_kms_key_ring" "dlp" {
  name     = "dlp-keyring"
  location = var.region
}

resource "google_kms_crypto_key" "dlp_key" {
  name     = "dlp-key"
  key_ring = google_kms_key_ring.dlp.id
  
  lifecycle {
    prevent_destroy = true
  }
}

# BigQuery column-level security
resource "google_bigquery_dataset_access" "column_level_security" {
  dataset_id = google_bigquery_dataset.onchain_data.dataset_id
  
  view {
    project_id = var.project_id
    dataset_id = google_bigquery_dataset.restricted_views.dataset_id
    table_id   = google_bigquery_table.redacted_events_view.table_id
  }
}

resource "google_bigquery_dataset" "restricted_views" {
  dataset_id  = "restricted_views"
  description = "Dataset with column-level access restricted views"
  location    = var.region

  access {
    role          = "OWNER"
    user_by_email = "admin@${var.project_id}.iam.gserviceaccount.com"
  }
}

resource "google_bigquery_table" "redacted_events_view" {
  dataset_id = google_bigquery_dataset.restricted_views.dataset_id
  table_id   = "redacted_events"

  view {
    query = <<EOF
SELECT 
  event_id,
  block_number,
  transaction_hash,
  CASE 
    WHEN '${google_service_account.api_gateway.email}' IN UNNEST(SPLIT(SESSION_USER(), '@'))
    THEN from_address 
    ELSE '[REDACTED]' 
  END as from_address,
  CASE 
    WHEN '${google_service_account.api_gateway.email}' IN UNNEST(SPLIT(SESSION_USER(), '@'))
    THEN to_address 
    ELSE '[REDACTED]' 
  END as to_address,
  value_usd,
  event_type,
  risk_score,
  labels,
  metadata,
  timestamp
FROM `${var.project_id}.${google_bigquery_dataset.onchain_data.dataset_id}.curated_events`
EOF
    use_legacy_sql = false
  }
}
