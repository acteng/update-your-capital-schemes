output "url" {
  description = "Cloud Run service URL"
  value       = google_cloud_run_v2_service.schemes.uri
}

output "github_action_private_key" {
  description = "Service account key for github action service account"
  value       = module.github_action.private_key
  sensitive   = true
}
