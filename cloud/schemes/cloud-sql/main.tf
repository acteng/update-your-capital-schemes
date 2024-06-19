resource "google_project_service" "sql_admin" {
  service = "sqladmin.googleapis.com"
}

resource "google_sql_database_instance" "main" {
  name   = "schemes"
  region = var.region

  database_version = "POSTGRES_15"

  settings {
    tier                  = "db-custom-1-3840"
    connector_enforcement = "REQUIRED"

    backup_configuration {
      enabled                        = var.database_backups
      point_in_time_recovery_enabled = var.database_backups
      start_time                     = "21:00"
      transaction_log_retention_days = 7

      backup_retention_settings {
        retained_backups = 30
      }
    }

    ip_configuration {
      ipv4_enabled = true
      require_ssl  = true
      ssl_mode     = "TRUSTED_CLIENT_CERTIFICATE_REQUIRED"
    }
  }
}

resource "google_sql_database" "schemes" {
  name     = "schemes"
  instance = google_sql_database_instance.main.name
}

resource "random_password" "schemes" {
  length  = 32
  special = false
}

resource "google_sql_user" "schemes" {
  name     = "schemes"
  instance = google_sql_database_instance.main.name

  password = random_password.schemes.result
}

resource "google_service_account" "cloud_sql_schemes" {
  account_id = "cloud-sql-schemes"
}

resource "google_project_iam_member" "cloud_sql_schemes_cloud_sql_client" {
  member  = "serviceAccount:${google_service_account.cloud_sql_schemes.email}"
  role    = "roles/cloudsql.client"
  project = var.project
}

resource "google_service_account_key" "cloud_sql_schemes" {
  service_account_id = google_service_account.cloud_sql_schemes.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

resource "google_secret_manager_secret" "database_private_key" {
  secret_id = "database-private-key"

  replication {
    auto {
    }
  }
}

resource "google_secret_manager_secret_version" "database_private_key" {
  secret      = google_secret_manager_secret.database_private_key.id
  secret_data = google_service_account_key.cloud_sql_schemes.private_key
}
