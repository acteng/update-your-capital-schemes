provider "google" {
  project = "dft-ate-schemes"
}

locals {
  location = "europe-west1"
}

resource "google_storage_bucket" "main" {
  name     = "dft-ate-schemes-tf-backend"
  location = local.location

  public_access_prevention = "enforced"

  versioning {
    enabled = true
  }
}
