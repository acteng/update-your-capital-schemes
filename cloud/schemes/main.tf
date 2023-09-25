terraform {
  backend "gcs" {
    bucket = "dft-ate-schemes-tf-backend"
    prefix = "schemes"
  }
}

provider "google" {
  project = local.project
}

locals {
  project  = "dft-ate-schemes-prt"
  location = "europe-west1"
}

module "cloud_run" {
  source = "./cloud-run"
  location = local.location
}

module "github_action" {
  source = "./github-action"
  project = local.project
}
