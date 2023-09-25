resource "google_project_service" "compute" {
  project = var.project
  service = "compute.googleapis.com"
}

resource "google_service_account" "github_action" {
  project      = var.project
  account_id   = "github-action"
  display_name = "Service account for use within GitHub actions"
}

resource "google_project_iam_member" "github_action_service_account_token_creator" {
  project = var.project
  role    = "roles/iam.serviceAccountTokenCreator"
  member  = "serviceAccount:${google_service_account.github_action.email}"
}

resource "google_project_iam_member" "github_action_artifact_registry_writer" {
  project = var.project
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.github_action.email}"
}

resource "google_service_account_key" "github_action" {
  service_account_id = google_service_account.github_action.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}