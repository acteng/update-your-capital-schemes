output "private_key" {
  description = "Service account key for github action service account"
  value       = google_service_account_key.github_action.private_key
  sensitive   = true
}
