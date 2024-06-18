resource "google_project_service" "run" {
  project = var.project
  service = "run.googleapis.com"
}

resource "google_service_account" "cloud_run_schemes" {
  account_id = "cloud-run-schemes"
}

resource "google_cloud_run_v2_service" "schemes" {
  name     = "schemes"
  project  = var.project
  location = var.region

  template {
    containers {
      image = "europe-west1-docker.pkg.dev/dft-schemes-common/docker/schemes"
      env {
        name  = "FLASK_ENV"
        value = var.env
      }
      env {
        name = "FLASK_SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.secret_key.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "FLASK_SQLALCHEMY_DATABASE_URI"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.database_uri.id
            version = "latest"
          }
        }
      }
      env {
        name = "FLASK_CAPITAL_SCHEMES_DATABASE_URI"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.capital_schemes_database_uri.id
            version = "latest"
          }
        }
      }
      dynamic "env" {
        for_each = var.basic_auth ? [1] : []
        content {
          name = "FLASK_BASIC_AUTH_USERNAME"
          value_source {
            secret_key_ref {
              secret  = data.google_secret_manager_secret.basic_auth_username[0].secret_id
              version = "latest"
            }
          }
        }
      }
      dynamic "env" {
        for_each = var.basic_auth ? [1] : []
        content {
          name = "FLASK_BASIC_AUTH_PASSWORD"
          value_source {
            secret_key_ref {
              secret  = data.google_secret_manager_secret.basic_auth_password[0].secret_id
              version = "latest"
            }
          }
        }
      }
      env {
        name = "FLASK_GOVUK_CLIENT_SECRET"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.govuk_client_secret.secret_id
            version = "latest"
          }
        }
      }
      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
    }
    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [
          var.database_connection_name,
          var.capital_schemes_database_connection_name,
        ]
      }
    }
    scaling {
      min_instance_count = var.keep_idle ? 1 : 0
      max_instance_count = 10
    }
    service_account = google_service_account.cloud_run_schemes.email
  }

  depends_on = [
    google_project_service.run,
    # secret key
    google_secret_manager_secret_version.secret_key,
    google_secret_manager_secret_iam_member.cloud_run_schemes_secret_key,
    # database URI
    google_secret_manager_secret_version.database_uri,
    google_secret_manager_secret_iam_member.cloud_run_schemes_database_uri,
    # capital schemes database URI,
    google_secret_manager_secret_version.capital_schemes_database_uri,
    google_secret_manager_secret_iam_member.cloud_run_schemes_capital_schemes_database_uri,
    # basic auth username
    google_secret_manager_secret_iam_member.cloud_run_schemes_basic_auth_username,
    # basic auth password
    google_secret_manager_secret_iam_member.cloud_run_schemes_basic_auth_password,
    # govuk client secret
    google_secret_manager_secret_iam_member.cloud_run_schemes_govuk_client_secret
  ]
}

resource "google_cloud_run_v2_service_iam_binding" "schemes_run_invoker" {
  name     = google_cloud_run_v2_service.schemes.name
  project  = var.project
  location = var.region

  role = "roles/run.invoker"
  members = [
    "allUsers"
  ]
}

data "google_project" "main" {
  project_id = var.project
}

resource "google_project_iam_member" "cloud_run_artifact_registry_reader" {
  project = "dft-schemes-common"
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:service-${data.google_project.main.number}@serverless-robot-prod.iam.gserviceaccount.com"

  depends_on = [google_project_service.run]
}

# secret key

resource "random_password" "secret_key" {
  length  = 32
  special = false
}

resource "google_secret_manager_secret" "secret_key" {
  secret_id = "secret-key"

  replication {
    auto {
    }
  }
}

resource "google_secret_manager_secret_version" "secret_key" {
  secret      = google_secret_manager_secret.secret_key.id
  secret_data = random_password.secret_key.result
}

resource "google_secret_manager_secret_iam_member" "cloud_run_schemes_secret_key" {
  member    = "serviceAccount:${google_service_account.cloud_run_schemes.email}"
  role      = "roles/secretmanager.secretAccessor"
  secret_id = google_secret_manager_secret.secret_key.id
}

# database

resource "google_project_iam_member" "cloud_run_schemes_cloud_sql_client" {
  project = var.project
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run_schemes.email}"
}

resource "google_secret_manager_secret" "database_uri" {
  secret_id = "database-uri"

  replication {
    auto {
    }
  }
}

resource "google_secret_manager_secret_version" "database_uri" {
  secret = google_secret_manager_secret.database_uri.id
  secret_data = join("", [
    "postgresql+pg8000://",
    var.database_username,
    ":",
    var.database_password,
    "@/",
    var.database_name,
    "?unix_sock=/cloudsql/",
    var.database_connection_name,
    "/.s.PGSQL.5432"
  ])
}

resource "google_secret_manager_secret_iam_member" "cloud_run_schemes_database_uri" {
  member    = "serviceAccount:${google_service_account.cloud_run_schemes.email}"
  role      = "roles/secretmanager.secretAccessor"
  secret_id = google_secret_manager_secret.database_uri.id
}

# capital schemes database

resource "google_project_iam_member" "cloud_run_schemes_schemes_database_cloud_sql_client" {
  project = var.capital_schemes_database_project
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run_schemes.email}"
}

resource "google_secret_manager_secret" "capital_schemes_database_uri" {
  secret_id = "capital-schemes-database-uri"

  replication {
    auto {
    }
  }
}

resource "google_secret_manager_secret_version" "capital_schemes_database_uri" {
  secret = google_secret_manager_secret.capital_schemes_database_uri.id
  secret_data = join("", [
    "postgresql+pg8000://",
    var.capital_schemes_database_username,
    ":",
    var.capital_schemes_database_password,
    "@/",
    var.capital_schemes_database_name,
    "?unix_sock=/cloudsql/",
    var.capital_schemes_database_connection_name,
    "/.s.PGSQL.5432"
  ])
}

resource "google_secret_manager_secret_iam_member" "cloud_run_schemes_capital_schemes_database_uri" {
  member    = "serviceAccount:${google_service_account.cloud_run_schemes.email}"
  role      = "roles/secretmanager.secretAccessor"
  secret_id = google_secret_manager_secret.capital_schemes_database_uri.id
}

# basic auth username

data "google_secret_manager_secret" "basic_auth_username" {
  count = var.basic_auth ? 1 : 0

  secret_id = "basic-auth-username"
}

resource "google_secret_manager_secret_iam_member" "cloud_run_schemes_basic_auth_username" {
  count = var.basic_auth ? 1 : 0

  member    = "serviceAccount:${google_service_account.cloud_run_schemes.email}"
  role      = "roles/secretmanager.secretAccessor"
  secret_id = data.google_secret_manager_secret.basic_auth_username[0].id
}

# basic auth password

data "google_secret_manager_secret" "basic_auth_password" {
  count = var.basic_auth ? 1 : 0

  secret_id = "basic-auth-password"
}

resource "google_secret_manager_secret_iam_member" "cloud_run_schemes_basic_auth_password" {
  count = var.basic_auth ? 1 : 0

  member    = "serviceAccount:${google_service_account.cloud_run_schemes.email}"
  role      = "roles/secretmanager.secretAccessor"
  secret_id = data.google_secret_manager_secret.basic_auth_password[0].id
}

# govuk client secret

data "google_secret_manager_secret" "govuk_client_secret" {
  secret_id = "govuk-client-secret"
}

resource "google_secret_manager_secret_iam_member" "cloud_run_schemes_govuk_client_secret" {
  member    = "serviceAccount:${google_service_account.cloud_run_schemes.email}"
  role      = "roles/secretmanager.secretAccessor"
  secret_id = data.google_secret_manager_secret.govuk_client_secret.id
}
