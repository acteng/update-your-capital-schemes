resource "google_compute_global_address" "schemes" {
  name = "schemes"
}

resource "google_compute_managed_ssl_certificate" "schemes" {
  name = "schemes"

  managed {
    domains = [var.domain]
  }
}

resource "google_compute_region_network_endpoint_group" "schemes" {
  name                  = "schemes"
  region                = var.region
  network_endpoint_type = "SERVERLESS"

  cloud_run {
    service = var.cloud_run_service_name
  }
}

resource "google_compute_backend_service" "schemes" {
  name                  = "schemes"
  load_balancing_scheme = "EXTERNAL_MANAGED"

  backend {
    group = google_compute_region_network_endpoint_group.schemes.id
  }
}

resource "google_compute_url_map" "schemes" {
  name            = "schemes"
  default_service = google_compute_backend_service.schemes.id
}

resource "google_compute_ssl_policy" "schemes" {
  name    = "schemes"
  profile = "RESTRICTED"
}

resource "google_compute_target_https_proxy" "schemes" {
  name             = "schemes"
  url_map          = google_compute_url_map.schemes.id
  ssl_certificates = [google_compute_managed_ssl_certificate.schemes.id]
  ssl_policy       = google_compute_ssl_policy.schemes.id
}

resource "google_compute_global_forwarding_rule" "schemes_https" {
  name                  = "schemes-https"
  ip_address            = google_compute_global_address.schemes.id
  target                = google_compute_target_https_proxy.schemes.id
  port_range            = "443"
  load_balancing_scheme = "EXTERNAL_MANAGED"
}
