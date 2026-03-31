resource "google_storage_bucket" "main" {
  name     = "${var.project}-tf-backend"
  project  = var.project
  location = var.location

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  versioning {
    enabled = true
  }
}

resource "google_storage_bucket_iam_member" "main_storage_object_user" {
  bucket = google_storage_bucket.main.name
  member = "projectEditor:${var.project}"
  role   = "roles/storage.objectUser"
}
