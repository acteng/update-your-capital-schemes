variable "project" {
  description = "GCP project"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "database_backups" {
  description = "Whether to enable database backups"
  type        = bool
}
