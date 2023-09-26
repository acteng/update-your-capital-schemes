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
  location = var.location

  template {
    containers {
      image = "europe-west1-docker.pkg.dev/dft-ate-schemes/docker/schemes"
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
    }
    service_account = google_service_account.cloud_run_schemes.email
  }

  depends_on = [google_project_service.run]
}

resource "google_cloud_run_v2_service_iam_binding" "schemes_run_invoker" {
  name     = google_cloud_run_v2_service.schemes.name
  project  = var.project
  location = var.location

  role = "roles/run.invoker"
  members = [
    "allUsers"
  ]
}

data "google_project" "main" {
  project_id = var.project
}

resource "google_project_iam_member" "cloud_run_artifact_registry_reader" {
  project = "dft-ate-schemes"
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:service-${data.google_project.main.number}@serverless-robot-prod.iam.gserviceaccount.com"

  depends_on = [google_project_service.run]
}

data "google_secret_manager_secret" "basic_auth_username" {
  secret_id = "basic-auth-username"
}

resource "google_secret_manager_secret_iam_member" "cloud_run_schemes_basic_auth_username" {
  member    = "serviceAccount:${google_service_account.cloud_run_schemes.email}"
  role      = "roles/secretmanager.secretAccessor"
  secret_id = data.google_secret_manager_secret.basic_auth_username.id
}

data "google_secret_manager_secret" "basic_auth_password" {
  secret_id = "basic-auth-password"
}

resource "google_secret_manager_secret_iam_member" "cloud_run_schemes_basic_auth_password" {
  member    = "serviceAccount:${google_service_account.cloud_run_schemes.email}"
  role      = "roles/secretmanager.secretAccessor"
  secret_id = data.google_secret_manager_secret.basic_auth_password.id
}
