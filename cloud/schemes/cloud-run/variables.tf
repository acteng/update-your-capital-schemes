variable "project" {
  description = "GCP project"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "env" {
  description = "App environment"
  type        = string
}

variable "database_uri_secret_id" {
  description = "Database URI secret ID"
  type        = string
}

variable "database_uri_secret_version_id" {
  description = "Database URI secret version ID"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}