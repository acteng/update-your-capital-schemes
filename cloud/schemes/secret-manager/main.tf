resource "google_project_service" "secret_manager" {
  project = var.project
  service = "secretmanager.googleapis.com"
}
