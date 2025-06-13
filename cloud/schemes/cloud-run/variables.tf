variable "project" {
  description = "GCP project"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "docker_repository_project" {
  description = "Docker repository GCP project"
  type        = string
}

variable "docker_repository_url" {
  description = "Docker repository URL"
  type        = string
}

variable "env" {
  description = "App environment"
  type        = string
}

variable "database_connection_name" {
  description = "Database connection name"
  type        = string
}

variable "database_name" {
  description = "Database name"
  type        = string
}

variable "database_username" {
  description = "Database username"
  type        = string
}

variable "database_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "capital_schemes_database_project" {
  description = "Capital schemes database GCP project"
  type        = string
}

variable "capital_schemes_database_connection_name" {
  description = "Capital schemes database connection name"
  type        = string
}

variable "capital_schemes_database_name" {
  description = "Capital schemes database name"
  type        = string
}

variable "capital_schemes_database_username" {
  description = "Capital schemes database username"
  type        = string
}

variable "capital_schemes_database_password" {
  description = "Capital schemes database password"
  type        = string
  sensitive   = true
}

variable "keep_idle" {
  description = "Whether to keep an instance idle to prevent cold starts"
  type        = bool
}

variable "basic_auth" {
  description = "Whether to enable basic auth"
  type        = bool
}

variable "ate_api_url" {
  description = "ATE API URL"
  type        = string
}

variable "ate_api_client_id" {
  description = "ATE API client id"
  type        = string
}

variable "ate_api_client_secret" {
  description = "ATE API client secret"
  type        = string
  sensitive   = true
}

variable "ate_api_server_metadata_url" {
  description = "ATE API OIDC configuration URL"
  type        = string
}

variable "ate_api_audience" {
  description = "ATE API OIDC audience"
  type        = string
}

variable "monitoring" {
  description = "Whether to enable monitoring"
  type        = bool
}

variable "domain" {
  description = "Domain name to monitor"
  type        = string
}
