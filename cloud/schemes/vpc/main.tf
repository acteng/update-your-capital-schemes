resource "google_project_service" "compute" {
  service = "compute.googleapis.com"
}

resource "google_project_service" "service_networking" {
  service = "servicenetworking.googleapis.com"
}

resource "google_compute_network" "main" {
  name                    = "schemes"
  auto_create_subnetworks = false

  depends_on = [google_project_service.compute]
}

resource "google_compute_global_address" "private_ip_address" {
  name    = "private-ip-address"
  network = google_compute_network.main.id

  address_type  = "INTERNAL"
  purpose       = "VPC_PEERING"
  prefix_length = 16
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]

  depends_on = [google_project_service.service_networking]
}
