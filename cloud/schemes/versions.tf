terraform {
  required_version = "~> 1.6.0"

  required_providers {
    bitwarden = {
      source  = "maxlaverse/bitwarden"
      version = "~> 0.7.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 5.8.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6.0"
    }
  }
}
