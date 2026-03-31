variable "project_prefix" {
  description = "GCP project prefix"
  type        = string
  default     = "dft-schemes"
}

variable "database_project_prefix" {
  description = "Database GCP project prefix"
  type        = string
  default     = "dft-ate-capitalschemes"
}

variable "ate_api_project_prefix" {
  description = "ATE API GCP project prefix"
  type        = string
  default     = "dft-ate-api"
}

variable "location" {
  description = "GCP location"
  type        = string
  default     = "europe-west1"
}
