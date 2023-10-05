terraform {
  required_version = "~> 1.6.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.82.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5.0"
    }
  }
}
