output "database_uri_secret_id" {
  description = "Database URI secret ID"
  value       = google_secret_manager_secret.database_uri.id
}

output "database_uri_secret_version_id" {
  description = "Database URI secret version ID"
  value       = google_secret_manager_secret_version.database_uri.id
}
