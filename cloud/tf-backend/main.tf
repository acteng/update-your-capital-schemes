locals {
  project  = "dft-ate-schemes"
  location = "europe-west1"
}

resource "google_storage_bucket" "main" {
  name     = "dft-ate-schemes-tf-backend"
  project  = local.project
  location = local.location

  uniform_bucket_level_access = true
  public_access_prevention = "enforced"

  versioning {
    enabled = true
  }
}

resource "google_storage_bucket_iam_member" "main_storage_object_user" {
  bucket = google_storage_bucket.main.name
  member = "projectEditor:${local.project}"
  role   = "roles/storage.objectUser"
}
