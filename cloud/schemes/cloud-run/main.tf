resource "google_project_service" "run" {
  project = var.project
  service = "run.googleapis.com"
}

resource "google_service_account" "cloud_run_schemes" {
  account_id = "cloud-run-schemes"
}

resource "google_cloud_run_v2_service" "schemes" {
  name         = "schemes"
  project      = var.project
  location     = var.region
  launch_stage = "BETA"

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
            secret  = var.database_uri_secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "FLASK_BASIC_AUTH_USERNAME"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.basic_auth_username.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "FLASK_BASIC_AUTH_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.basic_auth_password.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "FLASK_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.api_key.secret_id
            version = "latest"
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
        instances = [var.database_connection_name]
      }
    }
    vpc_access {
      network_interfaces {
        subnetwork = google_compute_subnetwork.cloud_run.name
      }
      egress = "PRIVATE_RANGES_ONLY"
    }
    service_account = google_service_account.cloud_run_schemes.email
  }

  depends_on = [
    google_project_service.run,
    # secret key
    google_secret_manager_secret_version.secret_key,
    google_secret_manager_secret_iam_member.cloud_run_schemes_secret_key,
    # database URI
    var.database_uri_secret_version_id,
    google_secret_manager_secret_iam_member.cloud_run_schemes_database_uri,
    # basic auth username
    google_secret_manager_secret_iam_member.cloud_run_schemes_basic_auth_username,
    # basic auth password
    google_secret_manager_secret_iam_member.cloud_run_schemes_basic_auth_password,
    # api key
    google_secret_manager_secret_version.api_key,
    google_secret_manager_secret_iam_member.cloud_run_schemes_api_key,
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

resource "google_project_iam_member" "cloud_run_schemes_cloud_sql_client" {
  project = var.project
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run_schemes.email}"
}

resource "google_compute_subnetwork" "cloud_run" {
  name          = "cloud-run"
  ip_cidr_range = "10.1.0.0/24"
  region        = var.region
  network       = var.vpc_id
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

# database URI

resource "google_secret_manager_secret_iam_member" "cloud_run_schemes_database_uri" {
  member    = "serviceAccount:${google_service_account.cloud_run_schemes.email}"
  role      = "roles/secretmanager.secretAccessor"
  secret_id = var.database_uri_secret_id
}

# basic auth username

data "google_secret_manager_secret" "basic_auth_username" {
  secret_id = "basic-auth-username"
}

resource "google_secret_manager_secret_iam_member" "cloud_run_schemes_basic_auth_username" {
  member    = "serviceAccount:${google_service_account.cloud_run_schemes.email}"
  role      = "roles/secretmanager.secretAccessor"
  secret_id = data.google_secret_manager_secret.basic_auth_username.id
}

# basic auth password

data "google_secret_manager_secret" "basic_auth_password" {
  secret_id = "basic-auth-password"
}

resource "google_secret_manager_secret_iam_member" "cloud_run_schemes_basic_auth_password" {
  member    = "serviceAccount:${google_service_account.cloud_run_schemes.email}"
  role      = "roles/secretmanager.secretAccessor"
  secret_id = data.google_secret_manager_secret.basic_auth_password.id
}

# api key

resource "random_password" "api_key" {
  length  = 32
  special = false
}

resource "google_secret_manager_secret" "api_key" {
  secret_id = "api-key"

  replication {
    auto {
    }
  }
}

resource "google_secret_manager_secret_version" "api_key" {
  secret      = google_secret_manager_secret.api_key.id
  secret_data = random_password.api_key.result
}

resource "google_secret_manager_secret_iam_member" "cloud_run_schemes_api_key" {
  member    = "serviceAccount:${google_service_account.cloud_run_schemes.email}"
  role      = "roles/secretmanager.secretAccessor"
  secret_id = google_secret_manager_secret.api_key.id
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
