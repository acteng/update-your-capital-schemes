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

resource "google_artifact_registry_repository" "main" {
  project       = local.project
  repository_id = "docker"
  location      = local.location

  format = "DOCKER"

  depends_on = [google_project_service.artifact_registry]
}

module "github_action" {
  source = "./github-action"
  project = local.project
}
