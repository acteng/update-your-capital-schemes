variable "region" {
  description = "GCP region"
  type        = string
}

variable "domain" {
  description = "Domain name for the SSL certificate"
  type        = string
}

variable "cloud_run_service_name" {
  description = "Cloud Run service name to load balance"
  type        = string
}
