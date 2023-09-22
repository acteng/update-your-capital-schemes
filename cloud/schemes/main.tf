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
      image = "${local.location}-docker.pkg.dev/${local.project}/docker/schemes"
    }
  }

  depends_on = [google_project_service.run]
}

resource "google_cloud_run_v2_service_iam_binding" "schemes_run_invoker" {
  name     = google_cloud_run_v2_service.schemes.name
  location = local.location

  role    = "roles/run.invoker"
  members = [
    "allUsers"
  ]
}
