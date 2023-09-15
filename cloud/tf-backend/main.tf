locals {
  location = "europe-west1"
  project  = "dft-ate-schemes-prt"
}

resource "google_storage_bucket" "main" {
  name     = "dft-ate-schemes-prt-tf-backend"
  location = local.location
  project  = local.project

  public_access_prevention = "enforced"

  versioning {
    enabled = true
  }
}
