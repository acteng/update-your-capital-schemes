output "url" {
  description = "Cloud Run service URL"
  value       = module.cloud_run.url
}

output "github_action_private_key" {
  description = "Service account key for github action service account"
  value       = module.github_action.private_key
  sensitive   = true
}

output "api_key" {
  description = "Schemes API key"
  value       = module.cloud_run.api_key
  sensitive   = true
}
