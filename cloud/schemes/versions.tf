terraform {
  required_version = "~> 1.6.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.10.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6.0"
    }
  }
}
