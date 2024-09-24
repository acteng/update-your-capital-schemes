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
  security_policy       = google_compute_security_policy.schemes.id

  backend {
    group = google_compute_region_network_endpoint_group.schemes.id
  }

  log_config {
    enable = true
  }
}

resource "google_compute_url_map" "schemes" {
  name            = "schemes"
  default_service = google_compute_backend_service.schemes.id
}

resource "google_compute_ssl_policy" "schemes" {
  name            = "schemes"
  profile         = "RESTRICTED"
  min_tls_version = "TLS_1_2"
}

resource "google_compute_target_https_proxy" "schemes_https" {
  name             = "schemes-https"
  url_map          = google_compute_url_map.schemes.id
  ssl_certificates = [google_compute_managed_ssl_certificate.schemes.id]
  ssl_policy       = google_compute_ssl_policy.schemes.id
}

resource "google_compute_global_forwarding_rule" "schemes_https" {
  name                  = "schemes-https"
  ip_address            = google_compute_global_address.schemes.id
  target                = google_compute_target_https_proxy.schemes_https.id
  port_range            = "443"
  load_balancing_scheme = "EXTERNAL_MANAGED"
}

# HTTP-to-HTTPS redirect

resource "google_compute_url_map" "https_redirect" {
  name = "schemes-https-redirect"

  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }
}

resource "google_compute_target_http_proxy" "schemes_http" {
  name    = "schemes-http"
  url_map = google_compute_url_map.https_redirect.id
}

resource "google_compute_global_forwarding_rule" "schemes_http" {
  name                  = "schemes-http"
  ip_address            = google_compute_global_address.schemes.id
  target                = google_compute_target_http_proxy.schemes_http.id
  port_range            = "80"
  load_balancing_scheme = "EXTERNAL_MANAGED"
}

# Cloud Armor

resource "google_compute_security_policy" "schemes" {
  name = "schemes"

  rule {
    description = "Block malicious IPs"
    action      = "deny(403)"
    priority    = 0
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["45.159.248.69"]
      }
    }
  }

  rule {
    description = "SQL injection"
    action      = "deny(403)"
    priority    = 1000
    match {
      expr {
        expression = "evaluatePreconfiguredWaf('sqli-v33-stable', {'sensitivity': 1})"
      }
    }
  }

  rule {
    description = "Cross-site scripting"
    action      = "deny(403)"
    priority    = 1001
    match {
      expr {
        expression = "evaluatePreconfiguredWaf('xss-v33-stable', {'sensitivity': 1})"
      }
    }
  }

  rule {
    description = "default rule"
    action      = "allow"
    priority    = 2147483647
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
  }
}
