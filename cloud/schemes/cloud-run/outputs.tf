output "url" {
  description = "Cloud Run service URL"
  value       = google_cloud_run_v2_service.schemes.uri
}

output "service_account_id" {
  description = "Cloud Run Service Account ID"
  value       = google_service_account.cloud_run_schemes.id
}