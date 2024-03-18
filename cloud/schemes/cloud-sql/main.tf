resource "google_project_service" "sql_admin" {
  service = "sqladmin.googleapis.com"
}

resource "google_sql_database_instance" "main" {
  name   = "schemes"
  region = var.region

  database_version = "POSTGRES_15"

  settings {
    tier = "db-f1-micro"

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

resource "google_secret_manager_secret" "database_uri" {
  secret_id = "database-uri"

  replication {
    auto {
    }
  }
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

resource "google_secret_manager_secret_version" "database_uri" {
  secret = google_secret_manager_secret.database_uri.id
  secret_data = join("", [
    "postgresql+pg8000://",
    google_sql_user.schemes.name,
    ":",
    random_password.schemes.result,
    "@",
    google_sql_database_instance.main.private_ip_address,
    "/",
    google_sql_database.schemes.name
  ])
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
