terraform {
  required_version = "~> 1.10.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.18.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6.0"
    }
  }
}
