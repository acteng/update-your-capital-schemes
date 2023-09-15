output "url" {
  description = "Cloud Run service URL"
  value       = google_cloud_run_v2_service.main.uri
}
