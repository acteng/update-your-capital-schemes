output "url" {
  description = "Cloud Run service URL"
  value       = module.cloud_run.url
}

output "github_action_deploy_private_key" {
  description = "Service account key for deploy GitHub Action service account"
  value       = module.github_action_deploy.private_key
  sensitive   = true
}

output "github_action_database_private_key" {
  description = "Service account key for database GitHub Action service account"
  value       = module.github_action_database.private_key
  sensitive   = true
}
