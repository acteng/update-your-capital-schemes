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

resource "google_project_iam_member" "github_action_run_admin" {
  project = var.project
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.github_action.email}"
}

data "google_compute_default_service_account" "main" {
  project    = var.project
  depends_on = [google_project_service.compute]
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