output "database_uri_secret_id" {
  description = "Database URI secret ID"
  value       = google_secret_manager_secret.database_uri.id
}
