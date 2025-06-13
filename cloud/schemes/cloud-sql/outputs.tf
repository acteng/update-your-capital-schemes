output "connection_name" {
  description = "Database connection name"
  value       = google_sql_database_instance.main.connection_name
}

output "name" {
  description = "Database name"
  value       = google_sql_database.schemes.name
}

output "username" {
  description = "Database username"
  value       = google_sql_user.schemes.name
}

output "password" {
  description = "Database password"
  value       = google_sql_user.schemes.password
  sensitive   = true
}
