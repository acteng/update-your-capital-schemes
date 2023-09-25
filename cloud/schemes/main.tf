terraform {
  backend "gcs" {
    bucket = "dft-ate-schemes-tf-backend"
    prefix = "schemes"
  }
}

provider "google" {
  project = local.project
}

locals {
  project  = "dft-ate-schemes-prt"
  location = "europe-west1"
}

resource "google_project_service" "run" {
  service = "run.googleapis.com"
}

resource "google_cloud_run_v2_service" "schemes" {
  name     = "schemes"
  location = local.location

  template {
    containers {
      image = "europe-west1-docker.pkg.dev/dft-ate-schemes/docker/schemes"
    }
  }

  depends_on = [google_project_service.run]
}

resource "google_cloud_run_v2_service_iam_binding" "schemes_run_invoker" {
  name     = google_cloud_run_v2_service.schemes.name
  location = local.location

  role = "roles/run.invoker"
  members = [
    "allUsers"
  ]
}

data "google_project" "main" {
}

resource "google_project_iam_member" "cloud_run_artifact_registry_reader" {
  project = "dft-ate-schemes"
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:service-${data.google_project.main.number}@serverless-robot-prod.iam.gserviceaccount.com"

  depends_on = [google_project_service.run]
}

module "github_action" {
  source = "./github-action"
  project = local.project
}
