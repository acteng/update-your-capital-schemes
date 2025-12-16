terraform {
  required_version = "~> 1.14.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.13.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.7.0"
    }
  }
}
