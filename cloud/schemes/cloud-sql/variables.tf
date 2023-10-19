variable "region" {
  description = "GCP region"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "vpc_private_ip_address_name" {
  description = "VPC private services IP address range name"
  type        = string
}
