resource "google_service_account" "main" {
  project      = var.project
  account_id   = "github-action-database"
  display_name = "Service account for database GitHub Action"
}

resource "google_project_iam_member" "service_account_token_creator" {
  project = var.project
  role    = "roles/iam.serviceAccountTokenCreator"
  member  = "serviceAccount:${google_service_account.main.email}"
}

resource "google_project_iam_member" "cloudsql_client" {
  project = var.project
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.main.email}"
}

resource "google_service_account_key" "main" {
  service_account_id = google_service_account.main.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}
