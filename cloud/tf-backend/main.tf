locals {
  project  = "dft-ate-schemes"
  location = "europe-west1"
}

resource "google_storage_bucket" "main" {
  name     = "dft-ate-schemes-tf-backend"
  project  = local.project
  location = local.location

  public_access_prevention = "enforced"

  versioning {
    enabled = true
  }
}
