output "ip_address" {
  description = "Load balancer IP address"
  value       = google_compute_global_address.schemes.address
}
