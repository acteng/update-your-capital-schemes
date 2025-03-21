output "url" {
  description = "Load balancer URL"
  value       = module.load_balancer.url
}

output "ip_address" {
  description = "Load balancer IP address"
  value       = module.load_balancer.ip_address
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

output "database_connection_name" {
  description = "Cloud SQL instance connection name"
  value       = module.cloud_sql.connection_name
}

output "database_password" {
  description = "Cloud SQL database password"
  value       = module.cloud_sql.password
  sensitive   = true
}
