terraform {
  backend "gcs" {
    bucket = "dft-ate-schemes-prt-tf-backend"
    prefix = "docker-repository"
  }
}

provider "google" {
  project = "dft-ate-schemes-prt"
}

locals {
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
