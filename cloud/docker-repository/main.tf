terraform {
  backend "gcs" {
    bucket = "dft-ate-schemes-prt-tf-backend"
    prefix = "docker-repository"
  }
}

provider "google" {
  project = local.project
}

locals {
  project  = "dft-ate-schemes-prt"
  location = "europe-west1"
}

resource "google_project_service" "artifact_registry" {
  service = "artifactregistry.googleapis.com"
}

resource "google_artifact_registry_repository" "main" {
  repository_id = "docker"
  location      = local.location

  format = "DOCKER"

  depends_on = [google_project_service.artifact_registry]
}

resource "google_service_account" "github_action" {
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

resource "google_service_account_key" "github_action" {
  service_account_id = google_service_account.github_action.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}
