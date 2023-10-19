output "id" {
  description = "VPC ID"
  value       = google_compute_network.main.id
}

output "private_ip_address_name" {
  description = "VPC private services IP address range name"
  value       = google_compute_global_address.private_ip_address.name
}
