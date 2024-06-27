terraform {
  backend "gcs" {
    bucket = "dft-schemes-common-tf-backend"
    prefix = "docker-repository"
  }
}

locals {
  project        = "dft-schemes-common"
  location       = "europe-west1"
  day_in_seconds = 24 * 60 * 60
}

resource "google_project_service" "iam_credentials" {
  project = local.project
  service = "iamcredentials.googleapis.com"
}

resource "google_project_service" "artifact_registry" {
  project = local.project
  service = "artifactregistry.googleapis.com"
}

resource "google_project_service" "container_scanning" {
  project = local.project
  service = "containerscanning.googleapis.com"
}

resource "google_project_iam_audit_config" "artifact_registry_data_write" {
  project = local.project
  service = "artifactregistry.googleapis.com"

  audit_log_config {
    log_type = "DATA_WRITE"
  }
}

resource "google_artifact_registry_repository" "main" {
  project       = local.project
  repository_id = "docker"
  location      = local.location
  format        = "DOCKER"

  cleanup_policies {
    id     = "delete-untagged"
    action = "DELETE"
    condition {
      tag_state = "UNTAGGED"
    }
  }

  cleanup_policies {
    id     = "keep-recent-untagged"
    action = "KEEP"
    condition {
      tag_state  = "UNTAGGED"
      newer_than = "${7 * local.day_in_seconds}s"
    }
  }

  depends_on = [google_project_service.artifact_registry]
}

module "github_action_push" {
  source  = "./github-action-push"
  project = local.project
}
