resource "google_service_account" "github_action_users" {
  project      = var.project
  account_id   = "github-action-users"
  display_name = "Service account for update user GitHub action"
}

resource "google_project_iam_member" "github_action_users_service_account_token_creator" {
  project = var.project
  role    = "roles/iam.serviceAccountTokenCreator"
  member  = "serviceAccount:${google_service_account.github_action_users.email}"
}

resource "google_project_iam_member" "github_action_users_cloudsql_client" {
  project = var.project
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.github_action_users.email}"
}

resource "google_service_account_key" "github_action_users" {
  service_account_id = google_service_account.github_action_users.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}
