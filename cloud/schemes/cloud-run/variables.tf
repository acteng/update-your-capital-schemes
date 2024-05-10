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
}

variable "basic_auth" {
  description = "Whether to enable basic auth"
  type        = bool
}
