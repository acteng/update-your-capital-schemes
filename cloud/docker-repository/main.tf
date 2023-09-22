terraform {
  backend "gcs" {
    bucket = "dft-ate-schemes-tf-backend"
    prefix = "docker-repository"
  }
}

locals {
  project  = "dft-ate-schemes-prt"
  location = "europe-west1"
}

resource "google_project_service" "iam_credentials" {
  project = local.project
  service = "iamcredentials.googleapis.com"
}

resource "google_project_service" "artifact_registry" {
  project = local.project
  service = "artifactregistry.googleapis.com"
}

resource "google_project_service" "compute" {
  project = local.project
  service = "compute.googleapis.com"
}

data "google_compute_default_service_account" "main" {
  project    = local.project
  depends_on = [google_project_service.compute]
}

resource "google_artifact_registry_repository" "main" {
  project       = local.project
  repository_id = "docker"
  location      = local.location

  format = "DOCKER"

  depends_on = [google_project_service.artifact_registry]
}

resource "google_service_account" "github_action" {
  project      = local.project
  account_id   = "github-action"
  display_name = "Service account for use within GitHub actions"
}

resource "google_project_iam_member" "github_action_service_account_token_creator" {
  project = local.project
  role    = "roles/iam.serviceAccountTokenCreator"
  member  = "serviceAccount:${google_service_account.github_action.email}"
}

resource "google_project_iam_member" "github_action_artifact_registry_writer" {
  project = local.project
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.github_action.email}"
}

resource "google_project_iam_member" "github_action_run_admin" {
  project = local.project
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.github_action.email}"
}

resource "google_service_account_iam_member" "github_action_service_account_user" {
  service_account_id = data.google_compute_default_service_account.main.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.github_action.email}"
}

resource "google_service_account_key" "github_action" {
  service_account_id = google_service_account.github_action.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}
