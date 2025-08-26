terraform {
  required_version = "~> 1.13.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.42.0"
    }
  }
}
