variable "project" {
  description = "GCP Project"
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
